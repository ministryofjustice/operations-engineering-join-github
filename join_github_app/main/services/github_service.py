import logging
from datetime import datetime, timedelta

import requests
from github import Github
from github.NamedUser import NamedUser

from join_github_app.main.config.constants import (
    MAX_ALLOWED_ORG_PENDING_INVITES, MINIMUM_ORG_SEATS, MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES, MOJ_ORGS, MOJ_TEST_ORG, SEND_EMAIL_INVITES)

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

    def invite_user_to_org_using_email_address(
        self, email_address: str, organisation: str
    ) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(
            email=email_address
        )

    def send_invitation_to_organisation(self, email: str, organisations: list) -> None:
        if SEND_EMAIL_INVITES is False:
            logger.debug("Sending invites is disabled at the moment.")
            return None

        for organisation in organisations:
            self.invite_user_to_org_using_email_address(
                email,
                organisation
            )

        return None
