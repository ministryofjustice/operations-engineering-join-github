import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import get_flashed_messages
from github import GithubException

from app.app import create_app
from app.main.services.github_service import GithubService


class TestSubmitEmail(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    def test_page_loads(self):
        response = self.app.test_client().get("/join/submit-email")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/submit-email")

    def test_join_github_invalid_email_flashes_warning(self):
        form_data = {"emailAddress": ""}
        expected_flashed_message = "Please enter a valid email address."

        with self.app.test_client() as client:
            response = client.post("/join/submit-email", data=form_data)
            flashed_message = dict(get_flashed_messages(with_categories=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/submit-email")
        self.assertEqual(flashed_message.get(
            "message"), expected_flashed_message)

    def test_redirects_to_select_organisation_when_email_is_pre_approved(self):
        form_data = {"emailAddress": "email@digital.justice.gov.uk"}

        with self.app.test_client() as client:
            response = client.post("/join/submit-email", data=form_data)
            flashed_message = dict(get_flashed_messages(with_categories=True))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.request.path, "/join/submit-email")
        self.assertEqual(
            response.headers["Location"], "/join/select-organisations")
        self.assertEqual(flashed_message.get("message"), None)

    def test_redirects_to_outside_collaborators_when_email_is_not_pre_approved(self):
        form_data = {"emailAddress": "email@example.com"}

        with self.app.test_client() as client:
            response = client.post("/join/submit-email", data=form_data)
            flashed_message = dict(get_flashed_messages(with_categories=True))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.request.path, "/join/submit-email")
        self.assertEqual(
            response.headers["Location"], "/join/outside-collaborator")
        self.assertEqual(flashed_message.get("message"), None)


class TestSelectOrganisation(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    @patch(
        "app.main.routes.join.app_config",
        new=SimpleNamespace(
            github=SimpleNamespace(
                organisations=[
                    SimpleNamespace(
                        name="moj-analytical-services",
                        enabled=True,
                        display_text="MoJ Analytical Services",
                    )
                ]
            )
        ),
    )
    def test_select_organisations_digital_justice_user(self):
        with self.client.session_transaction() as sess:
            sess["user_input_email"] = "user@digital.justice.gov.uk"

        response = self.client.get("/join/select-organisations")

        self.assertEqual(response.status_code, 200)
        self.assertIn("MoJ Analytical Services", str(response.data))
        self.assertIn(
            "disabled", str(response.data)
        )  # Check if the checkbox is disabled


class TestSelection(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    def test_join_selection_digital_justice_user(self):
        with self.client.session_transaction() as sess:
            sess["user_input_email"] = "user@digital.justice.gov.uk"
            sess["org_selection"] = ["ministryofjustice"]

        response = self.client.get("/join/selection")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Using Single Sign-On", str(response.data))

    def test_join_selection_justice_user(self):
        with self.client.session_transaction() as sess:
            sess["user_input_email"] = "user@justice.gov.uk"
            sess["org_selection"] = ["ministryofjustice"]

        response = self.client.get("/join/selection")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Office 365", str(response.data))

    def test_join_selection_other_user(self):
        with self.client.session_transaction() as sess:
            sess["user_input_email"] = "user@ppo.gov.uk"
            sess["org_selection"] = ["ministryofjustice"]

        response = self.client.get("/join/selection")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Office 365", str(response.data))


class TestSendInvitations(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    @patch(
        "app.main.routes.join.app_config",
        new=SimpleNamespace(
            github=SimpleNamespace(
                organisations=[
                    SimpleNamespace(
                        name="ministryofjustice",
                        enabled=True,
                        display_text="Ministry of Justice",
                    )
                ]
            )
        ),
    )
    def test_when_user_is_already_member_of_an_org(self):

        self.github_service.send_invites_to_user_email.side_effect = GithubException(
            status=422,
            data={
                "message": "Validation Failed",
                "errors": [
                    {
                        "resource": "OrganizationInvitation",
                        "code": "unprocessable",
                        "field": "data",
                        "message": "A user with this email address is already a part of this organization"
                    }
                ],
                "documentation_url": "https://docs.github.com/rest/orgs/members#create-an-organization-invitation"
            }
        )

        with self.client.session_transaction() as sess:
            sess["user"] = {"userinfo": {"email": "test@justice.gov.uk"}}
            sess["user_input_email"] = "test@justice.gov.uk"
            sess["org_selection"] = ["ministryofjustice"]

        response = self.client.get("/join/send-invitation")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "User test@justice.gov.uk is already a member of the organization.", response.data.decode())


class TestInvitationSent(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    @patch(
        "app.main.routes.join.app_config",
        new=SimpleNamespace(
            github=SimpleNamespace(
                organisations=[
                    SimpleNamespace(
                        name="ministryofjustice",
                        enabled=True,
                        display_text="Ministry of Justice",
                    )
                ]
            )
        ),
    )
    def test_single_invitation_sent(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {"userinfo": {"email": "test@justice.gov.uk"}}
            sess["org_selection"] = ["ministryofjustice"]

        response = self.client.get("/join/invitation-sent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/invitation-sent")
        self.assertIn("ministryofjustice", str(response.data))

    @patch(
        "app.main.routes.join.app_config",
        new=SimpleNamespace(
            github=SimpleNamespace(
                organisations=[
                    SimpleNamespace(
                        name="ministryofjustice",
                        enabled=True,
                        display_text="Ministry of Justice",
                    ),
                    SimpleNamespace(
                        name="moj-analytical-services",
                        enabled=True,
                        display_text="MoJ Analytical Services",
                    ),
                ]
            )
        ),
    )
    def test_multiple_invitations_sent(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {"userinfo": {"email": "test@justice.gov.uk"}}
            sess["org_selection"] = [
                "ministryofjustice", "moj-analytical-services"]

        response = self.client.get("/join/invitation-sent")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/invitation-sent")
        self.assertIn("Invitations sent to", str(response.data))
        self.assertIn(
            "ministryofjustice and moj-analytical-services", str(response.data)
        )


if __name__ == "__main__":
    unittest.main()
