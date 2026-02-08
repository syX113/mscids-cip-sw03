# mscids-cip-sw03

This repo includes a visually rich Marimo demo notebook showcasing reactive UI, layouts, media, and data exploration.

## Files

- `marimo_demo.py`: the demo notebook
- `env.yaml`: conda environment for running the demo
- `requirements.txt`: minimal pip requirements (marimo only)

## Setup (Conda)

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

Optional extras for charts and dataframe tooling:

```bash
conda install -c conda-forge pandas altair
```

## Setup (Pip)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional extras for charts and dataframe tooling:

```bash
pip install pandas altair
```

## Run

Interactive editor (recommended for the full notebook experience):

```bash
marimo edit marimo_demo.py
```

App mode:

```bash
marimo run marimo_demo.py
```

## Notes

- The media gallery embeds a sample video and a PDF from public URLs, so it needs internet access.
- If `pandas` or `altair` are missing, the notebook will show a friendly fallback message for those sections.
