<<<<<<< HEAD
# Farmer Middleman Loss Analyzer

Lightweight Flask app to estimate how much farmers lose due to middlemen by comparing farm-gate price vs market price and accounting for transport & storage loss.

Quick start (Windows PowerShell):

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
$env:FLASK_APP = "app.py"
flask run
```

Open http://127.0.0.1:5000 in your browser. Use the Register page to create a user, then view the Dashboard to see sample analysis.

What this repo includes:
- `app.py` — Flask application with auth and pages
- `analyzer.py` — loss calculation logic and CSV loader
- `templates/` — HTML templates for login, register, home, dashboard
- `static/style.css` — small stylesheet
- `sample_data.csv` — sample crop data used by the dashboard

Notes and next steps:
- You can extend the scraper and connect to real-time market data.
- Add stronger auth (Flask-Login) and input validation for production.
=======
# Farmer-middleman-loss-analyzer
>>>>>>> 65e3f14b38b4cff1220b0420152ff707e12de16d
