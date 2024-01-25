from datetime import datetime, timedelta

import logging
import requests
from github import Github
from github.NamedUser import NamedUser

from join_github_app.main.config.constants import (
    MAX_ALLOWED_ORG_PENDING_INVITES,
    MINIMUM_ORG_SEATS,
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_ORGS,
    MOJ_TEST_ORG,
    SEND_EMAIL_INVITES,
)

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

    def get_user(self, user_name: str) -> NamedUser:
        return self.github_client_core_api.get_user(user_name.lower())

    def invite_user_to_org_using_email_address(
        self, email_address: str, organisation: str
    ) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(
            email=email_address
        )

    def get_removed_users_from_audit_log(self, organisation_name: str) -> list:
        users = set()

        # Calculate the date three months ago
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        pagination = True
        url = f"https://api.github.com/orgs/{organisation_name}/audit-log?phrase=action:org.remove_member&created_at=>{three_months_ago}&per_page=100"

        while pagination:
            # Get log
            response = self.github_client_rest_api.get(url)
            response.raise_for_status()
            audit_log_data = response.json()

            # Extract users
            for event in audit_log_data:
                user = event.get("user")
                if user:
                    users.add(user.lower())

            # Check for next page in Pagination
            if response.links.get("next") is not None:
                url = response.links["next"]["url"]
            else:
                pagination = False
        return list(users)

    def get_org_available_seats(self, organisation_name: str) -> int:
        organisation = self.github_client_core_api.get_organization(organisation_name)
        return organisation.plan.seats - organisation.plan.filled_seats

    def get_org_pending_invites(self, organisation_name: str) -> int:
        return (
            self.github_client_core_api.get_organization(organisation_name)
            .invitations()
            .totalCount
        )

    def add_new_user_to_github_org(
        self,
        email_address: str,
        organisations: list,
        send_email_invites: bool = SEND_EMAIL_INVITES,
    ):
        if send_email_invites:
            if email_address == "" or email_address is None or len(organisations) == 0:
                logger.debug("add_new_user_to_github_org: incorrect function argument")
            else:
                for organisation in organisations:
                    if organisation.lower() in MOJ_ORGS:
                        # TODO: change MOJ_TEST_ORG to organisation
                        self.invite_user_to_org_using_email_address(
                            email_address.lower(), MOJ_TEST_ORG
                        )
                        logger.debug(
                            f"{email_address.lower()} has been invited to {organisation.lower()} with the role 'member'."
                        )
        else:
            logger.debug(
                f"send_email_invites toggle set to {str(send_email_invites)}: No invite sent."
            )

    def get_selected_organisations(self, moj_org: bool, as_org: bool) -> list:
        organisations = []
        if moj_org:
            organisations.append(MINISTRY_OF_JUSTICE)
        if as_org:
            organisations.append(MOJ_ANALYTICAL_SERVICES)
        return organisations

    def is_user_in_audit_log(self, username: str = "", organisation: str = ""):
        found_user = False
        # TODO: change MOJ_TEST_ORG to organisation
        removed_users = self.get_removed_users_from_audit_log(
            MOJ_TEST_ORG
        )
        username = username.lower()
        if username in removed_users:
            found_user = True
        return found_user

    def is_github_seat_protection_enabled(self):
        protection_enabled = False
        for organisation in MOJ_ORGS:
            available_seats = self.get_org_available_seats(organisation)
            pending_invites = self.get_org_pending_invites(organisation)
            if (
                available_seats <= MINIMUM_ORG_SEATS
                or pending_invites >= MAX_ALLOWED_ORG_PENDING_INVITES
            ):
                protection_enabled = True
                break
        return protection_enabled
