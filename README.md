# NUT Complaint Intelligence

NUT is a college project by **Nishant Kumar, Uday Kumar, and Tanu Yadav**. It
uses Natural Language Processing to suggest the right support queue for a
written customer complaint.

The dashboard recommends one of six categories:

- `Billing`
- `Customer Service`
- `Technical Support`
- `Account Management`
- `Security & Fraud`
- `Orders & Delivery`

The classifier uses a cue-assisted multinomial Naive Bayes text model. It runs
fully offline with Python's standard library and includes an interactive dashboard.

> The included dataset is fictional and balanced for classroom demonstration.
> It contains no real customer records.

## Quick start

### 1. Install Python

Install Python 3.10 or later. No third-party packages are required.

### 2. Train the example model

From this project folder, run:

```powershell
.\.venv\Scripts\python.exe train.py
```

This writes the reusable model to `models/complaint_classifier.json` and the
test results to `models/metrics.json`.

### 3. Start the dashboard

```powershell
.\venv\Scripts\python.exe app.py
```

If you do not use a virtual environment, run `python app.py` instead. Then
open [http://127.0.0.1:8000](http://127.0.0.1:8000).

### 4. Classify a new complaint from the terminal

```powershell
.\.venv\Scripts\python.exe predict.py "I was charged twice for my subscription."
```

The command returns the predicted category, its confidence, and probabilities
for every category.

The NUT dashboard lets you paste a complaint, view a model-backed routing
prediction, inspect category probabilities, and review a short analysis history.
Keep the PowerShell window open while you use the dashboard; press `Ctrl+C` in
that window to stop it.

## Use your own dataset

Replace `data/complaints.csv` with your data, or use a separate CSV. The CSV
needs two columns:

| complaint | category |
| --- | --- |
| I was charged twice for my plan | Billing |
| The website will not let me sign in | Technical Support |

Then train with:

```powershell
.\.venv\Scripts\python.exe train.py --data path\to\your_dataset.csv --text-column complaint --label-column category
```

Change `complaint` and `category` in that command if your headers have other
names. Each category needs at least two labelled complaints; in practice, aim
for 50 or more representative examples per category for an initial model.

## Project structure

- `data/complaints.csv` - 180 fictional, balanced training examples.
- `data/DATASET_NOTES.md` - dataset origin and limitations.
- `train.py` - cleans data, trains the model, and saves evaluation results.
- `predict.py` - predicts a category for a new complaint.
- `app.py` - serves the local NUT web dashboard and prediction API.
- `templates/` and `static/` - dashboard interface files.
- `start_dashboard.bat` - starts the dashboard with a double-click.
- `requirements.txt` - confirms that no third-party packages are required.
- `PROJECT_SUMMARY.md` - presentation-ready explanation of the project.
- `GITHUB_UPLOAD.md` - steps for publishing this project to GitHub.

## Deploy on Render

This repository includes `render.yaml` for deployment on [Render](https://render.com).
When creating a new **Blueprint** from this GitHub repository, Render runs
`python train.py` during the build to create the model, then starts the dashboard
with `python app.py`.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/udaykumar8688/nut-complaint-intelligence)

## Important note

This project demonstrates the complete workflow but is not production ready.
Its accuracy must be evaluated again after training on real, correctly labelled
complaints. Any future production deployment must also include privacy controls
and human review for uncertain predictions.
