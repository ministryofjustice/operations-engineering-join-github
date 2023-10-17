import unittest
from unittest.mock import patch, Mock
from github.NamedUser import NamedUser
from landing_page_app.main.scripts.github_script import GithubScript
from landing_page_app.main.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_TEST_ORG,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    AS_ORG_ALLOWED_EMAIL_DOMAINS,
)


class TestGithubScript(unittest.TestCase):
    def _create_user(self, name: str) -> Mock:
        return Mock(NamedUser, name=name)

    def setUp(self):
        self.test_email_address = "some-email"
        self.test_user = "some-user"
        self.approved_email_address = "some@justice.gov.uk"

    @patch("landing_page_app.main.services.github_service")
    def test_is_email_address_pre_approved_with_as_org_approved_email_addresses(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        for email_domain in AS_ORG_ALLOWED_EMAIL_DOMAINS:
            email_address = f"{self.test_user}@{email_domain}"
            is_pre_approved = github_script._is_email_address_pre_approved(
                MOJ_ANALYTICAL_SERVICES, email_address
            )
            self.assertTrue(is_pre_approved)

    @patch("landing_page_app.main.services.github_service")
    def test_is_email_address_pre_approved_with_moj_org_approved_email_addresses(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        for email_domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS:
            email_address = f"{self.test_user}@{email_domain}"
            is_pre_approved = github_script._is_email_address_pre_approved(
                MINISTRY_OF_JUSTICE, email_address
            )
            self.assertTrue(is_pre_approved)

    @patch("landing_page_app.main.services.github_service")
    def test_is_email_address_pre_approved_with_non_approved_email_address(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        is_pre_approved = github_script._is_email_address_pre_approved(
            MOJ_TEST_ORG, "some@email.com"
        )
        self.assertFalse(is_pre_approved)

    @patch("landing_page_app.main.services.github_service")
    def test_is_email_address_pre_approved_with_incorrect_inputs(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        is_pre_approved = github_script._is_email_address_pre_approved(
            MOJ_TEST_ORG, self.test_email_address
        )
        self.assertFalse(is_pre_approved)

        is_pre_approved = github_script._is_email_address_pre_approved(
            MOJ_TEST_ORG, None
        )
        self.assertFalse(is_pre_approved)

        is_pre_approved = github_script._is_email_address_pre_approved(MOJ_TEST_ORG, "")
        self.assertFalse(is_pre_approved)

        is_pre_approved = github_script._is_email_address_pre_approved(
            None, self.test_email_address
        )
        self.assertFalse(is_pre_approved)

        is_pre_approved = github_script._is_email_address_pre_approved(
            "", self.test_email_address
        )
        self.assertFalse(is_pre_approved)

    @patch("landing_page_app.main.services.github_service")
    def test_add_new_user_to_github_org_with_approved_email_addresses(
        self, mock_github_service
    ):
        mock_user = self._create_user("test_user")
        mock_github_service.get_user.return_value = mock_user
        github_script = GithubScript(mock_github_service)
        github_script._is_email_address_pre_approved = Mock()
        github_script._is_email_address_pre_approved.return_value = True
        non_approved_requests = github_script.add_new_user_to_github_org(
            self.test_user, self.approved_email_address, [MINISTRY_OF_JUSTICE]
        )
        self.assertEqual(len(non_approved_requests), 0)
        # TODO: change MOJ_TEST_ORG to MINISTRY_OF_JUSTICE
        mock_github_service.add_new_user_to_org.assert_called_with(
            mock_user, MOJ_TEST_ORG
        )
        non_approved_requests = github_script.add_new_user_to_github_org(
            self.test_user, self.approved_email_address, [MOJ_ANALYTICAL_SERVICES]
        )
        self.assertEqual(len(non_approved_requests), 0)
        # TODO: change MOJ_TEST_ORG to MOJ_ANALYTICAL_SERVICES
        mock_github_service.add_new_user_to_org.assert_called_with(
            mock_user, MOJ_TEST_ORG
        )

    @patch("landing_page_app.main.services.github_service")
    def test_add_new_user_to_github_org_with_non_approved_email_addresses(
        self, mock_github_service
    ):
        mock_github_service.get_user.return_value = self._create_user("test_user")
        github_script = GithubScript(mock_github_service)
        github_script._is_email_address_pre_approved = Mock()
        github_script._is_email_address_pre_approved.return_value = False
        github_script._add_non_pre_appoved_email_user_to_github_org = Mock()
        non_approved_requests = github_script.add_new_user_to_github_org(
            self.test_user, self.test_email_address, [MINISTRY_OF_JUSTICE]
        )
        self.assertEqual(len(non_approved_requests), 1)
        non_approved_requests = github_script.add_new_user_to_github_org(
            self.test_user, self.test_email_address, [MOJ_ANALYTICAL_SERVICES]
        )
        self.assertEqual(len(non_approved_requests), 1)

    @patch("landing_page_app.main.services.github_service")
    def test_add_new_user_to_github_org_with_incorrect_org_name(
        self, mock_github_service
    ):
        mock_github_service.get_user.return_value = self._create_user("test_user")
        github_script = GithubScript(mock_github_service)
        github_script._is_email_address_pre_approved = Mock()
        non_approved_requests = github_script.add_new_user_to_github_org(
            self.test_user, self.test_email_address, [MOJ_TEST_ORG]
        )
        self.assertEqual(len(non_approved_requests), 0)
        github_script._is_email_address_pre_approved.assert_not_called()

    @patch("landing_page_app.main.services.github_service")
    def test_add_new_user_to_github_org_with_incorrect_inputs(
        self, mock_github_service
    ):
        github_script = GithubScript(mock_github_service)
        github_script.add_new_user_to_github_org("", "", [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(None, "", [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(None, None, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(self.test_user, "", [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(self.test_user, None, [])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(
            self.test_user, self.test_email_address, []
        )
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(
            "", self.test_email_address, [MOJ_TEST_ORG]
        )
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(
            None, self.test_email_address, [MOJ_TEST_ORG]
        )
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(
            "", self.test_email_address, [MOJ_TEST_ORG]
        )
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org("", "", [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

        github_script.add_new_user_to_github_org(None, None, [MOJ_TEST_ORG])
        github_script.github_service.get_user.assert_not_called()

    @patch("landing_page_app.main.services.github_service")
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


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
