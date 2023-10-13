import unittest
from unittest.mock import MagicMock

from landing_page_app.main.scripts.github_script import GithubScript
import landing_page_app

from landing_page_app.main.views import (
    handle_github_exception,
    page_not_found,
    server_forbidden,
    unknown_server_error,
    gateway_timeout,
)


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_script = MagicMock(GithubScript)
        self.app = landing_page_app.create_app(self.github_script)

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
        response = self.app.test_client().get("/join-github-form.html")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/join-github-form.html")

    def test_thank_you(self):
        response = self.app.test_client().get("/thank-you")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/thank-you")

    def test_form_error(self):
        response = self.app.test_client().get("/form-error")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

    def test_handle_github_exception(self):
        with self.app.test_request_context():
            response = handle_github_exception("12345678")
            if "There was an intenal error: 12345678" in response:
                self.assertTrue(1)
            else:
                self.assertTrue(0)

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


class TestCompletedJoinGithubForm(unittest.TestCase):
    def setUp(self):
        self.form_data = {
            "githubUsername": "some-username",
            "userName": "some-name",
            "userEmailAddress": "some-email",
            "mojOrgAccess": "some-value",
            "asOrgAccess": "some-value",
        }

        self.github_script = MagicMock(GithubScript)
        self.app = landing_page_app.create_app(self.github_script)

    def test_completed_join_github_form(self):
        self.github_script.add_new_user_to_github_org.return_value = True, ""
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/thank-you")

    def test_completed_join_github_form_with_missing_username(self):
        self.form_data["githubUsername"] = None
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

        self.form_data["githubUsername"] = ""
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

    def test_completed_join_github_form_with_missing_email_address(self):
        self.form_data["userEmailAddress"] = None
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

        self.form_data["userEmailAddress"] = ""
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

    def test_completed_join_github_form_with_missing_name(self):
        self.form_data["userName"] = None
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

        self.form_data["userName"] = ""
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")

    def test_completed_join_github_form_with_missing_orgs(self):
        self.form_data["mojOrgAccess"] = None
        self.form_data["asOrgAccess"] = None
        response = self.app.test_client().post("/completed-join-github-form-handler", data=self.form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/form-error")


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
