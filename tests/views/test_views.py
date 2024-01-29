import unittest
from unittest.mock import MagicMock

from flask import get_flashed_messages

import join_github_app
from join_github_app.main.routes.error import error
from join_github_app.main.services.github_service import GithubService


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = join_github_app.create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"

    def test_default(self):
        response = self.app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/")

    def test_join_github_info_page(self):
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
        self.assertEqual(flashed_message.get("message"), expected_flashed_message)

    def test_join_github_allowed_email(self):
        form_data = {"emailAddress": "email@digital.justice.gov.uk"}
        with self.app.test_client() as client:
            response = client.post("/join/submit-email", data=form_data)
            flashed_message = dict(get_flashed_messages(with_categories=True))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.request.path, "/join/submit-email")
        self.assertEqual(response.headers["Location"], "/join/select-organisations")
        self.assertEqual(flashed_message.get("message"), None)

    def test_join_github_outside_collab_email(self):
        form_data = {"emailAddress": "cat@dog.com"}
        with self.app.test_client() as client:
            response = client.post("/join/submit-email", data=form_data)
            flashed_message = dict(get_flashed_messages(with_categories=True))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.request.path, "/join/submit-email")
        self.assertEqual(response.headers["Location"], "/join/outside-collaborator")
        self.assertEqual(flashed_message.get("message"), None)

    def test_join_github_form_redirects_when_user_not_in_session(self):
        response = self.app.test_client().get("/join/github-auth0-user")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")

    def test_join_selection_digital_justice_user(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["email"] = "user@digital.justice.gov.uk"
                sess["org_selection"] = ["ministryofjustice"]

            response = client.get("/join/selection")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Using Single Sign-On", str(response.data))

    def test_join_selection_justice_user(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["email"] = "user@justice.gov.uk"
                sess["org_selection"] = ["ministryofjustice"]

            response = client.get("/join/selection")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Azure", str(response.data))

    def test_select_organisations_digital_justice_user(self):
        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["email"] = "user@digital.justice.gov.uk"
            response = client.get("/join/select-organisations")
            self.assertEqual(response.status_code, 200)
            self.assertIn("MoJ Analytical Services", str(response.data))
            self.assertIn(
                "disabled", str(response.data)
            )  # Check if the checkbox is disabled

    def test_invitation_sent(self):
        response = self.app.test_client().get("/join/invitation-sent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/invitation-sent")

    def test_error(self):
        with self.app.test_request_context():
            response = error("12345678")
            self.assertRegex(response, "12345678")


class TestCompletedRateLimit(unittest.TestCase):
    def setUp(self):
        self.form_data = {
            "gh_username": "some-username",
            "access_moj_org": True,
            "access_as_org": True,
        }

        self.org = "some-org"
        self.github_service = MagicMock(GithubService)
        self.app = join_github_app.create_app(self.github_service, True)

    def test_rate_limit(self):
        # Send requests until you receive a 429 response
        exceeded_rate_limit = False
        request_count = 0

        while not exceeded_rate_limit:
            response = self.app.test_client().post(
                "/join/github-auth0-user", data=self.form_data, follow_redirects=True
            )
            request_count += 1

            if response.status_code == 429:
                exceeded_rate_limit = True

        # At this point, you have reached the rate limit
        self.assertGreaterEqual(request_count, 1)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
