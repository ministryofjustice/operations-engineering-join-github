import os
import unittest
from unittest.mock import patch
from app.app_config import __get_env_var_as_boolean as get_env_var_as_boolean


class TestGetEnvVarAsBoolean(unittest.TestCase):

    @patch.dict(os.environ, {"SEND_EMAIL_INVITES": "True"}, clear=True)
    def test_sentence_case_is_true(self):
        response = get_env_var_as_boolean("SEND_EMAIL_INVITES")
        self.assertEqual(response, True)

    @patch.dict(os.environ, {"SEND_EMAIL_INVITES": "TRUE"}, clear=True)
    def test_capitalised_is_true(self):
        response = get_env_var_as_boolean("SEND_EMAIL_INVITES")
        self.assertEqual(response, True)

    @patch.dict(os.environ, {"SEND_EMAIL_INVITES": "asdfa"}, clear=True)
    def test_returns_false_for_anything_else(self):
        response = get_env_var_as_boolean("SEND_EMAIL_INVITES")
        self.assertEqual(response, False)


if __name__ == "__main__":
    unittest.main()
