from os import environ
import re
from landing_page_app.main.services.github_service import GithubService
from landing_page_app.main.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_TEST_ORG,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    AS_ORG_ALLOWED_EMAIL_DOMAINS
)


def _add_non_pre_appoved_email_user_to_github_org(username, email_address, organization):
    pass


def _add_pre_appoved_email_user_to_github_org(github_service: GithubService, username: str, organisation: str) -> tuple:
    added_user = False
    error_message = None
    try:
        # TODO: replace Org in below function to use function argument
        github_service.add_new_user_to_org(username, MOJ_TEST_ORG)
        added_user = True
    except Exception as err:
        print(f"Add user to GH Error: {err}")
        error_message = repr(err)
    return added_user, error_message


def _is_email_address_pre_approved(organisation: str, email_address: str):
    pre_approved = False
    email_domain = re.search(r"@([\w.]+)", email_address).group(1)
    if organisation == MOJ_ANALYTICAL_SERVICES:
        if email_domain in AS_ORG_ALLOWED_EMAIL_DOMAINS:
            pre_approved = True
    elif organisation == MINISTRY_OF_JUSTICE:
        if email_domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS:
            pre_approved = True
    return pre_approved


def add_new_user_to_github_org(username: str, email_address: str, organisations: list):
    added_user = False
    error_message = None
    if username == "" or username is None or email_address == "" or email_address is None or len(organisations) == 0:
        print("Function argument error")
    else:
        github_token = environ.get("GH_TOKEN")
        github_service = GithubService(github_token)
        for organisation in organisations:
            if organisation == MINISTRY_OF_JUSTICE or organisation == MOJ_ANALYTICAL_SERVICES:
                if _is_email_address_pre_approved(organisation, email_address):
                    added_user, error_message = _add_pre_appoved_email_user_to_github_org(github_service, username, organisation)
                else:
                    added_user = _add_non_pre_appoved_email_user_to_github_org(username, email_address, organisation)
    return added_user, error_message
