from github import Github
from github.NamedUser import NamedUser


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)

    def get_user(self, user_name: str) -> NamedUser:
        return self.github_client_core_api.get_user(user_name.lower())

    def add_new_user_to_org(self, email_address: str, organisation: str) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(
            email=email_address
        )
