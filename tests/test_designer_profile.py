import pytest

from app.control.apply_designer_controller import ApplyDesignerController
from app.control.review_designer_application_controller import ReviewDesignerApplicationController
from app.control.view_designer_profile_controller import ViewDesignerProfileController
from app.entity.db import db
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


def approved_designer():
    admin = UserAccount.create("admin@test.com", "password123", "admin")
    application = ApplyDesignerController().apply(
        "Ben Lim", "ben@studio.com", "+65 8765 4321", "designer123", "designer123",
        "Oakline Studio", "201912345K", "https://oakline.sg", "5", "Warm, practical homes.")
    designer = ReviewDesignerApplicationController().approve(application.id, admin.id)
    db.session.add_all([
        IDP(title="Warm HDB", category="Living Room", designer_id=designer.id,
            view_count=3000, is_current=True),
        IDP(title="Galley kitchen", category="Kitchen", designer_id=designer.id, view_count=500),
        IDP(title="Bishan flat", category="Living Room", designer_id=designer.id, view_count=10),
    ])
    db.session.commit()
    return designer


def test_profile_uses_company_details_and_counts(app):
    designer = approved_designer()
    page = ViewDesignerProfileController().view(designer.id)
    assert page["designer"].display_name == "Oakline Studio"
    assert page["designer"].initials == "OS"
    assert (page["total"], page["current"], page["past"], page["views"]) == (3, 1, 2, 3510)
    assert page["category_share"] == [("Living Room", 67), ("Kitchen", 33)]


def test_profile_can_filter_current_and_past(app):
    designer = approved_designer()
    controller = ViewDesignerProfileController()
    assert [p.title for p in controller.view(designer.id, "current")["projects"]] == ["Warm HDB"]
    assert len(controller.view(designer.id, "past")["projects"]) == 2


def test_profile_rejects_non_designers(app):
    customer = UserAccount.create("cus@test.com", "password123", "customer")
    with pytest.raises(LookupError):
        ViewDesignerProfileController().view(customer.id)


def test_profile_page_is_public(client, app):
    designer = approved_designer()
    page = client.get(f"/customer/designers/{designer.id}").get_data(as_text=True)
    assert "Oakline Studio" in page
    assert "Projects (3)" in page
    assert client.get("/customer/designers/999").status_code == 404


def test_designers_page_lists_designers_with_projects(client, app):
    approved_designer()
    UserAccount.create("idle@test.com", "password123", "designer", name="Idle Person")
    page = client.get("/customer/designers").get_data(as_text=True)
    assert "Oakline Studio" in page
    assert "Idle Person" not in page
