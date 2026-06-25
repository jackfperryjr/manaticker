# MTG Collection Tracker

Tracks the market value of one or more Moxfield collections over time and
surfaces the biggest price movers, similar to a stock portfolio tracker.
Supports multiple user accounts, each with their own collections.

## How it works

- `moxfield.py` pulls every card from a **public** Moxfield collection via
  Moxfield's collection API (`https://moxfield.com/collection/<id>`). Each
  collection must be set to public in Moxfield's privacy settings or the
  fetch will fail.
- Each fetch is stored as a timestamped "snapshot" in Postgres — one row per
  card, including its current unit price, scoped to the collection it
  belongs to.
- The dashboard (`app.py`) shows total collection value over time and the
  top N gainers/losers in dollar value since the previous snapshot (N is
  adjustable per view, defaulting to a per-account setting).
- Movers require **at least two snapshots** to exist for a collection; the
  first fetch will show an empty state until a second snapshot is taken.
- Accounts: sign up with email/password, then add one or more Moxfield
  collection links. There's no per-account collection limit yet, but the
  schema and routes are built so a future paid-tier limit is a small check,
  not a migration.

## Local setup

This app uses Postgres, not SQLite. You need a `DATABASE_URL` to develop
against — easiest is a Postgres instance on Railway (see below), but any
reachable Postgres connection string works.

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Create a `.env` file in the project root (gitignored, never commit this):

```
DATABASE_URL=postgresql://user:password@host:port/railway
SECRET_KEY=some-long-random-string
```

Then:

```
venv\Scripts\python run_fetch.py   # creates tables, fetches nothing yet (no collections exist)
venv\Scripts\python app.py         # serve the dashboard at http://127.0.0.1:5000
```

Sign up, add a Moxfield collection link, and click **Refresh now** on the
dashboard whenever you want a new snapshot.

## Getting a Postgres connection string from Railway

1. In the Railway dashboard, open or create a project and add a PostgreSQL
   database (**+ New** → **Database** → **Add PostgreSQL**).
2. Click the Postgres service → **Variables** tab.
3. Copy `DATABASE_PUBLIC_URL` for local development (`DATABASE_URL` only
   works from inside Railway's private network, between services in the
   same project).
4. Once the Flask app itself is also deployed on Railway, use the internal
   `DATABASE_URL` for the deployed app instead — it's faster and doesn't
   leave Railway's network.

## Scheduling daily snapshots

`run_fetch.py` loops over every collection in the database and takes a new
snapshot. In production, run it on a schedule with Railway's own Cron Job
feature (pointed at the same Postgres instance as the web service) rather
than GitHub Actions, since GitHub Actions can't serve the live multi-user
site.

## Deploying to Railway

The web app, Postgres database, and the daily-fetch Cron Job all live in the
same Railway project.

1. Push this repo to GitHub.
2. In the Railway project that already has the Postgres database: **+ New**
   → **GitHub Repo** → select this repo. Railway detects the `Procfile`
   (`gunicorn app:app`) and deploys it as a web service automatically on
   every push to `main`.
3. On that new web service, open **Variables** and set:
   - `DATABASE_URL` → reference the Postgres service's internal URL, e.g.
     `${{Postgres.DATABASE_URL}}` (use the variable-reference picker in the
     Railway UI rather than typing it by hand — it stays in sync if the DB
     ever changes).
   - `SECRET_KEY` → a long random string (e.g. `python -c "import secrets;
     print(secrets.token_hex(32))"`). The app refuses to start in production
     without this set.
4. Under **Settings** → **Networking**, generate a public domain for the
   web service so it's reachable from a browser.
5. Add the Cron Job: **+ New** → **Empty Service** (or deploy from the same
   repo again) → set **Start Command** to `python run_fetch.py` and a
   **Cron Schedule** (e.g. `0 13 * * *` for daily). Give it the same
   `DATABASE_URL` variable reference as the web service. No public domain
   needed for this one.

After the first deploy, `db.init_db()` runs automatically on app startup and
creates the schema if it doesn't already exist — no separate migration step.

## Security notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2).
- All forms are CSRF-protected via Flask-WTF.
- There is no email verification or password reset flow yet.
