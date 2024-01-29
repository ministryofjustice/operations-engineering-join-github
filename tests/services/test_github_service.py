import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

from freezegun import freeze_time
from github.Organization import Organization
from github.PaginatedList import PaginatedList
from join_github_app.main.services.github_service import GithubService
from requests import Response

from join_github_app.main.config.constants import (
    MAX_ALLOWED_ORG_PENDING_INVITES,
    MINIMUM_ORG_SEATS,
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_TEST_ORG,
)


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


@patch("github.Github.__new__")
class TestGithubServiceOrganisationManagement(unittest.TestCase):

    def test_get_selected_organisations(self, mock_github_client_rest_api):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api

        orgs = github_service.get_selected_organisations(None, None)
        self.assertEqual(len(orgs), 0)
        orgs = github_service.get_selected_organisations(False, False)
        self.assertEqual(len(orgs), 0)
        orgs = github_service.get_selected_organisations(True, False)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0], MINISTRY_OF_JUSTICE)
        orgs = github_service.get_selected_organisations(True, True)
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs[0], MINISTRY_OF_JUSTICE)
        self.assertEqual(orgs[1], MOJ_ANALYTICAL_SERVICES)
        orgs = github_service.get_selected_organisations(False, True)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0], MOJ_ANALYTICAL_SERVICES)


@patch("github.Github.__new__")
@patch("join_github_app.main.services.github_service.GithubService.invite_user_to_org_using_email_address")
class TestGithubServiceUserManagementInvalidInputs(unittest.TestCase):

    def setUp(self):
        self.test_email_address = "some-email"
        self.test_org = "some-org"

    def test_add_new_user_to_github_org_with_invalid_inputs(
            self, mock_invite_user_to_org_using_email_address, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api

        github_service.add_new_user_to_github_org("", [MINISTRY_OF_JUSTICE], True)
        mock_invite_user_to_org_using_email_address.assert_not_called()

        github_service.add_new_user_to_github_org("", [self.test_org], True)
        mock_invite_user_to_org_using_email_address.assert_not_called()

        github_service.add_new_user_to_github_org(None, [MINISTRY_OF_JUSTICE], True)
        mock_invite_user_to_org_using_email_address.assert_not_called()

        github_service.add_new_user_to_github_org(None, [self.test_org], True)
        mock_invite_user_to_org_using_email_address.assert_not_called()

        github_service.add_new_user_to_github_org(self.test_email_address, [], True)
        mock_invite_user_to_org_using_email_address.assert_not_called()

        github_service.add_new_user_to_github_org(
            self.test_email_address, [self.test_org], True
        )
        mock_invite_user_to_org_using_email_address.assert_not_called()


@patch("github.Github.__new__")
@patch("join_github_app.main.services.github_service.GithubService.invite_user_to_org_using_email_address")
class TestGithubServiceUserManagementValidInputs(unittest.TestCase):

    def setUp(self):
        self.test_email_address = "some-email"

    def test_add_new_user_to_github_org_send_email_invites_true(
        self, mock_invite_user_to_org_using_email_address, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api

        github_service.add_new_user_to_github_org(
            self.test_email_address, [MINISTRY_OF_JUSTICE], True
        )
        mock_invite_user_to_org_using_email_address.assert_called()

    def test_add_new_user_to_github_org_send_email_invites_false(
        self, mock_invite_user_to_org_using_email_address, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api

        github_service.add_new_user_to_github_org(
            self.test_email_address, [MINISTRY_OF_JUSTICE], False
        )
        mock_invite_user_to_org_using_email_address.assert_not_called()


@patch("github.Github.__new__")
@patch("join_github_app.main.services.github_service.GithubService.get_removed_users_from_audit_log")
class TestGithubServiceAuditLog(unittest.TestCase):

    def setUp(self):
        self.test_user = "some-user"

    def test_is_user_in_audit_log(self, mock_get_removed_users_from_audit_log, mock_github_client_rest_api):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_removed_users_from_audit_log.return_value = [
            self.test_user
        ]
        found_user = github_service.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, True)

    def test_is_user_in_audit_log_when_no_users_in_audit_log(self, mock_get_removed_users_from_audit_log, mock_github_client_rest_api):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_removed_users_from_audit_log.return_value = []
        found_user = github_service.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, False)

    def test_is_user_in_audit_log_when_different_users_in_audit_log(
        self, mock_get_removed_users_from_audit_log, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_removed_users_from_audit_log.return_value = [
            "some-user1",
            "some-user2",
        ]
        found_user = github_service.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, False)


@patch("github.Github.__new__")
@patch("join_github_app.main.services.github_service.GithubService.get_org_available_seats")
@patch("join_github_app.main.services.github_service.GithubService.get_org_pending_invites")
class TestGithubServiceSeatProtection(unittest.TestCase):

    def test_is_github_seat_protection_enabled_when_conditions_are_okay(
        self, mock_get_org_pending_invites, mock_get_org_available_seats, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES - 1
        )
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)

    def test_is_github_seat_protection_enabled_when_minimum_seats(
        self, mock_get_org_pending_invites, mock_get_org_available_seats, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS
        mock_get_org_pending_invites.return_value = 0
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS - 1
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

    def test_is_github_seat_protection_enabled_when_more_than_minimum_seats(
        self, mock_get_org_pending_invites, mock_get_org_available_seats, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_get_org_pending_invites.return_value = 0
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)

    def test_is_github_seat_protection_enabled_when_more_than_allowed_max_pending_invites(
        self, mock_get_org_pending_invites, mock_get_org_available_seats, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES
        )
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

        mock_get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES + 1
        )
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

    def test_is_github_seat_protection_enabled_when_below_max_pending_invites(
        self, mock_get_org_pending_invites, mock_get_org_available_seats, mock_github_client_rest_api
    ):
        github_service = GithubService("")
        github_service.github_client_rest_api = mock_github_client_rest_api
        mock_get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES - 1
        )
        enabled = github_service.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
