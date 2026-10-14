from datetime import datetime, timedelta

from app.control.view_landing_page_controller import ViewLandingPageController
from app.entity.db import db
from app.entity.idp import IDP
from app.entity.user_account import UserAccount


def add_projects():
    designer = UserAccount.create("des@test.com", "password123", "designer", name="Dana Ong")
    old = datetime.now() - timedelta(days=30)
    db.session.add_all([
        IDP(title="Popular Loft", category="Living Room", designer_id=designer.id,
            view_count=900, created_at=old),
        IDP(title="New Kitchen", category="Kitchen", designer_id=designer.id, view_count=5),
    ])
    db.session.commit()


def test_landing_sorts_by_views_or_newest(app):
    add_projects()
    controller = ViewLandingPageController()
    assert controller.view()["popular"][0].title == "Popular Loft"
    assert controller.view("newest")["popular"][0].title == "New Kitchen"


def test_landing_counts_categories_and_features_designers(app):
    add_projects()
    page = ViewLandingPageController().view()
    assert ("Living Room", 1) in page["categories"]
    assert ("Bathroom", 0) in page["categories"]
    assert page["featured"][0]["designer"].display_name == "Dana Ong"
    assert page["featured"][0]["project_count"] == 2
    assert page["designer_count"] == 1


def test_landing_page_renders_for_visitors(client, app):
    add_projects()
    page = client.get("/").get_data(as_text=True)
    assert "Popular Loft" in page
    assert "Log in" in page
    assert "/login?next=" in page  # hearts ask visitors to log in


def test_logout_returns_to_landing(client, app):
    UserAccount.create("cus@test.com", "password123", "customer")
    client.post("/login", data={"email": "cus@test.com", "password": "password123"})
    assert client.get("/logout").headers["Location"] == "/"
