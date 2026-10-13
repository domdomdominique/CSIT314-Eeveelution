import pytest

from app.control.login_controller import LoginController
from app.control.register_controller import RegisterController
from app.entity.user_account import UserAccount

VALID = dict(name="Amy Tan", email="amy@test.com", phone="9123 4567",
             password="password123", confirm_password="password123")


def register(**changes):
    return RegisterController().register(**{**VALID, **changes})


def test_register_creates_customer_who_can_log_in(app):
    account = register()
    assert account.role == "customer"
    assert account.name == "Amy Tan"
    assert account.phone == "+65 91234567"
    assert LoginController().login("amy@test.com", "password123") is not None


def test_email_is_stored_lowercase_and_login_ignores_case(app):
    register(email="  Amy@Test.COM ")
    assert UserAccount.email_exists("amy@test.com")
    assert LoginController().login("AMY@test.com", "password123") is not None


def test_duplicate_email_is_rejected(app):
    register()
    with pytest.raises(ValueError, match="Email already registered"):
        register()


@pytest.mark.parametrize("changes, message", [
    ({"name": "  "}, "name"),
    ({"email": "not-an-email"}, "valid email"),
    ({"phone": "1234"}, "phone"),
    ({"password": "short", "confirm_password": "short"}, "at least 8"),
    ({"confirm_password": "different1"}, "do not match"),
])
def test_invalid_input_is_rejected(app, changes, message):
    with pytest.raises(ValueError, match=message):
        register(**changes)
    assert UserAccount.query.count() == 0


def test_register_page_creates_account_and_redirects_to_login(client):
    response = client.post("/register", data=VALID)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert UserAccount.email_exists("amy@test.com")


def test_register_page_shows_error_and_keeps_input(client):
    response = client.post("/register", data={**VALID, "confirm_password": "nope12345"})
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data
    assert b"Amy Tan" in response.data
