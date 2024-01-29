import unittest
from unittest.mock import call, patch

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


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
