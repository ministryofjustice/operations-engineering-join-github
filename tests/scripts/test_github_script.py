import unittest
from unittest.mock import patch, MagicMock
from join_github_app.main.scripts.github_script import GithubScript
from join_github_app.main.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_TEST_ORG,
    MINIMUM_ORG_SEATS,
    MAX_ALLOWED_ORG_PENDING_INVITES,
)


class TestGithubScript(unittest.TestCase):
    def setUp(self):
        self.test_email_address = "some-email"
        self.test_user = "some-user"
        self.approved_email_address = "some@justice.gov.uk"

    @patch("join_github_app.main.services.github_service")
    def test_is_github_seat_protection_enabled_when_conditions_are_okay(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_github_service.get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES - 1
        )
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)

    @patch("join_github_app.main.services.github_service")
    def test_is_github_seat_protection_enabled_when_minimum_seats(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS
        mock_github_service.get_org_pending_invites.return_value = 0
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS - 1
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

    @patch("join_github_app.main.services.github_service")
    def test_is_github_seat_protection_enabled_when_more_than_minimum_seats(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_github_service.get_org_pending_invites.return_value = 0
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)

    @patch("join_github_app.main.services.github_service")
    def test_is_github_seat_protection_enabled_when_more_than_allowed_max_pending_invites(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_github_service.get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES
        )
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

        mock_github_service.get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES + 1
        )
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, True)

    @patch("join_github_app.main.services.github_service")
    def test_is_github_seat_protection_enabled_when_below_max_pending_invites(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_org_available_seats.return_value = MINIMUM_ORG_SEATS + 1
        mock_github_service.get_org_pending_invites.return_value = (
            MAX_ALLOWED_ORG_PENDING_INVITES - 1
        )
        enabled = github_script.is_github_seat_protection_enabled()
        self.assertEqual(enabled, False)

    @patch("join_github_app.main.services.github_service")
    def test_is_user_in_audit_log_when_no_users_in_audit_log(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_removed_users_from_audit_log.return_value = []
        found_user = github_script.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, False)

    @patch("join_github_app.main.services.github_service")
    def test_is_user_in_audit_log_when_different_users_in_audit_log(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_removed_users_from_audit_log.return_value = [
            "some-user1",
            "some-user2",
        ]
        found_user = github_script.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, False)

    @patch("join_github_app.main.services.github_service")
    def test_is_user_in_audit_log(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        mock_github_service.get_removed_users_from_audit_log.return_value = [
            self.test_user
        ]
        found_user = github_script.is_user_in_audit_log(self.test_user, MOJ_TEST_ORG)
        self.assertEqual(found_user, True)

    @patch("join_github_app.main.services.github_service")
    def test_add_new_user_to_github_org_with_incorrect_inputs(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)

        github_script.add_new_user_to_github_org(None, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org("", [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(self.test_email_address, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(
            self.test_email_address, [MOJ_TEST_ORG]
        )
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org("", [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(None, [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

    @patch("join_github_app.main.services.github_service")
    def test_add_new_user_to_github_org(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        github_script.add_new_user_to_github_org(
            self.approved_email_address, [MINISTRY_OF_JUSTICE]
        )
        mock_github_service.invite_user_to_org_using_email_address.assert_called()

    @patch("join_github_app.main.services.github_service")
    def test_get_selected_organisations(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        orgs = github_script.get_selected_organisations(None, None)
        self.assertEqual(len(orgs), 0)
        orgs = github_script.get_selected_organisations(False, False)
        self.assertEqual(len(orgs), 0)
        orgs = github_script.get_selected_organisations(True, False)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0], MINISTRY_OF_JUSTICE)
        orgs = github_script.get_selected_organisations(True, True)
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs[0], MINISTRY_OF_JUSTICE)
        self.assertEqual(orgs[1], MOJ_ANALYTICAL_SERVICES)
        orgs = github_script.get_selected_organisations(False, True)
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0], MOJ_ANALYTICAL_SERVICES)

    @patch("join_github_app.main.services.github_service")
    def test_validate_user_rejoining_org(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        github_script.is_user_in_audit_log = MagicMock(return_value=False)
        result = github_script.validate_user_rejoining_org([MINISTRY_OF_JUSTICE], "")
        self.assertFalse(result)
        github_script.is_user_in_audit_log = MagicMock(return_value=True)
        result = github_script.validate_user_rejoining_org([MINISTRY_OF_JUSTICE], "")
        self.assertTrue(result)

    @patch("join_github_app.main.services.github_service")
    def test_add_returning_user_to_github_org_with_incorrect_inputs(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)

        github_script.add_returning_user_to_github_org(None, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_returning_user_to_github_org("", [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_returning_user_to_github_org(self.test_user, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_returning_user_to_github_org("", [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_returning_user_to_github_org(None, [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

    @patch("join_github_app.main.services.github_service")
    def test_add_returning_user_to_github_org(self, mock_github_service):
        github_script = GithubScript(mock_github_service)
        mock_github_service.github_service.get_user.return_value = "a real user"
        github_script.add_returning_user_to_github_org(
            self.test_user, [MOJ_ANALYTICAL_SERVICES, MINISTRY_OF_JUSTICE]
        )
        mock_github_service.invite_user_to_org_using_nameduser.assert_called()

    @patch("join_github_app.main.services.github_service")
    def test_add_returning_user_to_github_org_with_incorrect_org_name(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        mock_github_service.github_service.get_user.return_value = "a real user"
        github_script.add_returning_user_to_github_org(self.test_user, [MOJ_TEST_ORG])
        mock_github_service.invite_user_to_org_using_nameduser.assert_not_called()


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
