import unittest
from unittest.mock import MagicMock, patch
from landing_page_app.main.services.slack_service import SlackService


@patch("slack_sdk.WebClient.__new__")
class TestSlackServiceInit(unittest.TestCase):

    def test_sets_up_class(self, mock_slack_client: MagicMock):
        mock_slack_client.return_value = "test_mock"
        slack_service = SlackService("")
        self.assertEqual("test_mock",
                         slack_service.slack_client)


@patch("slack_sdk.WebClient.__new__")
class SendAddNewUserToGithubOrgs(unittest.TestCase):

    def test_send_add_new_user_to_github_orgs(self, mock_slack_client: MagicMock):
        test_data = {"username": "some-user", "email_address": "some-email", "organisation": "some-org"}
        test_data_list = [test_data, test_data]
        SlackService("").send_add_new_user_to_github_orgs(test_data_list)
        mock_slack_client.return_value.chat_postMessage.assert_called_with(
            channel="C033QBE511V",
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": '*Join GitHub Automation*\nPlease review adding the following user/s to GitHub Organisation/s:\nsome-user to some-org GH Org. (Email address is some-email) and some-user to some-org GH Org. (Email address is some-email)'
                    }
                }
            ]
        )


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
