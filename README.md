# 📘 Collection, Integration & Preprocessing - SW03

Course materials for SW03 with Marimo notebooks, a FastAPI demo, and an optional Streamlit demo.

---

## Quick Navigation

- [🧩 Project Components](#project-components)
- [⚙️ Pip Setup (Recommended)](#pip-setup-recommended)
- [🖥️ Run from Console](#run-from-console)
- [🌐 URLs](#urls)
- [🐍 Conda Alternative](#conda-alternative)
- [🛠️ Troubleshooting](#troubleshooting)

---

## Used Materials

| Material | File | Purpose |
| --- | --- | --- |
| 📓 Lecture Notebook | `sw03_lecture_content.py` | Main teaching notebook |
| 🧪 Exercises Notebook | `sw03_lecture_exercises.py` | Student exercises |
| ✅ Solutions Notebook | `sw03_lecture_exercises_solutions.py` | Reference solutions |
| 🚀 Demo API | `sw03_demo_api.py` | FastAPI service for API examples |
| 🎛️ Optional UI | `sw03_demo_streamlit.py` | Streamlit app using the API |

---

## Pip Setup (Recommended)

> [!IMPORTANT]
> Run all commands from the repository root folder: `mscids-cip-sw03`.

### 1. Check prerequisites

- 🐍 Python `3.12` recommended
- 📦 `pip`
- 💻 Terminal (bash/zsh on macOS/Linux, PowerShell on Windows)

```bash
python3 --version
pip3 --version
```

### 2. Create and activate virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Verify environment quickly

```bash
python -c "import marimo, pandas, duckdb, fastapi, pyarrow, PIL; print('Environment OK')"
```

---

## Run from Console

> [!TIP]
> Keep the virtual environment activated in each terminal session.

Use separate terminals so each service stays running.

| Terminal | What to run | Command |
| --- | --- | --- |
| Terminal 1 | 📓 Lecture notebook | `marimo run sw03_lecture_content.py` |
| Terminal 2 | 🧪 Exercises notebook | `marimo edit sw03_lecture_exercises.py` |
| Terminal 2 (optional) | ✅ Solutions notebook | `marimo edit sw03_lecture_exercises_solutions.py` |
| Terminal 3 | 🚀 FastAPI demo | `uvicorn sw03_demo_api:app --reload --host 127.0.0.1 --port 8000` |
| Terminal 4 (optional) | 🎛️ Streamlit demo | `streamlit run sw03_demo_streamlit.py` |

> [!IMPORTANT]
> On every API start, files in `data/` are reset from `data/seed/`.

If Streamlit needs the API, use `http://127.0.0.1:8000` as the base URL.

To stop a running process in a terminal: `Ctrl + C`.

---

## URLs

| Service | URL |
| --- | --- |
| 📚 API docs (Swagger) | `http://127.0.0.1:8000/docs` |
| ❤️ API health | `http://127.0.0.1:8000/health` |
| ⚡ Marimo | Printed in terminal, usually `http://127.0.0.1:2718` (or next free port) |
| 🎛️ Streamlit | Printed in terminal, usually `http://localhost:8501` |

---

## Conda Alternative

If you prefer Conda over pip:

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| 📦 `ModuleNotFoundError` | `python -m pip install -r requirements.txt` |
| ⚡ `marimo: command not found` | Activate the environment first: `source .venv/bin/activate` |
| 🌐 API not reachable | Start API again: `uvicorn sw03_demo_api:app --reload --host 127.0.0.1 --port 8000` |

> [!NOTE]
> If commands still fail, close the terminal, open a new one, re-activate `.venv`, and retry.
