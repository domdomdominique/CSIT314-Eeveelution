"""Generate test data: 100 records per data type, plus one known login per role.

Run:  python seed.py
"""
import random
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from app.entity.db import db
from app.entity.designer_application import DesignerApplication
from app.entity.idp import IDP
from app.entity.user_account import UserAccount

CATEGORIES = ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Office", "Retail", "Cafe"]
STYLES = ["Scandinavian", "Industrial", "Modern", "Minimalist", "Japandi", "Classic", "Tropical"]
PLACES = ["Loft", "HDB Flat", "Condo", "Landed House", "Studio", "Shophouse"]
FIRST_NAMES = ["Wei Ming", "Hui Min", "Jun Jie", "Xin Yi", "Ahmad", "Nur Aisyah", "Rajesh",
               "Priya", "Daniel", "Rachel", "Marcus", "Chloe", "Ethan", "Grace", "Farhan", "Divya"]
LAST_NAMES = ["Tan", "Lim", "Lee", "Ng", "Wong", "Goh", "Ong", "Koh", "Teo", "Rahman",
              "Ismail", "Kumar", "Singh", "Nair", "Chen", "Chua"]
COMPANY_WORDS = ["Oak", "Nest", "Haus", "Atelier", "Linea", "Terra", "Mosaic", "Ember", "Blanc", "Zen"]
COMPANY_TYPES = ["Interiors", "Design Studio", "Living", "Concepts", "Spaces"]

random.seed(314)  # same data every run, so demos are repeatable


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_phone():
    return f"+65 {random.choice('89')}{random.randint(0, 9999999):07d}"


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # One known account per role for demos (password: password123)
    for role in UserAccount.ROLES:
        UserAccount.create(f"{role}@demo.com", "password123", role,
                           name=f"Demo {role.title()}", phone=random_phone())

    for i in range(1, 101):
        UserAccount.create(f"customer{i}@test.com", "password123", "customer",
                           name=random_name(), phone=random_phone())
    designers = [UserAccount.create(f"designer{i}@test.com", "password123", "designer",
                                    name=random_name(), phone=random_phone())
                 for i in range(1, 101)]

    for _ in range(100):
        db.session.add(IDP(
            title=f"{random.choice(STYLES)} {random.choice(PLACES)}",
            category=random.choice(CATEGORIES),
            designer_id=random.choice(designers).id,
            view_count=random.randint(0, 500),
            shortlist_count=random.randint(0, 50),
        ))
    db.session.commit()

    # 100 designer applications: 60 pending, 25 approved, 15 rejected
    admin = UserAccount.query.filter_by(email="admin@demo.com").first()
    password_hash = generate_password_hash("password123")  # hash once, it's slow
    applications = []
    for i in range(1, 101):
        company = f"{random.choice(COMPANY_WORDS)} {random.choice(COMPANY_WORDS)} " \
                  f"{random.choice(COMPANY_TYPES)}"
        application = DesignerApplication(
            name=random_name(), email=f"applicant{i}@test.com", phone=random_phone(),
            password_hash=password_hash, company_name=company,
            uen=f"20{random.randint(10, 25)}{random.randint(10000, 99999)}"
                f"{random.choice('ABCDEFGHKMNRWZ')}",
            portfolio_url=f"https://{company.lower().replace(' ', '')}.sg",
            experience_years=random.randint(1, 20),
            description=f"{company} designs {random.choice(STYLES).lower()} homes.",
            submitted_at=datetime.now() - timedelta(days=random.randint(0, 60),
                                                    minutes=random.randint(0, 1439)),
        )
        db.session.add(application)
        applications.append(application)
    db.session.commit()

    for application in applications[60:85]:
        application.approve(admin.id)
    for application in applications[85:]:
        application.reject(admin.id, "Could not verify company UEN.")

    print(f"Accounts: {UserAccount.query.count()}, IDPs: {IDP.query.count()}, "
          f"Designer applications: {DesignerApplication.query.count()} "
          f"({DesignerApplication.count_pending()} pending)")
    print("Demo logins: admin@demo.com / designer@demo.com / customer@demo.com / "
          "platform@demo.com  (password: password123)")
    print("Pending applicant example: applicant1@test.com (cannot log in until approved)")
