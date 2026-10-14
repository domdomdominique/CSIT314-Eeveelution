from datetime import datetime, timedelta

import pytest

from app.control.change_password_controller import ChangePasswordController
from app.control.login_controller import LoginController
from app.control.report_idp_controller import ReportIDPController
from app.control.search_idp_controller import SearchIDPController
from app.control.send_enquiry_controller import SendEnquiryController
from app.control.update_profile_controller import UpdateProfileController
from app.entity.db import db
from app.entity.enquiry import Enquiry
from app.entity.idp import IDP
from app.entity.report import Report
from app.entity.user_account import UserAccount


def setup_data():
    designer = UserAccount.create("des@test.com", "password123", "designer", name="Dana Ong")
    customer = UserAccount.create("cus@test.com", "password123", "customer",
                                  name="Sarah Tan", phone="+65 91234567")
    old = datetime.now() - timedelta(days=30)
    loft = IDP(title="Scandinavian Loft", category="Living Room", designer_id=designer.id,
               view_count=900, is_current=True, created_at=old)
    kitchen = IDP(title="Modern Kitchen", category="Kitchen", designer_id=designer.id, view_count=5)
    bedroom = IDP(title="Calm Bedroom", category="Bedroom", designer_id=designer.id, view_count=50,
                  created_at=old - timedelta(days=1))
    db.session.add_all([loft, kitchen, bedroom])
    db.session.commit()
    return customer, designer, loft, kitchen, bedroom


def login(client, email="cus@test.com"):
    client.post("/login", data={"email": email, "password": "password123"})


# --- C-04 search, C-05 filter, C-17 sort ------------------------------------

def test_browse_filters_by_categories_and_status(app):
    setup_data()
    search = SearchIDPController()
    titles = [p.title for p in search.browse(categories=["Kitchen", "Bedroom"])]
    assert titles == ["Calm Bedroom", "Modern Kitchen"]
    assert [p.title for p in search.browse(status="current")] == ["Scandinavian Loft"]
    assert search.browse(categories=["Not a category"]) == search.browse()


def test_browse_sorts_by_views_or_newest_and_matches_designer(app):
    setup_data()
    search = SearchIDPController()
    assert search.browse(sort="views")[0].title == "Scandinavian Loft"
    assert search.browse(sort="newest")[0].title == "Modern Kitchen"
    assert len(search.browse("dana")) == 3  # designer's name


def test_browse_page_is_public_and_shows_filters(client, app):
    setup_data()
    page = client.get("/customer/?category=Kitchen").get_data(as_text=True)
    assert "1 project found" in page
    assert "Modern Kitchen" in page and "Scandinavian Loft" not in page


# --- C-06 view project -------------------------------------------------------

def test_project_page_counts_views_and_404s(client, app):
    _, _, loft, _, _ = setup_data()
    page = client.get(f"/customer/projects/{loft.id}").get_data(as_text=True)
    assert "Scandinavian Loft" in page and "Calm Bedroom" in page  # more by designer
    assert IDP.get(loft.id).view_count == 901
    assert client.get("/customer/projects/999").status_code == 404


# --- C-15 report -------------------------------------------------------------

def test_report_needs_a_valid_reason(app):
    customer, _, loft, _, _ = setup_data()
    controller = ReportIDPController()
    with pytest.raises(ValueError):
        controller.report(customer.id, loft.id, "Because")
    controller.report(customer.id, loft.id, "Spam or advertising", "Selling packages")
    assert Report.count_open() == 1


def test_report_page_requires_customer(client, app):
    _, _, loft, _, _ = setup_data()
    response = client.post(f"/customer/projects/{loft.id}/report", data={"reason": "Other"})
    assert "/login" in response.headers["Location"]
    login(client)
    response = client.post(f"/customer/projects/{loft.id}/report",
                           data={"reason": "Other"}, follow_redirects=True)
    assert "Your report has been sent" in response.get_data(as_text=True)


# --- C-16 enquiry ------------------------------------------------------------

def test_enquiry_is_saved_for_the_designer(app):
    customer, designer, loft, _, _ = setup_data()
    SendEnquiryController().send(customer.id, designer.id, "Sarah", "sarah@test.com",
                                 "Hi, I love this.", loft.id)
    [enquiry] = Enquiry.for_designer(designer.id)
    assert (enquiry.customer_id, enquiry.idp_id) == (customer.id, loft.id)


def test_enquiry_rejects_empty_message_and_non_designers(app):
    customer, designer, _, _, _ = setup_data()
    with pytest.raises(ValueError):
        SendEnquiryController().send(customer.id, designer.id, "Sarah", "sarah@test.com", "  ")
    with pytest.raises(LookupError):
        SendEnquiryController().send(customer.id, customer.id, "Sarah", "x", "Hello")


# --- C-11/C-12 profile, C-14 password ---------------------------------------

def test_update_profile_saves_and_checks_email(app):
    customer, designer, _, _, _ = setup_data()
    controller = UpdateProfileController()
    controller.update(customer.id, "Sarah", "Lim", "sarah@new.com", "8123 4567")
    assert (customer.name, customer.email, customer.phone) == ("Sarah Lim", "sarah@new.com", "+65 81234567")
    assert (customer.first_name, customer.last_name) == ("Sarah", "Lim")
    with pytest.raises(ValueError, match="already used"):
        controller.update(customer.id, "Sarah", "Lim", "des@test.com", "8123 4567")


def test_profile_page_shows_and_updates_details(client, app):
    setup_data()
    login(client)
    assert "cus@test.com" in client.get("/customer/profile").get_data(as_text=True)
    response = client.post("/customer/profile", data={
        "first_name": "Sarah", "last_name": "Lim", "email": "cus@test.com", "phone": "91234567",
    }, follow_redirects=True)
    page = response.get_data(as_text=True)
    assert "Profile updated" in page and "Sarah Lim" in page


def test_change_password_checks_current_password(app):
    customer, _, _, _, _ = setup_data()
    controller = ChangePasswordController()
    with pytest.raises(ValueError, match="current password"):
        controller.change(customer.id, "wrong", "newpassword1", "newpassword1")
    controller.change(customer.id, "password123", "newpassword1", "newpassword1")
    assert LoginController().login("cus@test.com", "newpassword1") is not None


# --- C-01/C-02/C-03 sign up, log in, log out --------------------------------

def test_login_as_role_must_match_account(app):
    setup_data()
    assert LoginController().login("cus@test.com", "password123", "designer") is None
    assert LoginController().login("cus@test.com", "password123", "customer") is not None


def test_register_joins_first_and_last_name(client, app):
    client.post("/register", data={
        "first_name": "Amy", "last_name": "Tan", "email": "amy@test.com", "phone": "91234567",
        "password": "password123", "confirm_password": "password123",
    })
    assert UserAccount.query.filter_by(email="amy@test.com").first().name == "Amy Tan"


def test_logout_shows_goodbye_message(client, app):
    setup_data()
    login(client)
    page = client.get("/logout", follow_redirects=True).get_data(as_text=True)
    assert "You have logged out" in page
