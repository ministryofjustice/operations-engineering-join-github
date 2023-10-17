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


class JoinGithubForm(Form):
    gh_username = StringField(
        "GitHub Username",
        [
            validators.Length(min=3, max=25),
            InputCheck(
                regex="^(?=.*[+_!@#$%^&*., ?])",
                message="Special characters not allowed",
            ),
            validators.InputRequired(),
        ],
    )
    email_address = StringField(
        "Email Address",
        [
            validators.Length(min=6, max=120),
            InputCheck(
                regex="^(?=.*[-+!#$%^&*,?])", message="Special characters not allowed"
            ),
            validators.Email(check_deliverability=True),
            validators.InputRequired(),
        ],
    )
    name = StringField(
        "Name",
        [
            validators.Length(min=3, max=35),
            InputCheck(
                regex="^(?=.*[-+_!@#$%^&*.,?])",
                message="Special characters not allowed",
            ),
            InputCheck(regex="^(?=.*[0123456789])", message="Numbers not allowed"),
            validators.InputRequired(),
        ],
    )
    access_moj_org = BooleanField("Ministry Of Justice")
    access_as_org = BooleanField("Analytical Services")

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
