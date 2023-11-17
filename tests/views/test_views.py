import unittest
from unittest.mock import MagicMock, patch

from landing_page_app.main.services.slack_service import SlackService
from landing_page_app.main.scripts.github_script import GithubScript
import landing_page_app

from landing_page_app.main.views import (
    handle_github_exception,
    page_not_found,
    server_forbidden,
    unknown_server_error,
    gateway_timeout,
    error,
    wrapper_join_github_auth0_users,
)


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_script = MagicMock(GithubScript)
        self.slack_service = MagicMock(SlackService)
        self.app = landing_page_app.create_app(
            self.github_script, self.slack_service, False
        )

    def test_index(self):
        response = self.app.test_client().get("index")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/index")

    def test_home(self):
        response = self.app.test_client().get("home")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/home")

    def test_default(self):
        response = self.app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/")

    def test_join_github_info_page(self):
        response = self.app.test_client().get("/join-github.html")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join-github.html")

    def test_join_github_form(self):
        response = self.app.test_client().get("/join-github-auth0-user.html")
        self.assertEqual(response.status_code, 302)
        redirect = False
        for item in response.headers:
            if item[0] == 'Location' and item[1] == '/index':
                redirect = True
        self.assertEqual(redirect, True)

    def test_thank_you(self):
        response = self.app.test_client().get("/thank-you")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/thank-you")

    def test_handle_github_exception(self):
        with self.app.test_request_context():
            response = handle_github_exception("12345678")
            self.assertRegex(response, "12345678")

    def test_page_not_found(self):
        with self.app.test_request_context():
            response = page_not_found("some-error")
            self.assertEqual(response[1], 404)

    def test_server_forbidden(self):
        with self.app.test_request_context():
            response = server_forbidden("some-error")
            self.assertEqual(response[1], 403)

    def test_unknown_server_error(self):
        with self.app.test_request_context():
            response = unknown_server_error("some-error")
            self.assertEqual(response[1], 500)

    def test_gateway_timeout(self):
        with self.app.test_request_context():
            response = gateway_timeout("some-error")
            self.assertEqual(response[1], 504)

    def test_error(self):
        with self.app.test_request_context():
            response = error("12345678")
            self.assertRegex(response, "12345678")


class TestJoinGithubAuth0User(unittest.TestCase):
    def setUp(self):
        self.org = "some-org"
        self.github_script = MagicMock(GithubScript)
        self.slack_service = MagicMock(SlackService)
        self.app = landing_page_app.create_app(
            self.github_script, self.slack_service, False
        )

    def test_join_github_auth0_user_decorator_is_working(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
        }
        response = self.app.test_client().post(
            "/join-github-auth0-user", data=form_data, follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        # Testing a function that has a decorator which redirect to /index
        # The private function in the function will test the logic
        self.assertEqual(response.request.path, "/index")
        self.app.github_script.add_new_user_to_github_org.assert_not_called()
        self.app.github_script.add_returning_user_to_github_org.assert_not_called()

    # @patch("session.__new__")
    # @patch("flask.session.__new__")
    def test_join_github_auth0_user_new_joiner(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
            "access_as_org": True,
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data
        ) as request_context:
            request_context.session = MagicMock()
            request_context.session = {'user': {'userinfo': {'email': "some-email"}}}
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            response = wrapper_join_github_auth0_users(request_context.request)
            self.assertEqual(response.status_code, 302)
            for item in response.headers:
                if item[0] == 'Location' and item[1] == 'thank-you':
                    redirect = True
            self.assertEqual(redirect, True)
            self.app.github_script.validate_user_rejoining_org.assert_not_called()
            self.app.github_script.add_new_user_to_github_org.assert_called_once_with(
                "some-email", [self.org]
            )

    def test_join_github_auth0_user_rejoining(self):
        form_data = {
            "gh_username": "some-username",
            "access_moj_org": True,
            "access_as_org": True,
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data
        ) as request_context:
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            self.app.github_script.validate_user_rejoining_org.return_value = True
            response = wrapper_join_github_auth0_users(request_context.request)
            self.assertEqual(response.status_code, 302)
            for item in response.headers:
                if item[0] == 'Location' and item[1] == 'thank-you':
                    redirect = True
            self.assertEqual(redirect, True)
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.app.github_script.add_returning_user_to_github_org.assert_called_once_with(
                'some-username', ['some-org']
            )

    def test_join_github_auth0_user_when_rejoining_but_username_not_found(self):
        form_data = {
            "gh_username": "some-username",
            "access_moj_org": True,
            "access_as_org": True,
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data
        ) as request_context:
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            self.app.github_script.validate_user_rejoining_org.return_value = False
            response = wrapper_join_github_auth0_users(request_context.request)
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.app.github_script.add_returning_user_to_github_org.assert_not_called()
            self.assertRegex(response, "Username not found or has expired. Create a new request and leave the username box empty.")

    def test_join_github_auth0_user_when_github_seat_protection_enabled(self):
        form_data = {
            "gh_username": "",
            "access_moj_org": True,
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data
        ) as request_context:
            self.app.github_script.get_selected_organisations.return_value = [self.org]
            self.app.github_script.is_github_seat_protection_enabled.return_value = True
            response = wrapper_join_github_auth0_users(request_context.request)
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.app.github_script.add_returning_user_to_github_org.assert_not_called()
            self.assertRegex(response, "GitHub Seat protection enabled")

    def test_join_github_form_with_incorrect_special_character_inputs(self):
        form_data = {
            "gh_username": "some!username",
            "access_moj_org": True,
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data
        ) as request_context:
            response = wrapper_join_github_auth0_users(request_context.request)
            self.assertRegex(response, "There is a problem")
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.app.github_script.add_returning_user_to_github_org.assert_not_called()

    def test_join_github_form_with_missing_orgs(self):
        form_data1 = {
            "gh_username": "",
        }
        with self.app.test_request_context(
            "/join-github-auth0-user", method="POST", data=form_data1
        ) as request_context:
            response = wrapper_join_github_auth0_users(request_context.request)
            self.assertRegex(response, "There is a problem")
            self.app.github_script.add_new_user_to_github_org.assert_not_called()
            self.app.github_script.add_returning_user_to_github_org.assert_not_called()


class TestCompletedRateLimit(unittest.TestCase):
    def setUp(self):
        self.form_data = {
            "gh_username": "some-username",
            "access_moj_org": True,
            "access_as_org": True,
        }

        self.org = "some-org"
        self.github_script = MagicMock(GithubScript)
        self.slack_service = MagicMock(SlackService)
        self.app = landing_page_app.create_app(
            self.github_script, self.slack_service, True
        )

    def test_rate_limit(self):
        # Send requests until you receive a 429 response
        exceeded_rate_limit = False
        request_count = 0

        while not exceeded_rate_limit:
            response = self.app.test_client().post(
                "/join-github-auth0-user", data=self.form_data, follow_redirects=True
            )
            request_count += 1

            if response.status_code == 429:
                exceeded_rate_limit = True

        # At this point, you have reached the rate limit
        self.assertGreaterEqual(request_count, 1)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
