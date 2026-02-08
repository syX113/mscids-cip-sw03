# mscids-cip-sw03

A course repo with two Marimo notebooks: a visual demo and a full lecture notebook on data storage, serialization, databases, and APIs.

## Table of Contents

1. Overview
2. Notebooks
3. Installation with Conda
4. Installation with Pip
5. Optional Extras
6. Run Notebooks

## Overview

This repository contains interactive Marimo notebooks for SW03. The lecture notebook is designed for live teaching with demos, controls, and discussion prompts.

## Notebooks

- `marimo_demo.py` — a compact UI/UX demo showing Marimo layouts, reactive elements, and charts.
- `lecture_sw03.py` — the main lecture notebook covering ACID, serialization, columnar storage, compression, DuckDB, REST, Pydantic, FastAPI, indexing, and charts.

## Installation with Conda

Uses `env.yaml`.

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

## Installation with Pip

Uses `requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Optional Extras

Some sections use optional packages. Install them if you want every demo to run.

```bash
pip install fastavro requests uvicorn dash flask
```

## Run Notebooks

Open in the Marimo editor (recommended for live teaching):

```bash
marimo edit lecture_sw03.py
```

Run in app mode:

```bash
marimo run lecture_sw03.py
```

Run the demo notebook:

```bash
marimo edit marimo_demo.py
```

```bash
marimo run marimo_demo.py
```
