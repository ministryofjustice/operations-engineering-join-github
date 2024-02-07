import unittest
from unittest.mock import MagicMock, patch

from flask import Response

from app.app import create_app
from app.main.middleware.error_handler import AuthTokenError
from app.main.services.github_service import GithubService


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.app.config["SECRET_KEY"] = "my_precious_test_key"
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()

    @patch("app.main.routes.auth.auth0_service")
    def test_login_route_redirects(self, mock_auth0_service):
        mock_auth0_service.login.return_value = Response(
            status=302, headers={"Location": "mock://auth0.redirect"}
        )

        response = self.client.get("/auth/login")

        self.assertEqual(response.status_code, 302)
        self.assertIn("mock://auth0.redirect", response.headers["Location"])
        mock_auth0_service.login.assert_called_once()

    @patch("app.main.routes.auth.auth0_service")
    def test_callback_route_stores_users_session_and_redirects(
        self, mock_auth0_service
    ):
        mock_auth0_service.get_access_token.return_value = "The users session! 🤩"

        response = self.client.get("/auth/callback")

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertEqual(session["user"], "The users session! 🤩")
        self.assertIn("join/send-invitation", response.headers["Location"])

    @patch("app.main.routes.auth.auth0_service")
    def test_logout_route_clears_session_and_redirects(self, mock_auth0_service):
        mock_auth0_service.logout.return_value = Response(
            status=302, headers={"Location": "/"}
        )

        response = self.client.get("/auth/logout")

        with self.client.session_transaction() as session:
            self.assertEqual(session.get("user", None), None)
        self.assertIn("/", response.headers["Location"])
        self.assertEqual(response.status_code, 302)
        mock_auth0_service.logout.assert_called_with("http://localhost/")


if __name__ == "__main__":
    unittest.main()
