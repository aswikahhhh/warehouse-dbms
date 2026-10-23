WARESMART - FIXED FLASK + MYSQL PROJECT

1. Install Python 3.11+ and MySQL Server.
2. Extract this folder.
3. Open terminal in this folder and run:
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
4. Copy .env.example to .env. Replace FLASK_SECRET_KEY with a long random value and DB_PASSWORD with your MySQL password.
5. In MySQL Workbench, run schema.sql first, then dummy_data.sql.
   If you already created an older database, back it up first. CREATE TABLE IF NOT EXISTS does not update old tables.
6. Create the three manager accounts:
   flask --app app.py seed-managers
7. Start the app:
   flask --app app.py run --debug
8. Open http://127.0.0.1:5000 in Chrome.

DEMO LOGINS (after seed-managers)
Main Warehouse:   manager1@waresmart.demo / WareSmart@101
North Warehouse:  manager2@waresmart.demo / WareSmart@202
Central Warehouse: manager3@waresmart.demo / WareSmart@303

These are demonstration passwords. Change them before any real use. Passwords are stored as Werkzeug hashes, not plaintext.
Do not upload your .env file or share real database credentials.
