# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-06

First public release.

### Added
- Passenger authentication: register, log in, log out with hashed passwords.
- Instant ride booking with an interactive map, live route drawing, and fare estimation.
- Scheduled ("future") ride booking with date and time selection.
- Ride history with status badges and ride cancellation.
- Driver dashboard to view and accept available rides, with auto-refresh.
- Admin dashboard with a searchable, sortable table of all bookings and fleet stats.
- Profile management: avatar upload, phone, and password change.
- Role-based access control for passengers, drivers, and admins.
- Reusable glassmorphism design system (`static/css/citycab.css`, `static/js/citycab.js`)
  with an animated aurora background, top navbar, toast notifications, and responsive layouts.
- Project documentation: README, contributing guide, code of conduct, security policy,
  issue/PR templates, and `.env.example`.

### Changed
- Redesigned the entire front end from the ground up with a new visual identity
  (glassmorphism, Sora/Inter typography, indigo–violet palette, top navigation).
- Replaced Google Maps with a key-free stack: Leaflet + OpenStreetMap tiles,
  Nominatim geocoding, and OSRM routing.

### Fixed
- Resolved a `sqlite3.OperationalError: disk I/O error` caused by a fragile relative
  database path; the database now resolves to an absolute path in `instance/`.
- Fixed a Windows-specific bug where `os.path.join` produced a backslash database URL
  that SQLAlchemy could not parse; paths are now normalized to forward slashes.
- Added `functools.wraps` to the admin authorization decorator so the admin route
  keeps its endpoint name.

### Security
- Removed a hardcoded Google Maps API key from the templates.
- Neutralized an unused `users.json` file that contained a plaintext credential and
  excluded it (along with `.env`, the database, uploads, and data files) via `.gitignore`.
- Made Flask debug mode opt-in through the `FLASK_DEBUG` environment variable
  (off by default) instead of being hardcoded on.
