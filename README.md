# mscids-cip-sw03

Interactive SW03 course materials with Marimo notebooks plus a FastAPI demo service.

<details>
<summary><strong>Table of Contents (click to expand)</strong></summary>

- [Overview](#overview)
- [Repository Layout](#repository-layout)
- [Run Matrix](#run-matrix)
- [Setup](#setup)
  - [Conda](#conda)
  - [Pip (venv)](#pip-venv)
- [Run Notebook Apps](#run-notebook-apps)
- [Run FastAPI Demo](#run-fastapi-demo)
- [Troubleshooting](#troubleshooting)

</details>

## Overview

This repo is designed for live teaching and hands-on demos:

- `lecture_sw03_content.py`: full lecture notebook (storage, serialization, DuckDB, REST, Pydantic, FastAPI, indexing, charts)
- `lecture_sw03_demo.py`: compact Marimo demo notebook
- `src/demo_api.py`: standalone FastAPI app used in the lecture API section

## Repository Layout

```text
.
├── lecture_sw03_content.py
├── lecture_sw03_demo.py
├── src/
│   ├── __init__.py
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

## Setup

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

Full lecture notebook:

```bash
marimo edit lecture_sw03_content.py
marimo run lecture_sw03_content.py
```

Compact demo notebook:

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

## Troubleshooting

- `Error loading ASGI app`: run from project root and use `uvicorn src.demo_api:app --reload`.
- Missing package errors: confirm the active environment and reinstall with `pip install -r requirements.txt` (or recreate conda env).
- Marimo startup warnings: update marimo in your env and re-run.
