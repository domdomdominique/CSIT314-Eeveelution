import pytest

from app.control.apply_designer_controller import ApplyDesignerController
from app.control.login_controller import LoginController
from app.control.review_designer_application_controller import ReviewDesignerApplicationController
from app.entity.user_account import UserAccount

VALID = dict(name="Ben Lim", email="ben@studio.com", phone="+65 8765 4321",
             password="designer123", confirm_password="designer123",
             company_name="Oak Studio", uen="201912345K",
             portfolio_url="https://oakstudio.sg", experience_years="5",
             description="HDB and condo specialists.")


def apply(**changes):
    return ApplyDesignerController().apply(**{**VALID, **changes})


def make_admin():
    return UserAccount.create("admin@test.com", "password123", "admin")


# --- Applying -----------------------------------------------------------

def test_application_is_pending_and_no_account_is_created(app):
    application = apply()
    assert application.status == "pending"
    assert not UserAccount.email_exists("ben@studio.com")
    assert LoginController().login("ben@studio.com", "designer123") is None


def test_cannot_apply_twice_while_pending(app):
    apply()
    with pytest.raises(ValueError, match="waiting for review"):
        apply()


def test_cannot_apply_with_email_that_already_has_account(app):
    UserAccount.create("ben@studio.com", "password123", "customer")
    with pytest.raises(ValueError, match="Email already registered"):
        apply()


@pytest.mark.parametrize("changes, message", [
    ({"company_name": ""}, "company name"),
    ({"uen": "123"}, "UEN"),
    ({"experience_years": "abc"}, "number"),
    ({"portfolio_url": "javascript:alert(1)"}, "http"),
])
def test_invalid_company_details_are_rejected(app, changes, message):
    with pytest.raises(ValueError, match=message):
        apply(**changes)


def test_customer_cannot_register_while_designer_application_pending(app):
    from app.control.register_controller import RegisterController
    apply()
    with pytest.raises(ValueError, match="Email already registered"):
        RegisterController().register("Ben", "ben@studio.com", "91234567",
                                      "password123", "password123")


# --- Admin review -------------------------------------------------------

def test_approving_creates_designer_account_with_chosen_password(app):
    admin = make_admin()
    application = apply()
    account = ReviewDesignerApplicationController().approve(application.id, admin.id)

    assert account.role == "designer"
    assert account.name == "Ben Lim"
    assert application.status == "approved"
    assert application.reviewed_by == admin.id
    assert application.account_id == account.id
    assert LoginController().login("ben@studio.com", "designer123") is not None


def test_rejecting_keeps_reason_and_creates_no_account(app):
    admin = make_admin()
    application = apply()
    ReviewDesignerApplicationController().reject(application.id, admin.id, "UEN not found")

    assert application.status == "rejected"
    assert application.rejection_reason == "UEN not found"
    assert not UserAccount.email_exists("ben@studio.com")


def test_application_cannot_be_reviewed_twice(app):
    admin = make_admin()
    controller = ReviewDesignerApplicationController()
    application = apply()
    controller.approve(application.id, admin.id)
    with pytest.raises(ValueError, match="already been reviewed"):
        controller.reject(application.id, admin.id)


def test_rejected_applicant_can_apply_again(app):
    admin = make_admin()
    controller = ReviewDesignerApplicationController()
    controller.reject(apply().id, admin.id)
    assert apply().status == "pending"


def test_pending_list_and_count(app):
    admin = make_admin()
    controller = ReviewDesignerApplicationController()
    first = apply()
    apply(email="cara@studio.com")
    controller.approve(first.id, admin.id)

    assert controller.pending_count() == 1
    assert [a.email for a in controller.list_applications("pending")] == ["cara@studio.com"]
    assert [a.email for a in controller.list_applications("approved")] == ["ben@studio.com"]


# --- Pages --------------------------------------------------------------

def login(client, email, password="password123"):
    client.post("/login", data={"email": email, "password": password})


def test_apply_page_submits_and_login_explains_pending(client):
    response = client.post("/register/designer", data=VALID)
    assert response.status_code == 302

    response = client.post("/login", data={"email": "ben@studio.com", "password": "designer123"},
                           follow_redirects=True)
    assert b"still being reviewed" in response.data


def test_admin_can_approve_from_the_page(client):
    make_admin()
    application = apply()
    login(client, "admin@test.com")

    assert b"Oak Studio" in client.get("/admin/applications").data
    assert b"Approve" in client.get(f"/admin/applications/{application.id}").data

    response = client.post(f"/admin/applications/{application.id}/approve")
    assert response.status_code == 302
    assert UserAccount.query.filter_by(email="ben@studio.com", role="designer").first()


def test_customer_cannot_see_applications(client):
    UserAccount.create("amy@test.com", "password123", "customer")
    login(client, "amy@test.com")
    assert client.get("/admin/applications").status_code == 403
