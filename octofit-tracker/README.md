OctoFit Tracker — Project skeleton

This folder contains the initial OctoFit Tracker layout.

Structure:

octofit-tracker/
├── backend/
│   ├── venv/            # (optional) Python virtual environment location
│   └── octofit_tracker/ # Django app package (empty scaffold)
└── frontend/            # React/frontend code

Quick setup (create venv & install requirements):

```bash
python3 -m venv octofit-tracker/backend/venv
source octofit-tracker/backend/venv/bin/activate
pip install -r octofit-tracker/backend/requirements.txt
```

Notes:
- Follow the project instructions in `.github/instructions` for detailed backend/frontend scaffolding.
- Do not change directories in automated scripts; refer to explicit paths as needed.
