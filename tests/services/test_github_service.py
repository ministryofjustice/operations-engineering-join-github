import os
import unittest
from unittest.mock import call, patch

from join_github_app.main.config.constants import MINISTRY_OF_JUSTICE
from join_github_app.main.services.github_service import GithubService


@patch("github.Github.__new__")
@patch("requests.sessions.Session.__new__")
class TestGithubServiceInit(unittest.TestCase):
    def test_sets_up_class(
        self, mock_github_client_rest_api, mock_github_client_core_api
    ):
        mock_github_client_core_api.return_value = "test_mock_github_client_core_api"
        github_service = GithubService("")
        self.assertEqual(
            "test_mock_github_client_core_api", github_service.github_client_core_api
        )
        mock_github_client_rest_api.assert_has_calls(
            [
                call().headers.update(
                    {
                        "Accept": "application/vnd.github+json",
                        "Authorization": "Bearer ",
                    }
                )
            ]
        )


@patch("github.Github.__new__")
class TestGithubServiceInvites(unittest.TestCase):

    def setUp(self) -> None:
        self.valid_email = "test@test.com"
        self.valid_orgs = ["test1", "test2"]

    @patch.dict(os.environ, {"SEND_EMAIL_INVITES": "False"}, clear=True)
    def test_send_email_invites_off(self, mock_github_client_rest_api):
        github_service = GithubService("test")
        github_service.github_client_rest_api = mock_github_client_rest_api

        self.assertEqual(github_service.send_invitation_to_organisation(self.valid_email, self.valid_orgs), None)

    @patch.dict(os.environ, {"SEND_EMAIL_INVITES": "True"}, clear=True)
    def test_send_email_invites_on(self, mock_github_client_rest_api):
        github_service = GithubService("test")
        github_service.github_client_rest_api = mock_github_client_rest_api

        github_service.send_invitation_to_organisation(self.valid_email, self.valid_orgs)
        mock_github_client_rest_api.assert_called()


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
