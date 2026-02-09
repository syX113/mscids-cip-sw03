import marimo

__generated_with = "0.19.8"
app = marimo.App()


@app.cell
def _():
    import csv
    import gzip
    import io
    import json
    import math
    import os
    import pickle
    import random
    import sqlite3
    import statistics
    import tempfile
    import textwrap
    import threading
    import time
    import urllib.error as url_error
    import urllib.parse as url_parse
    import urllib.request as url_request
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Any, Dict, List, Tuple

    import importlib
    import marimo as mo

    return (
        Any,
        Dict,
        List,
        Path,
        Tuple,
        csv,
        dataclass,
        gzip,
        importlib,
        io,
        json,
        math,
        mo,
        os,
        pickle,
        random,
        sqlite3,
        statistics,
        tempfile,
        textwrap,
        threading,
        time,
        url_error,
        url_parse,
        url_request,
    )


@app.cell
def _(importlib):
    def optional_import(module_name):
        """Import a module if available; return None otherwise."""
        if importlib.util.find_spec(module_name) is None:
            return None
        return importlib.import_module(module_name)

    def format_bytes(num_bytes):
        """Human-friendly byte counts."""
        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(num_bytes)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{value:,.2f} {unit}"
            value /= 1024
        return f"{value:,.2f} TB"

    def format_ms(seconds):
        return f"{seconds * 1000:,.2f} ms"

    return format_bytes, format_ms, optional_import


@app.cell
def _(mo):
    css = mo.Html(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

          :root {
            --ink: #0b1220;
            --ink-2: #22304d;
            --muted: #52627a;
            --border: rgba(11, 18, 32, 0.14);
            --surface: rgba(255, 255, 255, 0.9);
            --surface-strong: rgba(255, 255, 255, 0.98);
            --accent: #2f6fed;
            --accent-2: #14b8a6;
            --accent-3: #f59e0b;
            --shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
          }

          body {
            background:
              radial-gradient(circle at 12% 6%, rgba(47, 111, 237, 0.12), transparent 45%),
              radial-gradient(circle at 90% 12%, rgba(20, 184, 166, 0.1), transparent 40%),
              linear-gradient(180deg, #f8fafc 0%, #eef2f7 55%, #f8fafc 100%);
            color: var(--ink);
            font-family: "Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif;
            background-attachment: fixed;
          }

          main, .marimo-main, .mo-main {
            max-width: 100% !important;
            width: min(100vw, 2400px) !important;
            margin: 0 auto !important;
            padding: 0 28px 80px;
            box-sizing: border-box;
          }

          h1, h2, h3 {
            color: var(--ink);
          }

          h2 {
            margin-top: 2.2rem;
            position: relative;
            padding-bottom: 0.3rem;
          }

          h2::after {
            content: "";
            position: absolute;
            left: 0;
            bottom: 0;
            width: 100%;
            height: 3px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(47, 111, 237, 0.7), rgba(20, 184, 166, 0.6));
            opacity: 0.6;
          }

          h1, .hero-title {
            font-family: "Fraunces", "Space Grotesk", serif;
            letter-spacing: 0.01em;
          }

          pre, code {
            background: rgba(47, 111, 237, 0.08);
            border: 1px solid rgba(47, 111, 237, 0.18);
            border-radius: 10px;
            font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
            color: var(--ink);
          }

          pre {
            padding: 12px 14px;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface-strong);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: var(--shadow);
          }

          th, td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(11, 18, 32, 0.08);
          }

          thead th {
            text-align: left;
            font-weight: 700;
            color: var(--ink);
            background: rgba(47, 111, 237, 0.12);
          }

          .section-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(8px);
          }

          .section-card h3 {
            margin-top: 0;
          }

          .hero {
            position: relative;
            border-radius: 22px;
            padding: 28px 28px 24px 28px;
            background: linear-gradient(120deg, rgba(47, 111, 237, 0.12), rgba(20, 184, 166, 0.1), rgba(245, 158, 11, 0.1));
            border: 1px solid rgba(47, 111, 237, 0.22);
            box-shadow: 0 26px 60px rgba(15, 23, 42, 0.14);
            overflow: hidden;
          }

          .hero::after {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 20% 20%, rgba(47, 111, 237, 0.28), transparent 45%);
            opacity: 0.8;
            pointer-events: none;
          }

          .hero-content {
            position: relative;
            z-index: 2;
          }

          .eyebrow {
            display: inline-flex;
            gap: 8px;
            align-items: center;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(47, 111, 237, 0.18);
            color: var(--accent);
            font-weight: 600;
            letter-spacing: 0.08em;
            font-size: 12px;
            text-transform: uppercase;
          }

          .hero-title {
            font-size: 2.6rem;
            margin: 14px 0 10px 0;
            line-height: 1.05;
          }

          .hero-subtitle {
            max-width: 860px;
            color: var(--muted);
            font-size: 1.05rem;
          }

          .hero-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
          }

          .pill {
            padding: 6px 12px;
            border-radius: 999px;
            border: 1px solid rgba(11, 18, 32, 0.12);
            background: rgba(255, 255, 255, 0.7);
            color: var(--ink-2);
            font-size: 12px;
          }

          .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
          }

          .stat {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(11, 18, 32, 0.12);
            border-radius: 16px;
            padding: 14px 16px;
          }

          .stat-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
          }

          .stat-value {
            font-size: 1.4rem;
            font-weight: 600;
            margin-top: 6px;
          }

          details {
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.82);
          }

          details + details {
            margin-top: 10px;
          }

          summary {
            cursor: pointer;
            font-weight: 600;
            color: var(--ink-2);
          }

          summary::-webkit-details-marker {
            display: none;
          }

          summary::before {
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            border-right: 2px solid var(--muted);
            border-bottom: 2px solid var(--muted);
            margin-right: 10px;
            transform: translateY(-1px) rotate(-45deg);
            transition: transform 0.15s ease;
          }

          details[open] summary::before {
            transform: translateY(0px) rotate(45deg);
          }

          .mo-callout {
            border-radius: 16px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
          }
        </style>
        """
    )
    css
    return (css,)


@app.cell
def _(mo):
    title = mo.md(
        """
<div class="hero">
  <div class="hero-content">
    <div class="eyebrow">CIP - SW03 Lecture Studio</div>
    <div class="hero-title">Storage, Serialization, APIs & Apps</div>
    <div class="hero-subtitle">
      A hands‑on notebook to demonstrate:
      race conditions, serialization trade‑offs, columnar analytics, API design, and
      rapid app prototyping.
    </div>
    <div class="hero-pills">
      <span class="pill">ACID & Concurrency</span>
      <span class="pill">Atomicity Transfers</span>
      <span class="pill">Serialization Benchmarks</span>
      <span class="pill">Columnar Analytics</span>
      <span class="pill">APIs & FastAPI</span>
      <span class="pill">Indexes & Plans</span>
      <span class="pill">Marimo Charts</span>
    </div>
  </div>
</div>
        """
    )
    title
    return (title,)


@app.cell
def _(mo):
    agenda = mo.md(
        """
<div class="section-card">
  <h2>Discussed Topics  </h2>
  <div class="grid-2">
    <div>
      <ul>
        <li>File locks and why databases matter (ACID vs. files)</li>
        <li>Atomicity demo: transfer + rollback</li>
        <li>Serialization & deserialization benchmarks (JSON, Pickle, Arrow, Avro)</li>
        <li>Column‑based vs row‑based storage</li>
        <li>Compression & encoding (Parquet, gzip, compression ratios)</li>
        <li>DuckDB for analytics on files + schema‑on‑read vs write</li>
      </ul>
    </div>
    <div>
      <ul>
        <li>REST APIs (GET, POST, PUT, DELETE)</li>
        <li>Pydantic models for validation</li>
        <li>FastAPI demo + automatic documentation</li>
        <li>Indexing demo (SQLite) + query plans</li>
        <li>Frontend framework comparison (Streamlit, Dash, Flask, React, Marimo)</li>
        <li>Marimo charts lab: scatter, line, box + statistics</li>
      </ul>
    </div>
  </div>
</div>
        """
    )
    agenda
    return (agenda,)


@app.cell
def _(mo):
    _section = mo.md("## 1. File Locks vs Databases (ACID)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Why Files Are Not ACID

Files are great for **simple storage**, but they do **not** provide ACID guarantees:

- **Atomicity**: file writes can be partial or interleaved.
- **Consistency**: no built‑in rules about valid states.
- **Isolation**: concurrent writers can overwrite each other.
- **Durability**: durability depends on flush/fsync timing.

**What to observe:** when multiple workers update a shared file, the *actual* value drops below the *expected* value because increments are lost.

In our experiment, the expected final counter is:

$$
E = W \\times I
$$

and the number of lost updates is:

$$
L = E - A
$$

Databases coordinate concurrency, ensure isolation, and provide crash recovery.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    strategies = mo.ui.multiselect(
        options=["no_lock", "thread_lock", "file_lock", "sqlite"],
        value=["no_lock", "file_lock", "sqlite"],
        label="Strategies to run",
    )
    workers = mo.ui.slider(2, 12, value=4, label="Concurrent workers")
    iterations = mo.ui.slider(50, 2000, step=50, value=300, label="Increments per worker")
    jitter = mo.ui.slider(0, 5, value=1, step=1, label="Artificial jitter (ms)")
    run_race = mo.ui.button(label="Re-run counter experiment", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.md("### Concurrency demo: file vs locks vs database"),
            mo.hstack([workers, iterations], widths="equal"),
            jitter,
            strategies,
            run_race,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return iterations, jitter, run_race, strategies, workers


@app.cell
def _(Path, iterations, jitter, mo, os, run_race, sqlite3, strategies, tempfile, threading, time, workers):
    def _run_file_counter(path, iterations, workers, lock_mode, jitter_s):
        """Increment a shared file counter with different locking strategies."""
        path.write_text("0")
        thread_lock = threading.Lock() if lock_mode == "thread_lock" else None
        file_lock_supported = False
        fcntl = None
        if lock_mode == "file_lock":
            try:
                import fcntl  # type: ignore

                file_lock_supported = True
            except Exception:
                file_lock_supported = False

        def update_once():
            with path.open("r+", encoding="utf-8") as f:
                if lock_mode == "file_lock" and file_lock_supported:
                    fcntl.flock(f, fcntl.LOCK_EX)
                value = f.read().strip()
                current = int(value) if value else 0
                if jitter_s:
                    time.sleep(jitter_s)
                f.seek(0)
                f.truncate()
                f.write(str(current + 1))
                f.flush()
                os.fsync(f.fileno())
                if lock_mode == "file_lock" and file_lock_supported:
                    fcntl.flock(f, fcntl.LOCK_UN)

        def worker():
            for _ in range(iterations):
                if thread_lock:
                    with thread_lock:
                        update_once()
                else:
                    update_once()

        threads = [threading.Thread(target=worker) for _ in range(workers)]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.perf_counter() - start
        final_value = int(path.read_text().strip() or "0")
        return final_value, duration, file_lock_supported

    def _run_sqlite_counter(db_path, iterations, workers):
        """Increment a counter inside SQLite with transactions."""
        con = sqlite3.connect(db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("CREATE TABLE counter (value INTEGER NOT NULL)")
        con.execute("INSERT INTO counter VALUES (0)")
        con.commit()
        con.close()

        def worker():
            conn = sqlite3.connect(db_path, timeout=5, isolation_level=None)
            for _ in range(iterations):
                for _attempt in range(8):
                    try:
                        conn.execute("BEGIN IMMEDIATE")
                        conn.execute("UPDATE counter SET value = value + 1")
                        conn.execute("COMMIT")
                        break
                    except sqlite3.OperationalError as exc:
                        if "locked" in str(exc).lower():
                            time.sleep(0.002)
                            continue
                        raise
            conn.close()

        threads = [threading.Thread(target=worker) for _ in range(workers)]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.perf_counter() - start
        conn = sqlite3.connect(db_path)
        final_value = conn.execute("SELECT value FROM counter").fetchone()[0]
        conn.close()
        return final_value, duration

    if run_race.value == 0:
        _output = mo.md(
            "Click **Run counter experiment** to simulate concurrent writes."
        ).callout(kind="neutral")
    else:
        expected = workers.value * iterations.value
        jitter_s = jitter.value / 1000

        race_rows = []
        with tempfile.TemporaryDirectory() as _tmpdir:
            _tmp_path = Path(_tmpdir)
            if "no_lock" in strategies.value:
                value, _duration, _ = _run_file_counter(
                    _tmp_path / "counter.txt",
                    iterations.value,
                    workers.value,
                    "no_lock",
                    jitter_s,
                )
                race_rows.append(
                    {
                        "strategy": "file (no lock)",
                        "expected": expected,
                        "actual": value,
                        "lost updates": expected - value,
                        "duration": f"{_duration:.3f}s",
                    }
                )

            if "thread_lock" in strategies.value:
                value, _duration, _ = _run_file_counter(
                    _tmp_path / "counter_locked.txt",
                    iterations.value,
                    workers.value,
                    "thread_lock",
                    jitter_s,
                )
                race_rows.append(
                    {
                        "strategy": "file (thread lock)",
                        "expected": expected,
                        "actual": value,
                        "lost updates": expected - value,
                        "duration": f"{_duration:.3f}s",
                    }
                )

            if "file_lock" in strategies.value:
                value, _duration, supported = _run_file_counter(
                    _tmp_path / "counter_flock.txt",
                    iterations.value,
                    workers.value,
                    "file_lock",
                    jitter_s,
                )
                race_rows.append(
                    {
                        "strategy": "file (fcntl lock)"
                        if supported
                        else "file (lock unsupported)",
                        "expected": expected,
                        "actual": value,
                        "lost updates": expected - value,
                        "duration": f"{_duration:.3f}s",
                    }
                )

            if "sqlite" in strategies.value:
                value, _duration = _run_sqlite_counter(
                    str(_tmp_path / "counter.db"),
                    iterations.value,
                    workers.value,
                )
                race_rows.append(
                    {
                        "strategy": "sqlite transaction",
                        "expected": expected,
                        "actual": value,
                        "lost updates": expected - value,
                        "duration": f"{_duration:.3f}s",
                    }
                )

        _table = mo.ui.table(race_rows, label="Concurrency results")
        _summary = mo.md(
            """
**How to read the table**

- **No lock**: fastest but incorrect (lost updates).
- **File lock**: correct but slower (serializes access).
- **SQLite**: correct *and* often fast because the database manages concurrency.
            """
        ).callout(kind="info")

        _output = mo.vstack([_table, _summary], gap=0.6)

    _output
    return (_output,)


@app.cell
def _(mo):
    _interleave_intro = mo.md(
        """
### Interleaving Simulator: Why Lost Updates Happen

The file counter uses a **read → modify → write** sequence. Without a lock, two workers can interleave:

1. Worker A reads 0  
2. Worker B reads 0  
3. Worker A writes 1  
4. Worker B writes 1  ← lost update (A’s increment disappears)

The simulator below shuffles these steps to make the race condition visible.
        """
    ).callout(kind="neutral")
    _interleave_intro
    return (_interleave_intro,)


@app.cell
def _(mo):
    interleave_steps = mo.ui.slider(
        1, 6, value=2, label="Increments per worker (simulated)"
    )
    interleave_seed = mo.ui.slider(1, 999, value=13, label="Interleaving seed")
    show_trace = mo.ui.switch(value=True, label="Show step-by-step trace")

    _controls = mo.vstack(
        [
            mo.hstack([interleave_steps, interleave_seed], widths="equal"),
            show_trace,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return interleave_seed, interleave_steps, show_trace


@app.cell
def _(interleave_seed, interleave_steps, mo, random, show_trace):
    _rng = random.Random(interleave_seed.value)
    def _build_ops():
        ops = []
        for idx in range(interleave_steps.value):
            ops.append(("read", idx))
            ops.append(("write", idx))
        return ops

    _ops = {"A": _build_ops(), "B": _build_ops()}

    _local = {"A": None, "B": None}
    _shared = 0
    _log = []
    _step = 0

    while _ops["A"] or _ops["B"]:
        _available = [w for w in ("A", "B") if _ops[w]]
        _worker = _rng.choice(_available)
        _op = _ops[_worker].pop(0)
        _action, _idx = _op
        _before = _shared
        if _action == "read":
            _local[_worker] = _shared
            _after = _shared
            _note = "read shared"
        else:
            _shared = (_local[_worker] or 0) + 1
            _after = _shared
            _note = "write local+1"

        _log.append(
            {
                "step": _step,
                "worker": _worker,
                "action": _action,
                "shared_before": _before,
                "local_value": _local[_worker],
                "shared_after": _after,
                "note": _note,
            }
        )
        _step += 1

    _expected = interleave_steps.value * 2
    _lost = _expected - _shared
    _summary = mo.md(
        f"Expected **{_expected}**, actual **{_shared}**, lost updates **{_lost}**."
    ).callout(kind="info")

    _panel_items = [_summary]
    if show_trace.value:
        _panel_items.append(mo.ui.table(_log, label="Interleaving trace"))

    _panel = mo.vstack(_panel_items, gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    _atomic_intro = mo.md(
        """
### Atomicity Demo: Transfer With Failure

A transfer should preserve the total balance:

$$
B_{total} = B_{Alice} + B_{Bob}
$$

Without transactions, a crash between **debit** and **credit** can violate this invariant.
Databases roll back the partial work, so the total remains consistent.

**Try this:** run once with failure **on** (see the file total break),
then run with failure **off** (both systems remain consistent).
        """
    ).callout(kind="neutral")
    _atomic_intro
    return (_atomic_intro,)


@app.cell
def _(mo):
    atomic_amount = mo.ui.slider(10, 500, step=10, value=150, label="Transfer amount")
    atomic_fail = mo.ui.switch(value=True, label="Inject failure after debit")
    run_atomic = mo.ui.button(label="Run atomicity demo", value=1, kind="success")

    _controls = mo.vstack(
        [mo.hstack([atomic_amount, atomic_fail], widths="equal"), run_atomic],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return atomic_amount, atomic_fail, run_atomic


@app.cell
def _(Path, atomic_amount, atomic_fail, json, mo, run_atomic, sqlite3, tempfile):
    if run_atomic.value == 0:
        _output = mo.md(
            "Click **Run atomicity demo** to simulate the transfer step-by-step."
        ).callout(kind="neutral")
    else:
        _initial = {"Alice": 1000, "Bob": 500}
        _expected_total = sum(_initial.values())
        _timeline = []

        def _normalize_state(state):
            if isinstance(state, dict):
                _state = dict(state)
            else:
                try:
                    _state = dict(state)
                except Exception:
                    _state = {}
            return {
                "Alice": _state.get("Alice", 0),
                "Bob": _state.get("Bob", 0),
            }

        def _add_timeline(system, step, state, note):
            _state = _normalize_state(state)
            _timeline.append(
                {
                    "system": system,
                    "step": step,
                    "Alice": _state["Alice"],
                    "Bob": _state["Bob"],
                    "total": sum(_state.values()),
                    "note": note,
                }
            )

        with tempfile.TemporaryDirectory() as _tmpdir:
            _tmpdir = Path(_tmpdir)
            _file_path = _tmpdir / "ledger.json"
            _file_path.write_text(json.dumps(_initial), encoding="utf-8")

            _add_timeline("file (JSON)", "start", dict(_initial), "initial balances")
            _file_balances = dict(_initial)
            _file_balances["Alice"] -= atomic_amount.value
            _file_path.write_text(json.dumps(_file_balances), encoding="utf-8")
            _add_timeline(
                "file (JSON)", "debit", dict(_file_balances), "Alice debited"
            )
            if not atomic_fail.value:
                _file_balances["Bob"] += atomic_amount.value
                _file_path.write_text(json.dumps(_file_balances), encoding="utf-8")
                _add_timeline(
                    "file (JSON)", "credit", dict(_file_balances), "Bob credited"
                )
            else:
                _add_timeline(
                    "file (JSON)", "crash", dict(_file_balances), "crash before credit"
                )

            _file_final = json.loads(_file_path.read_text(encoding="utf-8"))

            _db_path = _tmpdir / "ledger.db"
            _con = sqlite3.connect(str(_db_path), isolation_level=None)
            _con.execute(
                "CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER)"
            )
            _con.executemany("INSERT INTO accounts VALUES (?, ?)", list(_initial.items()))

            try:
                _con.execute("BEGIN")
                _add_timeline(
                    "sqlite", "start", dict(_initial), "initial balances"
                )
                _con.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE name = 'Alice'",
                    (atomic_amount.value,),
                )
                _db_after_debit = dict(
                    _con.execute(
                        "SELECT name, balance FROM accounts ORDER BY name"
                    ).fetchall()
                )
                _add_timeline(
                    "sqlite",
                    "debit (txn)",
                    _db_after_debit,
                    "uncommitted debit",
                )
                if atomic_fail.value:
                    raise RuntimeError("Simulated crash after debit")
                _con.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE name = 'Bob'",
                    (atomic_amount.value,),
                )
                _con.execute("COMMIT")
                _db_final = dict(
                    _con.execute(
                        "SELECT name, balance FROM accounts ORDER BY name"
                    ).fetchall()
                )
                _add_timeline(
                    "sqlite", "commit", _db_final, "transaction committed"
                )
            except Exception:
                try:
                    _con.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                _db_final = dict(
                    _con.execute(
                        "SELECT name, balance FROM accounts ORDER BY name"
                    ).fetchall()
                )
                _add_timeline(
                    "sqlite", "rollback", _db_final, "transaction rolled back"
                )

            _db_rows = _con.execute(
                "SELECT name, balance FROM accounts ORDER BY name"
            ).fetchall()
            _con.close()

        if not _db_rows:
            _db_rows = list(_initial.items())

        _initial_table = mo.ui.table(
            [{"account": k, "balance": v} for k, v in _initial.items()],
            label="Initial balances",
        )
        _file_table = mo.ui.table(
            [{"account": k, "balance": v} for k, v in _file_final.items()],
            label="File ledger (JSON)",
        )
        _db_table = mo.ui.table(
            [{"account": name, "balance": bal} for name, bal in _db_rows],
            label="SQLite ledger (transaction)",
        )
        _timeline_table = mo.ui.table(_timeline, label="Step-by-step timeline")

        _file_total = sum(_file_final.values())
        _db_total = sum(row[1] for row in _db_rows)
        _status = "Failure injected" if atomic_fail.value else "No failure"
        _file_ok = _file_total == _expected_total
        _db_ok = _db_total == _expected_total

        _file_status = "consistent" if _file_ok else "BROKEN"
        _db_status = "consistent" if _db_ok else "BROKEN"
        _file_kind = "success" if _file_ok else "danger"
        _db_kind = "success" if _db_ok else "danger"

        _summary = mo.md(
            f"""
**Scenario:** {_status}  
**Expected total:** `{_expected_total}`  
**File total:** `{_file_total}` → **{_file_status}**  
**SQLite total:** `{_db_total}` → **{_db_status}**

When failure is injected, the file-based ledger can end in a **partial state**,
while the database rolls back to the consistent total.
            """
        ).callout(kind="info")

        _file_callout = mo.md(
            "File writes are **not atomic**: debit and credit can be split by a crash."
        ).callout(kind=_file_kind)
        _db_callout = mo.md(
            "SQLite uses **transactions**: either both updates happen or none."
        ).callout(kind=_db_kind)

        _output = mo.vstack(
            [
                _initial_table,
                _timeline_table,
                _file_callout,
                _file_table,
                _db_callout,
                _db_table,
                _summary,
            ],
            gap=0.6,
        )

    _output
    return (_output,)


@app.cell
def _(mo):
    _qa_block_concurrency = mo.md(
        """
<div class="section-card">
  <h3>Discussion — Atomicity & Concurrency</h3>
  <details>
    <summary><strong>Q1:</strong> If you were forced to use files, how would you implement an atomic transfer?</summary>
    <p><strong>Answer:</strong> Consider a write‑ahead log, append‑only records, or a temp file + atomic rename.
    Each approach trades simplicity for durability and complexity.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> What invariants must always hold in your system?</summary>
    <p><strong>Answer:</strong> Identify quantities that must never change (e.g., total balance), and design
    tests that verify them under failures and retries.</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> Would you prefer to fail fast or accept temporary inconsistency?</summary>
    <p><strong>Answer:</strong> Depends on risk: finance typically fails fast; analytics can tolerate eventual repair.
    The right choice follows the cost of bad data vs. downtime.</p>
  </details>
</div>
        """
    )
    _qa_block_concurrency
    return (_qa_block_concurrency,)


@app.cell
def _(mo):
    _section = mo.md("## 2. Serialization & Deserialization Benchmarks")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Serialization = Bytes on Disk

Serialization transforms Python objects into bytes. Deserialization rebuilds objects from bytes.
The format choice affects speed, file size, interoperability, and safety.

- **Speed**: write + read throughput  
- **Size**: how many bytes hit disk  
- **Interop**: language/tool compatibility  
- **Safety**: Pickle can execute arbitrary code

A simple performance lens:

$$
\\text{Throughput} = \\frac{\\text{bytes written}}{\\text{write time}}
\\qquad
\\text{Latency} = \\text{write time} + \\text{read time}
$$

In practice, JSON is human‑readable, Pickle is Python‑specific, Arrow/Feather is columnar, and Avro is schema‑driven.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    serial_rows = mo.ui.slider(200, 5000, step=200, value=1000, label="Rows")
    serial_cols = mo.ui.slider(2, 10, value=6, label="Numeric columns")
    serial_seed = mo.ui.slider(1, 999, value=42, label="Seed")
    include_optional = mo.ui.checkbox(value=True, label="Include optional formats")
    run_serial = mo.ui.button(label="Re-run serialization benchmark", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([serial_rows, serial_cols], widths="equal"),
            serial_seed,
            include_optional,
            run_serial,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return include_optional, run_serial, serial_cols, serial_rows, serial_seed


@app.cell
def _(
    csv,
    format_bytes,
    format_ms,
    include_optional,
    json,
    mo,
    optional_import,
    pickle,
    random,
    run_serial,
    serial_cols,
    serial_rows,
    serial_seed,
    tempfile,
    time,
):
    def _make_records(count, num_cols, seed_value):
        rng = random.Random(seed_value)
        cities = ["Zurich", "Basel", "Geneva", "Bern", "Lugano"]
        records = []
        for idx in range(count):
            row = {
                "id": idx,
                "city": rng.choice(cities),
                "score": round(rng.random() * 100, 3),
            }
            for c in range(num_cols):
                row[f"metric_{c}"] = round(rng.random() * 1000, 5)
            records.append(row)
        return records

    def bench(label, write_fn, read_fn, path):
        start = time.perf_counter()
        write_fn(path)
        write_time = time.perf_counter() - start
        size = path.stat().st_size
        start = time.perf_counter()
        read_fn(path)
        read_time = time.perf_counter() - start
        return {
            "format": label,
            "write": format_ms(write_time),
            "read": format_ms(read_time),
            "size": format_bytes(size),
        }

    if run_serial.value == 0:
        _output = mo.md("Click **Run serialization benchmark** to execute.").callout(
            kind="neutral"
        )
    else:
        _records = _make_records(
            serial_rows.value, serial_cols.value, serial_seed.value + run_serial.value
        )
        sample = mo.ui.table(_records[:5], label="Sample records")

        _results = []
        with tempfile.TemporaryDirectory() as _tmpdir:
            _tmpdir = Path(_tmpdir)

            def json_write(path):
                with path.open("w", encoding="utf-8") as f:
                    json.dump(_records, f)

            def json_read(path):
                with path.open("r", encoding="utf-8") as f:
                    json.load(f)

            _results.append(bench("JSON", json_write, json_read, _tmpdir / "data.json"))

            def pickle_write(path):
                with path.open("wb") as f:
                    pickle.dump(_records, f, protocol=pickle.HIGHEST_PROTOCOL)

            def pickle_read(path):
                with path.open("rb") as f:
                    pickle.load(f)

            _results.append(
                bench("Pickle (unsafe)", pickle_write, pickle_read, _tmpdir / "data.pkl")
            )

            def csv_write(path):
                with path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=_records[0].keys())
                    writer.writeheader()
                    writer.writerows(_records)

            def csv_read(path):
                with path.open("r", newline="", encoding="utf-8") as f:
                    list(csv.DictReader(f))

            _results.append(bench("CSV", csv_write, csv_read, _tmpdir / "data.csv"))

            if include_optional.value:
                _pyarrow = optional_import("pyarrow")
                _feather = optional_import("pyarrow.feather")
                if _pyarrow and _feather:

                    def arrow_write(path):
                        table = _pyarrow.Table.from_pylist(_records)
                        _feather.write_feather(table, path)

                    def arrow_read(path):
                        _feather.read_table(path)

                    _results.append(
                        bench(
                            "Arrow/Feather",
                            arrow_write,
                            arrow_read,
                            _tmpdir / "data.feather",
                        )
                    )

                fastavro = optional_import("fastavro")
                if fastavro:
                    schema = {
                        "type": "record",
                        "name": "Record",
                        "fields": [
                            {"name": "id", "type": "int"},
                            {"name": "city", "type": "string"},
                            {"name": "score", "type": "float"},
                        ]
                        + [
                            {"name": f"metric_{c}", "type": "float"}
                            for c in range(serial_cols.value)
                        ],
                    }

                    def avro_write(path):
                        with path.open("wb") as f:
                            fastavro.writer(f, schema, _records)

                    def avro_read(path):
                        with path.open("rb") as f:
                            list(fastavro.reader(f))

                    _results.append(
                        bench("Avro", avro_write, avro_read, _tmpdir / "data.avro")
                    )

        results_table = mo.ui.table(_results, label="Serialization benchmark")
        warning = mo.md(
            """
**Security note:** Pickle is not safe for untrusted data. Only load Pickle files you control.
            """
        ).callout(kind="warn")

        _output = mo.vstack([sample, results_table, warning], gap=0.6)

    _output
    return (_output,)


@app.cell
def _(json, mo, pickle):
    _safe_obj = {"coords": (3, 4), "active": True, "count": 7}
    _unsafe_obj = {"tags": {"blue", "green"}}

    _json_roundtrip = json.loads(json.dumps(_safe_obj))
    _pickle_roundtrip = pickle.loads(pickle.dumps(_safe_obj))

    _rows = [
        {
            "case": "Tuple in JSON",
            "original_type": type(_safe_obj["coords"]).__name__,
            "after_roundtrip": type(_json_roundtrip["coords"]).__name__,
            "note": "tuple becomes list (type loss)",
        },
        {
            "case": "Tuple in Pickle",
            "original_type": type(_safe_obj["coords"]).__name__,
            "after_roundtrip": type(_pickle_roundtrip["coords"]).__name__,
            "note": "tuple preserved",
        },
    ]

    try:
        json.dumps(_unsafe_obj)
        _error_note = "no error"
    except TypeError as exc:
        _error_note = f"TypeError: {exc}"

    _rows.append(
        {
            "case": "Set in JSON",
            "original_type": type(_unsafe_obj["tags"]).__name__,
            "after_roundtrip": "n/a",
            "note": _error_note,
        }
    )

    _table = mo.ui.table(_rows, label="Type fidelity: JSON vs Pickle")
    _note = mo.md(
        "JSON is interoperable but can lose types; Pickle preserves Python types but is unsafe for untrusted data."
    ).callout(kind="info")

    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    _qa_block_serialization = mo.md(
        """
<div class="section-card">
  <h3>Discussion — Serialization Choices</h3>
  <details>
    <summary><strong>Q1:</strong> How do you choose between JSON, Avro, and Parquet for a new system?</summary>
    <p><strong>Answer:</strong> Start with the workload. JSON for interoperability, Avro for schema‑evolving events,
    Parquet for analytics and columnar scans.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> What is your threat model for serialized data?</summary>
    <p><strong>Answer:</strong> If data crosses trust boundaries, avoid unsafe formats like Pickle and validate strictly.</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> Where would you measure size vs. speed trade‑offs in production?</summary>
    <p><strong>Answer:</strong> Instrument write/read latency and storage costs; compare before/after in a canary pipeline.</p>
  </details>
</div>
        """
    )
    _qa_block_serialization
    return (_qa_block_serialization,)


@app.cell
def _(mo):
    _section = mo.md("## 3. Column-Based vs Row-Based Storage")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Row Store vs Column Store

**Row stores** keep full records together. Great for OLTP and point lookups.  
**Column stores** group values by column. Great for scans, aggregates, and compression.

If you scan only *k* columns out of *C*, the I/O pattern changes:

$$
IO_{row} \\approx N \\times C
\\qquad
IO_{col} \\approx N \\times k
$$

Below we simulate column selection and filtering to reveal the shape of the speed gap.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    n_rows = mo.ui.slider(5_000, 50_000, step=5_000, value=15_000, label="Rows")
    n_cols = mo.ui.slider(3, 12, value=6, label="Columns")
    storage_seed = mo.ui.slider(1, 999, value=7, label="Seed")
    run_storage = mo.ui.button(label="Re-run storage benchmark", value=1, kind="success")

    _controls = mo.vstack(
        [mo.hstack([n_rows, n_cols], widths="equal"), storage_seed, run_storage], gap=0.6
    ).callout(kind="neutral")
    _controls
    return n_cols, n_rows, run_storage, storage_seed


@app.cell
def _(format_ms, mo, n_cols, n_rows, random, run_storage, storage_seed, time):
    def build_data(rows, cols, seed_value):
        rng = random.Random(seed_value)
        rows_list = [tuple(rng.random() for _ in range(cols)) for _ in range(rows)]
        col_names = [f"c{idx}" for idx in range(cols)]
        columns = {name: [row[i] for row in rows_list] for i, name in enumerate(col_names)}
        return rows_list, columns, col_names

    if run_storage.value == 0:
        _output = mo.md("Click **Run storage benchmark** to execute.").callout(
            kind="neutral"
        )
    else:
        rows_list, columns, col_names = build_data(
            n_rows.value, n_cols.value, storage_seed.value + run_storage.value
        )
        target_col = col_names[0]
        threshold = 0.75

        def time_it(fn):
            start = time.perf_counter()
            result = fn()
            return time.perf_counter() - start, result

        row_select_time, row_select = time_it(lambda: [row[0] for row in rows_list])
        col_select_time, col_select = time_it(lambda: columns[target_col])

        row_filter_time, row_filter = time_it(
            lambda: [row for row in rows_list if row[0] > threshold]
        )
        col_filter_time, col_filter = time_it(
            lambda: [val for val in columns[target_col] if val > threshold]
        )

        row_sum_time, row_sum = time_it(lambda: sum(row[0] for row in rows_list))
        col_sum_time, col_sum = time_it(lambda: sum(columns[target_col]))

        _results = [
            {
                "operation": "Select column",
                "row_store": format_ms(row_select_time),
                "column_store": format_ms(col_select_time),
            },
            {
                "operation": "Filter column > 0.75",
                "row_store": format_ms(row_filter_time),
                "column_store": format_ms(col_filter_time),
            },
            {
                "operation": "Sum column",
                "row_store": format_ms(row_sum_time),
                "column_store": format_ms(col_sum_time),
            },
        ]

        _table = mo.ui.table(_results, label="Row vs Column timing (Python simulation)")
        _note = mo.md(
            """
**Discussion:** Real column stores show bigger wins because they avoid reading unused columns from disk.
            """
        ).callout(kind="info")

        _output = mo.vstack([_table, _note], gap=0.6)

    _output
    return (_output,)


@app.cell
def _(mo):
    _qa_block_storage = mo.md(
        """
<div class="section-card">
  <h3>Discussion — Row vs Column Storage</h3>
  <details>
    <summary><strong>Q1:</strong> Which workload patterns make a row store the better choice?</summary>
    <p><strong>Answer:</strong> Point lookups, frequent updates, and transactions with full‑row access.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> How does projection pushdown change query cost?</summary>
    <p><strong>Answer:</strong> Reading only required columns reduces I/O, especially when each column compresses well.</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> When can compression hurt performance?</summary>
    <p><strong>Answer:</strong> For small datasets or CPU‑bound workloads, decompression overhead can dominate.</p>
  </details>
</div>
        """
    )
    _qa_block_storage
    return (_qa_block_storage,)


@app.cell
def _(mo):
    _section = mo.md("## 4. Compression & Encoding (Parquet, Gzip)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Compression & Encoding

Compression reduces storage and I/O. Columnar formats (like Parquet) compress well because
similar values are adjacent.

Compression ratio (lower is better):

$$
r = \\frac{\\text{compressed size}}{\\text{original size}}
\\qquad
\\text{Savings} = 1 - r
$$

We compare JSON/CSV to gzip and Parquet with different codecs.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    compress_rows = mo.ui.slider(500, 10_000, step=500, value=2_000, label="Rows")
    compress_cols = mo.ui.slider(3, 10, value=6, label="Numeric columns")
    compress_seed = mo.ui.slider(1, 999, value=11, label="Seed")
    run_compress = mo.ui.button(label="Re-run compression benchmark", value=1, kind="success")

    _controls = mo.vstack(
        [mo.hstack([compress_rows, compress_cols], widths="equal"), compress_seed, run_compress],
        gap=0.6,
    ).callout(kind="neutral")
    _controls
    return compress_cols, compress_rows, compress_seed, run_compress


@app.cell
def _(
    compress_cols,
    compress_rows,
    compress_seed,
    csv,
    format_bytes,
    json,
    mo,
    optional_import,
    random,
    run_compress,
    tempfile,
):
    def _make_records(count, num_cols, seed_value):
        rng = random.Random(seed_value)
        records = []
        for idx in range(count):
            row = {"id": idx, "category": rng.choice(["A", "B", "C", "D"])}
            for c in range(num_cols):
                row[f"metric_{c}"] = round(rng.random() * 1000, 5)
            records.append(row)
        return records

    if run_compress.value == 0:
        _output = mo.md("Click **Run compression benchmark** to execute.").callout(
            kind="neutral"
        )
    else:
        _records = _make_records(
            compress_rows.value,
            compress_cols.value,
            compress_seed.value + run_compress.value,
        )

        _results = []
        with tempfile.TemporaryDirectory() as _tmpdir:
            _tmpdir = Path(_tmpdir)

            json_path = _tmpdir / "data.json"
            with json_path.open("w", encoding="utf-8") as _f:
                json.dump(_records, _f)
            json_size = json_path.stat().st_size

            _csv_path = _tmpdir / "data.csv"
            with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                _writer = csv.DictWriter(_f, fieldnames=_records[0].keys())
                _writer.writeheader()
                _writer.writerows(_records)
            csv_size = _csv_path.stat().st_size

            baseline = json_size
            for label, _source_path, size in [
                ("JSON", json_path, json_size),
                ("CSV", _csv_path, csv_size),
            ]:
                _results.append(
                    {
                        "format": label,
                        "size": format_bytes(size),
                        "ratio_vs_json": f"{size / baseline:.2f}x",
                    }
                )

            # Gzip compression
            for label, _source_path in [("JSON+gzip", json_path), ("CSV+gzip", _csv_path)]:
                gz_path = _source_path.with_suffix(_source_path.suffix + ".gz")
                with _source_path.open("rb") as src, gzip.open(gz_path, "wb") as dst:
                    dst.write(src.read())
                _results.append(
                    {
                        "format": label,
                        "size": format_bytes(gz_path.stat().st_size),
                        "ratio_vs_json": f"{gz_path.stat().st_size / baseline:.2f}x",
                    }
                )

            _pyarrow = optional_import("pyarrow")
            _parquet = optional_import("pyarrow.parquet")
            if _pyarrow and _parquet:
                table = _pyarrow.Table.from_pylist(_records)
                for codec in ["snappy", "gzip", "zstd", "brotli"]:
                    parquet_path = _tmpdir / f"data_{codec}.parquet"
                    try:
                        _parquet.write_table(table, parquet_path, compression=codec)
                    except Exception:
                        continue
                    _results.append(
                        {
                            "format": f"Parquet ({codec})",
                            "size": format_bytes(parquet_path.stat().st_size),
                            "ratio_vs_json": f"{parquet_path.stat().st_size / baseline:.2f}x",
                        }
                    )

        _table = mo.ui.table(_results, label="Compression ratios (baseline: JSON size)")
        _note = mo.md(
            """
**Discussion:** Columnar + compression reduces IO, especially for analytics workloads.
            """
        ).callout(kind="info")

        _output = mo.vstack([_table, _note], gap=0.6)

    _output
    return (_output,)


@app.cell
def _(math, mo, random):
    _rng = random.Random(7)
    _categories = ["A", "B", "C", "D", "E"]
    _samples = [_rng.choice(_categories) for _ in range(2000)]
    _unique = len(set(_samples))
    _code_bits = max(1, math.ceil(math.log2(_unique)))
    _avg_len = 1
    _original_bytes = len(_samples) * _avg_len
    _dictionary_bytes = _unique * _avg_len
    _encoded_bytes = len(_samples) * (_code_bits / 8)
    _estimated_ratio = (_dictionary_bytes + _encoded_bytes) / _original_bytes

    _rows = [
        {
            "metric": "rows",
            "value": len(_samples),
        },
        {
            "metric": "unique values",
            "value": _unique,
        },
        {
            "metric": "code bits",
            "value": _code_bits,
        },
        {
            "metric": "estimated ratio",
            "value": f"{_estimated_ratio:.2f}x",
        },
    ]

    _table = mo.ui.table(_rows, label="Dictionary encoding intuition")
    _note = mo.md(
        "Fewer unique values → fewer bits per row → better compression (especially in columnar formats)."
    ).callout(kind="info")

    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    _section = mo.md("## 5. DuckDB Example (SQL on Files)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### DuckDB: SQL on Files, Zero Server

DuckDB is an **embedded analytical database**. It can scan CSV/Parquet files with SQL,
perform vectorized execution, and apply *predicate + projection pushdown*.

Why it often beats “pure files” for analytics:

- Query optimizer + execution engine  
- Columnar reads and filter pushdown  
- Fast joins and aggregations without a server

The demo below runs a GROUP BY directly on a CSV file to show the experience.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    duck_rows = mo.ui.slider(2_000, 50_000, step=2_000, value=12_000, label="Rows")
    duck_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Amount threshold")
    duck_storage = mo.ui.dropdown(
        options=["CSV scan", "CSV + DuckDB table", "Parquet + DuckDB table"],
        value="CSV + DuckDB table",
        label="Storage path",
    )
    run_duck = mo.ui.button(label="Re-run DuckDB demo", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([duck_rows, duck_threshold], widths="equal"),
            duck_storage,
            run_duck,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return duck_rows, duck_storage, duck_threshold, run_duck


@app.cell
def _(
    csv,
    format_ms,
    mo,
    optional_import,
    random,
    duck_rows,
    duck_storage,
    duck_threshold,
    run_duck,
    tempfile,
    time,
):
    if run_duck.value == 0:
        _output = mo.md("Click **Run DuckDB demo** to execute.").callout(
            kind="neutral"
        )
    else:
        _duckdb = optional_import("duckdb")
        if not _duckdb:
            _output = mo.md(
                "DuckDB is not installed. Install with `pip install duckdb` to run this demo."
            ).callout(kind="warn")
        else:
            _rng = random.Random(33 + run_duck.value)
            _records = []
            for _idx in range(duck_rows.value):
                _records.append(
                    {
                        "order_id": _idx,
                        "region": _rng.choice(["EU", "US", "APAC"]),
                        "segment": _rng.choice(["consumer", "enterprise", "startup"]),
                        "amount": round(_rng.random() * 1000, 2),
                        "day": _rng.randint(1, 30),
                    }
                )

            _pyarrow = optional_import("pyarrow")
            _parquet = optional_import("pyarrow.parquet")

            with tempfile.TemporaryDirectory() as _tmpdir:
                _tmpdir = Path(_tmpdir)
                _csv_path = _tmpdir / "orders.csv"
                with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                    _writer = csv.DictWriter(
                        _f, fieldnames=["order_id", "region", "segment", "amount", "day"]
                    )
                    _writer.writeheader()
                    _writer.writerows(_records)

                _parquet_path = None
                if _pyarrow and _parquet:
                    _parquet_path = _tmpdir / "orders.parquet"
                    _table = _pyarrow.Table.from_pylist(_records)
                    _parquet.write_table(_table, _parquet_path)

                _db_path = _tmpdir / "analytics.duckdb"
                _con = _duckdb.connect(str(_db_path))

                _ingest_time = None
                if duck_storage.value != "CSV scan":
                    _ingest_start = time.perf_counter()
                    if duck_storage.value.startswith("Parquet") and _parquet_path:
                        _con.execute(
                            f"CREATE TABLE orders AS SELECT * FROM read_parquet('{_parquet_path}')"
                        )
                    else:
                        _con.execute(
                            f"CREATE TABLE orders AS SELECT * FROM read_csv_auto('{_csv_path}')"
                        )
                    _ingest_time = time.perf_counter() - _ingest_start

                _threshold = duck_threshold.value
                _query = (
                    "SELECT region, COUNT(*) AS orders, AVG(amount) AS avg_amount "
                    f"FROM {{source}} WHERE amount > {_threshold} GROUP BY region ORDER BY region"
                )

                _timings = []
                _result_rows = None

                # 1) CSV scan
                _start = time.perf_counter()
                _csv_result = _con.execute(
                    _query.format(source=f"read_csv_auto('{_csv_path}')")
                ).fetchall()
                _timings.append(
                    {
                        "source": "CSV scan",
                        "query_ms": round((time.perf_counter() - _start) * 1000, 2),
                    }
                )

                # 2) Parquet scan (optional)
                if _parquet_path:
                    _start = time.perf_counter()
                    _pq_result = _con.execute(
                        _query.format(source=f"read_parquet('{_parquet_path}')")
                    ).fetchall()
                    _timings.append(
                        {
                            "source": "Parquet scan",
                            "query_ms": round((time.perf_counter() - _start) * 1000, 2),
                        }
                    )

                # 3) DuckDB table query
                if duck_storage.value != "CSV scan":
                    _start = time.perf_counter()
                    _tbl_result = _con.execute(
                        _query.format(source="orders")
                    ).fetchall()
                    _timings.append(
                        {
                            "source": "DuckDB table",
                            "query_ms": round((time.perf_counter() - _start) * 1000, 2),
                        }
                    )
                    _result_rows = _tbl_result
                else:
                    _result_rows = _csv_result

                _con.close()

                _sizes = [
                    {"file": "orders.csv", "size": format_bytes(_csv_path.stat().st_size)},
                    {
                        "file": "orders.parquet",
                        "size": format_bytes(_parquet_path.stat().st_size)
                        if _parquet_path
                        else "n/a",
                    },
                    {"file": "analytics.duckdb", "size": format_bytes(_db_path.stat().st_size)},
                ]

            _results_table = [
                {
                    "region": row[0],
                    "orders": row[1],
                    "avg_amount": round(row[2], 2),
                }
                for row in (_result_rows or [])
            ]

            _sizes_table = mo.ui.table(_sizes, label="File sizes")
            _timing_table = mo.ui.table(_timings, label="Query timing (ms)")
            _results_panel = mo.ui.table(_results_table, label="Query results")

            _notes = []
            if _ingest_time is not None:
                _notes.append(
                    mo.md(f"Ingest time to DuckDB table: **{format_ms(_ingest_time)}**")
                )
            _notes.append(
                mo.md(
                    "DuckDB persists a **columnar, optimized** table in a `.duckdb` file for fast scans."
                ).callout(kind="info")
            )

            _output = mo.vstack(
                [_sizes_table, _timing_table, _results_panel] + _notes, gap=0.6
            )

    _output
    return (_output,)


@app.cell
def _(mo):
    _index_intro = mo.md(
        """
### Indexing Demo: Full Scan vs Indexed Search

Databases accelerate selective queries with **indexes**. Here we compare:

- **Full table scan** (no index)
- **Indexed lookup** (index on `category` + `value`)

We also show the query plan to make the optimization explicit.
        """
    ).callout(kind="neutral")
    _index_intro
    return (_index_intro,)


@app.cell
def _(mo):
    idx_rows = mo.ui.slider(20_000, 200_000, step=20_000, value=80_000, label="Rows")
    idx_selectivity = mo.ui.slider(0.05, 0.9, step=0.05, value=0.2, label="Share of category = 'C'")
    idx_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Value threshold")
    idx_seed = mo.ui.slider(1, 999, value=17, label="Seed")
    run_index = mo.ui.button(label="Re-run indexing demo", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([idx_rows, idx_selectivity], widths="equal"),
            mo.hstack([idx_threshold, idx_seed], widths="equal"),
            run_index,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return idx_rows, idx_seed, idx_selectivity, idx_threshold, run_index


@app.cell
def _(
    idx_rows,
    idx_seed,
    idx_selectivity,
    idx_threshold,
    mo,
    random,
    run_index,
    sqlite3,
    tempfile,
    time,
):
    if run_index.value == 0:
        _output = mo.md("Click **Re-run indexing demo** to execute.").callout(
            kind="neutral"
        )
    else:
        _rng = random.Random(idx_seed.value)
        _rows = []
        for _i in range(idx_rows.value):
            _rows.append(
                (
                    _i,
                    "C" if _rng.random() < idx_selectivity.value else _rng.choice(["A", "B", "D"]),
                    round(_rng.random() * 1000, 2),
                )
            )

        with tempfile.TemporaryDirectory() as _tmpdir:
            _db_path = str(Path(_tmpdir) / "indexing.db")
            _con = sqlite3.connect(_db_path)
            _con.execute("CREATE TABLE events (id INTEGER, category TEXT, value REAL)")
            _con.executemany("INSERT INTO events VALUES (?, ?, ?)", _rows)
            _con.commit()

            _query = (
                "SELECT COUNT(*), AVG(value) FROM events "
                f"WHERE category = 'C' AND value > {idx_threshold.value}"
            )

            _plan_scan = _con.execute(f"EXPLAIN QUERY PLAN {_query}").fetchall()
            _start = time.perf_counter()
            _scan_result = _con.execute(_query).fetchone()
            _scan_time = time.perf_counter() - _start

            _con.execute("CREATE INDEX idx_cat_val ON events(category, value)")
            _plan_idx = _con.execute(f"EXPLAIN QUERY PLAN {_query}").fetchall()
            _start = time.perf_counter()
            _idx_result = _con.execute(_query).fetchone()
            _idx_time = time.perf_counter() - _start
            _con.close()

        _timing_table = mo.ui.table(
            [
                {"mode": "full scan", "query_ms": f"{_scan_time*1000:.2f}"},
                {"mode": "indexed", "query_ms": f"{_idx_time*1000:.2f}"},
                {
                    "mode": "speedup",
                    "query_ms": f"{(_scan_time / _idx_time):.2f}x" if _idx_time else "n/a",
                },
            ],
            label="Query timings",
        )

        _plan_table = mo.ui.table(
            [
                {"plan": "scan", "detail": str(_plan_scan[0])},
                {"plan": "index", "detail": str(_plan_idx[0])},
            ],
            label="Query plan (SQLite)",
        )

        _result_table = mo.ui.table(
            [
                {"metric": "count", "scan": _scan_result[0], "index": _idx_result[0]},
                {
                    "metric": "avg(value)",
                    "scan": round(_scan_result[1] or 0, 2),
                    "index": round(_idx_result[1] or 0, 2),
                },
            ],
            label="Query results",
        )

        _note = mo.md(
            "Look for the plan to switch from **SCAN** to **SEARCH** when the index is present."
        ).callout(kind="info")

        _output = mo.vstack(
            [_timing_table, _plan_table, _result_table, _note],
            gap=0.6,
        )

    _output
    return (_output,)


@app.cell
def _(mo):
    _schema_section = mo.md("### Schema-on-Read vs Schema-on-Write (DuckDB)")
    _schema_section
    return (_schema_section,)


@app.cell
def _(mo):
    _schema_expl = mo.md(
        """
DuckDB can **infer** types when reading files (schema‑on‑read), or you can **enforce** types
when loading data (schema‑on‑write). With messy data, these choices change:

- the inferred column types  
- how many values become `NULL`  
- whether errors are surfaced early

Example of a messy column:

```
amount
120.5
N/A
87.0
```

**Watch for:** the inferred type of `amount`, how many values become `NULL` after casting,
and whether numeric aggregates require explicit casts.
        """
    ).callout(kind="neutral")
    _schema_expl
    return (_schema_expl,)


@app.cell
def _(mo):
    schema_rows = mo.ui.slider(500, 8000, step=500, value=3000, label="Rows")
    schema_dirty = mo.ui.slider(0.0, 0.6, step=0.05, value=0.2, label="Dirty rate")
    schema_seed = mo.ui.slider(1, 999, value=29, label="Seed")
    run_schema = mo.ui.button(label="Re-run schema demo", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([schema_rows, schema_dirty], widths="equal"),
            mo.hstack([schema_seed, run_schema], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return run_schema, schema_dirty, schema_rows, schema_seed


@app.cell
def _(
    csv,
    mo,
    optional_import,
    random,
    run_schema,
    schema_dirty,
    schema_rows,
    schema_seed,
    tempfile,
):
    if run_schema.value == 0:
        _output = mo.md("Click **Re-run schema demo** to execute.").callout(
            kind="neutral"
        )
    else:
        _duckdb = optional_import("duckdb")
        if not _duckdb:
            _output = mo.md(
                "DuckDB is not installed. Install with `pip install duckdb` to run this demo."
            ).callout(kind="warn")
        else:
            _rng = random.Random(schema_seed.value)
            _rows = []
            _dirty_count = 0
            for idx in range(schema_rows.value):
                amount = round(_rng.random() * 1000, 2)
                if schema_dirty.value > 0 and idx == 0:
                    amount = "N/A"
                elif _rng.random() < schema_dirty.value:
                    amount = _rng.choice(["N/A", "", "oops"])
                if isinstance(amount, str):
                    _dirty_count += 1
                _rows.append(
                    {
                        "id": idx,
                        "category": _rng.choice(["A", "B", "C"]),
                        "amount": amount,
                        "day": _rng.randint(1, 30),
                    }
                )

            with tempfile.TemporaryDirectory() as _tmpdir:
                _tmpdir = Path(_tmpdir)
                _csv_path = _tmpdir / "dirty.csv"
                with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                    _writer = csv.DictWriter(
                        _f, fieldnames=["id", "category", "amount", "day"]
                    )
                    _writer.writeheader()
                    _writer.writerows(_rows)

                _con = _duckdb.connect()
                _inferred = _con.execute(
                    f"DESCRIBE SELECT * FROM read_csv_auto('{_csv_path}')"
                ).fetchall()
                _explicit = _con.execute(
                    "DESCRIBE SELECT "
                    "CAST(id AS INTEGER) AS id, "
                    "CAST(category AS VARCHAR) AS category, "
                    "TRY_CAST(amount AS DOUBLE) AS amount, "
                    "CAST(day AS INTEGER) AS day "
                    f"FROM read_csv_auto('{_csv_path}', all_varchar=true)"
                ).fetchall()

                _inferred_bad = _con.execute(
                    "SELECT SUM(TRY_CAST(amount AS DOUBLE) IS NULL AND amount IS NOT NULL) "
                    f"FROM read_csv_auto('{_csv_path}')"
                ).fetchone()[0]
                _num_avg = _con.execute(
                    f"SELECT AVG(TRY_CAST(amount AS DOUBLE)) FROM read_csv_auto('{_csv_path}')"
                ).fetchone()[0]
                _lex_min = _con.execute(
                    f"SELECT MIN(amount) FROM read_csv_auto('{_csv_path}')"
                ).fetchone()[0]
                _explicit_nulls = _con.execute(
                    "SELECT SUM(amount IS NULL) FROM ("
                    "SELECT TRY_CAST(amount AS DOUBLE) AS amount "
                    f"FROM read_csv_auto('{_csv_path}', all_varchar=true)"
                    ")"
                ).fetchone()[0]
                _con.close()

            _inferred_amount_type = next(
                (row[1] for row in _inferred if row[0] == "amount"), "unknown"
            )
            _dirty_pct = (_dirty_count / schema_rows.value * 100) if schema_rows.value else 0

            _dirty_rows = [row for row in _rows if isinstance(row["amount"], str)]
            _sample_source = _dirty_rows if _dirty_rows else _rows
            _sample_rows = [
                {
                    "id": row["id"],
                    "category": row["category"],
                    "amount": row["amount"],
                    "dirty": isinstance(row["amount"], str),
                    "day": row["day"],
                }
                for row in _sample_source[:6]
            ]

            _sample_table = mo.ui.table(
                _sample_rows, label="Sample rows (dirty values highlighted)"
            )

            _inferred_table = mo.ui.table(
                [
                    {"column": row[0], "inferred_type": row[1]}
                    for row in _inferred
                ],
                label="Schema-on-read (inferred types)",
            )
            _explicit_table = mo.ui.table(
                [
                    {"column": row[0], "explicit_type": row[1]}
                    for row in _explicit
                ],
                label="Schema-on-write (explicit types)",
            )
            _quality_table = mo.ui.table(
                [
                    {"metric": "non-numeric amount (inferred)", "value": _inferred_bad},
                    {"metric": "NULLs after explicit cast", "value": _explicit_nulls},
                ],
                label="Data quality impact",
            )

            _metrics_table = mo.ui.table(
                [
                    {"metric": "rows", "value": schema_rows.value},
                    {"metric": "dirty rows", "value": _dirty_count},
                    {"metric": "dirty rate", "value": f"{_dirty_pct:.1f}%"},
                    {"metric": "amount inferred type", "value": _inferred_amount_type},
                    {
                        "metric": "avg(amount) via TRY_CAST",
                        "value": f"{_num_avg:.2f}" if _num_avg is not None else "n/a",
                    },
                    {"metric": "lexicographic MIN(amount)", "value": str(_lex_min)},
                ],
                label="Why schema choice matters",
            )

            _note = mo.md(
                """
**What to notice:** when `amount` is inferred as `VARCHAR`, numeric calculations require `TRY_CAST`.
Schema‑on‑write forces a numeric type and surfaces dirty values as `NULL`.
                """
            ).callout(kind="info")

            _output = mo.vstack(
                [
                    _sample_table,
                    _metrics_table,
                    _inferred_table,
                    _explicit_table,
                    _quality_table,
                    _note,
                ],
                gap=0.6,
            )

    _output
    return (_output,)


@app.cell
def _(mo):
    _qa_block_duckdb = mo.md(
        """
<div class="section-card">
  <h3>Discussion — DuckDB & Schema</h3>
  <details>
    <summary><strong>Q1:</strong> When would you materialize data into DuckDB instead of scanning raw files?</summary>
    <p><strong>Answer:</strong> When repeated queries or joins are common, materialization amortizes parsing and
    enables columnar optimizations.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> What risks do you accept with schema‑on‑read?</summary>
    <p><strong>Answer:</strong> Flexibility is high, but validation is deferred; silent `NULL`s can distort aggregates.</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> How would you detect data drift in a schema‑on‑read pipeline?</summary>
    <p><strong>Answer:</strong> Track inferred types, null rates, and value distributions over time; alert on changes.</p>
  </details>
</div>
        """
    )
    _qa_block_duckdb
    return (_qa_block_duckdb,)


@app.cell
def _(mo):
    _section = mo.md("## 6. REST API Demo (GET, POST, PUT, DELETE)")
    _section
    return (_section,)


@app.cell
def _(mo):
    rest = mo.md(
        """
### REST Principles (Quick Recap)

- **GET**: fetch a resource  
- **POST**: create a new resource  
- **PUT**: update/replace a resource  
- **DELETE**: remove a resource  

Core REST constraints (why it scales):

- **Stateless** requests (no server session state)  
- **Uniform interface** (resources + verbs)  
- **Cacheable** responses  
- **Layered** architecture  

In a JSON API, the payload is the state representation:

$$
\\text{Resource} \\xleftrightarrow[\\text{response}]{\\text{request}} \\text{Representation}
$$
        """
    ).callout(kind="neutral")
    rest
    return (rest,)


@app.cell
def _(mo):
    method = mo.ui.dropdown(
        options=["GET", "POST", "PUT", "DELETE"], value="GET", label="HTTP method"
    )
    base_url = mo.ui.text(value="https://httpbin.org", label="Base URL")
    path = mo.ui.text(value="/anything", label="Path")
    payload = mo.ui.text_area(
        value='{"message": "hello"}', label="JSON payload (for POST/PUT)"
    )
    use_live_http = mo.ui.switch(
        value=False, label="Use live HTTP (requires internet)"
    )
    mock_latency = mo.ui.slider(0, 1500, step=100, value=200, label="Mock latency (ms)")
    send = mo.ui.button(label="Send request", value=1, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([method, base_url], widths="equal"),
            path,
            payload,
            mo.hstack([use_live_http, mock_latency], widths="equal"),
            send,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return base_url, method, mock_latency, path, payload, send, use_live_http


@app.cell
def _(
    base_url,
    json,
    method,
    mock_latency,
    mo,
    path,
    payload,
    send,
    time,
    url_error,
    url_request,
    use_live_http,
):
    if send.value == 0:
        _output = mo.md("Click **Send request** to call the API.").callout(
            kind="neutral"
        )
    else:
        url = base_url.value.rstrip("/") + "/" + path.value.lstrip("/")
        _meta = mo.md(
            f"**Request #{send.value}** · `{method.value}` `{url}`"
        ).callout(kind="info")

        data_bytes = None
        headers = {"Accept": "application/json"}
        _response_panel = None

        if method.value in {"POST", "PUT", "DELETE"}:
            try:
                payload_obj = json.loads(payload.value) if payload.value.strip() else {}
                data_bytes = json.dumps(payload_obj).encode("utf-8")
                headers["Content-Type"] = "application/json"
            except json.JSONDecodeError as exc:
                _response_panel = mo.md(
                    f"Invalid JSON payload: `{exc}`"
                ).callout(kind="danger")

        def _simulate_response():
            if mock_latency.value:
                time.sleep(mock_latency.value / 1000)

            payload_obj = None
            if payload.value.strip():
                try:
                    payload_obj = json.loads(payload.value)
                except json.JSONDecodeError:
                    payload_obj = {"raw": payload.value}

            _now = time.strftime("%Y-%m-%d %H:%M:%S")
            if method.value == "GET":
                status = 200
                body = {
                    "source": "simulated",
                    "resource": path.value,
                    "timestamp": _now,
                    "items": [
                        {"id": 1, "name": "alpha"},
                        {"id": 2, "name": "beta"},
                    ],
                }
            elif method.value == "POST":
                status = 201
                body = {
                    "source": "simulated",
                    "created": True,
                    "resource": path.value,
                    "payload": payload_obj,
                    "id": 100 + send.value,
                    "timestamp": _now,
                }
            elif method.value == "PUT":
                status = 200
                body = {
                    "source": "simulated",
                    "updated": True,
                    "resource": path.value,
                    "payload": payload_obj,
                    "timestamp": _now,
                }
            else:
                status = 204
                body = None
            return status, body

        if _response_panel is None:
            req = url_request.Request(
                url, data=data_bytes, headers=headers, method=method.value
            )

            if use_live_http.value:
                try:
                    with url_request.urlopen(req, timeout=10) as _response:
                        body = _response.read().decode("utf-8", errors="replace")
                        status = _response.status
                except Exception as exc:
                    _response_panel = mo.md(f"Request failed: `{exc}`").callout(
                        kind="danger"
                    )
                else:
                    try:
                        parsed = json.loads(body)
                        preview = json.dumps(parsed, indent=2)[:1200]
                    except json.JSONDecodeError:
                        preview = body[:1200]

                    _response_panel = mo.md(
                        f"""
**Status:** `{status}` · **Source:** `live`

```json
{preview}
```
        """
                    )
            else:
                status, body = _simulate_response()
                if body is None:
                    preview = ""
                else:
                    preview = json.dumps(body, indent=2)[:1200]
                _response_panel = mo.md(
                    f"""
**Status:** `{status}` · **Source:** `simulated`

```json
{preview}
```
        """
                )

        _output = mo.vstack([_meta, _response_panel], gap=0.5)

    _output
    return (_output,)


@app.cell
def _(mo):
    _qa_block_api = mo.md(
        """
<div class="section-card">
  <h3>Discussion — APIs & Validation</h3>
  <details>
    <summary><strong>Q1:</strong> When is a POST request idempotent, and why does it matter?</summary>
    <p><strong>Answer:</strong> It’s idempotent if repeated calls yield the same result (e.g., client‑supplied IDs).
    This matters for retries and reliability.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> Where should validation happen: client, server, or both?</summary>
    <p><strong>Answer:</strong> Both. Clients can provide fast feedback, but servers must enforce rules to protect data.</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> How would you evolve an API without breaking clients?</summary>
    <p><strong>Answer:</strong> Version endpoints, keep backward compatibility, and deprecate gradually with clear docs.</p>
  </details>
</div>
        """
    )
    _qa_block_api
    return (_qa_block_api,)


@app.cell
def _(mo):
    _section = mo.md("## 7. Pydantic Models")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Pydantic = Validated Data Models

Pydantic turns raw data into **validated Python objects**, guided by type hints.

Example constraint:

$$
0 \\leq \\text{gpa} \\leq 4
$$

Try editing the JSON below to trigger validation errors and see the message structure.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    input_data = mo.ui.text_area(
        value='{"id": 1, "name": "Ada", "gpa": 3.8, "email": "ada@example.com"}',
        label="Student JSON",
    )
    validate = mo.ui.button(label="Validate with Pydantic", value=1, kind="success")
    _controls = mo.vstack([input_data, validate], gap=0.6).callout(kind="neutral")
    _controls
    return input_data, validate


@app.cell
def _(input_data, json, mo, optional_import, validate):
    if validate.value == 0:
        _output = mo.md("Click **Validate with Pydantic** to parse.").callout(
            kind="neutral"
        )
    else:
        pydantic = optional_import("pydantic")
        if not pydantic:
            _output = mo.md(
                "Pydantic is not installed. Install with `pip install pydantic`."
            ).callout(kind="warn")
        else:
            _BaseModel = pydantic.BaseModel
            _Field = pydantic.Field
            _ValidationError = pydantic.ValidationError

            class Student(_BaseModel):
                id: int
                name: str
                gpa: float = _Field(ge=0.0, le=4.0)
                email: str

            try:
                raw = json.loads(input_data.value)
                if hasattr(Student, "model_validate"):
                    obj = Student.model_validate(raw)
                    data = obj.model_dump()
                else:
                    obj = Student.parse_obj(raw)
                    data = obj.dict()
                _output = mo.md(
                    f"""
**Validated object:**

```json
{json.dumps(data, indent=2)}
```
                    """
                ).callout(kind="success")
            except _ValidationError as exc:
                _output = mo.md(
                    f"""
Validation error:

```
{exc}
```
                    """
                ).callout(kind="danger")
            except json.JSONDecodeError as exc:
                _output = mo.md(f"Invalid JSON: `{exc}`").callout(kind="danger")

    _output
    return (_output,)


@app.cell
def _(mo):
    _section = mo.md("## 8. FastAPI Demo + Automatic Docs")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### FastAPI = Type Hints → OpenAPI

FastAPI uses Python type hints + Pydantic to build validated endpoints. It automatically generates:

- OpenAPI schema (`/openapi.json`)  
- Swagger UI (`/docs`)  
- ReDoc (`/redoc`)

The type hints become a formal schema:

$$
\\text{Python Types} \\rightarrow \\text{JSON Schema} \\rightarrow \\text{Interactive Docs}
$$
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    fastapi_code = mo.md(
        """
```python
# file: src/demo_api.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lecture API")

class Item(BaseModel):
    id: int
    name: str
    price: float

items = {}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return items.get(item_id, {"error": "not found"})

@app.post("/items")
def create_item(item: Item):
    items[item.id] = item
    return item
```

This repo includes the code above in `src/demo_api.py`.

Run from the project root with:

```
uvicorn src.demo_api:app --reload
```

Then open `http://127.0.0.1:8000/docs`.
        """
    )
    fastapi_code
    return (fastapi_code,)


@app.cell
def _(mo):
    _workflow = mo.md(
        """
### Live API Workflow

1. Start the API in a terminal:

   ```bash
   uvicorn src.demo_api:app --reload
   ```

2. Click **1) Check API status** to verify the server is reachable.  
3. Edit the JSON payload and click **2) POST /items**.  
4. Choose an item id and click **3) GET /items/{id}** to compare results.
        """
    ).callout(kind="info")
    _workflow
    return (_workflow,)


@app.cell
def _(mo):
    fastapi_base_url = mo.ui.text(value="http://127.0.0.1:8000", label="API base URL")
    fastapi_check = mo.ui.button(label="1) Check API status", kind="neutral")
    fastapi_payload = mo.ui.text_area(
        value='{"id": 1, "name": "Notebook", "price": 9.9}',
        label="POST /items payload (JSON)",
    )
    fastapi_post = mo.ui.button(label="2) POST /items", kind="success")
    fastapi_item_id = mo.ui.text(value="1", label="Item id for GET /items/{id}")
    fastapi_get = mo.ui.button(label="3) GET /items/{id}", kind="neutral")

    _controls = mo.vstack(
        [
            mo.hstack([fastapi_base_url, fastapi_check], widths="equal"),
            fastapi_payload,
            mo.hstack([fastapi_post, fastapi_item_id, fastapi_get], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return (
        fastapi_base_url,
        fastapi_check,
        fastapi_get,
        fastapi_item_id,
        fastapi_payload,
        fastapi_post,
    )


@app.cell
def _(fastapi_base_url, fastapi_check, json, mo, url_request):
    if fastapi_check.value == 0:
        _output = mo.md(
            "Click **1) Check API status** after starting `uvicorn src.demo_api:app --reload`."
        ).callout(kind="neutral")
    else:
        _url = fastapi_base_url.value.rstrip("/") + "/openapi.json"
        _request = url_request.Request(_url, headers={"Accept": "application/json"}, method="GET")

        try:
            with url_request.urlopen(_request, timeout=3) as _response:
                _status = _response.status
                _body = _response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            _output = mo.md(
                f"""
API check failed for `{_url}`.

Error:

```
{exc}
```
                """
            ).callout(kind="danger")
        else:
            try:
                _schema = json.loads(_body)
            except json.JSONDecodeError:
                _schema = {}

            _paths = sorted(_schema.get("paths", {}).keys())
            _preview = json.dumps(_paths[:6], indent=2)
            _title = _schema.get("info", {}).get("title", "unknown")

            _output = mo.md(
                f"""
API is running.

- Status: `{_status}`
- Title: `{_title}`
- Docs: `{fastapi_base_url.value.rstrip('/')}/docs`

Known routes (preview):

```json
{_preview}
```
                """
            ).callout(kind="success")

    _output
    return (_output,)


@app.cell
def _(fastapi_base_url, fastapi_payload, fastapi_post, json, mo, url_error, url_request):
    if fastapi_post.value == 0:
        _output = mo.md(
            "Edit the payload, then click **2) POST /items**."
        ).callout(kind="neutral")
    else:
        _url = fastapi_base_url.value.rstrip("/") + "/items"
        try:
            _payload_obj = json.loads(fastapi_payload.value)
        except json.JSONDecodeError as exc:
            _output = mo.md(f"Invalid JSON payload: `{exc}`").callout(kind="danger")
        else:
            _data_bytes = json.dumps(_payload_obj).encode("utf-8")
            _request = url_request.Request(
                _url,
                data=_data_bytes,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

            try:
                with url_request.urlopen(_request, timeout=5) as _response:
                    _status = _response.status
                    _body = _response.read().decode("utf-8", errors="replace")
            except url_error.HTTPError as exc:
                _status = exc.code
                _body = exc.read().decode("utf-8", errors="replace")
            except Exception as exc:
                _output = mo.md(
                    f"""
POST request failed for `{_url}`.

Error:

```
{exc}
```
                    """
                ).callout(kind="danger")
            else:
                try:
                    _parsed = json.loads(_body)
                    _preview = json.dumps(_parsed, indent=2)
                except json.JSONDecodeError:
                    _preview = _body

                _output = mo.md(
                    f"""
`POST /items` returned status `{_status}`.

```json
{_preview}
```
                    """
                ).callout(kind="success" if _status < 400 else "danger")

    _output
    return (_output,)


@app.cell
def _(fastapi_base_url, fastapi_get, fastapi_item_id, json, mo, url_error, url_request):
    if fastapi_get.value == 0:
        _output = mo.md("Click **3) GET /items/{id}** to fetch an item.").callout(
            kind="neutral"
        )
    else:
        try:
            _item_id = int(fastapi_item_id.value.strip())
        except ValueError:
            _output = mo.md("Item id must be an integer.").callout(kind="danger")
        else:
            _url = fastapi_base_url.value.rstrip("/") + f"/items/{_item_id}"
            _request = url_request.Request(_url, headers={"Accept": "application/json"}, method="GET")
            try:
                with url_request.urlopen(_request, timeout=5) as _response:
                    _status = _response.status
                    _body = _response.read().decode("utf-8", errors="replace")
            except url_error.HTTPError as exc:
                _status = exc.code
                _body = exc.read().decode("utf-8", errors="replace")
            except Exception as exc:
                _output = mo.md(
                    f"""
GET request failed for `{_url}`.

Error:

```
{exc}
```
                    """
                ).callout(kind="danger")
            else:
                try:
                    _parsed = json.loads(_body)
                    _preview = json.dumps(_parsed, indent=2)
                except json.JSONDecodeError:
                    _preview = _body

                _output = mo.md(
                    f"""
`GET /items/{_item_id}` returned status `{_status}`.

```json
{_preview}
```
                    """
                ).callout(kind="success" if _status < 400 else "danger")

    _output
    return (_output,)


@app.cell
def _(mo):
    _section = mo.md("## 9. Frontend Framework Comparison")
    _section
    return (_section,)


@app.cell
def _(mo):
    framework_rows = [
        {
            "framework": "Marimo",
            "strengths": "Reactive notebooks, tight data + UI loop",
            "tradeoffs": "Notebook-first; less suited to huge web apps",
            "use_case": "Interactive labs, teaching, analysis apps",
        },
        {
            "framework": "Dash",
            "strengths": "Plotly integration, component ecosystem",
            "tradeoffs": "Callback complexity for large apps",
            "use_case": "Interactive analytics",
        },
        {
            "framework": "Streamlit",
            "strengths": "Very fast Python app prototyping, simple widget model",
            "tradeoffs": "Less layout/state control for complex multi-page apps",
            "use_case": "Data apps, dashboards, quick internal tools",
        },
        {
            "framework": "Flask",
            "strengths": "Full control, flexible templates + APIs",
            "tradeoffs": "More setup, no built-in UI",
            "use_case": "Custom web apps + APIs",
        },
        {
            "framework": "React",
            "strengths": "Highly flexible, modern UI patterns",
            "tradeoffs": "Requires JS/TS stack, more tooling",
            "use_case": "Production web apps",
        },
    ]

    _framework_note = mo.md(
        """
### Choosing a Frontend Stack

Think in terms of trade‑offs: speed vs. control, Python‑native vs. JS ecosystems, and how far you need to scale.

A simple framing:

$$
\\text{Iteration Speed} \\uparrow \\quad \\Rightarrow \\quad \\text{UI Control} \\downarrow
$$
        """
    ).callout(kind="neutral")

    _framework_table = mo.ui.table(framework_rows, label="Framework comparison")
    _panel = mo.vstack([_framework_note, _framework_table], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    _section = mo.md("## 10. Marimo Charts Lab")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Marimo Charts Lab

Use the controls below to generate a dataset and explore it with **scatter**, **line + optional regression**, and **box** plots.  
We also compute summary statistics to make the patterns quantitative.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    chart_rows = mo.ui.slider(200, 4000, step=200, value=1200, label="Rows")
    chart_seed = mo.ui.slider(1, 999, value=21, label="Seed")
    chart_slope = mo.ui.slider(-3.0, 3.0, step=0.2, value=1.2, label="Trend slope")
    chart_noise = mo.ui.slider(0.2, 5.0, step=0.2, value=1.4, label="Noise level")
    chart_regression = mo.ui.switch(value=True, label="Show regression line")

    _controls = mo.vstack(
        [
            mo.hstack([chart_rows, chart_seed], widths="equal"),
            mo.hstack([chart_slope, chart_noise], widths="equal"),
            chart_regression,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return chart_noise, chart_regression, chart_rows, chart_seed, chart_slope


@app.cell
def _(
    chart_noise,
    chart_regression,
    chart_rows,
    chart_seed,
    chart_slope,
    mo,
    optional_import,
    random,
    statistics,
):
    _rng = random.Random(chart_seed.value)
    _rows = []
    for _idx in range(chart_rows.value):
        _x = _rng.gauss(0, 1)
        _y = chart_slope.value * _x + _rng.gauss(0, chart_noise.value)
        _rows.append(
            {
                "idx": _idx,
                "x": _x,
                "y": _y,
                "category": _rng.choice(["A", "B", "C", "D"]),
            }
        )

    def _stats(values):
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std": statistics.pstdev(values),
            "min": min(values),
            "max": max(values),
        }

    _x_vals = [row["x"] for row in _rows]
    _y_vals = [row["y"] for row in _rows]
    _stats_x = _stats(_x_vals)
    _stats_y = _stats(_y_vals)
    _stats_table = mo.ui.table(
        [
            {"metric": k, "x": f"{_stats_x[k]:.3f}", "y": f"{_stats_y[k]:.3f}"}
            for k in _stats_x.keys()
        ],
        label="Summary statistics",
    )

    _pd = optional_import("pandas")
    _alt = optional_import("altair")
    if _pd and _alt:
        _df = _pd.DataFrame(_rows)

        def _linear_regression(xs, ys):
            if len(xs) < 2:
                return None
            _mean_x = statistics.mean(xs)
            _mean_y = statistics.mean(ys)
            _var_x = sum((x - _mean_x) ** 2 for x in xs)
            if _var_x == 0:
                return None
            _cov = sum((x - _mean_x) * (y - _mean_y) for x, y in zip(xs, ys))
            _slope = _cov / _var_x
            _intercept = _mean_y - _slope * _mean_x
            return _slope, _intercept

        _scatter = _alt.Chart(_df).mark_circle(size=60, opacity=0.6).encode(
            x=_alt.X("x:Q"),
            y=_alt.Y("y:Q"),
            color=_alt.Color("category:N"),
            tooltip=[
                _alt.Tooltip("x:Q"),
                _alt.Tooltip("y:Q"),
                _alt.Tooltip("category:N"),
            ],
        )
        _scatter_layers = _scatter
        if chart_regression.value:
            _lr = _linear_regression(_x_vals, _y_vals)
            if _lr:
                _slope, _intercept = _lr
                _x_min = min(_x_vals)
                _x_max = max(_x_vals)
                _reg_df = _pd.DataFrame(
                    {
                        "x": [_x_min, _x_max],
                        "y": [_slope * _x_min + _intercept, _slope * _x_max + _intercept],
                    }
                )
                _reg_line = _alt.Chart(_reg_df).mark_line(color="#1f2937").encode(
                    x=_alt.X("x:Q"), y=_alt.Y("y:Q")
                )
                _scatter_layers = _scatter + _reg_line
        _scatter_chart = mo.ui.altair_chart(_scatter_layers.properties(height=260))

        _line = (
            _alt.Chart(_df)
            .mark_line(opacity=0.6)
            .encode(
                x=_alt.X("idx:Q"),
                y=_alt.Y("y:Q"),
                color=_alt.Color("category:N"),
                tooltip=[
                    _alt.Tooltip("idx:Q"),
                    _alt.Tooltip("y:Q"),
                    _alt.Tooltip("category:N"),
                ],
            )
            .properties(height=260)
        )
        _line_layers = _line
        if chart_regression.value:
            _lr_idx = _linear_regression([row["idx"] for row in _rows], _y_vals)
            if _lr_idx:
                _slope, _intercept = _lr_idx
                _i_min = min(row["idx"] for row in _rows)
                _i_max = max(row["idx"] for row in _rows)
                _line_df = _pd.DataFrame(
                    {
                        "idx": [_i_min, _i_max],
                        "y": [_slope * _i_min + _intercept, _slope * _i_max + _intercept],
                    }
                )
                _line_reg = _alt.Chart(_line_df).mark_line(color="#0f766e").encode(
                    x=_alt.X("idx:Q"), y=_alt.Y("y:Q")
                )
                _line_layers = _line + _line_reg
        _line_chart = mo.ui.altair_chart(_line_layers)

        _box = (
            _alt.Chart(_df)
            .mark_boxplot()
            .encode(
                x=_alt.X("category:N"),
                y=_alt.Y("y:Q"),
                color=_alt.Color("category:N"),
            )
            .properties(height=260)
        )
        _box_chart = mo.ui.altair_chart(_box)

        _panel = mo.vstack(
            [
                _scatter_chart,
                _line_chart,
                _box_chart,
                _stats_table,
            ],
            gap=0.8,
        )
    else:
        _panel = mo.vstack(
            [
                mo.md("Install `pandas` + `altair` to unlock charts.").callout(kind="info"),
                _stats_table,
                mo.ui.table(_rows[:10], label="Sample rows"),
            ],
            gap=0.6,
        )

    _panel
    return (_panel,)


@app.cell
def _(mo):
    _links_section = mo.md("## Some Useful Links")
    _links_section
    return (_links_section,)


@app.cell
def _(mo):
    _links = mo.md(
        """
<div class="section-card">
  <p>Reference material for deeper dives and lookup:</p>
  <ul>
    <li>Marimo documentation: <code>https://marimo.io</code></li>
    <li>DuckDB documentation: <code>https://duckdb.org/docs</code></li>
    <li>SQLite documentation: <code>https://www.sqlite.org/docs.html</code></li>
    <li>Apache Parquet: <code>https://parquet.apache.org</code></li>
    <li>Apache Arrow: <code>https://arrow.apache.org</code></li>
    <li>Apache Avro: <code>https://avro.apache.org</code></li>
    <li>FastAPI documentation: <code>https://fastapi.tiangolo.com</code></li>
    <li>Streamlit documentation: <code>https://docs.streamlit.io</code></li>
    <li>Pydantic documentation: <code>https://docs.pydantic.dev</code></li>
    <li>OpenAPI specification: <code>https://spec.openapis.org/oas/latest.html</code></li>
    <li>HTTP Semantics (RFC 9110): <code>https://www.rfc-editor.org/rfc/rfc9110</code></li>
  </ul>
</div>
        """
    )
    _links
    return (_links,)

if __name__ == "__main__":
    app.run()
