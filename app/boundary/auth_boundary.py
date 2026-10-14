from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.boundary import safe_next
from app.control.apply_designer_controller import ApplyDesignerController
from app.control.login_controller import LoginController
from app.control.register_controller import RegisterController
from app.control.view_landing_page_controller import ViewLandingPageController

auth_bp = Blueprint("auth", __name__)

HOME_BY_ROLE = {
    "admin": "admin.home",
    "designer": "designer.home",
    "customer": "customer.home",
    "platform": "platform.home",
}

# "Log in as" choices on the login page (C-02, ID-01, PM-01, UA-01)
LOGIN_ROLES = {
    "customer": "Customer",
    "designer": "Interior Designer",
    "platform": "Platform Management",
    "admin": "User Admin",
}

APPLICATION_MESSAGES = {
    "pending": "Your designer application is still being reviewed. "
               "You can log in once an admin approves it.",
    "rejected": "Your designer application was not approved. "
                "Please contact us or apply again.",
}


@auth_bp.route("/")
def index():
    """Boundary: LandingPage (public customer landing page)."""
    customer_id = session["user_id"] if session.get("role") == "customer" else None
    page = ViewLandingPageController().view(request.args.get("sort"), customer_id)
    return render_template("customer/landing.html", **page)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Boundary: LoginPage (C-02, and the login for every other actor)."""
    if request.method == "POST":
        controller = LoginController()
        role = request.form.get("role") if request.form.get("role") in LOGIN_ROLES else None
        account = controller.login(request.form["email"], request.form["password"], role)
        if account:
            session.clear()
            session.permanent = bool(request.form.get("remember"))
            session["user_id"] = account.id
            session["role"] = account.role
            session["name"] = account.name
            next_url = safe_next(request.args.get("next"))
            return redirect(next_url or url_for(HOME_BY_ROLE[account.role]))
        status = controller.application_status(request.form["email"])
        flash(APPLICATION_MESSAGES.get(status, "Invalid email or password."), "error")
    return render_template("auth/login.html", roles=LOGIN_ROLES, form=request.form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Boundary: RegisterPage (C-01 customer sign-up, account is active immediately)."""
    if request.method == "POST":
        f = request.form
        try:
            RegisterController().register(
                _full_name(f), f.get("email"), f.get("phone"),
                f.get("password"), f.get("confirm_password"),
            )
        except ValueError as error:
            flash(str(error), "error")
        else:
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", account_type="customer", form=request.form)


def _full_name(form):
    """The sign-up forms ask for first and last name; accounts store one name."""
    if form.get("name"):
        return form.get("name")
    return f"{form.get('first_name', '').strip()} {form.get('last_name', '').strip()}".strip()


@auth_bp.route("/register/designer", methods=["GET", "POST"])
def apply_designer():
    """Boundary: ApplyDesignerPage (application goes to the User Admin for approval)."""
    if request.method == "POST":
        f = request.form
        try:
            ApplyDesignerController().apply(
                _full_name(f), f.get("email"), f.get("phone"),
                f.get("password"), f.get("confirm_password"),
                f.get("company_name"), f.get("uen"), f.get("portfolio_url"),
                f.get("experience_years"), f.get("description"),
            )
        except ValueError as error:
            flash(str(error), "error")
        else:
            flash("Application submitted! An admin will review it, "
                  "and you can log in once it is approved.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", account_type="designer", form=request.form)


@auth_bp.route("/logout")
def logout():
    """Boundary: Log out (C-03). The confirm dialog is shown by the page before this link."""
    was_logged_in = "user_id" in session
    session.clear()
    if was_logged_in:
        flash("You have logged out. See you again soon!", "success")
    return redirect(url_for("auth.index"))
