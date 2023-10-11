from github import Github


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)

    def add_new_user_to_org(self, user_name: str, organisation: str) -> None:
        user = self.github_client_core_api.get_user(user_name)
        self.github_client_core_api.get_organization(organisation).invite_user(user)
        print(f"{user.login} has been invited to {organisation} with the role 'member'.")
