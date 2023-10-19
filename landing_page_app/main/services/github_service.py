from github import Github
from github.NamedUser import NamedUser
import requests
from datetime import datetime, timedelta


class GithubService:
    def __init__(self, org_token: str) -> None:
        self.github_client_core_api: Github = Github(org_token)

    def get_user(self, user_name: str) -> NamedUser:
        return self.github_client_core_api.get_user(user_name.lower())

    def add_new_user_to_org(self, email_address: str, organisation: str) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(
            email=email_address
        )

    # Needs an access token as PyGithub has no Audit Log functionality TODO: good way to do this
    def return_users_removed_from_audit_log(organization: str, access_token: str) -> list:
        users = set()

        # Calculate the date three months ago
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Set initial call
        url = f"https://api.github.com/orgs/{organization}/audit-log?phrase=action:org.remove_member&created_at=>{three_months_ago}&per_page=100"

        while True:
            try:
                headers = {
                    "Authorization": f"token {access_token}",
                }

                # Get log
                response = requests.get(url, headers=headers)
                response.raise_for_status()

                audit_log_data = response.json()

                # Extract users
                for event in audit_log_data:
                    user = event.get("user")
                    if user:
                        # Add to set
                        users.add(user)

                # Pagination
                if "Link" in response.headers:
                    links = response.headers["Link"]
                    if 'rel="next"' not in links:
                        break
                    url = response.links["next"]["url"]
                else:
                    break

            except Exception as e:
                print(f"An error occurred: {e}")
                break

        # Convert to list
        return list(users)
