import re
from wtforms import Form, BooleanField, StringField, validators, ValidationError


class InputCheck:
    def __init__(self, regex, message=None):
        self.regex = regex
        self.message = message

    def __call__(self, form, field):
        p = re.compile(self.regex)
        if field.data is None:
            raise ValidationError(self.message)
        if re.search(p, field.data.lower()):
            raise ValidationError(self.message)


class JoinGithubFormAuth0User(Form):
    gh_username = StringField(
        "GitHub Username",
        [
            validators.Length(min=0, max=25),
            InputCheck(
                regex="^(?=.*[+_!@#$%^&*., ?])",
                message="Special characters not allowed",
            ),
        ],
    )
    access_moj_org = BooleanField("Ministry of Justice")
    access_as_org = BooleanField("MoJ Analytical Services")

    def validate_org(self):
        if (
            self.access_moj_org.data is False
            and self.access_as_org.data is False
            or self.access_moj_org.data is None
            and self.access_as_org.data is None
        ):
            self.access_moj_org.errors.append("Select an Organisation")
            self.access_as_org.errors.append("Select an Organisation")
            return False
        return True
