import unittest
from unittest.mock import MagicMock

from app.app import create_app
from app.main.services.github_service import GithubService


class TestViews(unittest.TestCase):
    def setUp(self):
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, False)
        self.app.config["SECRET_KEY"] = "test_flask"
        self.client = self.app.test_client()

    def test_default(self):
        response = self.app.test_client().get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/")

    def test_robots(self):
        response = self.app.test_client().get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/robots.txt")


class TestCompletedRateLimit(unittest.TestCase):
    def setUp(self):
        self.form_data = {
            "gh_username": "some-username",
        }

        self.org = "some-org"
        self.github_service = MagicMock(GithubService)
        self.app = create_app(self.github_service, True)

    def test_rate_limit(self):
        # Send requests until you receive a 429 response
        exceeded_rate_limit = False
        request_count = 0

        while not exceeded_rate_limit:
            response = self.app.test_client().post(
                "/join/submit-email", data=self.form_data, follow_redirects=True
            )
            request_count += 1

            if response.status_code == 429:
                exceeded_rate_limit = True

        # At this point, you have reached the rate limit
        self.assertGreaterEqual(request_count, 1)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
