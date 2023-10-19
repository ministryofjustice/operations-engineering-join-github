from textwrap import dedent
from slack_sdk import WebClient


class SlackService:
    # TODO: Change "C033QBE511V" to the "C01BUKJSZD4" when go into Production
    OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID = "C033QBE511V"

    # Added to stop TypeError on instantiation. See https://github.com/python/cpython/blob/d2340ef25721b6a72d45d4508c672c4be38c67d3/Objects/typeobject.c#L4444
    def __new__(cls, *_, **__):
        return super(SlackService, cls).__new__(cls)

    def __init__(self, slack_token: str) -> None:
        self.slack_client = WebClient(slack_token)

    def send_add_new_user_to_github_orgs(self, requests: list):
        organisations = []
        for request in requests:
            username = request["username"]
            organisations.append(request["organisation"])
            email_address = request["email_address"]
        organisations = " and ".join(organisations)
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Join GitHub Automation*
                            Please review add user {username} to GitHub Organisation/s: {organisations}. Email address is {email_address}.
                            """).strip("\n"),
                    },
                }
            ],
        )

    def send_user_wants_to_rejoin_github_orgs(self, username: str, email_address: str, organisations: list):
        organisations = " and ".join(organisations)
        self.slack_client.chat_postMessage(
            channel=self.OPERATIONS_ENGINEERING_ALERTS_CHANNEL_ID,
            mrkdown=True,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": dedent(f"""
                            *Join GitHub Automation*
                            The user {username} wants to rejoin the GitHub Organisation/s: {organisations}. Email address is {email_address}.
                            """).strip("\n"),
                    },
                }
            ],
        )
