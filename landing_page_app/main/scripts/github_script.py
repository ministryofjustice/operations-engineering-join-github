# import logging
import re
from github import GithubException
from landing_page_app.main.services.github_service import GithubService
from landing_page_app.main.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_TEST_ORG,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    AS_ORG_ALLOWED_EMAIL_DOMAINS
)


class GitHubScript:
    def __init__(self, github_service: GithubService, logger):
        self.github_service = github_service
        self.logger = logger

    def _add_non_pre_appoved_email_user_to_github_org(self, username, email_address, organization):
        pass

    def _add_pre_appoved_email_user_to_github_org(self, user, organisation: str) -> tuple:
        added_user = False
        error_message = None
        try:
            # TODO: replace Org in below function to use function argument
            self.github_service.add_new_user_to_org(user, MOJ_TEST_ORG)
            self.logger.debug(f"{user.login} has been invited to {organisation} with the role 'member'.")
            added_user = True
        except GithubException as err:
            self.logger.error(f"Add user to GH Error: {err}")
            if err.status == 422:
                error_message = "User already a GitHub Org member"
            else:
                error_message = "Unknown error adding user to GitHub Org"
        return added_user, error_message

    def _get_github_user(self, username: str):
        user = None
        error_message = None
        try:
            user = self.github_service.get_user(username)
        except GithubException as err:
            self.logger.error(f"Add user to GH Error: {err}")
            if err.status == 404:
                error_message = "User not found on GitHub."
            else:
                error_message = "Uknown error getting user from GitHub"
        return user, error_message

    def _is_email_address_pre_approved(self, organisation: str, email_address: str):
        pre_approved = False
        email_domain = re.search(r"@([\w.]+)", email_address).group(1)
        if organisation == MOJ_ANALYTICAL_SERVICES:
            if email_domain in AS_ORG_ALLOWED_EMAIL_DOMAINS:
                pre_approved = True
        elif organisation == MINISTRY_OF_JUSTICE:
            if email_domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS:
                pre_approved = True
        return pre_approved

    def add_new_user_to_github_org(self, username: str, email_address: str, organisations: list):
        added_user = False
        error_message = None
        if username == "" or username is None or email_address == "" or email_address is None or len(organisations) == 0:
            self.logger.debug("add_new_user_to_github_org: incorrect function argument")
        else:
            user, error_message = self._get_github_user(username)
            if error_message is None:
                for organisation in organisations:
                    if organisation == MINISTRY_OF_JUSTICE or organisation == MOJ_ANALYTICAL_SERVICES:
                        if self._is_email_address_pre_approved(organisation, email_address):
                            added_user, error_message = self._add_pre_appoved_email_user_to_github_org(user, organisation)
                            if error_message:
                                break
                        else:
                            added_user = self._add_non_pre_appoved_email_user_to_github_org(username, email_address, organisation)
        return added_user, error_message
