from github import Github
from github.NamedUser import NamedUser
import requests
from datetime import datetime, timedelta


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

    def add_new_user_to_org(self, email_address: str, organisation: str) -> None:
        self.github_client_core_api.get_organization(organisation.lower()).invite_user(
            email=email_address
        )

    def get_removed_users_from_audit_log(self, organisation_name: str) -> list:
        users = set()

        # Calculate the date three months ago
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")

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
        return self.github_client_core_api.get_organization(organisation_name).invitations().totalCount
