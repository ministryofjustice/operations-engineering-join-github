from github import Github
from github.NamedUser import NamedUser


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)

    def get_user(self, user_name: str):
        return self.github_client_core_api.get_user(user_name.lower())

    def add_new_user_to_org(self, user: NamedUser, organisation: str) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(user)
