# Security Policy

## Supported Versions

CityCab is an actively developed portfolio project. Security fixes are applied to
the latest release on the `main` branch.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue.**

Instead, report it privately using GitHub's
[private vulnerability reporting](https://github.com/Ramandeep-Singh-Mathaon/CityCab/security/advisories/new)
(Security → Report a vulnerability). Please include:

- A description of the vulnerability and its impact
- Steps to reproduce it
- Any relevant logs, screenshots, or proof-of-concept code

You can expect an initial acknowledgement within a few days. Once the issue is
confirmed, a fix will be prepared and released, and you will be credited (unless
you prefer to remain anonymous).

## Security Practices in This Project

- Passwords are stored as salted hashes via Werkzeug, never in plaintext.
- Secrets (`SECRET_KEY`, database URLs) are loaded from a git-ignored `.env` file;
  `.env.example` documents the required variables without real values.
- The database, user uploads, and local data files are excluded from version control.
- Flask debug mode is disabled by default and only enabled via `FLASK_DEBUG=1`.

## Known Non-Production Notes

This is a demonstration project. Before deploying it publicly you should, at minimum:

- Set a strong, unique `SECRET_KEY`.
- Serve the app behind a production WSGI server (e.g. Gunicorn/Waitress) — not the
  Flask development server.
- Move from SQLite to a production database.
- Add CSRF protection and rate limiting to public forms.
