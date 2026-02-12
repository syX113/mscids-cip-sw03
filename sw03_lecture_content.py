import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


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
            --content-width: min(80vw, 1150px);
            --content-width-medium: min(80vw, 1150px);
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

          p {
            line-height: 1.6;
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

          .mo-md strong {
            background: linear-gradient(180deg, rgba(245, 158, 11, 0.16), rgba(245, 158, 11, 0.22));
            border-radius: 6px;
            padding: 0 4px;
          }

          .mo-md blockquote {
            margin: 0.8rem 0;
            padding: 10px 14px;
            border-left: 4px solid rgba(47, 111, 237, 0.6);
            background: rgba(47, 111, 237, 0.08);
            border-radius: 10px;
            color: var(--ink-2);
          }

          .mo-md mjx-container[display="true"] {
            display: block;
            margin: 0.85rem 0;
            padding: 10px 14px;
            background: linear-gradient(
              90deg,
              rgba(47, 111, 237, 0.09),
              rgba(20, 184, 166, 0.07)
            );
            border: 1px solid rgba(47, 111, 237, 0.24);
            border-radius: 12px;
            overflow-x: auto;
          }

          .key-chip {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 999px;
            border: 1px solid rgba(47, 111, 237, 0.28);
            background: rgba(47, 111, 237, 0.14);
            color: var(--accent);
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
          }

          .focus-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 10px;
            margin-top: 10px;
          }

          .focus-item {
            border: 1px solid rgba(11, 18, 32, 0.12);
            background: rgba(255, 255, 255, 0.75);
            border-radius: 12px;
            padding: 10px 12px;
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

          tbody tr:nth-child(even) td {
            background: rgba(248, 250, 252, 0.7);
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

          .flow-card {
            display: grid;
            gap: 12px;
          }

          .flow-diagram {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
          }

          .flow-box {
            padding: 10px 14px;
            border-radius: 14px;
            border: 1px solid rgba(11, 18, 32, 0.14);
            background: rgba(255, 255, 255, 0.8);
            font-weight: 600;
            text-align: center;
            min-width: 150px;
          }

          .flow-arrow {
            font-size: 1.4rem;
            color: var(--muted);
            line-height: 1;
          }

          .flow-note {
            color: var(--muted);
            font-size: 0.9rem;
          }

          .chart-grid {
            display: grid;
            gap: 14px;
          }

          .bar-chart {
            display: grid;
            gap: 10px;
          }

          .bar-row {
            display: grid;
            grid-template-columns: 140px 1fr 110px;
            align-items: center;
            gap: 10px;
            font-size: 0.92rem;
          }

          .bar-label {
            font-weight: 600;
            color: var(--ink);
          }

          .bar-track {
            position: relative;
            height: 10px;
            background: rgba(11, 18, 32, 0.12);
            border-radius: 999px;
            overflow: hidden;
          }

          .bar-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(47, 111, 237, 0.9), rgba(20, 184, 166, 0.9));
          }

          .bar-fill.good {
            background: linear-gradient(90deg, rgba(20, 184, 166, 0.9), rgba(47, 111, 237, 0.9));
          }

          .bar-fill.bad {
            background: linear-gradient(90deg, rgba(249, 115, 22, 0.92), rgba(239, 68, 68, 0.92));
          }

          .bar-marker {
            position: absolute;
            top: -4px;
            bottom: -4px;
            width: 2px;
            background: rgba(245, 158, 11, 0.9);
            transform: translateX(-50%);
            border-radius: 2px;
          }

          .bar-value {
            text-align: right;
            font-variant-numeric: tabular-nums;
            color: var(--ink-2);
          }

          .chart-note {
            color: var(--muted);
            font-size: 0.9rem;
          }

          .dirty-row td {
            background: rgba(249, 115, 22, 0.12);
          }

          .dirty-row td.dirty-cell {
            background: rgba(249, 115, 22, 0.22);
            font-weight: 600;
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
      race conditions, serialization trade‑offs (balancing size/speed/safety), columnar analytics, API design, and
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
        <li>Marimo charts lab: regression, category scatter, trend lines</li>
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
    _legend = mo.md(
        """
<div class="section-card">
  <h3>How to Read This Notebook</h3>
  <p><span class="key-chip">Key idea</span> appears where a core concept is introduced.</p>
  <div class="focus-grid">
    <div class="focus-item"><strong>Formulas</strong>: quick quantitative model of the concept.</div>
    <div class="focus-item"><strong>Mini-labs</strong>: interactive controls to test the model.</div>
    <div class="focus-item"><strong>Discussion blocks</strong>: interpretation and trade-offs (explicit design compromises).</div>
  </div>
</div>
        """
    )
    _legend
    return (_legend,)


@app.cell
def _(mo):
    _section = mo.md("## 1. File Locks vs Databases (ACID)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter1_guide = mo.md(
        """
### Chapter 1 Introduction

> **Key Question:** When many users update shared data at the same time, do we preserve correctness?

- **Atomicity:** all-or-nothing updates
- **Isolation:** one write should not corrupt another
- **Durability:** committed data survives crashes

Practical signal to watch:

$$
\\text{lost update rate} = \\frac{E - A}{E}
$$

Higher values indicate that concurrent writes are interfering.
        """
    ).callout(kind="neutral")
    _chapter1_guide
    return (_chapter1_guide,)


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

Where:
- $E$: expected final counter value  
- $W$: number of concurrent workers  
- $I$: increments per worker  
- $A$: actual final counter value observed  
- $L$: lost updates

Databases coordinate concurrency, ensure isolation, and provide crash recovery.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    _lost_update_diagram = mo.md(
        """
<div class="section-card flow-card">
  <h3>Visual: How a Lost Update Happens</h3>
  <div class="flow-diagram">
    <div class="flow-box">Worker A reads counter = 41</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Worker B reads counter = 41</div>
  </div>
  <div class="flow-diagram">
    <div class="flow-box">A writes 42</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">B also writes 42</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Expected 43, observed 42</div>
  </div>
  <div class="flow-note">Both workers used stale state. One increment is overwritten and effectively lost.</div>
</div>
        """
    )
    _lost_update_diagram
    return (_lost_update_diagram,)


@app.cell
def _(mo):
    lu_workers = mo.ui.slider(1, 20, value=5, label="Workers (concurrent updaters)")
    lu_iterations = mo.ui.slider(
        10, 2000, step=10, value=400, label="Iterations per worker"
    )
    lu_observed = mo.ui.number(
        value=1800, label="Observed final counter (actual result)"
    )
    _lu_note = mo.md(
        """
`Expected counter = workers x iterations per worker`

Enter the **actual value** observed after a run.  
If observed < expected, those are lost updates.
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Lost Update Sanity Check"),
            mo.hstack([lu_workers, lu_iterations], widths="equal"),
            lu_observed,
            _lu_note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return lu_iterations, lu_observed, lu_workers


@app.cell
def _(lu_iterations, lu_observed, lu_workers, mo):
    _expected_value = lu_workers.value * lu_iterations.value
    _observed_value = int(lu_observed.value or 0)
    _observed_value = max(0, min(_observed_value, _expected_value))
    _lost_value = _expected_value - _observed_value
    _lost_rate = (_lost_value / _expected_value) if _expected_value else 0.0
    _summary = mo.ui.table(
        [
            {"metric": "expected", "value": _expected_value},
            {"metric": "observed", "value": _observed_value},
            {"metric": "lost updates", "value": _lost_value},
            {"metric": "lost update rate", "value": round(_lost_rate * 100, 2)},
        ],
        label="Consistency check",
    )
    _interpretation = mo.md(
        "High lost-update rate means writes are racing. Add locking or transactional updates."
    ).callout(kind="info" if _lost_value > 0 else "success")
    _panel = mo.vstack([_summary, _interpretation], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    strategies = mo.ui.multiselect(
        options=["no_lock", "thread_lock", "file_lock", "sqlite"],
        value=["no_lock", "file_lock", "sqlite"],
        label="Strategies to run",
    )
    workers = mo.ui.slider(2, 12, value=4, label="Concurrent workers")
    iterations = mo.ui.slider(50, 2000, step=50, value=300, label="Increments per worker")
    jitter = mo.ui.slider(
        0, 5, value=1, step=1, label="Artificial jitter (ms) per update"
    )
    run_race = mo.ui.button(label="Re-run counter experiment", value=1, kind="success")
    _term_note = mo.md(
        """
**Strategy notes**
- `no_lock`: plain file writes, race conditions likely (overlapping unsynchronized updates)
- `thread_lock`: Python lock in one process
- `file_lock`: OS file lock around write
- `sqlite`: transactional database updates (ACID behavior)

**Jitter (ms)** adds delay to each update, which increases overlap between workers.
        """
    ).callout(kind="info")

    _controls = mo.vstack(
        [
            mo.md("### Concurrency demo: file vs locks vs database"),
            mo.hstack([workers, iterations], widths="equal"),
            jitter,
            strategies,
            run_race,
            _term_note,
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
        _expected_counter = workers.value * iterations.value
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
                        "expected": _expected_counter,
                        "actual": value,
                        "lost updates": _expected_counter - value,
                        "duration (ms)": round(_duration * 1000, 2),
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
                        "expected": _expected_counter,
                        "actual": value,
                        "lost updates": _expected_counter - value,
                        "duration (ms)": round(_duration * 1000, 2),
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
                        "expected": _expected_counter,
                        "actual": value,
                        "lost updates": _expected_counter - value,
                        "duration (ms)": round(_duration * 1000, 2),
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
                        "expected": _expected_counter,
                        "actual": value,
                        "lost updates": _expected_counter - value,
                        "duration (ms)": round(_duration * 1000, 2),
                    }
                )

        _table = mo.ui.table(race_rows, label="Concurrency results")
        _summary = mo.md(
            """
**How to read the table**

- **No lock**: often lowest wall-clock runtime, but can be incorrect (lost updates).
- **File lock**: usually correct, but can be higher latency (serializes access).
- **SQLite**: transactional and usually correct; runtime can remain competitive.
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

The simulator below shuffles these steps to make the race condition visible (non-deterministic interleaving of operations).
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

Atomicity means a transaction is **all-or-nothing**: either every step commits, or none do.

A transfer should preserve the total balance:

$$
B_{total} = B_{Alice} + B_{Bob}
$$

Where:
- $B_{total}$: total money in the system  
- $B_{Alice}$: Alice's balance  
- $B_{Bob}$: Bob's balance

Without transactions, a crash between **debit** and **credit** can violate this invariant.
Databases roll back the partial work, so the total remains consistent.

**What this demo highlights:**
- The invariant to preserve (total balance)
- The failure point between steps (crash after debit)
- The commit/rollback boundary that restores consistency
- Atomicity is separate from isolation (we are not modeling concurrency here)

**Try this:** run once with failure **on** (see the file total break),
then run with failure **off** (both systems remain consistent).
        """
    ).callout(kind="neutral")
    _atomic_flow = mo.Html(
        """
<div class="section-card flow-card">
  <h3>Transaction Boundary</h3>
  <div class="flow-diagram">
    <div class="flow-box">Debit Alice</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Credit Bob</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Commit or Rollback</div>
  </div>
  <div class="flow-note">Atomicity means either all steps commit or none do.</div>
</div>
        """
    )
    _panel = mo.vstack([_atomic_intro, _atomic_flow], gap=0.6)
    _panel
    return (_panel,)


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

        def _total_bar(label, total, expected, bar_class):
            pct = 0.0 if expected == 0 else min(100.0, (total / expected) * 100.0)
            return f"""
<div class="bar-row">
  <div class="bar-label">{label}</div>
  <div class="bar-track">
    <div class="bar-fill {bar_class}" style="width: {pct:.1f}%"></div>
    <div class="bar-marker" style="left: 100%"></div>
  </div>
  <div class="bar-value">{total:,} / {expected:,}</div>
</div>
            """

        _total_chart = mo.Html(
            f"""
<div class="section-card">
  <h3>Total Balance Snapshot</h3>
  <div class="chart-note">Gold marker = expected total ({_expected_total:,}).</div>
  <div class="bar-chart">
    {_total_bar("File total", _file_total, _expected_total, "good" if _file_ok else "bad")}
    {_total_bar("SQLite total", _db_total, _expected_total, "good" if _db_ok else "bad")}
  </div>
</div>
            """
        )

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
                _total_chart,
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
    <summary><strong>Q1:</strong> If only files were available (no database), how can a transfer be made all‑or‑nothing?</summary>
    <p><strong>Answer:</strong> Write a small log entry first (write‑ahead log, or WAL), or write to a temp file and rename it (an atomic rename).
    On restart, replay or roll back the log.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> What must always stay true in this system?</summary>
    <p><strong>Answer:</strong> The total balance should never change. Build checks/tests that verify this after crashes and retries (invariant checks).</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> Should a system stop on error or allow temporary mismatch?</summary>
    <p><strong>Answer:</strong> Finance usually prefers fail‑fast (abort immediately on error); analytics may allow temporary inconsistency and repair later (eventual consistency: convergence to a correct state after delay).
    Choose based on the cost of wrong data vs. downtime.</p>
  </details>
</div>
        """
    )
    _qa_block_concurrency
    return (_qa_block_concurrency,)


@app.cell
def _(mo):
    _conclusion_concurrency = mo.md(
        """
<div class="section-card">
  <h3>Chapter 1 Conclusion</h3>
  <ul>
    <li>Without proper synchronization, file updates lose increments under concurrency.</li>
    <li>Atomicity + isolation are easier to enforce with database transactions than plain files.</li>
    <li>Always track invariants (expected vs actual) to detect correctness issues early.</li>
  </ul>
</div>
        """
    ).callout(kind="success")
    _conclusion_concurrency
    return (_conclusion_concurrency,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

The previous section showed a **correctness** problem: many writers can break data if updates are not coordinated.
Now we switch to a **data representation** problem (serialization format choice): once data is correct, which format should be used to store/send it?

Simple idea:

$$
\\text{transfer time} \\approx \\frac{\\text{bytes}}{\\text{throughput}}
$$

So better formats can reduce waiting by shrinking bytes or speeding parsing.
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 2. Serialization & Deserialization Benchmarks")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter2_guide = mo.md(
        """
### Chapter 2 Introduction

> **Key Question:** Which format gives the best trade-off for the workload (actual data + query pattern)?

Serialization is packaging data for storage or transfer.
Different packages have different trade-offs (explicit compromises between competing goals):

- readable vs compact
- Python-specific vs cross-language
- fast writes vs fast reads

Rule of thumb:

$$
\\text{end-to-end cost} \\approx \\text{write time} + \\text{read time} + \\text{bytes moved cost}
$$
        """
    ).callout(kind="neutral")
    _chapter2_guide
    return (_chapter2_guide,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Serialization = Bytes on Disk (or Wire)

Serialization transforms Python objects into bytes so they can be stored or sent.
Deserialization rebuilds objects from bytes. The format choice affects speed, file size,
interoperability, type fidelity, schema evolution, and safety.

**Where it shows up:** storage files, API payloads, message queues, caches, checkpoints.  
**What to compare:** speed, size, interop, **type fidelity**, schema evolution, safety.

- **Speed**: write + read throughput  
- **Size**: how many bytes hit disk  
- **Interop**: language/tool compatibility  
- **Type fidelity**: do types round-trip cleanly?  
- **Safety**: Pickle can execute arbitrary code

A simple performance model (quantitative summary):

$$
\\text{Throughput} = \\frac{\\text{bytes written}}{\\text{write time}}
\\qquad
\\text{Latency} = \\text{write time} + \\text{read time}
$$

Where:
- $\\text{bytes written}$: serialized output size on disk  
- $\\text{write time}$: serialization time  
- $\\text{Latency}$: total round-trip time (write + read)

**Format quick reference:**  
- **JSON/CSV**: human‑readable, row‑oriented  
- **Avro**: row‑oriented, schema‑driven events  
- **Arrow/Feather**: columnar interchange (fast analytics)  
- **Parquet**: columnar on‑disk analytics  
- **Pickle**: Python‑specific (unsafe for untrusted data)
        """
    ).callout(kind="neutral")
    _flow = mo.Html(
        """
<div class="section-card flow-card">
  <h3>Serialization Pipeline</h3>
  <div class="flow-diagram">
    <div class="flow-box">Python object</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Bytes (disk / wire)</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Python object</div>
  </div>
  <div class="flow-note">Format choice determines runtime, file size, interoperability, and safety risk.</div>
</div>
        """
    )
    _panel = mo.vstack([_explanation, _flow], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    format_use_case = mo.ui.dropdown(
        options=[
            "Public API payload",
            "Internal Python checkpoint",
            "Analytics table",
            "Streaming event log",
        ],
        value="Public API payload",
        label="Use case",
    )
    format_priority = mo.ui.dropdown(
        options=["Interoperability", "Speed", "Small size", "Safety"],
        value="Interoperability",
        label="Priority",
    )
    _note = mo.md(
        """
Pick a context and goal, then compare the recommendation with the benchmark table below.
This is a starting heuristic, not a final rule.
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [mo.md("### Mini-lab: Format Decision Assistant"), format_use_case, format_priority, _note],
        gap=0.5,
    ).callout(kind="neutral")
    _panel
    return format_priority, format_use_case


@app.cell
def _(format_priority, format_use_case, mo):
    key = (format_use_case.value, format_priority.value)
    recommendations = {
        ("Public API payload", "Interoperability"): "JSON",
        ("Public API payload", "Speed"): "JSON (or MessagePack if both sides support it)",
        ("Public API payload", "Small size"): "Compressed JSON or binary protocol",
        ("Public API payload", "Safety"): "JSON with strict schema validation",
        ("Internal Python checkpoint", "Interoperability"): "Parquet/Arrow",
        ("Internal Python checkpoint", "Speed"): "Pickle (trusted data only)",
        ("Internal Python checkpoint", "Small size"): "Parquet or compressed pickle",
        ("Internal Python checkpoint", "Safety"): "Parquet/JSON, avoid untrusted pickle",
        ("Analytics table", "Interoperability"): "Parquet",
        ("Analytics table", "Speed"): "Parquet or Arrow",
        ("Analytics table", "Small size"): "Parquet + zstd/snappy",
        ("Analytics table", "Safety"): "Parquet with schema checks",
        ("Streaming event log", "Interoperability"): "Avro/JSON",
        ("Streaming event log", "Speed"): "Avro",
        ("Streaming event log", "Small size"): "Avro with compression",
        ("Streaming event log", "Safety"): "Avro + schema registry",
    }
    choice = recommendations.get(key, "JSON")
    _text = mo.md(
        f"Recommended starting point: **{choice}**\n\n"
        "Treat this as a default, then benchmark on the real workload (actual data + query pattern)."
    ).callout(kind="info")
    _text
    return (_text,)


@app.cell
def _(mo):
    serial_rows = mo.ui.slider(200, 3000, step=200, value=800, label="Rows")
    serial_cols = mo.ui.slider(2, 8, value=5, label="Numeric columns")
    serial_seed = mo.ui.slider(1, 999, value=42, label="Seed")
    run_serial = mo.ui.button(label="Re-run serialization benchmark", value=1, kind="success")
    _note = mo.md(
        "Includes Arrow, Parquet, and Avro by default (requires `pyarrow` + `fastavro`)."
    )

    _controls = mo.vstack(
        [
            mo.hstack([serial_rows, serial_cols], widths="equal"),
            serial_seed,
            _note,
            run_serial,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return run_serial, serial_cols, serial_rows, serial_seed


@app.cell
def _(
    csv,
    format_bytes,
    format_ms,
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
        latency = write_time + read_time
        throughput = 0.0 if write_time == 0 else size / write_time
        return {
            "format": label,
            "write_s": write_time,
            "read_s": read_time,
            "latency_s": latency,
            "size_bytes": size,
            "throughput_mbps": throughput / (1024 * 1024),
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

            _pyarrow = optional_import("pyarrow")
            _feather = optional_import("pyarrow.feather")
            _parquet = optional_import("pyarrow.parquet")
            fastavro = optional_import("fastavro")

            _missing = []
            if not (_pyarrow and _feather):
                _missing.append("pyarrow.feather")
            if not _parquet:
                _missing.append("pyarrow.parquet")
            if not fastavro:
                _missing.append("fastavro")

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

            if _pyarrow and _parquet:

                def parquet_write(path):
                    table = _pyarrow.Table.from_pylist(_records)
                    _parquet.write_table(table, path)

                def parquet_read(path):
                    _parquet.read_table(path)

                _results.append(
                    bench(
                        "Parquet",
                        parquet_write,
                        parquet_read,
                        _tmpdir / "data.parquet",
                    )
                )

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

        _display_rows = []
        for row in _results:
            _display_rows.append(
                {
                    "format": row["format"],
                    "write (ms)": round(row["write_s"] * 1000, 3),
                    "read (ms)": round(row["read_s"] * 1000, 3),
                    "latency (ms)": round(row["latency_s"] * 1000, 3),
                    "size (bytes)": row["size_bytes"],
                    "write (MB/s)": round(row["throughput_mbps"], 3),
                }
            )

        def _bar_chart(title, rows, value_key, formatter):
            if not rows:
                return None
            max_val = max(row[value_key] for row in rows) or 1
            _bars = []
            for row in rows:
                value = row[value_key]
                pct = min(100.0, (value / max_val) * 100.0)
                _bars.append(
                    f"""
<div class="bar-row">
  <div class="bar-label">{row["format"]}</div>
  <div class="bar-track">
    <div class="bar-fill" style="width: {pct:.1f}%"></div>
  </div>
  <div class="bar-value">{formatter(value)}</div>
</div>
                    """
                )
            return mo.Html(
                f"""
<div class="section-card">
  <h3>{title}</h3>
  <div class="bar-chart">
    {''.join(_bars)}
  </div>
  <div class="chart-note">Higher bars = larger values.</div>
</div>
                """
            )

        _size_chart = _bar_chart(
            "File size (smaller is better)",
            _results,
            "size_bytes",
            format_bytes,
        )
        _latency_chart = _bar_chart(
            "Total latency (write + read)",
            _results,
            "latency_s",
            format_ms,
        )
        _charts = mo.vstack([_size_chart, _latency_chart], gap=0.6)

        _missing_note = None
        if _missing:
            _missing_note = mo.md(
                "Missing libraries required for Arrow/Parquet/Avro: "
                + ", ".join(f"`{name}`" for name in _missing)
                + ". Install them to include these formats."
            ).callout(kind="warn")

        results_table = mo.ui.table(_display_rows, label="Serialization benchmark")
        benchmark_note = mo.md(
            "Numbers vary by machine and caching. Treat this as a **relative** comparison, not an absolute benchmark."
        ).callout(kind="info")
        warning = mo.md(
            """
**Security note:** Pickle is not safe for untrusted data. Only load Pickle files from trusted sources.
            """
        ).callout(kind="warn")

        _items = [sample, results_table, _charts, benchmark_note, warning]
        if _missing_note:
            _items.insert(1, _missing_note)
        _output = mo.vstack(_items, gap=0.6)

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
    <summary><strong>Q1:</strong> How is a format selected among JSON, Avro, or Parquet?</summary>
    <p><strong>Answer:</strong> Start with who reads it and how. JSON for broad tool support (interoperability),
    Avro for event streams with changing schemas (schema evolution),
    Parquet for analytics scans and compression (columnar).</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> Who can send this data, and can they be malicious?</summary>
    <p><strong>Answer:</strong> If data is untrusted, avoid Pickle and validate strictly (input validation).</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> Where should size vs. speed trade‑offs be measured?</summary>
    <p><strong>Answer:</strong> Measure write/read latency and storage costs in a staging or canary pipeline (test environment with production-like traffic), then compare before/after.</p>
  </details>
</div>
        """
    )
    _qa_block_serialization
    return (_qa_block_serialization,)


@app.cell
def _(mo):
    _conclusion_serialization = mo.md(
        """
<div class="section-card">
  <h3>Chapter 2 Conclusion</h3>
  <ul>
    <li>Format choice is a trade-off (explicit compromise) between speed, size, interoperability, and safety.</li>
    <li>Use benchmarks from a representative workload (actual data + query pattern) to compare latency and storage cost.</li>
    <li>Pickle preserves Python types but should not be used for untrusted data.</li>
  </ul>
</div>
        """
    ).callout(kind="success")
    _conclusion_serialization
    return (_conclusion_serialization,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

Now that we know how to serialize data, the next question is **how to lay it out** on disk.

- Row layout: good when queries read one full record at a time.
- Column layout: good when queries scan a few columns across many rows.

Rule of thumb:

$$
\\text{read work} \\propto \\text{rows read} \\times \\text{columns touched}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 3. Column-Based vs Row-Based Storage")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter3_guide = mo.md(
        """
### Chapter 3 Introduction

> **Key Question:** Is read work spent on data that queries do not need?

Storage layout determines read cost:

- Row store: incurs read cost (I/O + CPU) for whole rows
- Column store: incurs read cost mainly for selected columns

Quick mental model:

$$
\\text{cost ratio} \\approx \\frac{C}{k}
$$

If a query needs only $k$ of $C$ columns, columnar layout can reduce read work substantially.
        """
    ).callout(kind="neutral")
    _chapter3_guide
    return (_chapter3_guide,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Row Store vs Column Store

**Row stores** keep full records together. Great for OLTP (Online Transaction Processing) and point lookups.  
**Column stores** group values by column. Great for scans, aggregates, and compression.

If a query scans only *k* columns out of *C*, the I/O pattern changes:

$$
IO_{row} \\approx N \\times C
\\qquad
IO_{col} \\approx N \\times k
$$

Where:
- $N$: number of rows  
- $C$: total columns in the dataset  
- $k$: columns actually needed by the query ($k \\ll C$ for selective scans)

Below we simulate column selection and filtering to reveal the runtime difference (execution-time gap).

**Format perspective:** Avro is a row‑based, schema‑driven file format (great for event logs).
Parquet is a column‑based file format (great for analytics and scans).
Arrow is columnar in‑memory (fast interchange between systems).
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    _layout_diagram = mo.md(
        """
<div class="section-card flow-card">
  <h3>Visual: Same Table, Two Physical Layouts</h3>
  <div class="grid-2">
    <div>
      <h4>Row layout (record-oriented)</h4>
      <pre><code>row1: [id, city, sales, qty]
row2: [id, city, sales, qty]
row3: [id, city, sales, qty]</code></pre>
      <div class="flow-note">Good when each request needs most fields of one row.</div>
    </div>
    <div>
      <h4>Column layout (analytics-oriented)</h4>
      <pre><code>id:   [id1, id2, id3, ...]
city: [c1,  c2,  c3,  ...]
sales:[s1,  s2,  s3,  ...]
qty:  [q1,  q2,  q3,  ...]</code></pre>
      <div class="flow-note">Good when queries touch a few columns across many rows.</div>
    </div>
  </div>
</div>
        """
    )
    _layout_diagram
    return (_layout_diagram,)


@app.cell
def _(mo):
    io_total_cols = mo.ui.slider(2, 30, value=12, label="Total columns (C)")
    io_needed_cols = mo.ui.slider(1, 12, value=3, label="Columns needed (k)")
    io_rows = mo.ui.slider(1_000, 1_000_000, step=1_000, value=100_000, label="Rows (N)")
    _io_note = mo.md(
        """
I/O = **Input/Output**, meaning data moved between storage and compute.

This estimator uses simple "work units" (rows x columns touched) to explain why columnar
layout helps when queries use only a few columns.
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: I/O (Input/Output) Work Estimator"),
            mo.hstack([io_total_cols, io_needed_cols], widths="equal"),
            io_rows,
            _io_note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return io_needed_cols, io_rows, io_total_cols


@app.cell
def _(io_needed_cols, io_rows, io_total_cols, mo):
    c = io_total_cols.value
    k = min(io_needed_cols.value, c)
    n = io_rows.value
    io_row = n * c
    io_col = n * k
    _row_col_ratio = io_row / max(1, io_col)
    _table = mo.ui.table(
        [
            {"metric": "row-store work units", "value": io_row},
            {"metric": "column-store work units", "value": io_col},
            {"metric": "row/column ratio", "value": round(_row_col_ratio, 2)},
        ],
        label="Estimated read effort",
    )
    _note = mo.md(
        "As k gets much smaller than C, columnar advantage increases."
    ).callout(kind="info")
    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return (_panel,)


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
                "Avro row (ms)": round(row_select_time * 1000, 3),
                "Parquet col (ms)": round(col_select_time * 1000, 3),
            },
            {
                "operation": "Filter column > 0.75",
                "Avro row (ms)": round(row_filter_time * 1000, 3),
                "Parquet col (ms)": round(col_filter_time * 1000, 3),
            },
            {
                "operation": "Sum column",
                "Avro row (ms)": round(row_sum_time * 1000, 3),
                "Parquet col (ms)": round(col_sum_time * 1000, 3),
            },
        ]

        _table = mo.ui.table(_results, label="Row vs Column timing (Python simulation)")
        _note = mo.md(
            """
**Discussion:** These timings simulate access patterns (row‑style vs column‑style), not actual file I/O.
Real column formats like Parquet show bigger wins because they avoid reading unused columns from disk.
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
    <summary><strong>Q1:</strong> When is a row store a better choice?</summary>
    <p><strong>Answer:</strong> Point lookups, frequent updates, and transactions that read or write full records (OLTP workloads = Online Transaction Processing).</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> How does reading only needed columns help?</summary>
    <p><strong>Answer:</strong> Unused columns are skipped, which reduces I/O and speeds up scans. This is called projection pushdown (applying column selection early in query execution).</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> When can compression make things slower?</summary>
    <p><strong>Answer:</strong> If data is small or CPU is the dominant limiting resource (bottleneck), decompression overhead can outweigh I/O savings (CPU‑bound).</p>
  </details>
</div>
        """
    )
    _qa_block_storage
    return (_qa_block_storage,)


@app.cell
def _(mo):
    _conclusion_storage = mo.md(
        """
<div class="section-card">
  <h3>Chapter 3 Conclusion</h3>
  <ul>
    <li>Row layouts favor transactional record-level access; column layouts favor scans and aggregates.</li>
    <li>Reading only required columns cuts I/O and typically improves analytics performance.</li>
    <li>Compression gains depend on which resource is the dominant limiting factor (bottleneck): disk I/O or CPU.</li>
  </ul>
</div>
        """
    ).callout(kind="success")
    _conclusion_storage
    return (_conclusion_storage,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

Columnar data puts similar values together, and similar values are easier to compress.
Next we measure how much size reduction we can actually get.

$$
\\text{savings} = 1 - \\frac{\\text{compressed size}}{\\text{original size}}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 4. Compression & Encoding (Parquet, Gzip)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter4_guide = mo.md(
        """
### Chapter 4 Introduction

> **Key Question:** Will compression reduce total query time, not only file size?

Compression is not just about saving disk space.
It usually also reduces how much data must travel from disk to CPU.

Two quick checks:

- Is the workload I/O-bound (limited by data transfer from storage)? Compression helps more.
- Is CPU already saturated? Heavy codecs can hurt latency.

Quick timing model:

$$
T_{total} \\approx T_{io} + T_{decompress} + T_{compute}
$$
        """
    ).callout(kind="neutral")
    _chapter4_guide
    return (_chapter4_guide,)


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

Where:
- $r$: compression ratio  
- $\\text{compressed size}$: file size after compression  
- $\\text{original size}$: baseline uncompressed file size  
- $\\text{Savings}$: fraction of size removed by compression

We compare JSON/CSV to gzip and Parquet with different codecs.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    budget_size_gb = mo.ui.slider(1, 500, value=120, label="Raw dataset size (GB)")
    budget_ratio = mo.ui.slider(0.1, 1.0, step=0.05, value=0.35, label="Compression ratio")
    budget_scans_day = mo.ui.slider(1, 80, value=18, label="Full scans/day")
    _note = mo.md(
        "Set the estimated compression ratio and scan frequency to quantify daily I/O savings (reduced bytes read/written)."
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Compression Cost Impact"),
            mo.hstack([budget_size_gb, budget_ratio], widths="equal"),
            budget_scans_day,
            _note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return budget_ratio, budget_scans_day, budget_size_gb


@app.cell
def _(budget_ratio, budget_scans_day, budget_size_gb, mo):
    raw_gb = budget_size_gb.value
    _compression_ratio = budget_ratio.value
    comp_gb = raw_gb * _compression_ratio
    saved_gb = raw_gb - comp_gb
    daily_io_saved = saved_gb * budget_scans_day.value
    _table = mo.ui.table(
        [
            {"metric": "compressed size (GB)", "value": round(comp_gb, 2)},
            {"metric": "saved size per scan (GB)", "value": round(saved_gb, 2)},
            {"metric": "daily I/O saved (GB)", "value": round(daily_io_saved, 2)},
        ],
        label="Compression budget impact",
    )
    _note = mo.md(
        "Use this as a first-order estimate before deeper benchmarking."
    ).callout(kind="info")
    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    image_demo_rank = mo.ui.slider(
        4, 90, value=26, step=2, label="PCA components (rank k)"
    )
    image_demo_width = mo.ui.slider(
        200, 360, value=280, step=20, label="Image width (px)"
    )
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Visual Compression with PCA (Cat Image)"),
            mo.hstack([image_demo_rank, image_demo_width], widths="equal"),
            mo.md(
                "Left is the reference cat image. Right is reconstructed from only `k` PCA components per color channel."
            ).callout(kind="info"),
            mo.md(
                "Further Details: [Principal Component Analysis (PCA)](https://en.wikipedia.org/wiki/Principal_component_analysis)"
            ).callout(kind="neutral"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return image_demo_rank, image_demo_width


@app.cell
def _(image_demo_rank, image_demo_width, io, math, mo, optional_import):
    _pil_image = optional_import("PIL.Image")
    _pil_draw = optional_import("PIL.ImageDraw")
    _np = optional_import("numpy")

    if not (_pil_image and _pil_draw and _np):
        _output = mo.md(
            "Install `Pillow` and `numpy` to run the PCA image compression lab (`pip install pillow numpy`)."
        ).callout(kind="warn")
    else:
        _width = image_demo_width.value
        _height = int(_width * 0.74)
        _img = _pil_image.new("RGB", (_width, _height), color=(238, 242, 248))
        _draw = _pil_draw.Draw(_img)

        # Soft gradient background.
        for _y in range(_height):
            _r = int(218 + 18 * (_y / max(1, _height - 1)))
            _g = int(229 + 14 * (_y / max(1, _height - 1)))
            _b = int(242 + 10 * (_y / max(1, _height - 1)))
            _draw.line([(0, _y), (_width, _y)], fill=(_r, _g, _b))

        # Add a deterministic checker texture to reveal compression artifacts.
        _step = max(6, _width // 45)
        for _x in range(0, _width, _step):
            for _y in range(0, _height, _step):
                if ((_x // _step) + (_y // _step)) % 2 == 0:
                    _draw.rectangle(
                        [_x, _y, min(_width - 1, _x + _step), min(_height - 1, _y + _step)],
                        outline=None,
                        fill=(225, 232, 245),
                    )

        # Draw a cute cat face as the source image.
        _cx = _width // 2
        _cy = int(_height * 0.56)
        _r = int(min(_width, _height) * 0.24)
        _fur = (220, 192, 158)
        _fur_dark = (96, 74, 56)
        _ear_inner = (246, 186, 198)

        _draw.polygon(
            [(_cx - int(0.82 * _r), _cy - int(0.52 * _r)),
             (_cx - int(0.40 * _r), _cy - int(1.35 * _r)),
             (_cx - int(0.03 * _r), _cy - int(0.58 * _r))],
            fill=_fur,
            outline=_fur_dark,
            width=3,
        )
        _draw.polygon(
            [(_cx + int(0.82 * _r), _cy - int(0.52 * _r)),
             (_cx + int(0.40 * _r), _cy - int(1.35 * _r)),
             (_cx + int(0.03 * _r), _cy - int(0.58 * _r))],
            fill=_fur,
            outline=_fur_dark,
            width=3,
        )
        _draw.polygon(
            [(_cx - int(0.70 * _r), _cy - int(0.56 * _r)),
             (_cx - int(0.40 * _r), _cy - int(1.16 * _r)),
             (_cx - int(0.12 * _r), _cy - int(0.62 * _r))],
            fill=_ear_inner,
            outline=None,
        )
        _draw.polygon(
            [(_cx + int(0.70 * _r), _cy - int(0.56 * _r)),
             (_cx + int(0.40 * _r), _cy - int(1.16 * _r)),
             (_cx + int(0.12 * _r), _cy - int(0.62 * _r))],
            fill=_ear_inner,
            outline=None,
        )

        _draw.ellipse(
            [(_cx - _r), (_cy - _r), (_cx + _r), (_cy + _r)],
            fill=_fur,
            outline=_fur_dark,
            width=3,
        )
        _draw.ellipse(
            [(_cx - int(0.45 * _r)), (_cy + int(0.05 * _r)), (_cx + int(0.45 * _r)), (_cy + int(0.62 * _r))],
            fill=(236, 214, 190),
            outline=None,
        )

        _eye_w = int(0.25 * _r)
        _eye_h = int(0.18 * _r)
        _eye_y = _cy - int(0.14 * _r)
        _left_eye_x = _cx - int(0.50 * _r)
        _right_eye_x = _cx + int(0.50 * _r)
        _draw.ellipse(
            [(_left_eye_x - _eye_w, _eye_y - _eye_h), (_left_eye_x + _eye_w, _eye_y + _eye_h)],
            fill=(143, 198, 128),
            outline=(40, 40, 40),
            width=2,
        )
        _draw.ellipse(
            [(_right_eye_x - _eye_w, _eye_y - _eye_h), (_right_eye_x + _eye_w, _eye_y + _eye_h)],
            fill=(143, 198, 128),
            outline=(40, 40, 40),
            width=2,
        )
        _pupil_w = max(4, int(0.08 * _r))
        _pupil_h = max(7, int(0.20 * _r))
        _draw.ellipse(
            [(_left_eye_x - _pupil_w, _eye_y - _pupil_h), (_left_eye_x + _pupil_w, _eye_y + _pupil_h)],
            fill=(18, 22, 20),
        )
        _draw.ellipse(
            [(_right_eye_x - _pupil_w, _eye_y - _pupil_h), (_right_eye_x + _pupil_w, _eye_y + _pupil_h)],
            fill=(18, 22, 20),
        )
        _spark = max(3, int(0.05 * _r))
        _draw.ellipse(
            [(_left_eye_x - _spark, _eye_y - _spark), (_left_eye_x + _spark, _eye_y + _spark)],
            fill=(255, 255, 255),
        )
        _draw.ellipse(
            [(_right_eye_x - _spark, _eye_y - _spark), (_right_eye_x + _spark, _eye_y + _spark)],
            fill=(255, 255, 255),
        )

        _nose_y = _cy + int(0.13 * _r)
        _draw.polygon(
            [(_cx, _nose_y),
             (_cx - int(0.13 * _r), _nose_y + int(0.15 * _r)),
             (_cx + int(0.13 * _r), _nose_y + int(0.15 * _r))],
            fill=(234, 150, 165),
            outline=(120, 74, 86),
        )
        _draw.line(
            [(_cx, _nose_y + int(0.15 * _r)), (_cx, _cy + int(0.48 * _r))],
            fill=(88, 67, 54),
            width=2,
        )
        _draw.arc(
            [(_cx - int(0.24 * _r), _cy + int(0.38 * _r)), (_cx, _cy + int(0.62 * _r))],
            start=200,
            end=340,
            fill=(88, 67, 54),
            width=2,
        )
        _draw.arc(
            [(_cx, _cy + int(0.38 * _r)), (_cx + int(0.24 * _r), _cy + int(0.62 * _r))],
            start=200,
            end=340,
            fill=(88, 67, 54),
            width=2,
        )
        _draw.ellipse(
            [(_cx - int(0.70 * _r), _cy + int(0.16 * _r)), (_cx - int(0.44 * _r), _cy + int(0.36 * _r))],
            fill=(247, 178, 186),
            outline=None,
        )
        _draw.ellipse(
            [(_cx + int(0.44 * _r), _cy + int(0.16 * _r)), (_cx + int(0.70 * _r), _cy + int(0.36 * _r))],
            fill=(247, 178, 186),
            outline=None,
        )
        _draw.line(
            [(_cx, _cy - int(0.34 * _r)), (_cx - int(0.11 * _r), _cy - int(0.48 * _r))],
            fill=(187, 151, 118),
            width=2,
        )
        _draw.line(
            [(_cx, _cy - int(0.34 * _r)), (_cx + int(0.11 * _r), _cy - int(0.48 * _r))],
            fill=(187, 151, 118),
            width=2,
        )

        for _offset in [-1, 0, 1]:
            _dy = _offset * int(0.13 * _r)
            _draw.line(
                [(_cx - int(0.12 * _r), _cy + int(0.28 * _r) + _dy), (_cx - int(0.95 * _r), _cy + int(0.13 * _r) + _dy)],
                fill=(88, 67, 54),
                width=2,
            )
            _draw.line(
                [(_cx + int(0.12 * _r), _cy + int(0.28 * _r) + _dy), (_cx + int(0.95 * _r), _cy + int(0.13 * _r) + _dy)],
                fill=(88, 67, 54),
                width=2,
            )

        _arr = _np.asarray(_img, dtype=_np.float32) / 255.0
        _rank = int(min(image_demo_rank.value, _arr.shape[0], _arr.shape[1]))
        _reconstructed = _np.zeros_like(_arr)
        _factors = []

        for _channel_idx in range(3):
            _channel = _arr[:, :, _channel_idx]
            _u, _s, _vt = _np.linalg.svd(_channel, full_matrices=False)
            _ur = _u[:, :_rank]
            _sr = _s[:_rank]
            _vtr = _vt[:_rank, :]
            _reconstructed[:, :, _channel_idx] = (_ur * _sr) @ _vtr
            _factors.append((_ur.astype(_np.float32), _sr.astype(_np.float32), _vtr.astype(_np.float32)))

        _reconstructed = _np.clip(_reconstructed, 0.0, 1.0)
        _mse = float(_np.mean((_arr - _reconstructed) ** 2))
        _psnr = float("inf") if _mse <= 1e-12 else 10.0 * math.log10(1.0 / _mse)

        _ref_uint8 = (_arr * 255.0).astype(_np.uint8)
        _rec_uint8 = (_reconstructed * 255.0).astype(_np.uint8)
        _ref_img = _pil_image.fromarray(_ref_uint8)
        _rec_img = _pil_image.fromarray(_rec_uint8)

        _ref_buf = io.BytesIO()
        _ref_img.save(_ref_buf, format="PNG", optimize=True)
        _ref_bytes = _ref_buf.getvalue()

        _rec_buf = io.BytesIO()
        _rec_img.save(_rec_buf, format="PNG", optimize=True)
        _rec_bytes = _rec_buf.getvalue()

        _raw_rgb_bytes = _arr.shape[0] * _arr.shape[1] * 3

        _comparison_images = mo.hstack(
            [
                mo.image(
                    src=_ref_bytes,
                    width="100%",
                    caption="Reference cat image (display preview)",
                ),
                mo.image(
                    src=_rec_bytes,
                    width="100%",
                    caption=(
                        f"PCA reconstruction (k={_rank}, display preview)"
                    ),
                ),
            ],
            widths="equal",
            gap=0.8,
        )
        _payload16 = {}
        for _channel_idx, (_ur, _sr, _vtr) in enumerate(_factors):
            _payload16[f"u{_channel_idx}"] = _ur.astype(_np.float16)
            _payload16[f"s{_channel_idx}"] = _sr.astype(_np.float16)
            _payload16[f"vt{_channel_idx}"] = _vtr.astype(_np.float16)

        _npz16_buf = io.BytesIO()
        _np.savez_compressed(_npz16_buf, **_payload16)
        _pca_npz16_bytes = len(_npz16_buf.getvalue())
        _pca_ratio = _pca_npz16_bytes / max(1, _raw_rgb_bytes)
        _psnr_display = "infinite" if _psnr == float("inf") else round(_psnr, 2)

        _comparison_table = mo.ui.table(
            [
                {"metric": "PCA components kept (k)", "value": _rank},
                {"metric": "raw image bytes (RGB matrix)", "value": _raw_rgb_bytes},
                {"metric": "compressed PCA payload bytes", "value": _pca_npz16_bytes},
                {"metric": "compression ratio (compressed/raw)", "value": round(_pca_ratio, 4)},
                {"metric": "quality (PSNR, dB)", "value": _psnr_display},
            ],
            label="Image compression summary",
        )
        _comparison_note = mo.md(
            "Lower rank keeps fewer principal components, so storage drops but detail also drops.\n\n"
            "Summary compares **raw RGB data** vs **PCA payload**. Preview PNG sizes are not used as compression metrics."
        ).callout(kind="info")
        _pipeline = mo.md(
            """
<div class="section-card flow-card">
  <div class="flow-diagram">
    <div class="flow-box">Reference image matrix</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Keep top-k PCA components</div>
    <div class="flow-arrow">&rarr;</div>
    <div class="flow-box">Reconstructed image</div>
  </div>
</div>
            """
        )

        _output = mo.vstack(
            [_pipeline, _comparison_images, _comparison_table, _comparison_note], gap=0.6
        )

    _output
    return (_output,)


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
                        "size (bytes)": size,
                        "ratio vs JSON": round(size / baseline, 4),
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
                        "size (bytes)": gz_path.stat().st_size,
                        "ratio vs JSON": round(gz_path.stat().st_size / baseline, 4),
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
                            "size (bytes)": parquet_path.stat().st_size,
                            "ratio vs JSON": round(
                                parquet_path.stat().st_size / baseline, 4
                            ),
                        }
                    )

        _table = mo.ui.table(_results, label="Compression ratios (baseline: JSON size)")
        _note = mo.md(
            """
**Discussion:** Columnar + compression reduces I/O, especially for analytics workloads (scan-heavy query patterns).
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
            "value": round(_estimated_ratio, 4),
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
    _transition = mo.md(
        """
### Bridge to Next Chapter

Smaller files help, but analytics runtime is not only about file size.
We also need a query engine that avoids unnecessary work.

$$
\\text{query time} \\approx \\text{I/O time} + \\text{compute time}
$$

DuckDB helps reduce both parts for many analytical workloads (query/data access patterns).
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 5. DuckDB Example (SQL on Files)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter5_guide = mo.md(
        """
### Chapter 5 Introduction

> **Key Question:** How much work can the engine skip (prune: avoid reading/processing) before processing?

DuckDB provides SQL analytics without running a database server.
It helps because query planning decides what data can be skipped early (predicate/projection pruning).

Main idea:

$$
\\text{effective rows processed} = N \\times \\text{selectivity}
$$

Lower selectivity means more benefit from predicate pushdown.
        """
    ).callout(kind="neutral")
    _chapter5_guide
    return (_chapter5_guide,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### DuckDB: SQL on Files, Zero Server

DuckDB is an **embedded analytical database**. It can scan CSV/Parquet files with SQL,
perform vectorized execution, and apply *predicate + projection pushdown*.

Why it often outperforms direct plain-file scans for analytics (lower query runtime):

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
    push_rows = mo.ui.slider(10_000, 5_000_000, step=10_000, value=400_000, label="Rows (N)")
    push_selectivity = mo.ui.slider(
        0.001, 1.0, step=0.001, value=0.08, label="Filter selectivity (fraction kept)"
    )
    push_cols_total = mo.ui.slider(4, 80, value=24, label="Total columns")
    push_cols_needed = mo.ui.slider(1, 24, value=5, label="Columns used by query")
    _push_note = mo.md(
        "Selectivity 0.08 means about 8% of rows pass the filter."
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Pushdown Intuition"),
            mo.hstack([push_rows, push_selectivity], widths="equal"),
            mo.hstack([push_cols_total, push_cols_needed], widths="equal"),
            _push_note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return push_cols_needed, push_cols_total, push_rows, push_selectivity


@app.cell
def _(mo, push_cols_needed, push_cols_total, push_rows, push_selectivity):
    total_cols = push_cols_total.value
    needed_cols = min(push_cols_needed.value, total_cols)
    rows = push_rows.value
    sel = push_selectivity.value

    no_push = rows * total_cols
    with_push = rows * sel * needed_cols
    gain = no_push / max(with_push, 1)

    _table = mo.ui.table(
        [
            {"metric": "work without pushdown", "value": int(no_push)},
            {"metric": "work with pushdown", "value": int(with_push)},
            {"metric": "estimated reduction factor", "value": round(gain, 2)},
        ],
        label="Predicate + projection pushdown estimate",
    )
    _panel = mo.vstack(
        [_table, mo.md("Higher reduction factors usually mean larger query speedups.").callout(kind="info")],
        gap=0.6,
    )
    _panel
    return (_panel,)


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
                    {"file": "orders.csv", "size (bytes)": _csv_path.stat().st_size},
                    {"file": "analytics.duckdb", "size (bytes)": _db_path.stat().st_size},
                ]
                if _parquet_path:
                    _sizes.append(
                        {"file": "orders.parquet", "size (bytes)": _parquet_path.stat().st_size}
                    )

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
                {"mode": "full scan", "query_ms": round(_scan_time * 1000, 3)},
                {"mode": "indexed", "query_ms": round(_idx_time * 1000, 3)},
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

        _speedup = (_scan_time / _idx_time) if _idx_time else None
        _speedup_note = mo.md(
            f"Observed speedup: **{_speedup:.2f}x**" if _speedup else "Observed speedup: **n/a**"
        ).callout(kind="info")
        _note = mo.md(
            "Look for the plan to switch from **SCAN** to **SEARCH** when the index is present."
        ).callout(kind="info")

        _output = mo.vstack(
            [_timing_table, _plan_table, _result_table, _speedup_note, _note],
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
DuckDB can **infer** types when reading files (schema‑on‑read), or **enforce** types
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
            _clean_rows = [row for row in _rows if not isinstance(row["amount"], str)]
            _sample_size = 12
            _sample_dirty = []
            _sample_clean = []
            if _dirty_rows:
                _target_dirty = min(len(_dirty_rows), max(1, _sample_size // 2))
                _sample_dirty = _rng.sample(_dirty_rows, _target_dirty)
            if _clean_rows:
                _target_clean = _sample_size - len(_sample_dirty)
                if _target_clean == 0:
                    _target_clean = 1
                    _sample_dirty = _sample_dirty[: max(1, _sample_size - 1)]
                _sample_clean = _rng.sample(
                    _clean_rows, min(len(_clean_rows), _target_clean)
                )

            _sample_source = sorted(
                _sample_dirty + _sample_clean, key=lambda row: row["id"]
            )
            if not _sample_source:
                _sample_source = _rows[:_sample_size]

            _sample_rows = [
                {
                    "id": row["id"],
                    "category": row["category"],
                    "amount": row["amount"],
                    "dirty": isinstance(row["amount"], str),
                    "day": row["day"],
                }
                for row in _sample_source
            ]

            def _render_sample_table(rows):
                header = """
<thead>
  <tr>
    <th>id</th>
    <th>category</th>
    <th>amount</th>
    <th>dirty</th>
    <th>day</th>
  </tr>
</thead>
                """
                body_rows = []
                for row in rows:
                    dirty = bool(row["dirty"])
                    cls = "dirty-row" if dirty else ""
                    amount_cell = f'<td class="dirty-cell">{row["amount"]}</td>' if dirty else f"<td>{row['amount']}</td>"
                    body_rows.append(
                        f"""
  <tr class="{cls}">
    <td>{row["id"]}</td>
    <td>{row["category"]}</td>
    {amount_cell}
    <td>{str(row["dirty"]).lower()}</td>
    <td>{row["day"]}</td>
  </tr>
                        """
                    )
                body = "<tbody>" + "".join(body_rows) + "</tbody>"
                return mo.Html(
                    f"""
<div class="section-card">
  <h3>Sample rows (dirty values highlighted)</h3>
  <table>
    {header}
    {body}
  </table>
  <div class="chart-note">Rows with non-numeric amounts are shaded.</div>
</div>
                    """
                )

            _sample_table = _render_sample_table(_sample_rows)

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
                    {
                        "rows": schema_rows.value,
                        "dirty_rows": _dirty_count,
                        "dirty_rate_pct": round(_dirty_pct, 2),
                        "inferred_non_numeric": _inferred_bad,
                        "explicit_nulls": _explicit_nulls,
                        "avg_amount_try_cast": round(_num_avg, 3)
                        if _num_avg is not None
                        else None,
                    }
                ],
                label="Why schema choice matters (numeric)",
            )
            _types_table = mo.ui.table(
                [
                    {
                        "amount_inferred_type": _inferred_amount_type,
                        "lexicographic_min_amount": str(_lex_min),
                    }
                ],
                label="Schema observations (text)",
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
                    _types_table,
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
    <summary><strong>Q1:</strong> When is loading data into DuckDB better than scanning files each time?</summary>
    <p><strong>Answer:</strong> If the same queries or joins run repeatedly, loading once avoids repeated parsing and enables columnar optimizations (materialization = storing structured intermediate data for reuse).</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> What risk appears with schema‑on‑read?</summary>
    <p><strong>Answer:</strong> Bad types can slip through; errors show up later as `NULL`s or wrong totals (schema‑on‑read).</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> How can data drift be detected over time?</summary>
    <p><strong>Answer:</strong> Track inferred types, null rates, and value distributions; alert when they change (data drift = statistical change in incoming data over time).</p>
  </details>
</div>
        """
    )
    _qa_block_duckdb
    return (_qa_block_duckdb,)


@app.cell
def _(mo):
    _conclusion_duckdb = mo.md(
        """
<div class="section-card">
  <h3>Chapter 5 Conclusion</h3>
  <ul>
    <li>DuckDB gives SQL analytics directly on files with strong performance for scans and aggregates.</li>
    <li>Schema-on-write catches type issues earlier; schema-on-read is flexible but riskier.</li>
    <li>Track null rates and inferred types over time to detect data quality drift (distribution/type changes in incoming data).</li>
  </ul>
</div>
        """
    ).callout(kind="success")
    _conclusion_duckdb
    return (_conclusion_duckdb,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

So far, we worked locally with files and SQL.
Now we expose data to other programs through APIs.

API exchange model:
- request = client-sent input message
- response = server-returned output message

$$
\\text{API latency} = \\text{network} + \\text{server processing}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 6. REST API Demo (GET, POST, PUT, DELETE)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter6_guide = mo.md(
        """
### Chapter 6 Introduction

> **Key Question:** Did the client and server agree on the same contract?

An API is a contract between systems.
Most API bugs are contract mismatches (interface mismatches): wrong path, wrong payload shape, or wrong status handling.

Keep this mapping in mind:

- 2xx: success
- 4xx: client-side issue
- 5xx: server-side issue

Status family is computed from the code:

$$
\\text{family} = \\left\\lfloor \\frac{\\text{status code}}{100} \\right\\rfloor
$$
        """
    ).callout(kind="neutral")
    _chapter6_guide
    return (_chapter6_guide,)


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
    http_code = mo.ui.number(value=201, label="HTTP status code")
    http_method_hint = mo.ui.dropdown(
        options=["GET", "POST", "PUT", "DELETE"],
        value="POST",
        label="Method context",
    )
    _note = mo.md(
        """
Try `200`, `201`, `404`, `409`, and `500` to see how client behavior should change.

$$
\\text{status family} = \\left\\lfloor \\frac{\\text{code}}{100} \\right\\rfloor
$$
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [mo.md("### Mini-lab: HTTP Status Interpreter"), http_code, http_method_hint, _note],
        gap=0.5,
    ).callout(kind="neutral")
    _panel
    return http_code, http_method_hint


@app.cell
def _(http_code, http_method_hint, mo):
    code = int(http_code.value or 0)
    if 100 <= code < 200:
        family = "Informational"
        kind = "info"
    elif 200 <= code < 300:
        family = "Success"
        kind = "success"
    elif 300 <= code < 400:
        family = "Redirection"
        kind = "info"
    elif 400 <= code < 500:
        family = "Client error"
        kind = "warn"
    elif 500 <= code < 600:
        family = "Server error"
        kind = "danger"
    else:
        family = "Invalid/unknown"
        kind = "warn"

    retry_note = (
        "Safe retries are easiest for idempotent methods like GET/PUT/DELETE."
        if http_method_hint.value in {"GET", "PUT", "DELETE"}
        else "POST may create duplicates unless idempotency keys are used."
    )
    _msg = mo.md(
        f"Status **{code}** belongs to **{family}**.\n\n{retry_note}"
    ).callout(kind=kind)
    _msg
    return (_msg,)


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
    <summary><strong>Q1:</strong> When is a POST safe to retry?</summary>
    <p><strong>Answer:</strong> If repeating it produces the same result (e.g., client supplies a unique ID), then it’s idempotent.
    This prevents duplicate records on retries.</p>
  </details>
  <details>
    <summary><strong>Q2:</strong> Where should validation happen: client, server, or both?</summary>
    <p><strong>Answer:</strong> Both. Clients give fast feedback, but servers must enforce rules to protect data (server‑side validation).</p>
  </details>
  <details>
    <summary><strong>Q3:</strong> How can an API evolve without breaking clients?</summary>
    <p><strong>Answer:</strong> Add optional fields, version endpoints when needed, and deprecate slowly with clear timelines (backward compatibility).</p>
  </details>
</div>
        """
    )
    _qa_block_api
    return (_qa_block_api,)


@app.cell
def _(mo):
    _conclusion_api = mo.md(
        """
<div class="section-card">
  <h3>Chapter 6 Conclusion</h3>
  <ul>
    <li>Use HTTP method semantics intentionally (GET/POST/PUT/DELETE) and design for retries.</li>
    <li>Validation belongs on both client and server, with server validation as the final guard.</li>
    <li>Backward-compatible evolution and explicit versioning reduce integration breakage.</li>
  </ul>
</div>
        """
    ).callout(kind="success")
    _conclusion_api
    return (_conclusion_api,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

APIs fail when input data shape is wrong.
Pydantic acts as an input-validation checkpoint: required fields and types are checked before business logic runs.

$$
\\text{valid request} \\Rightarrow \\text{schema checks pass}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 7. Pydantic Models")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter7_guide = mo.md(
        """
### Chapter 7 Introduction

> **Key Question:** Which inputs are allowed into the trusted system boundary?

Validation is the system's input acceptance policy (formal schema enforcement rules).
With early validation, downstream code becomes simpler and safer.

Formal model:

$$
\\text{trusted internal data} = \\text{untrusted input} + \\text{validation rules}
$$
        """
    ).callout(kind="neutral")
    _chapter7_guide
    return (_chapter7_guide,)


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

Where:
- $gpa$: grade-point average score constrained to the valid range

Try editing the JSON below to trigger validation errors and see the message structure.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    req_id = mo.ui.switch(value=True, label="Require id")
    req_name = mo.ui.switch(value=True, label="Require name")
    req_email = mo.ui.switch(value=True, label="Require email")
    req_gpa = mo.ui.switch(value=True, label="Require gpa in [0,4]")
    _note = mo.md(
        "Turn rules on/off to see how stricter schemas reject more malformed input."
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Validation Rule Builder"),
            mo.hstack([req_id, req_name], widths="equal"),
            mo.hstack([req_email, req_gpa], widths="equal"),
            _note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return req_email, req_gpa, req_id, req_name


@app.cell
def _(mo, req_email, req_gpa, req_id, req_name):
    checks = [
        ("id present", req_id.value),
        ("name present", req_name.value),
        ("email present", req_email.value),
        ("gpa bounded", req_gpa.value),
    ]
    strictness = sum(1 for _, ok in checks if ok)
    _table = mo.ui.table(
        [{"rule": name, "enabled": ok} for name, ok in checks],
        label="Active schema rules",
    )
    _msg = mo.md(
        f"Current strictness score: **{strictness}/4**. "
        "Higher strictness catches more bad input, but can reject more requests."
    ).callout(kind="info")
    _panel = mo.vstack([_table, _msg], gap=0.6)
    _panel
    return (_panel,)


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
    _transition = mo.md(
        """
### Bridge to Next Chapter

Once models are defined, FastAPI can use them to:
- validate inputs,
- power endpoints,
- generate docs automatically.

$$
\\text{Python types + models} \\rightarrow \\text{OpenAPI schema} \\rightarrow \\text{interactive docs}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 8. FastAPI Demo + Automatic Docs")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter8_guide = mo.md(
        """
### Chapter 8 Introduction

> **Key Question:** How do we keep implementation and API documentation in sync?

FastAPI turns validated models into executable API endpoints plus shared docs.
This reduces mismatch between implementation and documentation.

Lifecycle:

1. Define model
2. Attach model to endpoint
3. FastAPI emits OpenAPI
4. Tools consume docs automatically

$$
\\text{Type Hints} + \\text{Validation Models} \\rightarrow \\text{Machine-readable API contract}
$$
        """
    ).callout(kind="neutral")
    _chapter8_guide
    return (_chapter8_guide,)


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
# file: sw03_demo_api.py
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Sales Analysis API", version="2.0.0")

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=300)
    category_id: int = Field(ge=1)

@app.get("/products/{product_id}")
def get_product(product_id: int):
    # simplified snippet: full implementation is in sw03_demo_api.py
    ...

@app.post("/products", status_code=201)
def create_product(payload: ProductCreate):
    ...
```

This repo includes the full implementation in `sw03_demo_api.py`.

Run from the project root with:

```
uvicorn sw03_demo_api:app --reload
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
   uvicorn sw03_demo_api:app --reload
   ```

2. Click **1) Check API status** to verify the server is reachable.  
3. Edit the JSON payload and click **2) POST /products**.  
4. Choose a product id and click **3) GET /products/{id}** to compare results.
        """
    ).callout(kind="info")
    _workflow
    return (_workflow,)


@app.cell
def _(mo):
    fa_network_ms = mo.ui.slider(5, 300, value=40, label="Network latency (ms)")
    fa_validation_ms = mo.ui.slider(1, 100, value=8, label="Validation cost (ms)")
    fa_logic_ms = mo.ui.slider(1, 500, value=25, label="Business logic (ms)")
    _note = mo.md(
        """
Change one component at a time to see which part dominates end-to-end latency.

$$
T_{endpoint} \\approx T_{network} + T_{validation} + T_{logic}
$$
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Endpoint Latency Budget"),
            mo.hstack([fa_network_ms, fa_validation_ms], widths="equal"),
            fa_logic_ms,
            _note,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return fa_logic_ms, fa_network_ms, fa_validation_ms


@app.cell
def _(fa_logic_ms, fa_network_ms, fa_validation_ms, mo):
    total = fa_network_ms.value + fa_validation_ms.value + fa_logic_ms.value
    _table = mo.ui.table(
        [
            {"component": "network", "ms": fa_network_ms.value},
            {"component": "validation", "ms": fa_validation_ms.value},
            {"component": "logic", "ms": fa_logic_ms.value},
            {"component": "total", "ms": total},
        ],
        label="Estimated latency budget",
    )
    _msg = mo.md("Use this to decide whether to optimize code, validation, or infrastructure first.").callout(
        kind="info"
    )
    _panel = mo.vstack([_table, _msg], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    fastapi_base_url = mo.ui.text(value="http://127.0.0.1:8000", label="API base URL")
    fastapi_check = mo.ui.button(label="1) Check API status", kind="neutral")
    fastapi_payload = mo.ui.text_area(
        value='{"name": "Notebook Pro", "price": 99.9, "description": "Lecture demo product", "category_id": 1}',
        label="POST /products payload (JSON)",
    )
    fastapi_post = mo.ui.button(label="2) POST /products", kind="success")
    fastapi_item_id = mo.ui.text(value="1", label="Product id for GET /products/{id}")
    fastapi_get = mo.ui.button(label="3) GET /products/{id}", kind="neutral")

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
    _output = mo.md("Waiting for API status check...").callout(kind="neutral")
    if fastapi_check.value == 0:
        _output = mo.md(
            "Click **1) Check API status** after starting `uvicorn sw03_demo_api:app --reload`."
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
    _output = mo.md("Waiting for POST request...").callout(kind="neutral")
    if fastapi_post.value == 0:
        _output = mo.md(
            "Edit the payload, then click **2) POST /products**."
        ).callout(kind="neutral")
    else:
        _url = fastapi_base_url.value.rstrip("/") + "/products"
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

            _status = None
            _body = ""
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
            if _status is not None:
                try:
                    _parsed = json.loads(_body)
                    _preview = json.dumps(_parsed, indent=2)
                except json.JSONDecodeError:
                    _preview = _body

                _output = mo.md(
                    f"""
`POST /products` returned status `{_status}`.

```json
{_preview}
```
                    """
                ).callout(kind="success" if _status < 400 else "danger")

    _output
    return (_output,)


@app.cell
def _(fastapi_base_url, fastapi_get, fastapi_item_id, json, mo, url_error, url_request):
    _output = mo.md("Waiting for GET request...").callout(kind="neutral")
    if fastapi_get.value == 0:
        _output = mo.md("Click **3) GET /products/{id}** to fetch a product.").callout(
            kind="neutral"
        )
    else:
        try:
            _item_id = int(fastapi_item_id.value.strip())
        except ValueError:
            _output = mo.md("Product id must be an integer.").callout(kind="danger")
        else:
            _url = fastapi_base_url.value.rstrip("/") + f"/products/{_item_id}"
            _request = url_request.Request(_url, headers={"Accept": "application/json"}, method="GET")
            _status = None
            _body = ""
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
            if _status is not None:
                try:
                    _parsed = json.loads(_body)
                    _preview = json.dumps(_parsed, indent=2)
                except json.JSONDecodeError:
                    _preview = _body

                _output = mo.md(
                    f"""
`GET /products/{_item_id}` returned status `{_status}`.

```json
{_preview}
```
                    """
                ).callout(kind="success" if _status < 400 else "danger")

    _output
    return (_output,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

Backend answers are useful, but users still need a clear interface.
Now we compare frontend options and their trade-offs (explicit compromises between speed, control, and complexity).

$$
\\text{user value} = \\text{backend correctness} \\times \\text{frontend usability}
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 9. Frontend Framework Comparison")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter9_guide = mo.md(
        """
### Chapter 9 Introduction

> **Key Question:** Which frontend maximizes delivery speed without exceeding complexity?

Framework choice is a product decision, not only a technical preference.
Pick the tool that best matches team skill and delivery constraints.

Common axes:
- speed of iteration
- UI control depth
- long-term maintainability

Heuristic framing:

$$
\\text{fit score} = w_s \\cdot \\text{speed} + w_c \\cdot \\text{control} + w_j \\cdot \\text{team JS readiness}
$$
        """
    ).callout(kind="neutral")
    _chapter9_guide
    return (_chapter9_guide,)


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

Think in terms of trade‑offs (explicit engineering compromises): speed vs. control, Python‑native vs. JS ecosystems, and expected scale.

A simple framing:

$$
\\text{Iteration Speed} \\uparrow \\quad \\Rightarrow \\quad \\text{UI Control} \\downarrow
$$

Interpretation:
- faster iteration often comes with less low-level UI control; more control usually needs more engineering effort
        """
    ).callout(kind="neutral")

    _framework_table = mo.ui.table(framework_rows, label="Framework comparison")
    _panel = mo.vstack([_framework_note, _framework_table], gap=0.6)
    _panel
    return (_panel,)


@app.cell
def _(mo):
    fw_speed = mo.ui.slider(1, 5, value=5, label="Need fast iteration")
    fw_control = mo.ui.slider(1, 5, value=3, label="Need fine UI control")
    fw_js = mo.ui.slider(1, 5, value=2, label="Team JavaScript strength")
    _note = mo.md(
        """
Higher scores are teaching heuristics only. Validate against real team constraints.

$$
\\text{fit} = w_s s + w_c c + w_j j
$$
        """
    ).callout(kind="info")
    _panel = mo.vstack(
        [mo.md("### Mini-lab: Framework Fit Assistant"), fw_speed, fw_control, fw_js, _note],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return fw_control, fw_js, fw_speed


@app.cell
def _(fw_control, fw_js, fw_speed, mo):
    # Simple weighted scoring for teaching, not a strict recommendation engine.
    _framework_scores = {
        "Marimo": fw_speed.value * 1.2 + (6 - fw_js.value) * 0.8 + fw_control.value * 0.6,
        "Streamlit": fw_speed.value * 1.3 + (6 - fw_js.value) * 0.7 + fw_control.value * 0.5,
        "Dash": fw_speed.value * 0.9 + fw_js.value * 0.4 + fw_control.value * 0.8,
        "Flask": fw_speed.value * 0.6 + fw_js.value * 0.5 + fw_control.value * 1.2,
        "React": fw_speed.value * 0.5 + fw_js.value * 1.4 + fw_control.value * 1.3,
    }
    _ranked_frameworks = sorted(
        _framework_scores.items(), key=lambda x: x[1], reverse=True
    )
    _fit_table = mo.ui.table(
        [{"framework": name, "score": round(score, 2)} for name, score in _ranked_frameworks],
        label="Teaching score (higher = better fit)",
    )
    _fit_message = mo.md(
        f"Current top fit: **{_ranked_frameworks[0][0]}**"
    ).callout(kind="info")
    _fit_panel = mo.vstack([_fit_table, _fit_message], gap=0.6)
    _fit_panel
    return (_fit_panel,)


@app.cell
def _(mo):
    _transition = mo.md(
        """
### Bridge to Next Chapter

Tables show exact values; charts show patterns faster.
We close with visual analysis so trends and relationships are easier to explain.

A key model we will visualize:

$$
y = \\alpha + \\beta x
$$
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


@app.cell
def _(mo):
    _section = mo.md("## 10. Marimo Charts Lab")
    _section
    return (_section,)


@app.cell
def _(mo):
    _chapter10_guide = mo.md(
        """
### Chapter 10 Introduction

> **Key Question:** Which pattern is signal, and which is noise?

Charts help humans detect patterns quickly.
Regression summarizes trend direction with two numbers:

$$
y = \\alpha + \\beta x
$$

- $\\alpha$: baseline level
- $\\beta$: change in y for one unit change in x
        """
    ).callout(kind="neutral")
    _chapter10_guide
    return (_chapter10_guide,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Marimo Charts Lab

Use the controls below to generate a dataset and explore it with:

- **XY scatter + linear regression** (equation updates automatically)  
- **2D scatter by category** (four colors)  
- **Two trend lines** to compare upward trajectories

We also compute summary statistics to make the patterns quantitative.
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    reg_alpha = mo.ui.slider(-5.0, 5.0, step=0.1, value=0.5, label="Intercept (alpha)")
    reg_beta = mo.ui.slider(-4.0, 4.0, step=0.1, value=1.4, label="Slope (beta)")
    reg_x = mo.ui.slider(-10.0, 10.0, step=0.5, value=2.0, label="Input x")
    _panel = mo.vstack(
        [mo.md("### Mini-lab: Regression Predictor"), reg_alpha, reg_beta, reg_x],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return reg_alpha, reg_beta, reg_x


@app.cell
def _(mo, reg_alpha, reg_beta, reg_x):
    _y_hat = reg_alpha.value + reg_beta.value * reg_x.value
    _regression_table = mo.ui.table(
        [
            {"symbol": "alpha", "value": reg_alpha.value},
            {"symbol": "beta", "value": reg_beta.value},
            {"symbol": "x", "value": reg_x.value},
            {"symbol": "predicted y", "value": round(_y_hat, 4)},
        ],
        label="Linear prediction snapshot",
    )
    _regression_note = mo.md(
        "Adjust beta and observe how quickly y changes. "
        "Large |beta| means stronger trend sensitivity."
    ).callout(kind="info")
    _regression_panel = mo.vstack([_regression_table, _regression_note], gap=0.6)
    _regression_panel
    return (_regression_panel,)


@app.cell
def _(mo):
    chart_rows = mo.ui.slider(100, 1000, step=100, value=600, label="Rows (max 1000)")
    chart_seed = mo.ui.slider(1, 999, value=21, label="Seed")
    chart_slope = mo.ui.slider(-3.0, 3.0, step=0.2, value=1.2, label="Trend slope")
    chart_noise = mo.ui.slider(0.2, 5.0, step=0.2, value=1.4, label="Noise level")

    _controls = mo.vstack(
        [
            mo.hstack([chart_rows, chart_seed], widths="equal"),
            mo.hstack([chart_slope, chart_noise], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return chart_noise, chart_rows, chart_seed, chart_slope


@app.cell
def _(
    chart_noise,
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
            {
                "metric": k,
                "x": round(_stats_x[k], 3),
                "y": round(_stats_y[k], 3),
            }
            for k in _stats_x.keys()
        ],
        label="Summary statistics (x, y)",
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

        _scatter = _alt.Chart(_df).mark_circle(size=60, opacity=0.6, color="#2f6fed").encode(
            x=_alt.X("x:Q"),
            y=_alt.Y("y:Q"),
            tooltip=[
                _alt.Tooltip("x:Q"),
                _alt.Tooltip("y:Q"),
            ],
        )
        _scatter_layers = _scatter
        _formula = None
        _lr = _linear_regression(_x_vals, _y_vals)
        if _lr:
            _beta, _alpha = _lr[0], _lr[1]
            _x_min = min(_x_vals)
            _x_max = max(_x_vals)
            _reg_df = _pd.DataFrame(
                {
                    "x": [_x_min, _x_max],
                    "y": [_beta * _x_min + _alpha, _beta * _x_max + _alpha],
                }
            )
            _reg_line = _alt.Chart(_reg_df).mark_line(color="#1f2937").encode(
                x=_alt.X("x:Q"), y=_alt.Y("y:Q")
            )
            _scatter_layers = _scatter + _reg_line
            _formula = mo.md(
                f"Regression: **y = {_alpha:.3f} + {_beta:.3f} x**  \n"
                f"$\\alpha$ (intercept) = ${_alpha:.3f}$, $\\beta$ (slope) = ${_beta:.3f}$"
            ).callout(kind="info")
        else:
            _formula = mo.md("Regression could not be computed for this sample.").callout(
                kind="warn"
            )

        _scatter_chart = mo.ui.altair_chart(_scatter_layers.properties(height=280))

        _scatter_cat = (
            _alt.Chart(_df)
            .mark_circle(opacity=0.6)
            .encode(
                x=_alt.X("x:Q"),
                y=_alt.Y("y:Q"),
                color=_alt.Color("category:N"),
                tooltip=[
                    _alt.Tooltip("x:Q"),
                    _alt.Tooltip("y:Q"),
                    _alt.Tooltip("category:N"),
                ],
            )
            .properties(height=280)
        )
        _scatter_cat_chart = mo.ui.altair_chart(_scatter_cat)

        _line_len = min(chart_rows.value, 200)
        _line_rows = []
        _base_slope = abs(chart_slope.value) * 0.05 + 0.02
        _slope_a = _base_slope
        _slope_b = _base_slope + 0.015
        _noise_scale = chart_noise.value * 0.2
        for _i in range(_line_len):
            _line_rows.append(
                {
                    "idx": _i,
                    "series": "Trend A",
                    "y": _slope_a * _i + _rng.gauss(0, _noise_scale),
                }
            )
            _line_rows.append(
                {
                    "idx": _i,
                    "series": "Trend B",
                    "y": _slope_b * _i + 0.6 + _rng.gauss(0, _noise_scale),
                }
            )

        _line_df = _pd.DataFrame(_line_rows)
        _line_chart = mo.ui.altair_chart(
            _alt.Chart(_line_df)
            .mark_line(opacity=0.8)
            .encode(
                x=_alt.X("idx:Q", title="index"),
                y=_alt.Y("y:Q", title="value"),
                color=_alt.Color("series:N"),
                tooltip=[
                    _alt.Tooltip("idx:Q"),
                    _alt.Tooltip("y:Q"),
                    _alt.Tooltip("series:N"),
                ],
            )
            .properties(height=260)
        )

        _panel = mo.vstack(
            [
                _formula,
                mo.md("#### XY scatter + regression"),
                _scatter_chart,
                mo.md("#### 2D scatter by category"),
                _scatter_cat_chart,
                mo.md("#### Two upward trends"),
                _line_chart,
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
    _transition = mo.md(
        """
### Wrap-up

The notebook covered one full data-product workflow sequence (ordered implementation stages):

1. Keep writes correct under concurrency
2. Choose efficient serialization formats
3. Use columnar layout and compression for analytics
4. Query files with DuckDB
5. Expose data through REST APIs
6. Validate contracts with Pydantic and FastAPI
7. Present results in frontends and charts

If students remember one thing: correctness first, then performance, then usability.
        """
    ).callout(kind="neutral")
    _transition
    return (_transition,)


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
