import logging

import requests
from github import Github, GithubException

from app.main.config.app_config import app_config

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

    def send_invites_to_user_email(self, email: str, organisations: list) -> list[str]:
        valid_orgs = [
            organisation.name
            for organisation in app_config.github.organisations
            if organisation.enabled
        ]
        orgs_failed = []
        for organisation in organisations:
            if (
                organisation in valid_orgs
                and app_config.github.send_email_invites_is_enabled
            ):
                try:
                    self.github_client_core_api.get_organization(
                        organisation.lower()
                    ).invite_user(email=email)

                except GithubException as e:
                    if "already a part of this organization" in str(e):
                        logger.error(
                            "User %s is already a member of the organization.", email
                        )
                        orgs_failed.append(organisation)

                    # Reraise the exception to be caught by the caller
                    logger.error("An unexpected GithubException occurred: %s", e)
                    raise e
                except Exception as e:
                    logger.error("An unexpected exception occurred: %s", str(e))
                    raise e

            elif not app_config.github.send_email_invites_is_enabled:
                logger.info(
                    "Invitation for organisation [ %s ] \
                    not sent as SEND_EMAIL_INVITES is [ %s ]",
                    organisation,
                    app_config.github.send_email_invites_is_enabled,
                )
            else:
                logger.info(
                    "Invitation for organisation [ %s ] \
                    not sent as selected organisation is invalid",
                    organisation,
                )

        return orgs_failed
