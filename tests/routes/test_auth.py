import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Response, session

import app
from app.main.middleware.error_handler import AuthTokenError
from app.main.routes.auth import (
    process_user_session,
    send_github_invitation,
    user_email_allowed,
    user_is_valid,
)
from app.main.services.github_service import GithubService


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = app.create_app(self.github_service, False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.app.config["SECRET_KEY"] = "my_precious_test_key"
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    @patch("app.main.routes.auth.oauth.auth0.authorize_redirect")
    def test_login_route(self, mock_authorize_redirect):
        mock_response = Response(status=302, headers={'Location': 'mock://auth0.redirect'})
        mock_authorize_redirect.return_value = mock_response

        response = self.client.get("/auth/login")
        self.assertEqual(response.status_code, 302)
        mock_authorize_redirect.assert_called_once()

    @patch(
        "app.main.routes.auth.app_config",
        new=SimpleNamespace(
            auth0=SimpleNamespace(client_id="test_id", domain="auth0.com")
        ),
    )
    def test_logout_route_redirects_and_clears_session_data(self):
        with self.client.session_transaction() as session:
            session["user"] = {"some": "data"}

        response = self.client.get("/auth/logout")

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("user", session)
        self.assertIn("auth0.com/v2/logout", response.headers["Location"])

    @patch("app.main.routes.join.invitation_sent")
    @patch("app.main.routes.auth.send_github_invitation", return_value=True)
    @patch("app.main.routes.auth.process_user_session", return_value=True)
    @patch("app.main.routes.auth.get_token")
    def test_callback_route_success(self, mock_get_token, mock_process_user_session,
                                    mock_send_github_invitation, mock_invitation_sent):
        mock_get_token.return_value = {'userinfo': {'email': 'test@example.com'}}
        mock_invitation_sent.return_value = Response(status=302)

        with self.client as c:
            with c.session_transaction() as sess:
                sess["org_selection"] = ["some-org"]

            response = self.client.get("/auth/callback")

        self.assertEqual(response.status_code, 302)
        self.assertIn('join/invitation-sent', response.headers['Location'])
        mock_get_token.assert_called_once()
        mock_process_user_session.assert_called_once()
        mock_send_github_invitation.assert_called_once()

    @patch("app.main.routes.auth.get_token")
    def test_callback_route_token_failure(self, mock_get_token):
        mock_get_token.side_effect = AuthTokenError("Token error")

        response = self.client.get("/auth/callback")
        self.assertIn('/auth/server-error', response.headers['Location'])
        self.assertEqual(response.status_code, 302)
        mock_get_token.assert_called_once()

    @patch("app.main.routes.auth.app_config.github.allowed_email_domains",
           new=["example.com", "test.com"])
    def test_process_user_session_success(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['user_input_email'] = 'user@test.com'
            session['org_selection'] = ['some_org']

            result = process_user_session()
            self.assertTrue(result)

    def test_process_user_session_without_session(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': ''}}
            session['email'] = ''
            session['org_selection'] = ['']

            result = process_user_session()
            self.assertFalse(result)

    def test_process_user_session_without_approved_email(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test.com'
            session['org_selection'] = ['some_org']

            result = process_user_session()
            self.assertFalse(result)

    @patch("app.main.routes.auth.app_config.github.allowed_email_domains",
           new=["example.com", "test.com"])
    def test_process_user_session_with_mismatched_user_email(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test2.com'
            session['org_selection'] = ['some_org']

            result = process_user_session()
            self.assertFalse(result)

    @patch("app.main.routes.auth.app_config.github.allowed_email_domains",
           new=["example.com", "test.com"])
    def test_process_user_session_with_missing_org_selection(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test.com'
            session['org_selection'] = []

            result = process_user_session()
            self.assertFalse(result)

    def test_send_github_invitation_success(self):
        self.app.github_service.send_invites_to_user_email = MagicMock(return_value=None)

        result = send_github_invitation("test@example.com", ["org1", "org2"])

        self.assertTrue(result)

        self.app.github_service.send_invites_to_user_email.assert_called_once_with("test@example.com", ["org1", "org2"])

    def test_send_github_invitation_fail(self):
        self.app.github_service.send_invites_to_user_email = MagicMock(side_effect=Exception("Some error"))

        result = send_github_invitation("test@example.com", ["org1", "org2"])

        self.assertFalse(result)


class TestUserValidation(unittest.TestCase):
    @patch("app.main.routes.auth.user_email_allowed", return_value=True)
    def test_user_is_valid_matching_emails(self, mock_user_email_allowed):
        self.assertTrue(user_is_valid("test@example.com", "test@example.com"))

    @patch("app.main.routes.auth.user_email_allowed", return_value=False)
    def test_user_is_valid_non_matching_emails(self, mock_user_email_allowed):
        self.assertFalse(user_is_valid("test@example.com", "other@example.com"))


class TestEmailAllowed(unittest.TestCase):
    @patch("app.main.routes.auth.app_config.github.allowed_email_domains", new=["example.com"])
    def test_user_email_allowed(self):
        self.assertTrue(user_email_allowed("user@example.com"))
        self.assertFalse(user_email_allowed("user@notallowed.com"))


if __name__ == "__main__":
    unittest.main()
