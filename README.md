# CIP SW03: Data Collection, Integration and Preprocessing

Course materials for SW03 using:
- Marimo notebooks (`.py` files)
- FastAPI
- Parquet datasets

## Quick Start (pip)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Project

From the repository root, use separate terminals:

1. Lecture notebook

```bash
marimo run sw03_lecture_content.py
```

2. Exercises notebook

```bash
marimo edit sw03_lecture_exercises.py
```

3. Demo API

```bash
uvicorn sw03_demo_api:app --reload
```

4. Optional Streamlit dashboard

```bash
streamlit run sw03_demo_streamlit.py
```

Use API base URL `http://127.0.0.1:8000` in Streamlit.

## Useful URLs

- API docs: `http://127.0.0.1:8000/docs`
- API health: `http://127.0.0.1:8000/health`
- Marimo usually starts on: `http://127.0.0.1:2718` (or next free port)

## Conda (optional)

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

## Troubleshooting

- Missing package errors: reinstall with `pip install -r requirements.txt`
- API not reachable: start `uvicorn sw03_demo_api:app --reload`
- Marimo command not found: ensure the environment is activated
