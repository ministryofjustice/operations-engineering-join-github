import unittest
from unittest.mock import MagicMock

import landing_page_app
from landing_page_app import GithubScript
from landing_page_app.main.middleware.utils import is_valid_email_pattern


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.github_script = MagicMock(GithubScript)
        self.app = landing_page_app.create_app(self.github_script, False)

    


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
