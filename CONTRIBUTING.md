# Contributing to CityCab

Thanks for your interest in improving CityCab! This project welcomes issues, ideas, and pull requests.

## Ways to contribute

- 🐛 **Report bugs** — open an issue using the *Bug report* template.
- 💡 **Suggest features** — open an issue using the *Feature request* template.
- 📝 **Improve docs** — typos, clarifications, and examples are all welcome.
- 🔧 **Submit code** — fix a bug or build a feature from the roadmap.

## Development setup

```bash
git clone https://github.com/Ramandeep-Singh-Mathaon/CityCab.git
cd CityCab
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

The app runs at http://127.0.0.1:5000 and creates its SQLite database automatically.

## Branching & commits

1. Fork the repository and create a topic branch:
   ```bash
   git checkout -b feat/short-description
   ```
2. Keep changes focused — one logical change per pull request.
3. Write clear commit messages. This project follows a lightweight
   [Conventional Commits](https://www.conventionalcommits.org/) style:
   - `feat:` a new feature
   - `fix:` a bug fix
   - `docs:` documentation only
   - `refactor:` code change that neither fixes a bug nor adds a feature
   - `style:` formatting, no logic change
   - `chore:` tooling, dependencies, housekeeping

## Coding guidelines

- **Python** — follow [PEP 8](https://peps.python.org/pep-0008/); keep functions small and readable.
- **Templates** — extend `templates/base.html`; reuse the design-system classes from `static/css/citycab.css` rather than adding one-off styles.
- **JavaScript** — keep it dependency-free and use the shared `CityCab` helpers (`CityCab.toast`, validation) where possible.
- **Secrets** — never commit `.env`, credentials, API keys, or the database. Use `.env.example` to document new variables.

## Pull request checklist

Before opening a PR, please confirm:

- [ ] The app runs (`python app.py`) with no errors.
- [ ] All existing pages still load and forms still submit.
- [ ] No secrets, personal data, or large binaries are included.
- [ ] The PR description explains **what** changed and **why**.

Fill out the pull request template when you open your PR. A maintainer will review it as soon as possible. Thank you! 🙌
