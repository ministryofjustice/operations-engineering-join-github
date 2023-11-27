import os
import unittest
from unittest.mock import MagicMock, patch

import landing_page_app
from landing_page_app.main.routes.auth import _user_has_approved_auth0_email_address
from landing_page_app.main.scripts.github_script import GithubScript


class TestAuth0AuthenticationView(unittest.TestCase):
    def setUp(self) -> None:
        self.github_script = MagicMock(GithubScript)
        self.app = landing_page_app.create_app(self.github_script, False)
        self.app.secret_key = "dev"
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        self.auth0_mock = MagicMock()

    def test_login(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            response = self.client.get("/login")
            self.assertEqual(response.status_code, 200)

    def test_callback_token_error(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            self.auth0_mock.auth0.authorize_access_token.side_effect = KeyError()
            response = self.client.get("/callback")
            self.assertEqual(response.status_code, 500)

    def test_callback_email_error(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            self.auth0_mock.auth0.authorize_access_token.return_value = {"userinfo": {}}
            response = self.client.get("/callback")
            self.assertEqual(response.status_code, 500)

    def test_callback_not_allowed_email(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            self.auth0_mock.auth0.authorize_access_token.return_value = {
                "userinfo": {"email": "email@example.com"}
            }
            response = self.client.get("/callback")
            self.assertEqual(response.status_code, 302)
            self.assertIn("Location", response.headers)
            self.assertEqual(response.headers["Location"], "/logout")

    def test_callback_allowed_email(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            self.auth0_mock.auth0.authorize_access_token.return_value = {
                "userinfo": {"email": "email@justice.gov.uk"}
            }
            response = self.client.get("/callback")
            self.assertEqual(response.status_code, 302)
            self.assertIn("Location", response.headers)
            self.assertEqual(response.headers["Location"], "/join-github-auth0-user")

    def test_callback_email_is_none(self):
        with patch.dict(
            self.app.extensions,
            {"authlib.integrations.flask_client": self.auth0_mock},
            clear=True,
        ):
            self.auth0_mock.auth0.authorize_access_token.return_value = {
                "userinfo": {"email": None}
            }
            response = self.client.get("/callback")
            self.assertEqual(response.status_code, 302)
            self.assertIn("Location", response.headers)
            self.assertEqual(response.headers["Location"], "/logout")

    @patch.dict(os.environ, {"AUTH0_DOMAIN": ""})
    @patch.dict(os.environ, {"AUTH0_CLIENT_ID": ""})
    def test_logout(self):
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertIn("Location", response.headers)
        self.assertIn("v2/logout", response.headers["Location"])


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_script = MagicMock(GithubScript)
        self.app = landing_page_app.create_app(self.github_script, False)

    def test_user_has_approved_auth0_email_address(self):
        self.assertFalse(_user_has_approved_auth0_email_address("email@example.com"))
        self.assertTrue(_user_has_approved_auth0_email_address("email@justice.gov.uk"))
        self.assertTrue(_user_has_approved_auth0_email_address("email@cica.gov.uk"))
        self.assertTrue(_user_has_approved_auth0_email_address("email@yjb.gov.uk"))


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
