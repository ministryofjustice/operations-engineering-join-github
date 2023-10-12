from github import Github


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)

    def get_user(self, user_name):
        return self.github_client_core_api.get_user(user_name)

    def add_new_user_to_org(self, user, organisation: str) -> None:
        self.github_client_core_api.get_organization(organisation).invite_user(user)
