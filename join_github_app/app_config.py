import os
from types import SimpleNamespace


def __get_env_var(name: str) -> str | None:
    return os.getenv(name)


def __get_env_var_as_boolean(name: str) -> bool | None:
    value = __get_env_var(name)

    print("function: ", value)

    if value is None:
        return False

    if value.lower() == "true":
        return True

    return False


app_config = SimpleNamespace(
    flask=SimpleNamespace(
        app_secret_key=__get_env_var("APP_SECRET_KEY")
    ),
    github=SimpleNamespace(
        send_email_invites_is_enabled=__get_env_var_as_boolean("SEND_EMAIL_INVITES")
    )
)
