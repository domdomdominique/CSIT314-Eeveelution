# CSIT314-Assignment-Eeveelution
CSIT314 Software Development Methodology Group Assignment

Group Name: Eeveelution

Team Members:
- Jeremiah
- Dominique
- Bryan
- Thiri
- Bingxuan
- Xi Ze

An online platform matching renovation customers to interior designers, built with Python + Flask using the Boundary-Control-Entity (B-C-E) design.

## Clone the Repository

```
git clone https://github.com/domdomdominique/CSIT314-Eeveelution.git
code CSIT314-Eeveelution
```


## Run the app locally (Windows PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate          # Mac/Git Bash: source venv/bin/activate
pip install -r requirements.txt
python seed.py                 # creates test data (100 records per type)
python run.py                  # open http://127.0.0.1:5000
```

Demo logins (password `password123`): `admin@demo.com`, `designer@demo.com`, `customer@demo.com`, `platform@demo.com`.

Run tests: `pytest -v`

## Structure (B-C-E)

```
CSIT314-Eeveelution/
├── app/
│   ├── boundary/            Routes + pages, one file per actor
│   │   ├── auth_boundary.py      LoginPage
│   │   ├── customer_boundary.py  SearchIDPPage
│   │   ├── admin_boundary.py, designer_boundary.py, platform_boundary.py
│   │   └── templates/            HTML (Jinja), one folder per actor
│   ├── control/             One controller class per use case
│   │   ├── login_controller.py   LoginController
│   │   └── search_idp_controller.py  SearchIDPController
│   └── entity/              Data classes; the only code that touches the database
│       ├── user_account.py       UserAccount
│       └── idp.py                IDP
├── tests/                   pytest tests, one file per use case
├── seed.py                  Test data generator (100 records per type)
├── run.py                   Starts the app
└── requirements.txt         Python packages
```

Rule: boundary calls one controller; controller calls entities; only entities touch the database.
