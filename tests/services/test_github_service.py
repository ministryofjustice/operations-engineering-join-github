import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

from freezegun import freeze_time
from github.Organization import Organization
from github.PaginatedList import PaginatedList
from join_github_app.main.services.github_service import GithubService
from requests import Response


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
class TestGithubServiceGetOrgAvailableSeats(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        org = MagicMock(Organization)
        org.plan.seats = 5
        org.plan.filled_seats = 3
        mock_github_client_core_api.return_value.get_organization.return_value = org
        github_service = GithubService("")
        seats = github_service.get_org_available_seats("test_org")
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call("test_org")]
        )
        self.assertEqual(seats, 2)


@patch("github.Github.__new__")
class TestGithubServiceGetOrgPendingInvites(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        invites = MagicMock(PaginatedList)
        invites.totalCount = 5
        mock_github_client_core_api.return_value.get_organization.return_value.invitations.return_value = (
            invites
        )
        github_service = GithubService("")
        pending_invites = github_service.get_org_pending_invites("test_org")
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call("test_org"), call().invitations()]
        )
        self.assertEqual(pending_invites, 5)


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
class TestGithubServiceInviteUserToOrgUsingEmailAddress(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_core_api):
        github_service = GithubService("")
        github_service.invite_user_to_org_using_email_address(
            "approved@email.com", "some-org"
        )
        github_service.github_client_core_api.get_organization.assert_has_calls(
            [call("some-org"), call().invite_user(email="approved@email.com")]
        )


@freeze_time("2023-02-01")
@patch("github.Github.__new__", new=MagicMock)
@patch("requests.sessions.Session.__new__")
class TestGithubServiceGetRemovedUsersFromAuditLog(unittest.TestCase):
    def test_calls_downstream_services(self, mock_github_client_rest_api):
        github_service = GithubService("")
        response = MagicMock(Response)
        response.links = {}
        mock_github_client_rest_api.get.return_value = response
        github_service.github_client_rest_api = mock_github_client_rest_api
        users = github_service.get_removed_users_from_audit_log("test-org")
        self.assertEqual(len(users), 0)
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        mock_github_client_rest_api.assert_has_calls(
            [
                call.get(
                    f"https://api.github.com/orgs/test-org/audit-log?phrase=action:org.remove_member&created_at=>{three_months_ago}&per_page=100"
                ),
                call.get().raise_for_status(),
                call.get().json(),
                call.get().json().__iter__(),
            ]
        )

    def test_get_removed_users_from_audit_log_return_users(
        self, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        response = MagicMock(Response)
        response.links = {}
        response.json.return_value = [{"user": "some-user"}]
        mock_github_client_rest_api.get.return_value = response
        github_service.github_client_rest_api = mock_github_client_rest_api
        users = github_service.get_removed_users_from_audit_log("test-org")
        self.assertEqual(len(users), 1)

    def test_get_removed_users_from_audit_log_return_no_users(
        self, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        response = MagicMock(Response)
        response.links = {}
        response.json.return_value = []
        mock_github_client_rest_api.get.return_value = response
        github_service.github_client_rest_api = mock_github_client_rest_api
        users = github_service.get_removed_users_from_audit_log("test-org")
        self.assertEqual(len(users), 0)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
