# CIP SW03: Data Collection, Integration and Preprocessing

Interactive course materials for SW03 using Marimo notebooks, FastAPI, and Parquet datasets.

## Table of Contents
- [What is in this repo](#what-is-in-this-repo)
- [Prerequisites](#prerequisites)
- [Environment setup](#environment-setup)
- [Run the Marimo notebooks](#run-the-marimo-notebooks)
- [Start the Demo API](#start-the-demo-api)
- [Optional: Streamlit dashboard](#optional-streamlit-dashboard)
- [Troubleshooting](#troubleshooting)

## What is in this repo

```text
.
├── sw03_lecture_content.py      # main lecture notebook
├── sw03_lecture_exercises.py    # exercises notebook
├── sw03_demo_api.py             # FastAPI service backed by Parquet files
├── sw03_demo_streamlit.py       # frontend demo app
├── data/                        # parquet datasets
├── env.yaml                     # conda environment definition
├── requirements.txt             # pip dependencies
└── README.md
```

## Prerequisites

- Python 3.12 recommended
- `pip` available
- Optional: Conda (Miniconda/Anaconda)

## Environment setup

Choose one setup path.

### Option A: Conda (macOS + Windows)

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

If the environment already exists:

```bash
conda env update -f env.yaml --prune
conda activate mscids-cip-sw03
```

### Option B: pip + virtual environment

#### macOS (zsh/bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (cmd.exe)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the Marimo notebooks

Open two terminals (with the same activated environment):

1. **Content notebook in app mode**

```bash
marimo run sw03_lecture_content.py
```

2. **Exercises notebook in edit mode**

```bash
marimo edit sw03_lecture_exercises.py
```

Typical local URLs:
- App mode: `http://127.0.0.1:2718`
- Edit mode: `http://127.0.0.1:2719` (or next available port)

## Start the Demo API

From the repository root:

```bash
uvicorn sw03_demo_api:app --reload
```

Then open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

## Optional: Streamlit dashboard

If you want to run the frontend demo:

```bash
streamlit run sw03_demo_streamlit.py
```

In the sidebar, use API base URL:

```text
http://127.0.0.1:8000
```

## Troubleshooting

- `Error loading ASGI app`:
  - Run from repo root and use `uvicorn sw03_demo_api:app --reload`.
- `ModuleNotFoundError` or missing packages:
  - Confirm the active environment, then reinstall with `pip install -r requirements.txt`.
- Streamlit cannot connect to API:
  - Make sure `uvicorn sw03_demo_api:app --reload` is running and health endpoint returns `{"status":"ok"}`.
- Marimo command not found:
  - Reinstall dependencies in the active environment.
