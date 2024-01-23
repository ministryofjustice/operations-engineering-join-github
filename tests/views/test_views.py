import unittest
from unittest.mock import MagicMock

import join_github_app
from flask import get_flashed_messages
from join_github_app.main.scripts.github_script import GithubScript
from join_github_app.main.routes.join import _join_github_auth0_users
from join_github_app.main.routes.error import error


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_script = MagicMock(GithubScript)
        self.app = join_github_app.create_app(self.github_script, False)
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

    def test_thank_you(self):
        response = self.app.test_client().get("/join/submitted")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join/submitted")

    def test_error(self):
        with self.app.test_request_context():
            response = error("12345678")
            self.assertRegex(response, "12345678")


class TestJoinGithubAuth0User(unittest.TestCase):
    def setUp(self):
        self.org = "some-org"
        self.github_script = MagicMock(GithubScript)
        self.app = join_github_app.create_app(self.github_script, False)

    def test_join_github_auth0_user_decorator_is_working(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
        }
        response = self.app.test_client().post(
            "/join/github-auth0-user", data=form_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Testing a function that has a decorator which redirect to /index
        # The private function in the function will test the logic
        self.assertEqual(response.request.path, "/")
        self.app.github_script.add_new_user_to_github_org.assert_not_called()

    def test_join_github_auth0_user_new_joiner(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
            "access_as_org": True,
        }
        with self.app.test_request_context(
            "/join/github-auth0-user", method="POST", data=form_data
        ) as request_context:
            request_context.session = MagicMock()
            request_context.session = {"user": {"userinfo": {"email": "some-email"}}}
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            response = _join_github_auth0_users(request_context.request)
            self.assertEqual(response.status_code, 302)
            for item in response.headers:
                if item[0] == "Location" and item[1] == "thank-you":
                    redirect = True
            self.assertEqual(redirect, True)
            self.app.github_script.add_new_user_to_github_org.assert_called_once_with(
                "some-email", [self.org]
            )

    def test_join_github_auth0_user_when_github_seat_protection_enabled(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
        }
        with self.app.test_request_context(
            "/join/github-auth0-user", method="POST", data=form_data
        ) as request_context:
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            self.app.github_script.is_github_seat_protection_enabled.return_value = True
            response = _join_github_auth0_users(request_context.request)
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.assertRegex(response, "GitHub Seat protection enabled")

    def test_join_github_form_with_incorrect_special_character_inputs(self):
        form_data = {
            "gh_username": "some!username",
            "access_moj_org": True,
        }
        with self.app.test_request_context(
            "/join/github-auth0-user", method="POST", data=form_data
        ) as request_context:
            response = _join_github_auth0_users(request_context.request)
            self.assertRegex(response, "There is a problem")
            self.app.github_script.add_new_user_to_github_org.assert_not_called()

    def test_join_github_form_with_missing_orgs(self):
        form_data = {
            "gh_username": "",
        }
        with self.app.test_request_context(
            "/join/github-auth0-user", method="POST", data=form_data
        ) as request_context:
            response = _join_github_auth0_users(request_context.request)
            self.assertRegex(response, "There is a problem")
            self.app.github_script.add_new_user_to_github_org.assert_not_called()


class TestCompletedRateLimit(unittest.TestCase):
    def setUp(self):
        self.form_data = {
            "gh_username": "some-username",
            "access_moj_org": True,
            "access_as_org": True,
        }

        self.org = "some-org"
        self.github_script = MagicMock(GithubScript)
        self.app = join_github_app.create_app(self.github_script, True)

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
