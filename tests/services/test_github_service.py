import unittest
from unittest.mock import patch, call, Mock
from github.NamedUser import NamedUser
from landing_page_app.main.services.github_service import GithubService


@patch("github.Github.__new__")
class TestGithubServiceInit(unittest.TestCase):
    def test_sets_up_class(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value = "test_mock_github_client_core_api"
        github_service = GithubService("")
        self.assertEqual(
            "test_mock_github_client_core_api", github_service.github_client_core_api
        )


@patch("github.Github.__new__")
class TestGithubServiceGetUser(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        mock_github_client_core_api.return_value.get_user.return_value = "mock_user"
        github_service = GithubService("")
        github_service.get_user("test_user")
        github_service.github_client_core_api.get_user.assert_has_calls(
            [call("test_user")]
        )


@patch("github.Github.__new__")
class TestGithubServiceAddNewUserToOrg(unittest.TestCase):
    def _create_user(self, name: str) -> Mock:
        return Mock(NamedUser, name=name)

    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("")
        mock_user = self._create_user("test_user")
        github_service.add_new_user_to_org(mock_user, "some-org")
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call("some-org"), call().invite_user(mock_user)]
        )


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
