import os
from types import SimpleNamespace


def __get_env_var(name: str) -> str | None:
    return os.getenv(name)


def __get_env_var_as_boolean(name: str) -> bool | None:
    value = __get_env_var(name)

    if value is None:
        return False

    if value.lower() == "true":
        return True

    return False


app_config = SimpleNamespace(
    auth0=SimpleNamespace(
        domain=__get_env_var("AUTH0_DOMAIN"),
        client_id=__get_env_var("AUTH0_CLIENT_ID"),
        client_secret=__get_env_var("AUTH0_CLIENT_SECRET"),
    ),
    flask=SimpleNamespace(
        app_secret_key=__get_env_var("APP_SECRET_KEY"),
    ),
    github=SimpleNamespace(
        send_email_invites_is_enabled=__get_env_var_as_boolean("SEND_EMAIL_INVITES"),
        token=__get_env_var("ADMIN_GITHUB_TOKEN"),
        allowed_email_domains=[
            "digital.justice.gov.uk",
            "justice.gov.uk",
            "publicguardian.gov.uk",
            "cica.gov.uk",
            "ima-citizensrights.org.uk",
            "judicialappointments.gov.uk",
            "judiciary.uk",
            "ppo.gov.uk",
            "sentencingcouncil.gov.uk",
            "yjb.gov.uk",
        ],
        organisations=[
            SimpleNamespace(
                name="ministryofjustice",
                enabled=__get_env_var_as_boolean("MOJ_ORG_ENABLED"),
                display_text="Ministry of Justice",
            ),
            SimpleNamespace(
                name="moj-analytical-services",
                enabled=__get_env_var_as_boolean("MOJ_AS_ORG_ENABLED"),
                display_text="MoJ Analytical Services",
            ),
            SimpleNamespace(
                name="ministryofjustice-test",
                enabled=__get_env_var_as_boolean("MOJ_TEST_ORG_ENABLED"),
                display_text="Ministry of Justice Test Organisation",
            ),
        ],
    ),
    logging_level=__get_env_var("LOGGING_LEVEL"),
    phase_banner_text=__get_env_var("PHASE_BANNER_TEXT"),
    sentry=SimpleNamespace(
        dsn_key=__get_env_var("SENTRY_DSN_KEY"), environment=__get_env_var("SENTRY_ENV")
    ),
)
