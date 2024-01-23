import pytest

from join_github_app.main.validators.index import is_valid_email_pattern


class TestUtils:

    @pytest.mark.parametrize(
        argnames="email,expected",
        argvalues=[
            ("good.email@example.com", True),
            ("GOOD.A.B@example.co.uk", True),
            ("good2@email", True),
            ("bad@", False),
            ("@bad", False),
            ("bad@@", False),
            ("", False),
            ("%bad@gov.uk.com", False)
        ]
    )
    def test_is_valid_email_pattern(self, email, expected):
        assert is_valid_email_pattern(email) == expected
