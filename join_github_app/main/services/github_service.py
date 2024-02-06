import logging

import requests
from github import Github

from join_github_app.app_config import app_config

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
        valid_orgs = [ organisation.name for organisation in app_config.github.organisations if organisation.enabled ]
        for organisation in organisations:
            if organisation in valid_orgs and app_config.github.send_email_invites_is_enabled:
                self.github_client_core_api.get_organization(organisation.lower()).invite_user(email=email)
            elif not app_config.github.send_email_invites_is_enabled:
                logger.info("Not sending invitation for organisation [ %s ] as SEND_EMAIL_INVITES is [ %s ]", organisation, app_config.github.send_email_invites_is_enabled)
            else:
                logger.info("Invitation for organisation [ %s ] not sent as selected organisation is invalid", organisation)
