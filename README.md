# CIP: Data Collection, Integration and Preprocessing - SW03

Interactive SW03 course materials with Marimo notebooks.

**Table of Contents**
- [Overview](#overview)
- [Repository Layout](#repository-layout)
- [Run Matrix](#run-matrix)
- [Setup](#setup)
  - [Conda](#conda)
  - [Pip (venv)](#pip-venv)
- [Run Notebook Apps](#run-notebook-apps)
- [Run FastAPI Demo](#run-fastapi-demo)
- [Run Backend API + Streamlit App](#run-backend-api--streamlit-app)
- [Troubleshooting](#troubleshooting)

## Overview

- `lecture_sw03_content.py`: lecture notebook (storage, serialization, DuckDB, REST, Pydantic, FastAPI, etc.)
- `lecture_sw03_demo.py`: compact Marimo demo notebook
- `src/demo_api.py`: standalone FastAPI app used in the lecture API section
- `src/parquet_api.py`: Parquet-backed FastAPI service with read/create/update endpoints
- `streamlit_demo.py`: Streamlit frontend that queries the FastAPI service and renders charts

## Repository Layout

```text
.
├── lecture_sw03_content.py
├── lecture_sw03_demo.py
├── streamlit_demo.py
├── data/
│   └── sales_demo.parquet   # created automatically on first API start
├── src/
│   ├── __init__.py
│   ├── parquet_api.py
│   └── demo_api.py
├── env.yaml
├── requirements.txt
└── README.md
```

## Run Matrix

| Component | Purpose | Command |
| --- | --- | --- |
| `lecture_sw03_content.py` | Full lecture notebook in app mode | `marimo run lecture_sw03_content.py` |
| `lecture_sw03_content.py` | Full lecture notebook in editor mode | `marimo edit lecture_sw03_content.py` |
| `lecture_sw03_demo.py` | Demo notebook in app mode | `marimo run lecture_sw03_demo.py` |
| `lecture_sw03_demo.py` | Demo notebook in editor mode | `marimo edit lecture_sw03_demo.py` |
| `src/demo_api.py` | FastAPI backend for API chapter | `uvicorn src.demo_api:app --reload` |
| `src/parquet_api.py` | FastAPI backend with Parquet persistence | `uvicorn src.parquet_api:app --reload` |
| `streamlit_demo.py` | Streamlit frontend for 3-tier architecture demo | `streamlit run streamlit_demo.py` |

## Setup to Run the Code

### Conda

Use `env.yaml`:

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

### Pip (venv)

Use `requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Notebook Apps

Lecture notebook:

```bash
marimo edit lecture_sw03_content.py
marimo run lecture_sw03_content.py
```

Marimo demo notebook:

```bash
marimo edit lecture_sw03_demo.py
marimo run lecture_sw03_demo.py
```

## Run FastAPI Demo

From the project root:

```bash
uvicorn src.demo_api:app --reload
```

Then open:

- API docs: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Run Backend API + Streamlit App

Start the required backend API first, then run the Streamlit frontend.

1. Terminal 1: run the FastAPI backend:

```bash
uvicorn src.parquet_api:app --reload
```

2. Terminal 2: run the Streamlit app:

```bash
streamlit run streamlit_demo.py
```

3. Open the Streamlit URL shown in the terminal (typically `http://localhost:8501`) and use this API base URL in the sidebar:

```text
http://127.0.0.1:8000
```

This demonstrates a standard 3-tier architecture:
- Presentation tier: Streamlit (`streamlit_demo.py`)
- Service tier: FastAPI (`src/parquet_api.py`)
- Data tier: Parquet file (`data/sales_demo.parquet`)

## Troubleshooting

- `Error loading ASGI app`: run from project root and use `uvicorn src.demo_api:app --reload`.
- Missing package errors: confirm the active environment and reinstall with `pip install -r requirements.txt` (or recreate conda env).
- Marimo startup warnings: update marimo in your env and re-run.
- Streamlit cannot connect: confirm `uvicorn src.parquet_api:app --reload` is running and the Streamlit sidebar URL is `http://127.0.0.1:8000`.
- `Descriptors cannot be created directly`: rebuild env with `python=3.12` from `env.yaml`, or reinstall with `pip install -r requirements.txt`.
