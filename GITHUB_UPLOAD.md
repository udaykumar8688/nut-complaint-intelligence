# Upload NUT to GitHub

## What is included

The repository is safe to upload for a college project. It includes the source
code, NUT dashboard assets, synthetic dataset, and project documentation.

It intentionally excludes:

- `.venv/` local Python environment
- generated model JSON files in `models/`
- `logs/` and local cache files

Anyone who clones the project can recreate the generated model by running:

```powershell
python train.py
```

## First upload

1. Sign in to GitHub and create a new empty repository, for example
   `nut-complaint-intelligence`.
2. Do **not** add a README, `.gitignore`, or license on GitHub because this
   local project already has a README and `.gitignore`.
3. In this project folder, run the following commands. Replace `YOUR-USERNAME`
   with your GitHub username.

```powershell
git init
git add .
git commit -m "Initial commit: NUT complaint intelligence project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nut-complaint-intelligence.git
git push -u origin main
```

## Later updates

```powershell
git add .
git commit -m "Describe your update here"
git push
```

## Before pushing

Run these checks:

```powershell
python train.py
python app.py
```

Then open `http://127.0.0.1:8000` and test one complaint for each routing
queue: Billing, Customer Service, Technical Support, Account Management,
Security & Fraud, and Orders & Delivery.
