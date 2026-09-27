# 📘 Collection, Integration & Preprocessing - SW03

Course materials for SW03: a Marimo lecture notebook, exercises, a FastAPI demo, and an optional Streamlit demo.

The lecture builds one data product in **three tiers**:

| Tier | What it does | Chapters | Files |
| --- | --- | --- | --- |
| 🗄️ Data | Where the bytes rest | 1-5 | `data/`, DuckDB and Parquet demos |
| ⚙️ Logic | Rules and the API | 6-8 | `sw03_demo_api.py` |
| 🖥️ Presentation | What people see | 9-10 | `sw03_demo_streamlit.py`, Marimo charts |

---

## Quick Navigation

- [🧩 Used Materials](#used-materials)
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
| 🔍 API self-check | `test_sw03_demo_api.py` | Confirms the API works after changes |

---

## Pip Setup (Recommended)

### 0. Get the repository

If you do not have the folder yet:

```bash
git clone https://github.com/syX113/mscids-cip-sw03.git
cd mscids-cip-sw03
```

> [!IMPORTANT]
> Run every command below from inside the `mscids-cip-sw03` folder.
> If a command fails with "file not found", you are probably in the wrong folder. Check with `pwd` (works in PowerShell too).

### 1. Check prerequisites

- 🐍 Python `3.14` (this is the version everything was tested on)
- 📦 `pip`
- 💻 A terminal: Terminal on macOS, any shell on Linux, **PowerShell** on Windows

macOS/Linux:

```bash
python3 --version
pip3 --version
```

Windows PowerShell:

```powershell
python --version
pip --version
```

> [!NOTE]
> On Windows the command is `python`, not `python3`. Every macOS/Linux command below that starts with `python3` becomes `python` on Windows.

### 2. Create and activate virtual environment

A virtual environment keeps this course's packages separate from everything else on your machine.

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

> [!TIP]
> If PowerShell refuses with "running scripts is disabled on this system", allow it for your user once:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Then run the activate command again.

You know it worked when your prompt starts with `(.venv)`.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` pins exact versions on purpose, so everyone in the class runs the same stack.

### 4. Verify the environment

```bash
python -c "import marimo, pandas, duckdb, fastapi, pyarrow, PIL, altair, streamlit, fastavro, numpy, pydantic, requests, uvicorn, httpx2; print('Environment OK')"
```

This checks **every** package the materials need. If it prints `Environment OK`, you are ready.

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
| Terminal 3 | 🚀 FastAPI demo | `uvicorn sw03_demo_api:app --host 127.0.0.1 --port 8000` |
| Terminal 4 (optional) | 🎛️ Streamlit demo | `streamlit run sw03_demo_streamlit.py` |

Chapters 6 and 8 of the lecture talk to the API, so start Terminal 3 before those chapters.
The Streamlit demo needs the API too; its default base URL is `http://127.0.0.1:8000`.

To stop a running process in a terminal: `Ctrl + C`.

> [!IMPORTANT]
> On every API start, the files in `data/` are reset from `data/seed/`. Anything you create through the
> API is deliberately temporary, so you can experiment without breaking the lecture.

> [!WARNING]
> With `--reload` the API restarts, and resets `data/`, whenever a `.py` file in this folder is saved.
> marimo autosaves the exercises notebook while you type, so leave `--reload` out during the lecture
> and add it only while you edit `sw03_demo_api.py` yourself.

### Benchmarks run only when you click

The benchmarks in the lecture notebook sit behind **Run** buttons: click a chapter's button to run
its experiment.

### Check the API still works

```bash
python test_sw03_demo_api.py
```

Prints one line per check and exits non-zero if anything is broken. Stop the API first: the check
resets `data/` and then edits the same files a running API reads. Starting the API again reseeds them.

---

## URLs

| Service | URL |
| --- | --- |
| 📚 API docs (Swagger) | `http://127.0.0.1:8000/docs` |
| 📖 API docs (ReDoc) | `http://127.0.0.1:8000/redoc` |
| ❤️ API health | `http://127.0.0.1:8000/health` |
| ⚡ Marimo | Printed in terminal, usually `http://127.0.0.1:2718` (or next free port) |
| 🎛️ Streamlit | Printed in terminal, usually `http://localhost:8501` |

The API supports all four REST verbs (`GET`, `POST`, `PUT`, `DELETE`) on regions, countries,
categories, products and sales. Try them from `/docs`.

---

## Conda Alternative

If you prefer Conda over pip:

```bash
conda env create -f env.yaml
conda activate mscids-cip-sw03
```

Conda provides the interpreter; the packages come from the same pinned `requirements.txt`, so both
routes give identical versions.

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| 📦 `ModuleNotFoundError` | Activate the environment, then `python -m pip install -r requirements.txt` |
| ⚡ `marimo: command not found` | Activate the environment first: `source .venv/bin/activate` (Windows: `.\.venv\Scripts\Activate.ps1`) |
| 🚫 PowerShell blocks `Activate.ps1` | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then activate again |
| 🌐 API not reachable | Start it again: `uvicorn sw03_demo_api:app --host 127.0.0.1 --port 8000` |
| 🔌 `Address already in use` / port taken | Something is still running on that port. Either press `Ctrl + C` in the old terminal, or pick another port: `--port 8001` for the API, `--server.port 8502` for Streamlit. If you change the API port, update the base URL in the notebook and the Streamlit sidebar. |
| 🔄 Your API changes are gone | Expected: the API reseeds `data/` from `data/seed/` on every start, and with `--reload` on every saved `.py` file. Start it without `--reload` to keep your changes while you work. |
| 📧 Streamlit stops at an `Email:` prompt | Press Enter to skip it; the app then starts. |
| 📁 Wrong folder | `ls` (works in PowerShell too) should show `sw03_lecture_content.py`. If not, `cd` into `mscids-cip-sw03`. |

> [!NOTE]
> If commands still fail, close the terminal, open a new one, re-activate the environment, and retry.
