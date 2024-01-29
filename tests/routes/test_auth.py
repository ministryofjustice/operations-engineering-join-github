import unittest
from unittest.mock import MagicMock, patch

from flask import Response, session

import join_github_app
from join_github_app.main.middleware.error_handler import AuthTokenError
from join_github_app.main.routes.auth import (process_user_session,
                                              send_github_invitation,
                                              user_email_allowed,
                                              user_is_valid)
from join_github_app.main.services.github_service import GithubService


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = join_github_app.create_app(self.github_service, False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    @patch("join_github_app.main.routes.auth.oauth.auth0.authorize_redirect")
    def test_login_route(self, mock_authorize_redirect):
        mock_response = Response(status=302, headers={'Location': 'mock://auth0.redirect'})
        mock_authorize_redirect.return_value = mock_response

        response = self.client.get("/auth/login")
        self.assertEqual(response.status_code, 302)
        mock_authorize_redirect.assert_called_once()

    def test_logout_route(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = {'some': 'data'}

            response = c.get("/auth/logout")

            self.assertEqual(response.status_code, 302)

            with c.session_transaction() as sess:
                self.assertNotIn('user', sess)

        self.assertIn('auth0.com/v2/logout', response.headers['Location'])

    @patch("join_github_app.main.routes.auth.render_success_page")
    @patch("join_github_app.main.routes.auth.send_github_invitation", return_value=True)
    @patch("join_github_app.main.routes.auth.process_user_session", return_value=True)
    @patch("join_github_app.main.routes.auth.get_token")
    def test_callback_route_success(self, mock_get_token, mock_process_user_session,
                                    mock_send_github_invitation, mock_render_success_page):
        mock_get_token.return_value = {'userinfo': {'email': 'test@example.com'}}
        mock_render_success_page.return_value = Response(status=200)

        response = self.client.get("/auth/callback")
        self.assertEqual(response.status_code, 200)
        mock_get_token.assert_called_once()
        mock_process_user_session.assert_called_once()
        mock_send_github_invitation.assert_called_once()
        mock_render_success_page.assert_called_once()

    @patch("join_github_app.main.routes.auth.render_error_page", return_value=Response(status=500))
    @patch("join_github_app.main.routes.auth.get_token")
    def test_callback_route_token_failure(self, mock_get_token, mock_render_error_page):
        mock_get_token.side_effect = AuthTokenError("Token error")

        response = self.client.get("/auth/callback")
        self.assertEqual(response.status_code, 500)
        mock_get_token.assert_called_once()
        mock_render_error_page.assert_called_once()

    @patch("join_github_app.main.routes.auth.ALLOWED_EMAIL_DOMAINS",
           new=["example.com", "test.com"])
    def test_process_user_session_success(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test.com'
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

    @patch("join_github_app.main.routes.auth.ALLOWED_EMAIL_DOMAINS",
           new=["example.com", "test.com"])
    def test_process_user_session_with_invalid_user(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test2.com'
            session['org_selection'] = ['some_org']

            result = process_user_session()
            self.assertFalse(result)

    @patch("join_github_app.main.routes.auth.ALLOWED_EMAIL_DOMAINS",
           new=["example.com", "test.com"])
    def test_process_user_session_with_missing_org_selection(self):
        with self.app.test_request_context('/auth/callback'):
            session['user'] = {'userinfo': {'email': 'user@test.com'}}
            session['email'] = 'user@test2.com'
            session['org_selection'] = ['some_org']

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
    @patch("join_github_app.main.routes.auth.user_email_allowed", return_value=True)
    def test_user_is_valid_matching_emails(self, mock_user_email_allowed):
        self.assertTrue(user_is_valid("test@example.com", "test@example.com"))

    @patch("join_github_app.main.routes.auth.user_email_allowed", return_value=False)
    def test_user_is_valid_non_matching_emails(self, mock_user_email_allowed):
        self.assertFalse(user_is_valid("test@example.com", "other@example.com"))


class TestEmailAllowed(unittest.TestCase):
    @patch("join_github_app.main.routes.auth.ALLOWED_EMAIL_DOMAINS", new=["example.com"])
    def test_user_email_allowed(self):
        self.assertTrue(user_email_allowed("user@example.com"))
        self.assertFalse(user_email_allowed("user@notallowed.com"))


if __name__ == "__main__":
    unittest.main()
