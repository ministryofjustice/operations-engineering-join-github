import logging

import requests
from github import Github

from join_github_app.main.config.github import SEND_EMAIL_INVITES

logger = logging.getLogger(__name__)


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)
        self.github_client_rest_api = requests.Session()
        self.github_client_rest_api.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {org_token}",
            }
        )

    def send_invites_to_user_email(self, email: str, organisations: list) -> None:
        if SEND_EMAIL_INVITES == "True":
            for organisation in organisations:
                self.github_client_core_api.get_organization(organisation.lower()).invite_user(email=email)

        logger.debug("Not sending email as SEND_EMAIL_INVITES is %s", SEND_EMAIL_INVITES)
        return None
