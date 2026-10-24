WARESMART - FIXED FLASK + MYSQL PROJECT

1. Install Python 3.11+ and MySQL Server.
2. Extract this folder.
3. Open terminal in this folder and run:
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
4. Copy .env.example to .env. Replace FLASK_SECRET_KEY with a long random value and DB_PASSWORD with your MySQL password. The app falls back to a development-only secret if not configured, but production deployments should always set a real secret.
5. In MySQL Workbench, run schema.sql first, then dummy_data.sql.
   The warehouse seed rows are updated when schema.sql is rerun. CREATE TABLE IF NOT EXISTS does not update old table structures.
6. Create the three manager accounts:
   flask --app app.py seed-managers
7. Start the app:
   flask --app app.py run --debug
8. Open http://127.0.0.1:5000 in Chrome.

DEMO LOGINS (after seed-managers)
Warehouse-Palakkad:   manager1@waresmart.demo / WareSmart@101
Warehouse-Kozhikode:  manager2@waresmart.demo / WareSmart@202
Warehouse-Ernakulam:  manager3@waresmart.demo / WareSmart@303

These are demonstration passwords. Change them before any real use. Passwords are stored as Werkzeug hashes, not plaintext.
Do not upload your .env file or share real database credentials.
