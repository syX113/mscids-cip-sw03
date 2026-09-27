import marimo

__generated_with = "0.25.0"
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
    import urllib.request as url_request
    from pathlib import Path

    import altair as alt
    import duckdb
    import fastavro
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pydantic
    import requests
    from PIL import Image, ImageDraw
    from pyarrow import feather

    return (
        Image,
        ImageDraw,
        Path,
        alt,
        csv,
        duckdb,
        fastavro,
        feather,
        gzip,
        io,
        json,
        math,
        mo,
        np,
        os,
        pa,
        pd,
        pickle,
        pq,
        pydantic,
        random,
        requests,
        sqlite3,
        statistics,
        tempfile,
        threading,
        time,
        url_error,
        url_request,
    )


@app.cell
def _(Path, mo):
    # Real sales rows (data/seed/) that several labs below read.
    SEED_DIR = Path(mo.notebook_dir()) / "data" / "seed"
    SALES_SEED = SEED_DIR / "sales.parquet"
    return SALES_SEED, SEED_DIR


@app.cell
def _(requests):
    def format_bytes(num_bytes):
        """Human-friendly byte counts."""
        value = float(num_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if value < 1024:
                return f"{value:,.2f} {unit}"
            value /= 1024
        return f"{value:,.2f} TB"

    def format_ms(seconds):
        return f"{seconds * 1000:,.2f} ms"

    def call_api(method: str, url: str, body: dict | None = None) -> tuple[int, object]:
        """One HTTP request -> (status code, parsed JSON or raw text).

        Network failures raise requests.RequestException, so a caller can say "start the API".
        """
        response = requests.request(method, url, json=body, timeout=5)
        try:
            return response.status_code, response.json()
        except requests.JSONDecodeError:
            return response.status_code, response.text

    return call_api, format_bytes, format_ms


@app.cell
def _(mo):
    mo.Html(
        """
        <style>
          /* One palette for both marimo themes: marimo sets color-scheme: dark on its dark
             theme, and light-dark() picks the matching value. Names avoid marimo's own
             variables (--accent, --border, --muted, ...), which its UI depends on. */
          :root {
            /* marimo's layout width, widened for the projector */
            --content-width: min(80vw, 1150px);
            --content-width-medium: min(80vw, 1150px);

            --ink: light-dark(#0b1220, #e8edf4);
            --ink-soft: light-dark(#2b3a55, #c5cfdc);
            --ink-muted: light-dark(#56657c, #98a4b5);
            --line: light-dark(rgb(11 18 32 / 0.12), rgb(255 255 255 / 0.12));
            --surface: light-dark(#ffffff, #1f2423);
            --surface-2: light-dark(#f4f7fb, #282d2c);
            --brand: light-dark(#2f6fed, #86abff);
            --teal: light-dark(#0f9488, #3fd0bd);
            --amber: light-dark(#d97706, #f5b43c);
            --red: light-dark(#b42318, #ff9b8f);
            /* short on purpose: each marimo cell paints over the one above it */
            --shadow: 0 1px 2px light-dark(rgb(15 23 42 / 0.06), rgb(0 0 0 / 0.3)),
              0 4px 10px light-dark(rgb(15 23 42 / 0.05), rgb(0 0 0 / 0.2));
          }

          .markdown h2 {
            margin-top: 2.2rem;
            padding-bottom: 0.35rem;
            background: linear-gradient(90deg, var(--brand), var(--teal)) left bottom / 100% 3px no-repeat;
          }

          .section-card {
            padding: 18px 20px;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: var(--surface);
            box-shadow: var(--shadow);
          }

          .section-card :is(h2, h3) {
            margin-top: 0;
          }

          .hero {
            padding: 28px;
            border: 1px solid color-mix(in srgb, var(--brand) 25%, transparent);
            border-radius: 22px;
            background:
              radial-gradient(circle at 18% 18%, color-mix(in srgb, var(--brand) 24%, transparent), transparent 48%),
              linear-gradient(
                120deg,
                color-mix(in srgb, var(--brand) 12%, var(--surface)),
                color-mix(in srgb, var(--teal) 10%, var(--surface)),
                color-mix(in srgb, var(--amber) 10%, var(--surface))
              );
            box-shadow: var(--shadow);
          }

          .eyebrow {
            display: inline-flex;
            padding: 6px 12px;
            border-radius: 999px;
            background: color-mix(in srgb, var(--brand) 16%, transparent);
            color: var(--brand);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }

          .hero-title {
            margin: 14px 0 10px;
            color: var(--ink);
            font-family: var(--heading-font);
            font-size: 2.6rem;
            font-weight: 700;
            line-height: 1.1;
          }

          .hero-subtitle {
            max-width: 860px;
            color: var(--ink-soft);
            font-size: 1.05rem;
            line-height: 1.6;
          }

          .hero-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
          }

          .pill {
            padding: 6px 12px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: color-mix(in srgb, var(--surface) 75%, transparent);
            color: var(--ink-soft);
            font-size: 13px;
          }

          .grid-2 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
          }

          .focus-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 10px;
            margin-top: 10px;
          }

          .focus-item {
            padding: 10px 12px;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: var(--surface-2);
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
            min-width: 150px;
            padding: 10px 14px;
            border: 1px solid var(--line);
            border-radius: 14px;
            background: var(--surface-2);
            color: var(--ink);
            font-weight: 600;
            text-align: center;
          }

          .flow-arrow {
            color: var(--ink-muted);
            font-size: 1.4rem;
            line-height: 1;
          }

          .flow-note,
          .chart-note {
            color: var(--ink-muted);
            font-size: 0.9rem;
          }

          .lost-update-wrap {
            overflow-x: auto;
          }

          .lost-update-grid {
            display: grid;
            grid-template-columns: 90px repeat(3, minmax(180px, 1fr));
            min-width: 760px;
            border: 1px solid var(--line);
            border-radius: 14px;
            overflow: hidden;
            background: var(--surface);
          }

          .lu-header,
          .lu-step,
          .lu-event,
          .lu-state {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            border-right: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
            color: var(--ink);
            font-weight: 600;
          }

          .lu-header {
            font-weight: 700;
            background: color-mix(in srgb, var(--brand) 14%, transparent);
          }

          .lu-step {
            justify-content: center;
            font-weight: 700;
            background: var(--surface-2);
          }

          .lu-state {
            font-weight: 700;
          }

          .lu-read {
            background: color-mix(in srgb, var(--teal) 15%, transparent);
          }

          .lu-write {
            background: color-mix(in srgb, var(--amber) 18%, transparent);
          }

          .lu-idle {
            color: var(--ink-muted);
            background: var(--surface-2);
            font-weight: 500;
          }

          .lu-stale,
          .lu-problem {
            color: var(--red);
            background: color-mix(in srgb, var(--red) 13%, transparent);
            font-weight: 700;
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
            color: var(--ink);
            font-weight: 600;
          }

          .bar-track {
            height: 10px;
            border-radius: 999px;
            overflow: hidden;
            background: color-mix(in srgb, var(--ink) 12%, transparent);
          }

          .bar-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--brand), var(--teal));
          }

          .bar-fill.good {
            background: linear-gradient(90deg, var(--teal), var(--brand));
          }

          .bar-fill.bad {
            background: linear-gradient(90deg, #f97316, #ef4444);
          }

          .bar-value {
            color: var(--ink-soft);
            font-variant-numeric: tabular-nums;
            text-align: right;
          }

          .disclaimer-red {
            padding: 12px 14px;
            border: 1px solid color-mix(in srgb, var(--red) 55%, transparent);
            border-radius: 14px;
            background: color-mix(in srgb, var(--red) 13%, transparent);
            color: var(--red);
            font-weight: 600;
          }
        </style>
        """
    )
    return


@app.cell
def _(mo):
    _title = mo.md(
        """
    <div class="hero">
      <div class="hero-content">
        <div class="eyebrow">CIP - SW03 Lecture Studio</div>
        <div class="hero-title">Storage, Serialization, APIs & Apps</div>
        <div class="hero-subtitle">
          One data product, built in <strong>three tiers</strong>: where the data rests,
          what serves it, and what people look at. We build each tier in turn and stack
          them &mdash; race conditions, serialization trade&#8209;offs, columnar analytics,
          API design, and rapid app prototyping.
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
    _title
    return


@app.cell
def _(mo):
    _agenda = mo.md(
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
    _agenda
    return


@app.cell
def _(mo):
    _tier_map = mo.md(
        """
    <div class="section-card flow-card">
      <h3>The Map: One Product, Three Tiers</h3>
      <p>
        Almost every data application is split into three layers, called <strong>tiers</strong>.
        Each tier only talks to its neighbour, so any one of them can be replaced without
        rewriting the others. This notebook builds them from the bottom up.
      </p>
      <div class="flow-diagram">
        <div class="flow-box"><strong>Presentation tier</strong><br/>what a person sees<br/><em>chapters 9&ndash;10</em></div>
        <div class="flow-arrow">&rarr;</div>
        <div class="flow-box"><strong>Logic tier</strong><br/>rules and the API<br/><em>chapters 6&ndash;8</em></div>
        <div class="flow-arrow">&rarr;</div>
        <div class="flow-box"><strong>Data tier</strong><br/>where bytes rest<br/><em>chapters 1&ndash;5</em></div>
      </div>
      <div class="grid-2">
        <div>
          <ul>
            <li><strong>Data tier</strong> &mdash; keep writes correct (ch. 1), pick a format (ch. 2),
                choose a layout (ch. 3), shrink it (ch. 4), query it (ch. 5).</li>
            <li><strong>Logic tier</strong> &mdash; agree on a contract (ch. 6), check what comes in
                (ch. 7), serve it over HTTP (ch. 8).</li>
          </ul>
        </div>
        <div>
          <ul>
            <li><strong>Presentation tier</strong> &mdash; choose a frontend (ch. 9),
                show the numbers honestly (ch. 10).</li>
            <li>The arrows point the way a <em>request</em> travels. The answer travels back
                the other way.</li>
          </ul>
        </div>
      </div>
      <div class="flow-note">
        Keep this picture in mind. At the start of every chapter we say which tier we are standing in.
      </div>
    </div>
            """
    )
    _tier_map
    return


@app.cell
def _(mo):
    _legend = mo.md(
        """
    <div class="section-card">
      <h3>How to Read This Notebook</h3>
      <div class="focus-grid">
        <div class="focus-item"><strong>Formulas</strong>: quick quantitative model of the concept.</div>
        <div class="focus-item"><strong>Mini-labs</strong>: interactive controls to test the model.</div>
        <div class="focus-item"><strong>Discussion blocks</strong>: interpretation and trade-offs (explicit design compromises).</div>
      </div>
    </div>
            """
    )
    _legend
    return


@app.cell
def _(mo):
    _section = mo.md("## 1. File Locks vs Databases (ACID)")
    _section
    return


@app.cell
def _(mo):
    _chapter1_guide = mo.md(
        """
    ### Chapter 1 Introduction

    > **Key Question:** When many users update shared data at the same time, do we preserve correctness?

    We are standing in the **data tier**. Databases promise four things, abbreviated **ACID**:

    - **A — Atomicity:** all-or-nothing updates
    - **C — Consistency:** the data obeys its rules before and after every change
    - **I — Isolation:** one write should not corrupt another
    - **D — Durability:** committed data survives crashes

    Practical signal to watch:

    $$
    \\text{lost update rate} = \\frac{E - A}{E}
    $$

    Higher values indicate that concurrent writes are interfering.
            """
    ).callout(kind="neutral")
    _chapter1_guide
    return


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
    return


@app.cell
def _(mo):
    _lost_update_diagram = mo.md(
        """
    <div class="section-card flow-card">
      <h3>Visual: Lost Update Timeline (Who Does What, When)</h3>
      <div class="lost-update-wrap">
        <div class="lost-update-grid">
          <div class="lu-header">Step</div>
          <div class="lu-header">Worker A</div>
          <div class="lu-header">Worker B</div>
          <div class="lu-header">Shared counter</div>

          <div class="lu-step">1</div>
          <div class="lu-event lu-read">reads 41 into local copy</div>
          <div class="lu-event lu-read">reads 41 into local copy</div>
          <div class="lu-state">41</div>

          <div class="lu-step">2</div>
          <div class="lu-event lu-write">writes 42</div>
          <div class="lu-event lu-idle">waiting</div>
          <div class="lu-state">42</div>

          <div class="lu-step">3</div>
          <div class="lu-event lu-idle">done</div>
          <div class="lu-event lu-stale">writes stale 42</div>
          <div class="lu-state lu-problem">42 (A increment overwritten)</div>
        </div>
      </div>
      <div class="flow-note"><strong>Expected after 2 increments: 43.</strong> Observed: 42, so one update was lost.</div>
    </div>
            """
    )
    _lost_update_diagram
    return


@app.cell
def _(mo):
    _lock_metaphor = mo.md(
        """
    ### What a Lock Actually Is

    Four flatmates share one bathroom. **There is no lock on the door.** Instead a single key hangs
    on a hook in the hall, and the house rule is: do not go in unless you are holding the key.
    If everyone follows the rule, nobody is ever walked in on.

    Notice what is doing the work. Not the door, which has no lock and never did. **The agreement**
    is doing the work.

    That is exactly what an operating-system file lock is. The OS hands out one key per file and
    makes everyone else wait at the hook. It does not touch the door. Any program that opens the file
    without reaching for the key walks straight in and overwrites whatever it likes.

    Three things the picture gets right, and one it does not:

    - The OS empties the pockets of anyone who leaves the building, so a program that crashes while
      holding the key does **not** wedge the file forever.
    - There is a second kind of key that many people may hold at once, for looking but not touching.
      The code below asks for the exclusive one, `LOCK_EX`.
    - The hook is in *one* hallway. Two computers sharing a network drive each get their own hook,
      which is why this technique stops working across a network filesystem.
    - **Where it breaks:** the flatmate rule is only as good as the flatmates. A database does not
      rely on an agreement - it refuses to hand out the data in the first place. That is the
      difference you are about to measure.
            """
    ).callout(kind="neutral")
    _lock_metaphor
    return


@app.cell
def _(mo):
    strategies = mo.ui.multiselect(
        options=["no_lock", "thread_lock", "file_lock", "sqlite_naive", "sqlite"],
        value=["no_lock", "file_lock", "sqlite_naive", "sqlite"],
        label="Strategies to run",
    )
    workers = mo.ui.slider(2, 8, value=4, label="Concurrent workers", show_value=True)
    iterations = mo.ui.slider(20, 600, step=20, value=60, label="Increments per worker", show_value=True)
    jitter = mo.ui.slider(0, 5, value=1, step=1, label="Artificial jitter (ms) per update", show_value=True)
    run_race = mo.ui.button(label="Run counter experiment", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _term_note = mo.md(
        """
    **Strategy notes**
    - `no_lock`: plain file writes, race conditions likely (overlapping unsynchronized updates)
    - `thread_lock`: Python lock in one process
    - `file_lock`: OS file lock around write, the key on the hook from the section above
    - `sqlite_naive`: a real database, used the way most people first use one. Read the value,
      add one in Python, write it back.
    - `sqlite`: the same database, one statement, `UPDATE counter SET value = value + 1`,
      inside a transaction

    **Compare the last two rows.** Both are SQLite. The difference is not the database, it is
    whether the read and the write were locked together as one step. A transaction protects the
    steps you actually put inside it, and nothing else.

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
def _(
    Path,
    iterations,
    jitter,
    mo,
    os,
    run_race,
    sqlite3,
    strategies,
    tempfile,
    threading,
    time,
    workers,
):
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

    def _run_sqlite_naive_counter(db_path, iterations, workers):
        """The way most people first use a database: read it, add one in Python, write it back."""
        con = sqlite3.connect(db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("CREATE TABLE counter (value INTEGER NOT NULL)")
        con.execute("INSERT INTO counter VALUES (0)")
        con.commit()
        con.close()

        def worker():
            conn = sqlite3.connect(db_path, timeout=5, isolation_level=None)
            for _ in range(iterations):
                current = conn.execute("SELECT value FROM counter").fetchone()[0]
                conn.execute("UPDATE counter SET value = ?", (current + 1,))
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
        _output = mo.md("Click **Run counter experiment** to simulate concurrent writes.").callout(kind="neutral")
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
                        "strategy": "file (fcntl lock)" if supported else "file (lock unsupported)",
                        "expected": _expected_counter,
                        "actual": value,
                        "lost updates": _expected_counter - value,
                        "duration (ms)": round(_duration * 1000, 2),
                    }
                )

            if "sqlite_naive" in strategies.value:
                value, _duration = _run_sqlite_naive_counter(
                    str(_tmp_path / "counter_naive.db"),
                    iterations.value,
                    workers.value,
                )
                race_rows.append(
                    {
                        "strategy": "sqlite (read, +1 in Python, write)",
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

        _table = mo.ui.table(race_rows, label="Concurrency results", selection=None, pagination=False, show_download=False, show_search=False)
        _summary = mo.md(
            """
    **How to read the table**

    - **No lock**: often lowest wall-clock runtime, but can be incorrect (lost updates).
    - **File lock**: correct here, but at a cost, because writers queue and latency rises.
    - **SQLite, read-modify-write in Python**: a real database, and it still loses updates.
      Watch how close the final value lands to *one* worker's total, as if the others never ran.
    - **SQLite, one statement in a transaction**: correct, because the read and the write are a
      single indivisible step no other writer can interleave with.

    The lost-update counts for the unlocked rows will not repeat between runs. That is the lesson,
    not a flaw: a race has no fixed answer.
                """
        ).callout(kind="info")

        _output = mo.vstack([_table, _summary], gap=0.6)

    _output
    return


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
    return


@app.cell
def _(mo):
    interleave_steps = mo.ui.slider(1, 6, value=2, label="Increments per worker (simulated)", show_value=True)
    interleave_seed = mo.ui.slider(1, 999, value=13, label="Interleaving seed", show_value=True)
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
    _summary = mo.md(f"Expected **{_expected}**, actual **{_shared}**, lost updates **{_lost}**.").callout(kind="info")

    _panel_items = [_summary]
    if show_trace.value:
        _panel_items.append(mo.ui.table(_log, label="Interleaving trace", selection=None, pagination=False, show_download=False, show_search=False))

    _panel = mo.vstack(_panel_items, gap=0.6)
    _panel
    return


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
    return


@app.cell
def _(mo):
    atomic_amount = mo.ui.slider(10, 500, step=10, value=150, label="Transfer amount", show_value=True)
    atomic_fail = mo.ui.switch(value=True, label="Inject failure after debit")
    run_atomic = mo.ui.button(label="Run atomicity demo", value=0, on_click=lambda clicks: clicks + 1, kind="success")

    _controls = mo.vstack(
        [mo.hstack([atomic_amount, atomic_fail], widths="equal"), run_atomic],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return atomic_amount, atomic_fail, run_atomic


@app.cell
def _(
    Path,
    atomic_amount,
    atomic_fail,
    json,
    mo,
    run_atomic,
    sqlite3,
    tempfile,
):
    if run_atomic.value == 0:
        _output = mo.md("Click **Run atomicity demo** to simulate the transfer step-by-step.").callout(kind="neutral")
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
            _add_timeline("file (JSON)", "debit", dict(_file_balances), "Alice debited")
            if not atomic_fail.value:
                _file_balances["Bob"] += atomic_amount.value
                _file_path.write_text(json.dumps(_file_balances), encoding="utf-8")
                _add_timeline("file (JSON)", "credit", dict(_file_balances), "Bob credited")
            else:
                _add_timeline("file (JSON)", "crash", dict(_file_balances), "crash before credit")

            _file_final = json.loads(_file_path.read_text(encoding="utf-8"))

            _db_path = _tmpdir / "ledger.db"
            _con = sqlite3.connect(str(_db_path), isolation_level=None)
            _con.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER)")
            _con.executemany("INSERT INTO accounts VALUES (?, ?)", list(_initial.items()))

            try:
                _con.execute("BEGIN")
                _add_timeline("sqlite", "start", dict(_initial), "initial balances")
                _con.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE name = 'Alice'",
                    (atomic_amount.value,),
                )
                _db_after_debit = dict(_con.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())
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
                _db_final = dict(_con.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())
                _add_timeline("sqlite", "commit", _db_final, "transaction committed")
            except Exception:
                try:
                    _con.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                _db_final = dict(_con.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())
                _add_timeline("sqlite", "rollback", _db_final, "transaction rolled back")

            _db_rows = _con.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall()
            _con.close()

        if not _db_rows:
            _db_rows = list(_initial.items())

        _initial_table = mo.ui.table(
            [{"account": k, "balance": v} for k, v in _initial.items()],
            label="Initial balances",
            selection=None, pagination=False, show_download=False, show_search=False,
        )
        _file_table = mo.ui.table(
            [{"account": k, "balance": v} for k, v in _file_final.items()],
            label="File ledger (JSON)",
            selection=None, pagination=False, show_download=False, show_search=False,
        )
        _db_table = mo.ui.table(
            [{"account": name, "balance": bal} for name, bal in _db_rows],
            label="SQLite ledger (transaction)",
            selection=None, pagination=False, show_download=False, show_search=False,
        )
        _timeline_table = mo.ui.table(_timeline, label="Step-by-step timeline", selection=None, pagination=False, show_download=False, show_search=False)

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
      </div>
      <div class="bar-value">{total:,} / {expected:,}</div>
    </div>
                """

        _total_chart = mo.Html(
            f"""
    <div class="section-card">
      <h3>Total Balance Snapshot</h3>
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

        _file_callout = mo.md("File writes are **not atomic**: debit and credit can be split by a crash.").callout(kind=_file_kind)
        _db_callout = mo.md("SQLite uses **transactions**: either both updates happen or none.").callout(kind=_db_kind)

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
    return


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
    return


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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 2. Serialization & Deserialization Benchmarks")
    _section
    return


@app.cell
def _(mo):
    _chapter2_guide = mo.md(
        """
    ### Chapter 2 Introduction

    > **Key Question:** Which format gives the best trade-off for the workload (actual data + query pattern)?

    *Still in the **data tier**. Chapter 1 made writes correct; now we choose what those bytes look like.*

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
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### Serialization = Bytes on Disk (or Wire)

    Serialization transforms Python objects into bytes so they can be stored or sent.
    Deserialization rebuilds objects from bytes. The format choice affects speed, file size,
    interoperability, type fidelity, schema evolution, and safety.

    **First, one word we will use all day.** A **schema** is the blank form. Not the answers,
    the printed boxes: what fields exist, in what order, and what kind of thing goes in each one.
    `sale_id` a whole number, `sale_date` a date, `total_price` a decimal.

    JSON is longhand on blank paper. Anyone can read it, and nothing stops you writing
    "about forty" in the price box. Avro is a **pre-printed form**: compact, because the labels
    live on the form instead of being repeated on every sheet, but you must keep the form to read
    the sheets back.

    **Schema evolution** is what happens when the office adds a box to the form. Do last year's
    sheets, printed on the old form, still get read? We will test exactly that below.

    *Where the picture breaks:* a paper form is inseparable from its answers, which is true for
    Avro and false for JSON and CSV. There the form exists only in the mind of whoever reads the
    file, which is why two teams can disagree about what the same sheet means. That is the reason
    chapter 7 exists.

    You will meet this blank form three more times today: DuckDB **guesses** it in chapter 5,
    Pydantic **enforces** it in chapter 7, FastAPI **publishes** it in chapter 8.

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

    Two words that sound alike and are not.

    **Latency** is how long *one* thing takes, end to end. Post a letter to Vienna: two days.

    **Throughput** is how much gets through per unit of time. The van leaving the depot each
    night carries 40,000 letters.

    They trade against each other, and this is the part people get wrong. Waiting to fill the van
    raises throughput and *hurts* the latency of the first letter that boarded it. A container
    ship has appalling latency and colossal throughput. When someone says a system is fast, ask
    which one they mean. In the benchmark below we measure both, and they do not rank the same way.

    *Sometimes you get both*, by making the letters smaller. That is what chapter 4 is for.

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
    return


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
    _text = mo.md(f"Recommended starting point: **{choice}**\n\n" "Treat this as a default, then benchmark on the real workload (actual data + query pattern).").callout(
        kind="info"
    )
    _text
    return


@app.cell
def _(mo):
    serial_rows = mo.ui.slider(200, 3000, step=200, value=800, label="Rows", show_value=True)
    serial_cols = mo.ui.slider(2, 8, value=5, label="Numeric columns", show_value=True)
    serial_seed = mo.ui.slider(1, 999, value=42, label="Seed", show_value=True)
    run_serial = mo.ui.button(label="Run serialization benchmark", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _note = mo.md("Includes Arrow, Parquet, and Avro.")

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
    Path,
    csv,
    fastavro,
    feather,
    format_bytes,
    format_ms,
    json,
    mo,
    pa,
    pickle,
    pq,
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
        _output = mo.md("Click **Run serialization benchmark** to execute.").callout(kind="neutral")
    else:
        _records = _make_records(serial_rows.value, serial_cols.value, serial_seed.value + run_serial.value)
        sample = mo.ui.table(_records[:5], label="Sample records", selection=None, pagination=False, show_download=False, show_search=False)

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

            _results.append(bench("Pickle (unsafe)", pickle_write, pickle_read, _tmpdir / "data.pkl"))

            def csv_write(path):
                with path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=_records[0].keys())
                    writer.writeheader()
                    writer.writerows(_records)

            def csv_read(path):
                with path.open("r", newline="", encoding="utf-8") as f:
                    list(csv.DictReader(f))

            _results.append(bench("CSV", csv_write, csv_read, _tmpdir / "data.csv"))

            # Pay pyarrow's one-time initialisation before the clock starts,
            # otherwise the first measurement is ~70x too slow.
            feather.write_feather(
                pa.Table.from_pylist([{"warmup": 1}]), (_tmpdir / "_warmup.feather").as_posix()
            )

            def arrow_write(path):
                table = pa.Table.from_pylist(_records)
                feather.write_feather(table, path)

            def arrow_read(path):
                feather.read_table(path)

            _results.append(
                bench(
                    "Arrow/Feather",
                    arrow_write,
                    arrow_read,
                    _tmpdir / "data.feather",
                )
            )

            def parquet_write(path):
                table = pa.Table.from_pylist(_records)
                pq.write_table(table, path)

            def parquet_read(path):
                pq.read_table(path)

            _results.append(
                bench(
                    "Parquet",
                    parquet_write,
                    parquet_read,
                    _tmpdir / "data.parquet",
                )
            )

            schema = {
                "type": "record",
                "name": "Record",
                "fields": [
                    {"name": "id", "type": "int"},
                    {"name": "city", "type": "string"},
                    {"name": "score", "type": "double"},
                ]
                + [{"name": f"metric_{c}", "type": "double"} for c in range(serial_cols.value)],
            }

            def avro_write(path):
                with path.open("wb") as f:
                    fastavro.writer(f, schema, _records)

            def avro_read(path):
                with path.open("rb") as f:
                    list(fastavro.reader(f))

            _results.append(bench("Avro", avro_write, avro_read, _tmpdir / "data.avro"))

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

        results_table = mo.ui.table(_display_rows, label="Serialization benchmark", selection=None, pagination=False, show_download=False, show_search=False)
        benchmark_note = mo.md("Numbers vary by machine and caching. Treat this as a **relative** comparison, not an absolute benchmark.").callout(kind="info")
        warning = mo.md(
            """
    **Security note:** Pickle is not safe for untrusted data. Only load Pickle files from trusted sources.
                """
        ).callout(kind="warn")

        _items = [sample, results_table, _charts, benchmark_note, warning]
        _output = mo.vstack(_items, gap=0.6)

    _output
    return


@app.cell
def _(Path, SALES_SEED, mo, pd, tempfile):
    _src = pd.read_parquet(SALES_SEED, columns=["sale_id", "sale_date", "total_price"]).head(500).copy()
    _src["sale_date"] = pd.to_datetime(_src["sale_date"])
    # Store codes are the classic case: they look like numbers and are not.
    _src["store_code"] = [f"{n:03d}" for n in ([7, 10, 42] * 167)[: len(_src)]]

    with tempfile.TemporaryDirectory() as _td:
        _csv_p = Path(_td) / "sales.csv"
        _pq_p = Path(_td) / "sales.parquet"
        _src.to_csv(_csv_p, index=False)
        _src.to_parquet(_pq_p, index=False)
        _from_csv = pd.read_csv(_csv_p)
        _from_pq = pd.read_parquet(_pq_p)

    _dtypes = [
        {
            "column": _c,
            "wrote": str(_src[_c].dtype),
            "back from CSV": str(_from_csv[_c].dtype),
            "back from Parquet": str(_from_pq[_c].dtype),
        }
        for _c in _src.columns
    ]

    def _span(_df):
        try:
            return str(_df["sale_date"].max() - _df["sale_date"].min())
        except Exception as _exc:
            return f"{type(_exc).__name__}: {_exc}"

    _answers = [
        {
            "question": "How long did sales run?",
            "via Parquet": _span(_from_pq),
            "via CSV": _span(_from_csv),
        },
        {
            "question": "First three store codes",
            "via Parquet": str(list(_from_pq["store_code"].head(3))),
            "via CSV": str(list(_from_csv["store_code"].head(3))),
        },
    ]

    _note = mo.md(
        """
    Open both files in a text editor and the date looks identical in each: `2024-03-07`.
    The bytes did not lose the date. The file lost **the note saying it was a date**, and that
    note is what your analysis was standing on.

    The first failure shouted. The second did not: the store codes came back as `7, 10, 42`
    with no error, no warning and nothing in the log. That is the one that ends up in a report.
            """
    ).callout(kind="warn")

    _panel = mo.vstack(
        [
            mo.ui.table(_dtypes, label="Same 500 rows, written two ways and read back", selection=None, pagination=False, show_download=False, show_search=False),
            mo.ui.table(_answers, label="Now ask the data a question", selection=None, pagination=False, show_download=False, show_search=False),
            _note,
        ],
        gap=0.6,
    )
    _panel
    return


@app.cell
def _(csv, fastavro, io, mo):
    # It is next March. Your team adds a `channel` field to the sales event.
    # Two years of old files sit on disk, and one old program nobody redeployed
    # is still running in production. What happens?
    _v1 = {
        "type": "record",
        "name": "Sale",
        "fields": [{"name": "sale_id", "type": "int"}, {"name": "total_price", "type": "double"}],
    }
    _v2 = {
        "type": "record",
        "name": "Sale",
        "fields": [
            {"name": "sale_id", "type": "int"},
            {"name": "total_price", "type": "double"},
            {"name": "channel", "type": "string", "default": "in-store"},
        ],
    }

    def _avro_bytes(_schema, _rows):
        _buf = io.BytesIO()
        fastavro.writer(_buf, _schema, _rows)
        return _buf.getvalue()

    _old_file = _avro_bytes(_v1, [{"sale_id": 1, "total_price": 4034.91}])
    _new_file = _avro_bytes(_v2, [{"sale_id": 3, "total_price": 99.0, "channel": "online"}])

    _old_by_new = list(fastavro.reader(io.BytesIO(_old_file), reader_schema=_v2))
    _new_by_old = list(fastavro.reader(io.BytesIO(_new_file), reader_schema=_v1))

    _csv_buf = io.StringIO()
    _writer = csv.DictWriter(_csv_buf, fieldnames=["sale_id", "total_price"])
    _writer.writeheader()
    _writer.writerow({"sale_id": 1, "total_price": 4034.91})
    _csv_row = next(csv.DictReader(io.StringIO(_csv_buf.getvalue())))
    try:
        _csv_row["channel"]
        _csv_result = "no error"
    except KeyError as _exc:
        _csv_result = f"KeyError: {_exc}"

    _rows = [
        {
            "situation": "Last year's Avro file, read by this year's code",
            "result": str(_old_by_new[0]),
            "verdict": "works: the reader supplied the default the writer never wrote",
        },
        {
            "situation": "This year's Avro file, read by the old program",
            "result": str(_new_by_old[0]),
            "verdict": "works: the extra field is skipped, nothing crashes",
        },
        {
            "situation": "Last year's CSV file, read by this year's code",
            "result": _csv_result,
            "verdict": "breaks: the only fix is changing every program that reads it",
        },
    ]
    _note = mo.md(
        "The packing list on the box is not decoration. It is what lets a file written last "
        "year and a program written this morning still agree. CSV has no packing list, so "
        "the agreement lives only in someone's memory."
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Schema Evolution: the office adds a box to the form"),
            mo.ui.table(_rows, label="Same change, three situations", selection=None, pagination=False, show_download=False, show_search=False),
            _note,
        ],
        gap=0.6,
    )
    _panel
    return


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
    return


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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 3. Column-Based vs Row-Based Storage")
    _section
    return


@app.cell
def _(mo):
    _chapter3_guide = mo.md(
        """
    ### Chapter 3 Introduction

    > **Key Question:** Is read work spent on data that queries do not need?

    *Still in the **data tier**. Chapter 2 picked a format; now we choose how it is arranged on disk.*

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
    return


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

    A shop keeps its sales two ways.

    **The shoebox.** Every sale is one till receipt: date, product, country, units, price and
    rating printed together on one slip. To answer *what did we take in January 2026?* you pick up
    all 3,360 slips one at a time, read the date, read the price, and put down the other four
    fields untouched. You handled every field of every sale to use two of them. That is a **row
    store**, and it is exactly the right shape for *show me sale 2,914*: one slip, one grab.

    **The ledger.** The same sales copied into a bookkeeper's ledger, one field per page: a long
    page of dates, a long page of prices, a long page of product codes. The same question now
    means taking down two pages and leaving the other five on the shelf. That is a **column
    store**. It is the wrong shape for *show me sale 2,914*, which is now line 2,914 of seven
    different pages.

    Same sales, same shop. The cost of a question changed because the paper was arranged
    differently.

    *Two things the picture does not show.* The ledger pages are written in shorthand, so they are
    not all the same size, which is chapter 4. And the ledger is not one endless page per field,
    which is the next cell.

    Below we simulate column selection and filtering to reveal the runtime difference (execution-time gap).

    **Format perspective:** Avro is a row‑based, schema‑driven file format (great for event logs).
    Parquet is a column‑based file format (great for analytics and scans).
    Arrow is columnar in‑memory (fast interchange between systems).
            """
    ).callout(kind="neutral")
    _explanation
    return


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
    return


@app.cell
def _(mo):
    _binder = mo.md(
        """
    ### The Binder and the Index Card

    The ledger is not seven endless pages. It is a **binder**.

    The binder is divided into **sections**. Each section holds a horizontal slice of the shop's
    sales, say 420 of them, and inside a section each field still gets its own page. So section 3
    holds a dates page, a prices page and a countries page, all covering the same 420 sales.
    Parquet calls a section a **row group**.

    At the very back of the binder is an **index card**. For every section and every field it
    records two numbers and nothing else: the smallest value in that section and the largest.
    Parquet calls this the **footer**, and those two numbers the **column statistics**.

    Now watch what the index card buys. Someone asks for revenue in 2026. You read the card first
    and it says:

    ```
    section 0   dates 2024-03-01 .. 2024-05-27
    section 1   dates 2024-06-01 .. 2024-08-27
    ...
    section 6   dates 2025-09-01 .. 2025-11-27
    section 7   dates 2025-12-01 .. 2026-02-27
    ```

    Sections 0 to 6 end before 2026 began. Not *probably*. **Provably**: their latest date is
    earlier than your earliest date, so no page inside them can hold a 2026 sale. You leave seven
    sections closed, open section 7, and take out 2 of its 7 pages.

    That is how a program skips data it never read. It read the index card.

    **Two fences, and the second one matters more than it looks.**

    - The card can prove a section is **hopeless**. It can never prove a section is **useful**.
      A section labelled `2024-03-01 .. 2026-02-27` must be opened even if it holds one match.
      Min and max are a rejection test, not a search.
    - This is why the order rows were written in is not cosmetic. Drop the sales into the binder
      in random order and every section's card reads roughly `2024-03-01 .. 2026-02-27`. Every
      label spans everything, every label is useless, and you open all eight sections. The
      mechanism did not fail. You gave it nothing to work with. The next cell measures exactly
      that, on the real file.
        """
    ).callout(kind="neutral")
    _binder
    return


@app.cell
def _(mo):
    n_rows = mo.ui.slider(5_000, 50_000, step=5_000, value=15_000, label="Rows", show_value=True)
    n_cols = mo.ui.slider(3, 12, value=6, label="Columns", show_value=True)
    storage_seed = mo.ui.slider(1, 999, value=7, label="Seed", show_value=True)
    run_storage = mo.ui.button(label="Run storage benchmark", value=0, on_click=lambda clicks: clicks + 1, kind="success")

    _controls = mo.vstack([mo.hstack([n_rows, n_cols], widths="equal"), storage_seed, run_storage], gap=0.6).callout(kind="neutral")
    _controls
    return n_cols, n_rows, run_storage, storage_seed


@app.cell
def _(mo, n_cols, n_rows, random, run_storage, storage_seed, time):
    def build_data(rows, cols, seed_value):
        rng = random.Random(seed_value)
        rows_list = [tuple(rng.random() for _ in range(cols)) for _ in range(rows)]
        col_names = [f"c{idx}" for idx in range(cols)]
        columns = {name: [row[i] for row in rows_list] for i, name in enumerate(col_names)}
        return rows_list, columns, col_names

    if run_storage.value == 0:
        _output = mo.md("Click **Run storage benchmark** to execute.").callout(kind="neutral")
    else:
        rows_list, columns, col_names = build_data(n_rows.value, n_cols.value, storage_seed.value + run_storage.value)
        target_col = col_names[0]
        threshold = 0.75

        def time_it(fn):
            start = time.perf_counter()
            result = fn()
            return time.perf_counter() - start, result

        row_filter_time, row_filter = time_it(lambda: [row for row in rows_list if row[0] > threshold])
        col_filter_time, col_filter = time_it(lambda: [val for val in columns[target_col] if val > threshold])

        row_sum_time, row_sum = time_it(lambda: sum(row[0] for row in rows_list))
        col_sum_time, col_sum = time_it(lambda: sum(columns[target_col]))

        _results = [
            {
                "operation": "Filter column > 0.75",
                "Row-style access (ms)": round(row_filter_time * 1000, 3),
                "Column-style access (ms)": round(col_filter_time * 1000, 3),
            },
            {
                "operation": "Sum column",
                "Row-style access (ms)": round(row_sum_time * 1000, 3),
                "Column-style access (ms)": round(col_sum_time * 1000, 3),
            },
        ]

        _table = mo.ui.table(_results, label="Row vs Column timing (Python simulation)", selection=None, pagination=False, show_download=False, show_search=False)
        _note = mo.md(
            """
    **Discussion:** These timings simulate the two *access patterns* in plain Python. No file is written
    and no library is called, so this is not a measurement of Avro against Parquet. Avro stores data the
    row way and Parquet the column way, which is why the pattern matters.

    Both operations read one column out of many. The row layout still has to step over every other value
    in each record to reach it; the column layout has that column already lying together. Real column
    formats like Parquet win by more than this, because they also skip reading the unused columns from
    disk entirely.
                """
        ).callout(kind="info")

        _output = mo.vstack([_table, _note], gap=0.6)

    _output
    return


@app.cell
def _(mo):
    run_rowgroup = mo.ui.button(label="Run row-group audit", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Which Sections Did We Open?"),
            mo.md(
                "Same 3,360 real sales, written twice with 420-row sections: once in date order, "
                "once shuffled. Then we ask the file's own index card what the query "
                "`avg(total_price) WHERE sale_date >= '2026-01-01'` is entitled to skip."
            ).callout(kind="info"),
            run_rowgroup,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_rowgroup,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, run_rowgroup, tempfile):
    if run_rowgroup.value == 0:
        _output = mo.md("Click **Run row-group audit** to read the index card.").callout(kind="neutral")
    else:
        _df = pd.read_parquet(SALES_SEED)
        _df["sale_date"] = pd.to_datetime(_df["sale_date"])
        _cut = "2026-01-01"
        _wanted = ["sale_date", "total_price"]

        with tempfile.TemporaryDirectory() as _td:
            _ordered = Path(_td) / "date_ordered.parquet"
            _shuffled = Path(_td) / "shuffled.parquet"
            _df.sort_values("sale_date").to_parquet(_ordered, index=False, row_group_size=420)
            _df.sample(frac=1, random_state=7).to_parquet(_shuffled, index=False, row_group_size=420)

            _con = duckdb.connect()
            _rows = []
            for _label, _path in (("date-ordered", _ordered), ("shuffled", _shuffled)):
                _md = _con.execute(
                    "SELECT row_group_id, path_in_schema, total_compressed_size, stats_max "
                    f"FROM parquet_metadata('{_path.as_posix()}')"
                ).df()
                _groups = _md["row_group_id"].nunique()
                _all_cols = int(_md["total_compressed_size"].sum())
                _two_cols_all = _md[_md["path_in_schema"].isin(_wanted)]
                _b_bytes = int(_two_cols_all["total_compressed_size"].sum())
                # The index card: a section survives only if its LATEST date reaches the cut-off.
                _dates = _md[_md["path_in_schema"] == "sale_date"]
                _live = _dates[_dates["stats_max"] >= _cut]["row_group_id"].tolist()
                _c_bytes = int(_two_cols_all[_two_cols_all["row_group_id"].isin(_live)]["total_compressed_size"].sum())
                _answer = _con.execute(
                    f"SELECT round(avg(total_price), 2) FROM '{_path.as_posix()}' WHERE sale_date >= '{_cut}'"
                ).fetchone()[0]
                _rows.append(
                    {
                        "file": _label,
                        "file size (B)": _path.stat().st_size,
                        "A: every column, every section": _all_cols,
                        "B: 2 columns, every section": _b_bytes,
                        "C: 2 columns, surviving sections": _c_bytes,
                        "sections opened": f"{len(_live)} of {_groups}",
                        "answer": _answer,
                    }
                )

        _note = mo.md(
            """
    Read the top row left to right. Choosing columns took the read from **62,705** bytes to
    **33,029**. That is what chapter 3 has taught so far. The index card then took it from
    33,029 to **4,131**, and nobody wrote that in the query.

    Now read the second row. Identical data, identical query, rows written in a different order,
    and the index card buys **nothing**: every section survives, because every label spans the
    whole range. Sorting is not tidying. It is what makes the skipping possible.

    Two honesty notes. These are bytes the engine is *entitled to skip*, computed from the file's
    own footer, not bytes measured leaving the disk. And the shuffled file is also 23% larger
    from the very same rows, which is a preview of chapter 4: order is itself a form of
    compression. Both files return the same answer, which is the point.
                """
        ).callout(kind="info")
        _output = mo.vstack(
            [mo.ui.table(_rows, label="Bytes the query must read", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
        )
    _output
    return


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
    return


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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 4. Compression & Encoding (Parquet, Gzip)")
    _section
    return


@app.cell
def _(mo):
    _chapter4_guide = mo.md(
        """
    ### Chapter 4 Introduction

    > **Key Question:** Will compression reduce total query time, not only file size?

    *Still in the **data tier**. Chapter 3 put similar values next to each other, which is exactly what makes them squeeze well.*

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
    return


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

    **Compression level.** gzip takes a level from 1 to 9. Level 1 compresses quickly and
    saves less; level 9 works hardest and saves most; level 6 is the default compromise.
    The gain from 1 to 9 is usually small while the CPU cost is not, which is why almost
    nobody runs level 9 in production. Watch the level rows in the table below.
                """
    ).callout(kind="neutral")
    _explanation
    return


@app.cell
def _(mo):
    budget_size_gb = mo.ui.slider(1, 500, value=120, label="Raw dataset size (GB)", show_value=True)
    budget_ratio = mo.ui.slider(0.1, 1.0, step=0.05, value=0.35, label="Compression ratio", show_value=True)
    budget_scans_day = mo.ui.slider(1, 80, value=18, label="Full scans/day", show_value=True)
    _note = mo.md("Set the estimated compression ratio and scan frequency to quantify daily I/O savings (reduced bytes read/written).").callout(kind="info")
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
        selection=None, pagination=False, show_download=False, show_search=False,
    )
    _note = mo.md("Use this as a first-order estimate before deeper benchmarking.").callout(kind="info")
    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return


@app.cell
def _(mo):
    _pca_disclaimer = mo.Html(
        """
    <div class="disclaimer-red">
      Disclaimer: PCA will be discussed in-depth in the <strong>Machine Learning 2</strong> module.
      Here it is only used as a simple example to illustrate compression ideas.
    </div>
            """
    )
    _pca_disclaimer
    return


@app.cell
def _(mo):
    image_demo_rank = mo.ui.slider(4, 90, value=26, step=2, label="PCA components (rank k)", show_value=True)
    image_demo_width = mo.ui.slider(200, 360, value=280, step=20, label="Image width (px)", show_value=True)
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Visual Compression with PCA (Cat Image)"),
            mo.hstack([image_demo_rank, image_demo_width], widths="equal"),
            mo.md("Left is the reference cat image. Right is reconstructed from only `k` PCA components per color channel.").callout(kind="info"),
            mo.md("Further Details: [Principal Component Analysis (PCA)](https://en.wikipedia.org/wiki/Principal_component_analysis)").callout(kind="neutral"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return image_demo_rank, image_demo_width


@app.cell
def _(
    Image,
    ImageDraw,
    gzip,
    image_demo_rank,
    image_demo_width,
    io,
    math,
    mo,
    np,
):
    _width = image_demo_width.value
    _height = int(_width * 0.74)
    _img = Image.new("RGB", (_width, _height), color=(238, 242, 248))
    _draw = ImageDraw.Draw(_img)

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
        [(_cx - int(0.82 * _r), _cy - int(0.52 * _r)), (_cx - int(0.40 * _r), _cy - int(1.35 * _r)), (_cx - int(0.03 * _r), _cy - int(0.58 * _r))],
        fill=_fur,
        outline=_fur_dark,
        width=3,
    )
    _draw.polygon(
        [(_cx + int(0.82 * _r), _cy - int(0.52 * _r)), (_cx + int(0.40 * _r), _cy - int(1.35 * _r)), (_cx + int(0.03 * _r), _cy - int(0.58 * _r))],
        fill=_fur,
        outline=_fur_dark,
        width=3,
    )
    _draw.polygon(
        [(_cx - int(0.70 * _r), _cy - int(0.56 * _r)), (_cx - int(0.40 * _r), _cy - int(1.16 * _r)), (_cx - int(0.12 * _r), _cy - int(0.62 * _r))],
        fill=_ear_inner,
        outline=None,
    )
    _draw.polygon(
        [(_cx + int(0.70 * _r), _cy - int(0.56 * _r)), (_cx + int(0.40 * _r), _cy - int(1.16 * _r)), (_cx + int(0.12 * _r), _cy - int(0.62 * _r))],
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
        [(_cx, _nose_y), (_cx - int(0.13 * _r), _nose_y + int(0.15 * _r)), (_cx + int(0.13 * _r), _nose_y + int(0.15 * _r))],
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

    _arr = np.asarray(_img, dtype=np.float32) / 255.0
    _rank = int(min(image_demo_rank.value, _arr.shape[0], _arr.shape[1]))
    _reconstructed = np.zeros_like(_arr)
    _factors = []

    for _channel_idx in range(3):
        _channel = _arr[:, :, _channel_idx]
        _u, _s, _vt = np.linalg.svd(_channel, full_matrices=False)
        _ur = _u[:, :_rank]
        _sr = _s[:_rank]
        _vtr = _vt[:_rank, :]
        _reconstructed[:, :, _channel_idx] = (_ur * _sr) @ _vtr
        _factors.append((_ur.astype(np.float32), _sr.astype(np.float32), _vtr.astype(np.float32)))

    _reconstructed = np.clip(_reconstructed, 0.0, 1.0)
    _mse = float(np.mean((_arr - _reconstructed) ** 2))
    _psnr = float("inf") if _mse <= 1e-12 else 10.0 * math.log10(1.0 / _mse)

    _ref_uint8 = (_arr * 255.0).astype(np.uint8)
    _rec_uint8 = (_reconstructed * 255.0).astype(np.uint8)
    _ref_img = Image.fromarray(_ref_uint8)
    _rec_img = Image.fromarray(_rec_uint8)

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
                caption=(f"PCA reconstruction (k={_rank}, display preview)"),
            ),
        ],
        widths="equal",
        gap=0.8,
    )
    _payload16 = {}
    for _channel_idx, (_ur, _sr, _vtr) in enumerate(_factors):
        _payload16[f"u{_channel_idx}"] = _ur.astype(np.float16)
        _payload16[f"s{_channel_idx}"] = _sr.astype(np.float16)
        _payload16[f"vt{_channel_idx}"] = _vtr.astype(np.float16)

    _npz16_buf = io.BytesIO()
    np.savez_compressed(_npz16_buf, **_payload16)
    _pca_npz16_bytes = len(_npz16_buf.getvalue())
    _pca_ratio = _pca_npz16_bytes / max(1, _raw_rgb_bytes)
    _psnr_display = "infinite" if _psnr == float("inf") else round(_psnr, 2)

    # The same image, squeezed losslessly, so the two kinds sit in one table.
    _orig_u8 = (_arr * 255.0).astype(np.uint8)
    _gz_bytes = gzip.compress(_orig_u8.tobytes(), 6)
    _gz_back = np.frombuffer(gzip.decompress(_gz_bytes), dtype=np.uint8).reshape(_orig_u8.shape)
    _gz_identical = bool(np.array_equal(_gz_back, _orig_u8))
    _pca_worst = int(np.max(np.abs(_rec_uint8.astype(int) - _orig_u8.astype(int))))

    _comparison_table = mo.ui.table(
        [
            {
                "method": "gzip (lossless)",
                "bytes": len(_gz_bytes),
                "ratio (compressed/raw)": round(len(_gz_bytes) / max(1, _raw_rgb_bytes), 4),
                "identical to the original?": "yes" if _gz_identical else "no",
                "worst pixel off by (of 255)": 0,
            },
            {
                "method": f"PCA k={_rank} (lossy)",
                "bytes": _pca_npz16_bytes,
                "ratio (compressed/raw)": round(_pca_ratio, 4),
                "identical to the original?": "no",
                "worst pixel off by (of 255)": _pca_worst,
            },
        ],
        label=f"Same {_raw_rgb_bytes:,}-byte image, two kinds of compression",
        selection=None, pagination=False, show_download=False, show_search=False,
    )
    _comparison_note = mo.md(
        """
    **Two different promises, and confusing them is expensive.**

    **Lossless** is a photocopy shrunk to fit A5. Every word is still there; enlarge it and you
    get the original back exactly, byte for byte. gzip, PNG and Parquet are lossless. This is the
    only kind you may use on a sales ledger.

    **Lossy** is a summary. Much smaller, still useful, and the original is gone forever. PCA
    here, JPEG and MP3 in the world. Fine for a photo, where nobody can tell. Never fine for a price.

    The `identical` column is the whole difference, and it is why gzip has no quality score:
    there is no quality to score. Notice which row is actually smaller, too. On this image the
    lossless method wins, because a smooth drawing repeats itself enormously and repetition is
    exactly what lossless compression removes.
            """
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

    _output = mo.vstack([_pipeline, _comparison_images, _comparison_table, _comparison_note], gap=0.6)

    _output
    return


@app.cell
def _(mo):
    run_lossy_money = mo.ui.button(label="Run lossy vs lossless on money", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: The Cat Trick, Applied to the Sales Ledger"),
            mo.md(
                """
    Blurring a cat is fine because nobody can tell. So try the same idea on the real sales file:
    store the prices less precisely and see how much smaller it gets.

    **Predict first.** Which file is smallest, and which ones still add up to the right total?
                """
            ).callout(kind="info"),
            run_lossy_money,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_lossy_money,)


@app.cell
def _(Path, SALES_SEED, mo, pd, run_lossy_money, tempfile):
    if run_lossy_money.value == 0:
        _output = mo.md("Write your prediction down, then click **Run lossy vs lossless on money**.").callout(kind="neutral")
    else:
        _src = pd.read_parquet(SALES_SEED, columns=["sale_id", "total_price"])
        _truth = round(float(_src["total_price"].sum()), 2)

        with tempfile.TemporaryDirectory() as _td:
            _dir = Path(_td)

            def _store(_frame, _name, **_kw):
                _path = _dir / _name
                _frame.to_parquet(_path, index=False, **_kw)
                _back = pd.read_parquet(_path)
                return _path.stat().st_size, round(float(_back["total_price"].sum()), 2)

            _rows = []
            for _label, _frame, _kw in (
                ("exact", _src, {}),
                ("exact + gzip", _src, {"compression": "gzip"}),
            ):
                _bytes, _total = _store(_frame, f"{_label}.parquet", **_kw)
                _rows.append(
                    {
                        "how the prices are stored": f"{_label} (lossless)",
                        "bytes": _bytes,
                        "total revenue it reports": _total,
                        "off by": round(_total - _truth, 2),
                    }
                )
            for _digits, _label in ((0, "rounded to the franc"), (-1, "rounded to 10 francs"), (-2, "rounded to 100 francs")):
                _lossy = _src.copy()
                _lossy["total_price"] = _lossy["total_price"].round(_digits)
                _bytes, _total = _store(_lossy, f"lossy{_digits}.parquet", compression="gzip")
                _rows.append(
                    {
                        "how the prices are stored": f"{_label} (lossy)",
                        "bytes": _bytes,
                        "total revenue it reports": _total,
                        "off by": round(_total - _truth, 2),
                    }
                )

        _note = mo.md(
            f"""
    **The lossy files really are smaller.** Rounding to the nearest 100 francs saves roughly 40%
    of the bytes, which is a bigger win than gzip managed on the exact data.

    **And the last column is why nobody does this.** The true total is
    `{_truth:,.2f}`. Every lossy row reports a different number, and none of them is flagged: the
    file loads cleanly, the column is still a decimal, every tool downstream is perfectly happy.

    This is the same trick that was completely acceptable on the cat. The difference is not the
    technique, it is **what the numbers mean**. Nobody can see a pixel that is 5 shades off. Every
    accountant can see a total that is off by hundreds of francs, and by then the original is
    gone.

    So the rule is not "lossy compression is bad". It is: **lossy compression is a decision about
    whether an approximation of this particular value is still the truth you need.** For a photo,
    usually yes. For money, an identifier or a date, never.
                """
        ).callout(kind="danger")
        _output = mo.vstack(
            [mo.ui.table(_rows, label="Same 3,360 prices, stored five ways", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
        )
    _output
    return


@app.cell
def _(mo):
    compress_rows = mo.ui.slider(500, 10_000, step=500, value=2_000, label="Rows", show_value=True)
    compress_cols = mo.ui.slider(3, 10, value=6, label="Numeric columns", show_value=True)
    compress_seed = mo.ui.slider(1, 999, value=11, label="Seed", show_value=True)
    run_compress = mo.ui.button(label="Run compression benchmark", value=0, on_click=lambda clicks: clicks + 1, kind="success")

    _controls = mo.vstack(
        [mo.hstack([compress_rows, compress_cols], widths="equal"), compress_seed, run_compress],
        gap=0.6,
    ).callout(kind="neutral")
    _controls
    return compress_cols, compress_rows, compress_seed, run_compress


@app.cell
def _(
    Path,
    compress_cols,
    compress_rows,
    compress_seed,
    csv,
    gzip,
    json,
    mo,
    pa,
    pq,
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
        _output = mo.md("Click **Run compression benchmark** to execute.").callout(kind="neutral")
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

            # Gzip compression. Level 1 is fastest, 9 squeezes hardest, 6 is the default.
            for label, _source_path in [("JSON+gzip", json_path), ("CSV+gzip", _csv_path)]:
                for _level in (1, 6, 9):
                    gz_path = _source_path.with_suffix(f"{_source_path.suffix}.{_level}.gz")
                    with _source_path.open("rb") as src, gzip.open(gz_path, "wb", compresslevel=_level) as dst:
                        dst.write(src.read())
                    _results.append(
                        {
                            "format": f"{label} (level {_level})",
                            "size (bytes)": gz_path.stat().st_size,
                            "ratio vs JSON": round(gz_path.stat().st_size / baseline, 4),
                        }
                    )

            table = pa.Table.from_pylist(_records)
            for codec in ["snappy", "gzip", "zstd", "brotli"]:
                parquet_path = _tmpdir / f"data_{codec}.parquet"
                try:
                    pq.write_table(table, parquet_path, compression=codec)
                except Exception:
                    continue
                _results.append(
                    {
                        "format": f"Parquet ({codec})",
                        "size (bytes)": parquet_path.stat().st_size,
                        "ratio vs JSON": round(parquet_path.stat().st_size / baseline, 4),
                    }
                )

        _table = mo.ui.table(_results, label="Compression ratios (baseline: JSON size)", selection=None, pagination=False, show_download=False, show_search=False)
        _note = mo.md(
            """
    How to read this table:

    - `ratio vs JSON = 1.00` means same size as JSON.
    - `< 1.00` means the format is smaller than JSON (good for I/O).
    - `> 1.00` means the format is larger than JSON.

    Why this matters:

    - In analytics, we often scan many rows and columns.
    - Smaller files mean fewer bytes read from disk/network.

    **And why the ranking is not a law.** Compression does not make files smaller; it removes
    **repetition**. So the winner depends on your columns, not on the format's reputation.
    On 2,000 rows of six columns, measured with this same code:

    - columns of distinct measurements: Parquet 125,490 bytes, JSON+gzip 131,586. Parquet wins.
    - the same shape, but each column holding five repeated values: Parquet 17,622 bytes,
      JSON+gzip 15,650. Parquet **loses**.

    Nothing about Parquet changed. What changed is how much repetition there was to remove.
    A column of 2,000 different measurements has almost none. Before you pick a format, look at
    your columns.
                """
        ).callout(kind="info")

        _output = mo.vstack([_table, _note], gap=0.6)

    _output
    return


@app.cell
def _(mo):
    run_ctime = mo.ui.button(label="Run compression timing", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Does Compression Make the Query *Faster*?"),
            mo.md(
                "This chapter opened by asking whether compression cuts total query time, not just "
                "file size. So far we have only measured size. Now we time the whole job: read the "
                "file, parse it, and sum one column. Best of 7 runs."
            ).callout(kind="info"),
            run_ctime,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_ctime,)


@app.cell
def _(SALES_SEED, gzip, io, mo, pd, run_ctime, time):
    if run_ctime.value == 0:
        _output = mo.md("Click **Run compression timing** to measure it.").callout(kind="neutral")
    else:
        _raw = pd.read_parquet(SALES_SEED).to_csv(index=False).encode("utf-8")

        def _best(_fn, _n=7):
            _times = []
            for _ in range(_n):
                _t0 = time.perf_counter()
                _fn()
                _times.append(time.perf_counter() - _t0)
            return min(_times)

        def _answer(_blob, _gzipped):
            _data = gzip.decompress(_blob) if _gzipped else _blob
            return pd.read_csv(io.BytesIO(_data))["total_price"].sum()

        _plain_time = _best(lambda: _answer(_raw, False))
        _rows = [
            {
                "variant": "plain CSV",
                "bytes": len(_raw),
                "read + parse + sum (ms)": round(_plain_time * 1000, 2),
                "vs plain": "1.00x",
                "compress (ms)": "-",
                "decompress (ms)": "-",
            }
        ]
        for _level in (1, 6, 9):
            _t0 = time.perf_counter()
            _blob = gzip.compress(_raw, _level)
            _ctime = time.perf_counter() - _t0
            _rtime = _best(lambda _b=_blob: _answer(_b, True))
            _dtime = _best(lambda _b=_blob: gzip.decompress(_b))
            _rows.append(
                {
                    "variant": f"gzip level {_level}",
                    "bytes": len(_blob),
                    "read + parse + sum (ms)": round(_rtime * 1000, 2),
                    "vs plain": f"{_rtime / _plain_time:.2f}x",
                    "compress (ms)": round(_ctime * 1000, 2),
                    "decompress (ms)": round(_dtime * 1000, 2),
                }
            )

        _note = mo.md(
            """
    **The answer is no, not here.** The gzipped file is roughly a third of the size and takes
    *longer* to answer the same question.

    Compression trades CPU for I/O. The bytes it saved were bytes the operating system had
    already cached, so reading them was nearly free, and the CPU work to unpack them was not.
    When I/O is already cheap, that is a bad trade. Send the same file across a network and the
    trade flips, which is why compression is normal for transfer and a judgement call on a local
    disk.

    Look at levels 6 and 9 too. They land a few dozen bytes apart, and level 9 spent roughly
    twice the CPU to find them. Decompression costs about the same at every level, so **the
    level you pick is a decision about writing, not reading.**
                """
        ).callout(kind="warn")
        _output = mo.vstack(
            [mo.ui.table(_rows, label="Same question, four ways to store the file", selection=None, pagination=False, show_download=False, show_search=False), _note],
            gap=0.6,
        )
    _output
    return


@app.cell
def _(mo):
    dict_rows = mo.ui.slider(1000, 200000, step=1000, value=20000, label="Rows", show_value=True)
    dict_unique = mo.ui.slider(2, 1000, step=1, value=20, label="Unique values", show_value=True)
    dict_value_bytes = mo.ui.slider(1, 40, step=1, value=10, label="Average bytes per original value", show_value=True)
    _panel = mo.vstack(
        [
            mo.md("### Dictionary Encoding Intuition (Toy Model)"),
            mo.hstack([dict_rows, dict_unique], widths="equal"),
            dict_value_bytes,
            mo.md("We estimate storage in two ways:\n" "1) store full values directly, and 2) store a dictionary + compact integer codes.").callout(kind="info"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return dict_rows, dict_unique, dict_value_bytes


@app.cell
def _(dict_rows, dict_unique, dict_value_bytes, math, mo):
    _rows_count = dict_rows.value
    _unique_values = min(dict_unique.value, _rows_count)
    _bytes_per_value = dict_value_bytes.value

    _code_bits = max(1, math.ceil(math.log2(_unique_values)))
    _raw_bytes = _rows_count * _bytes_per_value
    _dictionary_bytes = _unique_values * _bytes_per_value
    _encoded_index_bytes = _rows_count * (_code_bits / 8)
    _encoded_total_bytes = _dictionary_bytes + _encoded_index_bytes
    _encoded_ratio = _encoded_total_bytes / max(_raw_bytes, 1)
    _savings = 1 - _encoded_ratio

    _table = mo.ui.table(
        [
            {
                "metric": "Raw storage (no dictionary)",
                "formula": "rows x bytes_per_value",
                "value": int(_raw_bytes),
            },
            {
                "metric": "Dictionary storage",
                "formula": "unique_values x bytes_per_value",
                "value": int(_dictionary_bytes),
            },
            {
                "metric": "Code size per row",
                "formula": "ceil(log2(unique_values)) bits",
                "value": int(_code_bits),
            },
            {
                "metric": "Encoded indexes storage",
                "formula": "rows x code_bits/8",
                "value": round(_encoded_index_bytes, 2),
            },
            {
                "metric": "Estimated encoded/ raw ratio",
                "formula": "(dictionary + indexes) / raw",
                "value": round(_encoded_ratio, 4),
            },
            {
                "metric": "Estimated savings",
                "formula": "1 - ratio",
                "value": f"{round(_savings * 100, 2)}%",
            },
        ],
        label="Dictionary encoding intuition (toy calculation)",
        selection=None, pagination=False, show_download=False, show_search=False,
    )
    _note = mo.md(
        """
    Interpretation:

    - Lower `unique values` usually means fewer bits per code and better compression.
    - If almost every row has a different value, dictionary encoding helps less.
    - Columnar formats often benefit because repeated values are common in a column.
            """
    ).callout(kind="info")

    _panel = mo.vstack([_table, _note], gap=0.6)
    _panel
    return


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
    return


@app.cell
def _(mo):
    _db_disclaimer = mo.Html(
        """
    <div class="disclaimer-red">
      Disclaimer: Databases will be discussed in-depth later in the semester in the
      <strong>Database Management for Data Scientists (DBM)</strong> module.
      Here we focus only on practical intuition for analytics workflows.
    </div>
            """
    )
    _db_disclaimer
    return


@app.cell
def _(mo):
    _section = mo.md("## 5. DuckDB Example (SQL on Files)")
    _section
    return


@app.cell
def _(mo):
    _chapter5_guide = mo.md(
        """
    ### Chapter 5 Introduction

    > **Key Question:** How can DuckDB answer a query while reading much less data?

    *Last stop in the **data tier**. Chapters 1-4 built the files; now something has to read them back.*

    DuckDB is a database engine that runs directly inside your Python process.
    No separate server is needed for this lecture demo.

    Two key ideas:

    - **Predicate pushdown**: filters are applied early, so rows that do not match are skipped.
    - **Projection pushdown**: only needed columns are read, unused columns are skipped.

    Main idea:

    $$
    \\text{work units} \\approx N \\times \\text{selectivity} \\times C_{needed}
    $$

    Lower selectivity and fewer needed columns usually mean less total work.
            """
    ).callout(kind="neutral")
    _chapter5_guide
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### DuckDB: SQL on Files, Zero Server

    DuckDB is an **embedded analytical database**:

    - **Embedded** means it runs in your app process (like a library).
    - **Analytical** means it is optimized for scans, filters, GROUP BY, joins, and aggregates.

    For this notebook, think of DuckDB as a fast SQL engine for local files.

    What "pushdown" means in plain words:

    - Predicate pushdown: if query says `WHERE amount > 600`, DuckDB tries to skip rows/blocks that cannot match.
    - Projection pushdown: if query only needs `region` and `amount`, DuckDB avoids reading irrelevant columns.

    Why it often outperforms direct plain-file scans for analytics (lower query runtime):

    - Query optimizer + vectorized execution
    - Columnar reads + pushdown
    - Fast joins and aggregations without standing up a server process

    The mini-labs below first estimate skipped work, then run an actual query timing demo.
            """
    ).callout(kind="neutral")
    _explanation
    return


@app.cell
def _(mo):
    push_rows = mo.ui.slider(10_000, 5_000_000, step=10_000, value=400_000, label="Rows (N)", show_value=True)
    push_selectivity = mo.ui.slider(0.001, 1.0, step=0.001, value=0.08, label="Filter selectivity (fraction of rows kept)", show_value=True)
    push_cols_total = mo.ui.slider(4, 80, value=24, label="Total columns", show_value=True)
    push_cols_needed = mo.ui.slider(1, 24, value=5, label="Columns used by query", show_value=True)
    _push_note = mo.md(
        """
    Model used in this mini-lab:

    - Without pushdown, approximate work is `rows x total_columns`.
    - With predicate + projection pushdown, approximate work is
      `rows x selectivity x needed_columns`.

    So this is a simplified *relative work* estimate, not exact runtime.
            """
    ).callout(kind="info")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Pushdown Intuition (What Work Gets Skipped?)"),
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
            {
                "metric": "Estimated work without pushdown",
                "formula": "rows x total_columns",
                "value": int(no_push),
            },
            {
                "metric": "Estimated work with pushdown",
                "formula": "rows x selectivity x needed_columns",
                "value": int(with_push),
            },
            {
                "metric": "Estimated reduction factor",
                "formula": "without / with",
                "value": round(gain, 2),
            },
        ],
        label="Predicate + projection pushdown estimate (toy model)",
        selection=None, pagination=False, show_download=False, show_search=False,
    )
    _panel = mo.vstack(
        [
            _table,
            mo.md("If reduction factor is high, DuckDB has a stronger chance to speed up the query.").callout(kind="info"),
        ],
        gap=0.6,
    )
    _panel
    return


@app.cell
def _(mo):
    duck_rows = mo.ui.slider(2_000, 50_000, step=2_000, value=12_000, label="Rows", show_value=True)
    duck_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Amount threshold", show_value=True)
    duck_storage = mo.ui.dropdown(
        options=["CSV scan", "CSV + DuckDB table", "Parquet + DuckDB table"],
        value="CSV + DuckDB table",
        label="Storage path",
    )
    run_duck = mo.ui.button(label="Run DuckDB demo", value=0, on_click=lambda clicks: clicks + 1, kind="success")

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
    Path,
    csv,
    duck_rows,
    duck_storage,
    duck_threshold,
    duckdb,
    format_ms,
    mo,
    pa,
    pq,
    random,
    run_duck,
    tempfile,
    time,
):
    if run_duck.value == 0:
        _output = mo.md("Click **Run DuckDB demo** to execute.").callout(kind="neutral")
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

        with tempfile.TemporaryDirectory() as _tmpdir:
            _tmpdir = Path(_tmpdir)
            _csv_path = _tmpdir / "orders.csv"
            with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                _writer = csv.DictWriter(_f, fieldnames=["order_id", "region", "segment", "amount", "day"])
                _writer.writeheader()
                _writer.writerows(_records)

            _parquet_path = _tmpdir / "orders.parquet"
            _table = pa.Table.from_pylist(_records)
            pq.write_table(_table, _parquet_path)

            _db_path = _tmpdir / "analytics.duckdb"
            _con = duckdb.connect(str(_db_path))

            _ingest_time = None
            if duck_storage.value != "CSV scan":
                _ingest_start = time.perf_counter()
                if duck_storage.value.startswith("Parquet"):
                    _con.execute(f"CREATE TABLE orders AS SELECT * FROM read_parquet('{_parquet_path}')")
                else:
                    _con.execute(f"CREATE TABLE orders AS SELECT * FROM read_csv_auto('{_csv_path}')")
                _ingest_time = time.perf_counter() - _ingest_start

            _threshold = duck_threshold.value
            _query = "SELECT region, COUNT(*) AS orders, AVG(amount) AS avg_amount " f"FROM {{source}} WHERE amount > {_threshold} GROUP BY region ORDER BY region"

            _timings = []
            _result_rows = None

            # 1) CSV scan
            _start = time.perf_counter()
            _csv_result = _con.execute(_query.format(source=f"read_csv_auto('{_csv_path}')")).fetchall()
            _timings.append(
                {
                    "source": "CSV scan",
                    "query_ms": round((time.perf_counter() - _start) * 1000, 2),
                }
            )

            # 2) Parquet scan
            _start = time.perf_counter()
            _pq_result = _con.execute(_query.format(source=f"read_parquet('{_parquet_path}')")).fetchall()
            _timings.append(
                {
                    "source": "Parquet scan",
                    "query_ms": round((time.perf_counter() - _start) * 1000, 2),
                }
            )

            # 3) DuckDB table query
            if duck_storage.value != "CSV scan":
                _start = time.perf_counter()
                _tbl_result = _con.execute(_query.format(source="orders")).fetchall()
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
            _sizes.append({"file": "orders.parquet", "size (bytes)": _parquet_path.stat().st_size})

        _results_table = [
            {
                "region": row[0],
                "orders": row[1],
                "avg_amount": round(row[2], 2),
            }
            for row in (_result_rows or [])
        ]

        _sizes_table = mo.ui.table(_sizes, label="File sizes", selection=None, pagination=False, show_download=False, show_search=False)
        _timing_table = mo.ui.table(_timings, label="Query timing (ms)", selection=None, pagination=False, show_download=False, show_search=False)
        _results_panel = mo.ui.table(_results_table, label="Query results", selection=None, pagination=False, show_download=False, show_search=False)

        _notes = []
        if _ingest_time is not None:
            _notes.append(mo.md(f"Ingest time to DuckDB table: **{format_ms(_ingest_time)}**"))
        _notes.append(mo.md("DuckDB persists a **columnar, optimized** table in a `.duckdb` file for fast scans.").callout(kind="info"))

        _output = mo.vstack([_sizes_table, _timing_table, _results_panel] + _notes, gap=0.6)

    _output
    return


@app.cell
def _(mo):
    _index_intro = mo.md(
        """
    ### Indexing Demo: Full Scan vs Indexed Search

    So far, DuckDB pushdown helped by skipping work during scans.
    Indexes solve a related but different problem:

    - Pushdown: reduce work while scanning large datasets.
    - Index: jump directly to matching rows for selective filters.

    Now we compare:

    - **Full table scan** (no index)
    - **Indexed lookup** (index on `category` + `value`)

    We also show the query plan to make the optimization explicit.
            """
    ).callout(kind="neutral")
    _index_intro
    return


@app.cell
def _(mo):
    idx_rows = mo.ui.slider(20_000, 200_000, step=20_000, value=80_000, label="Rows", show_value=True)
    idx_selectivity = mo.ui.slider(0.05, 0.9, step=0.05, value=0.2, label="Share of category = 'C'", show_value=True)
    idx_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Value threshold", show_value=True)
    idx_seed = mo.ui.slider(1, 999, value=17, label="Seed", show_value=True)
    run_index = mo.ui.button(label="Run indexing demo", value=0, on_click=lambda clicks: clicks + 1, kind="success")

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
    Path,
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
        _output = mo.md("Click **Run indexing demo** to execute.").callout(kind="neutral")
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

            _query = "SELECT COUNT(*), AVG(value) FROM events " f"WHERE category = 'C' AND value > {idx_threshold.value}"

            def _time_query():
                _best = None
                for _ in range(5):
                    _t0 = time.perf_counter()
                    _res = _con.execute(_query).fetchone()
                    _el = time.perf_counter() - _t0
                    _best = _el if _best is None else min(_best, _el)
                return _res, _best

            _states = []
            _plan_scan = _con.execute(f"EXPLAIN QUERY PLAN {_query}").fetchall()
            _scan_result, _scan_time = _time_query()
            _states.append(("no index", 0.0, _scan_time, _plan_scan[0], _scan_result))

            for _name, _sql in (
                ("index on (category)", "CREATE INDEX idx_cat ON events(category)"),
                ("index on (category, value)", "CREATE INDEX idx_cat_val ON events(category, value)"),
            ):
                _t0 = time.perf_counter()
                _con.execute(_sql)
                _con.commit()
                _build = time.perf_counter() - _t0
                _plan = _con.execute(f"EXPLAIN QUERY PLAN {_query}").fetchall()
                _res, _el = _time_query()
                _states.append((_name, _build, _el, _plan[0], _res))

            _idx_time = _states[-1][2]
            _idx_result = _states[-1][4]
            _con.close()

        _timing_table = mo.ui.table(
            [
                {
                    "state": _name,
                    "build time (ms)": round(_build * 1000, 1),
                    "query time (ms)": round(_el * 1000, 3),
                    "faster than no index": "-" if _build == 0 else f"{_scan_time / _el:.1f}x",
                }
                for _name, _build, _el, _plan, _res in _states
            ],
            label="What the index costs, and what it buys",
            selection=None, pagination=False, show_download=False, show_search=False,
        )

        _plan_table = mo.ui.table(
            [{"state": _name, "SQLite plan": str(_plan[-1])} for _name, _build, _el, _plan, _res in _states],
            label="Query plan (SQLite)",
            selection=None, pagination=False, show_download=False, show_search=False,
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
            selection=None, pagination=False, show_download=False, show_search=False,
        )

        _note = mo.md(
            """
    **An index is not a speed setting.** It is a second copy of some of your columns, and three
    things in this table say so.

    - **It is not free.** Look at the build column. That cost is paid once here, but in a real
      system it is paid again on **every insert, update and delete**, forever. A table with six
      indexes is a table where every write does seven pieces of work.
    - **Width matters more than existence.** The narrow index knows only the category, so once it
      has found the matching rows it must still visit the table to read each `value`. The wide one
      contains both columns the query asked for, so the answer never touches the table at all.
      Watch the plan say **COVERING INDEX**: that word is the whole difference.
    - **The planner decides, not you.** `CREATE INDEX` is a suggestion. SQLite looks at each
      index, estimates the cost, and is free to ignore it and scan anyway, which it will do when
      a query matches a large share of the rows. Widen the selectivity slider and watch.

    So the honest rule is not "add an index to make it fast". It is: an index pays when it holds
    what the query asks for, and the query asks for **few** rows.
            """
        ).callout(kind="info")

        _output = mo.vstack(
            [_timing_table, _plan_table, _result_table, _note],
            gap=0.6,
        )

    _output
    return


@app.cell
def _(mo):
    _schema_section = mo.md("### Schema-on-Read vs Schema-on-Write (DuckDB)")
    _schema_section
    return


@app.cell
def _(mo):
    _schema_expl = mo.md(
        """
    Two ways to deal with the fact that a file has no types of its own.

    **Schema-on-read** means you point a tool at the file and let it guess. DuckDB looks at the
    values and picks `INTEGER`, `DOUBLE`, `DATE` or `VARCHAR`. Fast to start, and forgiving: one
    bad value in a column and the whole column becomes text.

    **Schema-on-write** means you declare the blank form *first*, with its types and its rules,
    and then load into it. Slower to start, and unforgiving on purpose.

    The difference is not which one uses a cast. It is **when the check happens, and who gets
    told.** Below, the same messy export goes down both lanes. Watch what each one reports.
            """
    ).callout(kind="neutral")
    _schema_expl
    return


@app.cell
def _(mo):
    run_schema = mo.ui.button(label="Run schema demo", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _controls = mo.vstack(
        [
            mo.md(
                "We take 400 real sales, export them to CSV, and corrupt 5% of `total_price` with "
                "the things that actually appear in real exports: `n/a`, an empty cell, a European "
                "decimal comma (`1 234,50`), and a currency inside the value (`EUR 900`)."
            ).callout(kind="info"),
            run_schema,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _controls
    return (run_schema,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, random, run_schema, tempfile):
    if run_schema.value == 0:
        _output = mo.md("Click **Run schema demo** to send one messy file down both lanes.").callout(kind="neutral")
    else:
        _src = pd.read_parquet(SALES_SEED).head(400).copy()
        _src["sale_date"] = pd.to_datetime(_src["sale_date"]).dt.date
        _export = _src[["sale_id", "sale_date", "product_id", "units_sold", "total_price"]].astype(
            {"total_price": str}
        )
        _rng = random.Random(5)
        _dirty_values = ["", "1 234,50", "EUR 900", "n/a"]
        _prices = _export["total_price"].tolist()
        for _k, _row in enumerate(_rng.sample(range(len(_prices)), 20)):
            _prices[_row] = _dirty_values[_k % 4]
        _export["total_price"] = _prices

        with tempfile.TemporaryDirectory() as _td:
            _csv = Path(_td) / "sales_export.csv"
            _export.to_csv(_csv, index=False)
            _url = _csv.as_posix()
            _con = duckdb.connect()

            # Lane 1: let DuckDB guess the types, then do what a student would do next.
            _described = _con.execute(f"DESCRIBE SELECT * FROM read_csv_auto('{_url}')").df()
            _inferred = _described.set_index("column_name").loc["total_price", "column_type"]
            _counts = _con.execute(
                "SELECT count(*), count(TRY_CAST(total_price AS DOUBLE)), "
                "round(sum(TRY_CAST(total_price AS DOUBLE)), 2) "
                f"FROM read_csv_auto('{_url}')"
            ).fetchone()

            # Lane 2: declare the form first, with its rules, then try to load into it.
            _con.execute(
                """
                    CREATE TABLE sales_clean (
                        sale_id     INTEGER PRIMARY KEY,
                        sale_date   DATE    NOT NULL,
                        product_id  INTEGER NOT NULL,
                        units_sold  INTEGER NOT NULL,
                        total_price DOUBLE  NOT NULL CHECK (total_price > 0)
                    )
                    """
            )
            try:
                _con.execute(f"INSERT INTO sales_clean SELECT * FROM read_csv_auto('{_url}')")
                _write_result = "loaded without complaint"
            except Exception as _exc:
                _write_result = f"{type(_exc).__name__}: {str(_exc).splitlines()[0]}"
            _loaded = _con.execute("SELECT count(*) FROM sales_clean").fetchone()[0]

        _rows = [
            {
                "lane": "schema-on-read (guess the types)",
                "type of total_price": str(_inferred),
                "rows in the file": _counts[0],
                "rows that reached the answer": _counts[1],
                "what you are told": "nothing at all",
                "revenue reported": _counts[2],
            },
            {
                "lane": "schema-on-write (declare, then load)",
                "type of total_price": "DOUBLE NOT NULL CHECK (> 0)",
                "rows in the file": _counts[0],
                "rows that reached the answer": _loaded,
                "what you are told": _write_result[:90],
                "revenue reported": "none, the load stopped",
            },
        ]
        _note = mo.md(
            f"""
    **Same file. Same 20 bad values. Two completely different days at work.**

    Schema-on-read gave you a number, and it is wrong. {_counts[0] - _counts[1]} of {_counts[0]}
    rows were silently discarded, because `TRY_CAST` turns anything it cannot convert into `NULL`
    and `SUM` skips nulls. Nothing raised, nothing warned. The figure looks completely ordinary
    and would go straight into a report.

    Schema-on-write refused to load and named the line it choked on. You have no number yet, and
    that is the point: you have a **problem you know about** instead of an answer you trust by
    mistake.

    Neither lane is correct in the abstract. Schema-on-read is right for exploring a file you
    have just been handed. Schema-on-write is right for anything a decision rests on.
                """
        ).callout(kind="warn")
        _output = mo.vstack(
            [mo.ui.table(_rows, label="One messy export, two lanes", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
        )
    _output
    return


@app.cell
def _(mo):
    run_evolution = mo.ui.button(label="Run schema evolution demo", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Add One Column, Then Read Last Year's Files"),
            mo.md(
                "Chapter 2 showed a *format* handling a changed form. This is the same problem one "
                "tier up, where you keep one file per year in a folder and read them together. "
                "We split the real sales into `sales_2024.parquet`, written **before** anyone "
                "thought of `customer_rating`, and `sales_2025.parquet`, written after."
            ).callout(kind="info"),
            run_evolution,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_evolution,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, run_evolution, tempfile):
    if run_evolution.value == 0:
        _output = mo.md("Click **Run schema evolution demo** to ask the same question three ways.").callout(kind="neutral")
    else:
        _all = pd.read_parquet(SALES_SEED)
        _all["sale_date"] = pd.to_datetime(_all["sale_date"])
        _old = _all[_all["sale_date"] < "2025-01-01"].drop(columns=["customer_rating"])
        _new = _all[_all["sale_date"] >= "2025-01-01"]

        with tempfile.TemporaryDirectory() as _td:
            _dir = Path(_td)
            _f2024 = _dir / "sales_2024.parquet"
            _f2025 = _dir / "sales_2025.parquet"
            _old.to_parquet(_f2024, index=False)
            _new.to_parquet(_f2025, index=False)
            _con = duckdb.connect()
            _question = "SELECT count(*) AS rows, round(avg(customer_rating), 3) AS avg_rating FROM "

            def _try(_from_clause):
                try:
                    _r = _con.execute(_question + _from_clause).fetchone()
                    return f"rows {_r[0]}, average rating {_r[1]}"
                except Exception as _exc:
                    return f"{type(_exc).__name__}: {str(_exc).splitlines()[0][:95]}"

            _list_old_first = f"read_parquet(['{_f2024.as_posix()}', '{_f2025.as_posix()}'])"
            _list_new_first = f"read_parquet(['{_f2025.as_posix()}', '{_f2024.as_posix()}'])"
            _by_name = f"read_parquet('{(_dir / 'sales_*.parquet').as_posix()}', union_by_name=true)"

            _rows = [
                {
                    "how you read the folder": "old file first",
                    "what happens": _try(_list_old_first),
                    "why": "the first file sets the shape, so the newer column is simply not there",
                },
                {
                    "how you read the folder": "new file first",
                    "what happens": _try(_list_new_first),
                    "why": "now the shapes disagree and the read is refused outright",
                },
                {
                    "how you read the folder": "union_by_name=true",
                    "what happens": _try(_by_name),
                    "why": "match columns by name, fill the missing ones with NULL",
                },
            ]

        _note = mo.md(
            """
    **Same data, same question, three different answers, and only one is right.**

    The first is the dangerous one. Nothing failed: you asked for the average rating and the
    column had quietly vanished, because the first file read decided what the shape was. The
    second at least had the decency to shout. Only the third gives the honest answer, over the
    rows that actually have a rating.

    This is what "schema evolution" means once your data lives in more than one file. The rule to
    take away: **when a folder of files has grown new columns over time, say so when you read
    it.** The default is not to guess kindly.
                """
        ).callout(kind="warn")
        _output = mo.vstack(
            [mo.ui.table(_rows, label="One folder, two file shapes, three readings", selection=None, pagination=False, show_download=False, show_search=False), _note],
            gap=0.6,
        )
    _output
    return


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
    return


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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 6. REST API Demo (GET, POST, PUT, DELETE)")
    _section
    return


@app.cell
def _(mo):
    _chapter6_guide = mo.md(
        """
    ### Chapter 6 Introduction

    > **Key Question:** Did the client and server agree on the same contract?

    *We move up to the **logic tier**. The data tier is finished; now other programs need to ask for that data.*

    An API is a contract between systems.
    Most API bugs are contract mismatches (interface mismatches): wrong path, wrong payload shape, or wrong status handling.

    Quick basics:

    - **HTTP** is the message protocol used by clients and servers on the web.
    - **HTTPS** is HTTP with encryption (TLS), so data is protected in transit.
    - In practice: same API idea, but HTTPS is the secure default.

    Keep this mapping in mind:

    - 2xx: success
    - 4xx: client-side issue
    - 5xx: server-side issue

    Reference list of status codes:
    https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

    Status family is computed from the code:

    $$
    \\text{family} = \\left\\lfloor \\frac{\\text{status code}}{100} \\right\\rfloor
    $$
            """
    ).callout(kind="neutral")
    _chapter6_guide
    return


@app.cell
def _(mo):
    rest = mo.md(
        """
    ### REST Principles (Quick Recap)

    First the four words this whole chapter is built from:

    - A **resource** is one thing the server knows about, like a product or a sale.
    - A **path** is the address of a resource, like `/products/8`.
    - An **endpoint** is one path combined with one verb, like `GET /products/8`.
    - A **payload** is the data you send along with a request, written as JSON.

    The four verbs say what you want done to a resource:

    - **GET**: fetch a resource  
    - **POST**: create a new resource  
    - **PUT**: update a resource  
    - **DELETE**: remove a resource  

    One more word, because the next mini-lab turns on it. **Idempotent** means pressing it twice
    changes nothing more than pressing it once. The button to call a lift is idempotent: jab it
    ten times, one lift comes. A ticket dispenser is not: press it ten times and you are holding
    ten tickets.

    GET, PUT and DELETE are lift buttons. POST is a ticket dispenser. That is the whole reason a
    failed POST is frightening to retry and a failed PUT is not: when the network drops before
    the answer arrives, you cannot tell whether the server acted, and only for POST does guessing
    wrong cost you a duplicate.

    *The lift button suggests nothing happens on the second press, and something does.* The
    request really is sent and really is processed. Idempotent means the **end state** is the
    same, not that the work is skipped.

    Core REST constraints (why it scales):

    - **Stateless** — the server keeps no memory of *you* between requests: no notion of where
      you are in a conversation, what you asked last, or which page you were on. Every request
      must carry everything needed to answer it. It absolutely does remember your **data**, which
      is what the whole data tier was for. Session state no, resource state yes. That distinction
      is what lets a second copy of the server answer your next request without anyone noticing.
    - **Uniform interface** — the same four verbs work on every resource, so once you
      can read one endpoint you can read all of them.
    - **Cacheable** — a response may say "this stays valid for a while", so the answer
      can be reused instead of recomputed.
    - **Layered** — the client talks only to the next layer, never past it. That is the
      tier idea from the start of this notebook, applied to the network.

    In a JSON API, the payload is the state representation:

    $$
    \\text{Resource} \\xleftrightarrow[\\text{response}]{\\text{request}} \\text{Representation}
    $$
            """
    ).callout(kind="neutral")
    rest
    return


@app.cell
def _(mo):
    _status_real = mo.md(
        """
    ### Four Real Answers From Our Own API

    Not a lookup table. These are the actual replies `sw03_demo_api.py` gives, and the difference
    between the three failures is the part worth learning.

    | You send | You get | Why |
    | --- | --- | --- |
    | `POST /sales` with a valid sale | **201 Created** | it worked, and a new thing now exists |
    | `GET /sales/999999` | **404 Not Found** | the address is fine, nothing lives there |
    | `POST /countries` with `region_id: 999` | **400 Bad Request** | the form is fine, what it asks for is impossible |
    | `POST /sales` with `customer_rating: 9` | **422 Unprocessable** | the form itself is malformed, the server never looked |

    All three failures are **4xx**, and that first digit is the instruction: *you* must change the
    request. Retrying it unchanged will fail identically forever. A **5xx** is the opposite
    message: the request was fine and the server broke, so retrying may well work.

    The distinction between 400 and 422 is the one students trip on. 422 means the request never
    reached your logic, because Pydantic rejected the shape at the door, which is chapter 7 doing
    its job. 400 means it got through the door and then broke a rule of the business, like
    pointing at a region that does not exist.
        """
    ).callout(kind="neutral")
    _status_real
    return


@app.cell
def _(mo):
    method = mo.ui.dropdown(options=["GET", "POST", "PUT", "DELETE"], value="GET", label="HTTP method")
    base_url = mo.ui.text(value="https://httpbin.org", label="Base URL")
    path = mo.ui.text(value="/anything", label="Path")
    payload = mo.ui.text_area(value='{"message": "hello"}', label="JSON payload (for POST/PUT)")
    use_live_http = mo.ui.switch(value=False, label="Use live HTTP (requires internet)")
    mock_latency = mo.ui.slider(0, 1500, step=100, value=200, label="Mock latency (ms)", show_value=True)
    send = mo.ui.button(label="Send request", value=0, on_click=lambda clicks: clicks + 1, kind="success")

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
    mo,
    mock_latency,
    path,
    payload,
    send,
    time,
    url_error,
    url_request,
    use_live_http,
):
    if send.value == 0:
        _output = mo.md("Click **Send request** to call the API.").callout(kind="neutral")
    else:
        url = base_url.value.rstrip("/") + "/" + path.value.lstrip("/")
        _meta = mo.md(f"**Request #{send.value}** · `{method.value}` `{url}`").callout(kind="info")

        data_bytes = None
        headers = {"Accept": "application/json"}
        _response_panel = None

        if method.value in {"POST", "PUT", "DELETE"}:
            try:
                payload_obj = json.loads(payload.value) if payload.value.strip() else {}
                data_bytes = json.dumps(payload_obj).encode("utf-8")
                headers["Content-Type"] = "application/json"
            except json.JSONDecodeError as exc:
                _response_panel = mo.md(f"Invalid JSON payload: `{exc}`").callout(kind="danger")

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
            if use_live_http.value:
                try:
                    req = url_request.Request(url, data=data_bytes, headers=headers, method=method.value)
                    with url_request.urlopen(req, timeout=10) as _response:
                        body = _response.read().decode("utf-8", errors="replace")
                        status = _response.status
                except url_error.HTTPError as http_error:
                    # 404, 409, 500 ... are real answers from the server, not failures.
                    body = http_error.read().decode("utf-8", errors="replace")
                    status = http_error.code
                except Exception as exc:
                    _response_panel = mo.md(
                        f"Could not reach `{url}`: `{exc}`. Check the base URL and that the server is running."
                    ).callout(kind="danger")
                if _response_panel is None:
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
    return


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
    return


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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 7. Pydantic Models")
    _section
    return


@app.cell
def _(mo):
    _chapter7_guide = mo.md(
        """
    ### Chapter 7 Introduction

    > **Key Question:** Which inputs are allowed into the trusted system boundary?

    *Still in the **logic tier**. Chapter 6 agreed on a contract; now we enforce it.*

    Validation is the system's input acceptance policy (formal schema enforcement rules).
    With early validation, downstream code becomes simpler and safer.

    Formal model:

    $$
    \\text{trusted internal data} = \\text{untrusted input} + \\text{validation rules}
    $$
            """
    ).callout(kind="neutral")
    _chapter7_guide
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### Pydantic = Validated Data Models

    Pydantic turns raw data into **validated Python objects**, guided by type hints.

    A **type hint** is the note after a colon that says what kind of value a name should hold:

    ```python
    name: str        # this should be text
    age: int         # this should be a whole number
    gpa: float       # this should be a decimal number
    ```

    Plain Python does not enforce these; they are documentation. Pydantic reads the same
    hints and *does* enforce them, which is why one line of description becomes a real check.

    Example constraint:

    $$
    0 \\leq \\text{gpa} \\leq 4
    $$

    Where:
    - $gpa$: grade-point average score constrained to the valid range

    Try editing the JSON below to trigger validation errors and see the message structure.

    **Then run the last two presets, which are the point of this chapter.**

    `garbage_that_passes` sends a negative id, a name of three spaces, a gpa of 0.0 and
    `"definitely not an email"`. Every field is the declared type and inside its declared range,
    so pydantic **accepts all of it**.

    `silently_coerced` sends `"42"` and `"3.5"` as text. Pydantic does not reject them; it
    converts them and hands you numbers.

    So validation checks **shape**, not **truth**. It is a bouncer with a list of rules, not a
    person who knows whether the answer makes sense. A negative id and a blank name are shaped
    correctly and are still garbage, and the only way to stop them is to write the rule down:
    `id: int = Field(gt=0)`, `name: str = Field(min_length=1)`, `email: EmailStr`. Validation is
    exactly as good as the rules you thought to write.
            """
    ).callout(kind="neutral")
    _explanation
    return


@app.cell
def _(mo):
    payload_case = mo.ui.dropdown(
        options=[
            "valid",
            "missing_email",
            "gpa_out_of_range",
            "wrong_type",
            "garbage_that_passes",
            "silently_coerced",
        ],
        value="valid",
        label="Preset payload scenario",
    )
    payload_templates = {
        "valid": {
            "id": 1,
            "name": "Ada",
            "gpa": 3.8,
            "email": "ada@example.com",
        },
        "missing_email": {
            "id": 2,
            "name": "Lin",
            "gpa": 3.4,
        },
        "gpa_out_of_range": {
            "id": 3,
            "name": "Mira",
            "gpa": 5.2,
            "email": "mira@example.com",
        },
        "wrong_type": {
            "id": "not-an-int",
            "name": "Sam",
            "gpa": "high",
            "email": "sam@example.com",
        },
        # Every field is the declared type and inside its declared range.
        # Every field is also nonsense. Pydantic accepts all of it.
        "garbage_that_passes": {
            "id": -7,
            "name": "   ",
            "gpa": 0.0,
            "email": "definitely not an email",
        },
        # Nothing here is the declared type, and nothing is rejected either.
        "silently_coerced": {
            "id": "42",
            "name": "Ada",
            "gpa": "3.5",
            "email": "ada@example.com",
        },
    }
    _model_code = mo.md(
        """
    ### Pydantic model used in this mini-lab

    ```python
    from pydantic import BaseModel, Field

    class Student(BaseModel):
        id: int
        name: str
        gpa: float = Field(ge=0.0, le=4.0)
        email: str
    ```
            """
    ).callout(kind="neutral")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Interactive Payload Validation"),
            payload_case,
            mo.md("Choose a preset scenario, then edit the JSON below and click **Validate with Pydantic**.").callout(kind="info"),
            _model_code,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return payload_case, payload_templates


@app.cell
def _(json, mo, payload_case, payload_templates):
    selected_payload = payload_templates[payload_case.value]
    selected_payload_text = json.dumps(selected_payload, indent=2)
    expected_result = {
        "valid": "should pass",
        "missing_email": "should fail (missing required field)",
        "gpa_out_of_range": "should fail (gpa > 4.0)",
        "wrong_type": "should fail (type mismatch)",
    }[payload_case.value]

    _preview = mo.md(
        f"""
    Selected preset expectation: **{expected_result}**

    ```json
    {selected_payload_text}
    ```
            """
    ).callout(kind="info")
    _preview
    return (selected_payload_text,)


@app.cell
def _(mo, selected_payload_text):
    input_data = mo.ui.text_area(
        value=selected_payload_text,
        label="Student JSON",
    )
    validate = mo.ui.button(label="Validate with Pydantic", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _controls = mo.vstack([input_data, validate], gap=0.6).callout(kind="neutral")
    _controls
    return input_data, validate


@app.cell
def _(input_data, json, mo, pydantic, validate):
    if validate.value == 0:
        _output = mo.md("Click **Validate with Pydantic** to parse.").callout(kind="neutral")
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
            obj = Student.model_validate(raw)   # raises if the data breaks a rule
            data = obj.model_dump()             # back to a plain dictionary
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
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 8. FastAPI Demo + Automatic Docs")
    _section
    return


@app.cell
def _(mo):
    _chapter8_guide = mo.md(
        """
    ### Chapter 8 Introduction

    > **Key Question:** How do we keep implementation and API documentation in sync?

    *Last stop in the **logic tier**. We turn the rules from chapter 7 into a running server.*

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
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### FastAPI = Type Hints → OpenAPI

    FastAPI uses the type hints from chapter 7 plus Pydantic to build validated endpoints.
    Write the model once and the documentation comes out for free:

    Most restaurants write the menu by hand. Then the kitchen changes a recipe and the menu
    quietly starts lying, and every customer who orders from it is disappointed. FastAPI does not
    let that happen, because **the menu is printed from the recipes**. You wrote
    `customer_rating: int = Field(ge=1, le=5)` once, in the model. That one line becomes the
    machine-readable menu, the buttons a human clicks, and the rule the server enforces. Change
    the 5 to a 10 and all three change together, because there is only one 5.

    *What the menu cannot tell you* is whether the food is good. It describes shapes, not
    behaviour: nothing in it says that `total_price` is recomputed when you change `units_sold`.

    - **OpenAPI** (`/openapi.json`) is a standard file format that describes every endpoint
      an API has, in a way other programs can read. FastAPI writes it for you.
    - **Swagger UI** (`/docs`) is a web page that reads that file and turns it into buttons
      you can click to try each endpoint. This is the page we use below.
    - **ReDoc** (`/redoc`) reads the same file and renders it as a reference manual instead.

    You start the server with **uvicorn**, the program that actually listens on a port and
    hands incoming requests to your FastAPI code:

    ```bash
    uvicorn sw03_demo_api:app --reload
    ```

    `sw03_demo_api` is the file, `app` is the variable inside it, and `--reload` restarts the
    server whenever you save a change.

    The type hints become a formal schema:

    $$
    \\text{Python Types} \\rightarrow \\text{JSON Schema} \\rightarrow \\text{Interactive Docs}
    $$
            """
    ).callout(kind="neutral")
    _explanation
    return


@app.cell
def _(mo):
    fastapi_code = mo.md(
        """
    ```python
    # file: sw03_demo_api.py
    from fastapi import FastAPI
    from pydantic import BaseModel, Field

    app = FastAPI(title="Sales Analysis API", version="3.0.0")

    class ProductCreate(BaseModel):          # what the client is allowed to send
        name: str = Field(min_length=1, max_length=120)
        price: float = Field(gt=0)
        description: str = Field(min_length=1, max_length=300)
        category_id: int = Field(ge=1)

    class Product(ProductCreate):            # what the server sends back
        product_id: int
        category_name: str

    @app.get("/products/{product_id}", response_model=Product, tags=["Products"])
    def get_product(product_id: int) -> Product:
        'Fetch one product by id.'         # this line becomes the description in /docs
        ...                                 # full implementation is in sw03_demo_api.py

    @app.post("/products", response_model=Product, status_code=201, tags=["Products"])
    def create_product(payload: ProductCreate) -> Product:
        'Create a product.'
        ...

    @app.delete("/products/{product_id}", status_code=204, tags=["Products"])
    def delete_product(product_id: int) -> None:
        'Delete a product. Refused while sales still reference it.'
        ...
    ```

    Read the three decorators as a sentence: *verb*, *path*, and the shape of the answer.
    The `tags` group the endpoints in `/docs`, and the docstring under each function becomes
    its description there. Nothing else had to be written to get documentation.

    This repo includes the full implementation in `sw03_demo_api.py`.

    Run from the project root with:

    ```
    uvicorn sw03_demo_api:app --reload
    ```

    Then open `http://127.0.0.1:8000/docs`.
            """
    )
    fastapi_code
    return


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
    return


@app.cell
def _(mo):
    fastapi_base_url = mo.ui.text(value="http://127.0.0.1:8000", label="API base URL")
    fastapi_check = mo.ui.button(label="1) Check API status", value=0, on_click=lambda clicks: clicks + 1, kind="neutral")
    fastapi_payload = mo.ui.text_area(
        value='{"name": "Lecture Demo Widget", "price": 99.9, "description": "Created live in Chapter 8", "category_id": 1}',
        label="POST /products payload (JSON)",
    )
    fastapi_post = mo.ui.button(label="2) POST /products", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    fastapi_item_id = mo.ui.text(value="1", label="Product id for GET /products/{id}")
    fastapi_get = mo.ui.button(label="3) GET /products/{id}", value=0, on_click=lambda clicks: clicks + 1, kind="neutral")

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
        _output = mo.md("Click **1) Check API status** after starting `uvicorn sw03_demo_api:app --reload`.").callout(kind="neutral")
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
    return


@app.cell
def _(
    fastapi_base_url,
    fastapi_payload,
    fastapi_post,
    json,
    mo,
    url_error,
    url_request,
):
    _output = mo.md("Waiting for POST request...").callout(kind="neutral")
    if fastapi_post.value == 0:
        _output = mo.md("Edit the payload, then click **2) POST /products**.").callout(kind="neutral")
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
    return


@app.cell
def _(
    fastapi_base_url,
    fastapi_get,
    fastapi_item_id,
    json,
    mo,
    url_error,
    url_request,
):
    _output = mo.md("Waiting for GET request...").callout(kind="neutral")
    if fastapi_get.value == 0:
        _output = mo.md("Click **3) GET /products/{id}** to fetch a product.").callout(kind="neutral")
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
    return


@app.cell
def _(mo):
    run_gates = mo.ui.button(label="Send six slips through both gates", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Six Sale Slips, One Model, Two Gates"),
            mo.md(
                """
    Chapter 7 validated a payload on your laptop with no network at all, because Pydantic is just
    Python. Chapter 8 put the very same kind of model on a server. So what is the difference?

    Six slips go through **gate 1** here in the notebook, and then the identical six are sent to
    the running API for **gate 2**. Read the table across.
                """
            ).callout(kind="info"),
            run_gates,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_gates,)


@app.cell
def _(fastapi_base_url, json, mo, pydantic, run_gates, url_error, url_request):
    if run_gates.value == 0:
        _output = mo.md("Click **Send six slips through both gates** to compare them.").callout(kind="neutral")
    else:
        from datetime import date as _date

        class _SaleCreate(pydantic.BaseModel):
            # The same shape sw03_demo_api.py declares, running here on your laptop.
            sale_date: _date
            product_id: int = pydantic.Field(ge=1)
            country_id: int = pydantic.Field(ge=1)
            units_sold: int = pydantic.Field(ge=1, le=100000)
            customer_rating: int = pydantic.Field(ge=1, le=5)

        _ok = {"sale_date": "2026-03-01", "product_id": 1, "country_id": 3, "units_sold": 10, "customer_rating": 5}
        _slips = {
            "a good sale": _ok,
            "rating of 9": {**_ok, "customer_rating": 9},
            "zero units sold": {**_ok, "units_sold": 0},
            "date as 01/03/2026": {**_ok, "sale_date": "01/03/2026"},
            "no country at all": {_k: _v for _k, _v in _ok.items() if _k != "country_id"},
            "product 9999": {**_ok, "product_id": 9999},
        }

        _base = fastapi_base_url.value.rstrip("/")
        _created, _rows = [], []
        try:
            for _name, _slip in _slips.items():
                try:
                    _SaleCreate.model_validate(_slip)
                    _gate1 = "passes"
                except Exception as _exc:
                    _err = _exc.errors()[0]
                    _gate1 = f"rejected: {_err['loc'][0]} — {_err['msg']}"
                try:
                    _req = url_request.Request(
                        f"{_base}/sales",
                        data=json.dumps(_slip).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with url_request.urlopen(_req, timeout=10) as _r:
                        _body = json.loads(_r.read())
                        _created.append(_body["sale_id"])
                        _gate2 = f"{_r.status} created — {len(_body)} fields back, total_price {_body['total_price']}"
                except url_error.HTTPError as _http:
                    _detail = json.loads(_http.read()).get("detail")
                    _msg = _detail if isinstance(_detail, str) else _detail[0]["msg"]
                    _gate2 = f"{_http.code} — {_msg}"
                _rows.append({"the slip": _name, "gate 1: your laptop": _gate1, "gate 2: the server": _gate2})

            for _sid in _created:
                try:
                    url_request.urlopen(
                        url_request.Request(f"{_base}/sales/{_sid}", method="DELETE"), timeout=10
                    )
                except Exception:
                    pass

            _note = mo.md(
                """
    **Read the last column down.** Four slips die at gate 1 and would have died at gate 2 too,
    with `422` and the *same message*, because it is the same model in both places. One slip,
    `product 9999`, sails through gate 1 and dies at gate 2 with `400`. And one gets `201`.

    That difference is the whole lesson. Gate 1 can check **shape**: is this a date, is the rating
    between 1 and 5. Only gate 2 can check **facts**, because only the server can open the filing
    cabinet and discover there is no product 9999. Your laptop had no way to know.

    **Then look at the successful row.** We sent five fields and got thirteen back, and we never
    sent `total_price` at all: the server computed 10 x 195.00 itself. A price the client is
    allowed to invent is a price the client can lie about.

    Two fences. Validating on the laptop is a **courtesy** to the user, instant feedback with no
    round trip, and never a substitute for the server's check, because anyone can bypass this
    notebook and post directly with `curl`. And the split between 422 and 400 is this API's
    convention, not a law of HTTP: FastAPI produces the 422 automatically from the model, while
    the 400s are business rules somebody wrote by hand.
                    """
            ).callout(kind="info")
            _output = mo.vstack(
                [mo.ui.table(_rows, label="The same six slips, checked twice", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
            )
        except url_error.URLError as _exc:
            _output = mo.md(
                f"Could not reach `{_base}`. Start the API first: `uvicorn sw03_demo_api:app --reload`. ({_exc})"
            ).callout(kind="danger")
    _output
    return


@app.cell
def _(mo):
    run_twice = mo.ui.button(label="Press every verb twice", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Press It Twice"),
            mo.md(
                "The lift button or the ticket dispenser? Let us stop asserting it. Each verb is "
                "sent to the running API **twice in a row**, against one sale, and we look at what "
                "changed. Needs the API from chapter 8."
            ).callout(kind="info"),
            run_twice,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_twice,)


@app.cell
def _(fastapi_base_url, json, mo, run_twice, url_error, url_request):
    if run_twice.value == 0:
        _output = mo.md("Click **Press every verb twice** to test it against the running API.").callout(kind="neutral")
    else:
        _base = fastapi_base_url.value.rstrip("/")

        def _call(_method, _path, _body=None):
            _data = json.dumps(_body).encode("utf-8") if _body is not None else None
            _req = url_request.Request(
                f"{_base}{_path}", data=_data, headers={"Content-Type": "application/json"}, method=_method
            )
            try:
                with url_request.urlopen(_req, timeout=10) as _r:
                    return _r.status, (json.loads(_r.read()) if _r.status != 204 else None)
            except url_error.HTTPError as _err:
                return _err.code, None

        _sale = {
            "sale_date": "2026-03-01",
            "product_id": 1,
            "country_id": 3,
            "units_sold": 10,
            "customer_rating": 5,
        }

        try:
            def _sales_count():
                return len(_call("GET", "/sales?limit=20000")[1])

            _before = _sales_count()
            _post1, _first = _call("POST", "/sales", _sale)
            _post2, _second = _call("POST", "/sales", _sale)
            _after = _sales_count()
            _sale_id = _first["sale_id"]

            _put1, _ = _call("PUT", f"/sales/{_sale_id}", {"units_sold": 25})
            _put2, _ = _call("PUT", f"/sales/{_sale_id}", {"units_sold": 25})
            _units = _call("GET", f"/sales/{_sale_id}")[1]["units_sold"]

            _get1, _ = _call("GET", f"/sales/{_sale_id}")
            _get2, _ = _call("GET", f"/sales/{_sale_id}")

            _del1, _ = _call("DELETE", f"/sales/{_sale_id}")
            _del2, _ = _call("DELETE", f"/sales/{_sale_id}")

            _call("DELETE", f"/sales/{_second['sale_id']}")  # tidy up the duplicate

            _rows = [
                {
                    "verb": "GET",
                    "first press": _get1,
                    "second press": _get2,
                    "what changed in the world": "nothing",
                    "lift button?": "yes",
                },
                {
                    "verb": "POST",
                    "first press": _post1,
                    "second press": _post2,
                    "what changed in the world": f"sales went {_before} to {_after}: a SECOND sale was booked",
                    "lift button?": "NO",
                },
                {
                    "verb": "PUT",
                    "first press": _put1,
                    "second press": _put2,
                    "what changed in the world": f"units_sold is {_units} either way",
                    "lift button?": "yes",
                },
                {
                    "verb": "DELETE",
                    "first press": _del1,
                    "second press": _del2,
                    "what changed in the world": "the sale is gone, both times",
                    "lift button?": "yes",
                },
            ]
            _note = mo.md(
                """
    **GET, PUT and DELETE are safe to press twice. The world ends up the same.** POST is not: the
    second press booked a second sale. That is exactly why a checkout page begs you not to hit
    refresh, and why a payment that times out is frightening in a way a profile edit is not.

    **Now the trap.** The second DELETE answered `404`, not `204`. That looks like a
    contradiction, and it is not. Idempotent is a promise about the **effect on the world**, not
    about the status code. The sale is equally gone after one press or five; only the answer to
    "did *you* delete it" changed.

    One more honest note: idempotence is a promise the API author makes, not something HTTP
    enforces. A carelessly written `PUT` can behave exactly like `POST`. It holds here because
    this server updates a row you named by id, not because the word PUT is magic.
                """
            ).callout(kind="info")
            _output = mo.vstack(
                [mo.ui.table(_rows, label="Each verb, sent twice", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
            )
        except url_error.URLError as _exc:
            _output = mo.md(
                f"Could not reach `{_base}`. Start the API first: `uvicorn sw03_demo_api:app --reload`. ({_exc})"
            ).callout(kind="danger")
    _output
    return


@app.cell
def _(mo):
    run_follow = mo.ui.button(label="Follow the sale into the file", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Where Does a POST Actually Go?"),
            mo.md(
                "We count the rows in `data/sales.parquet`, POST one sale through the API, count "
                "again, and then put the row that landed in the file next to the JSON that came "
                "back. Needs the API running."
            ).callout(kind="info"),
            run_follow,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_follow,)


@app.cell
def _(
    Path,
    duckdb,
    fastapi_base_url,
    json,
    mo,
    run_follow,
    url_error,
    url_request,
):
    if run_follow.value == 0:
        _output = mo.md("Click **Follow the sale into the file** to watch the tiers hand over.").callout(kind="neutral")
    else:
        _sales_file = Path(mo.notebook_dir()) / "data" / "sales.parquet"
        if not _sales_file.exists():
            _output = mo.md("Needs a running API (which creates `data/sales.parquet`).").callout(kind="warn")
        else:
            _base = fastapi_base_url.value.rstrip("/")

            def _call(_method, _path, _body=None):
                _data = json.dumps(_body).encode("utf-8") if _body is not None else None
                _req = url_request.Request(
                    f"{_base}{_path}", data=_data, headers={"Content-Type": "application/json"}, method=_method
                )
                with url_request.urlopen(_req, timeout=10) as _r:
                    return json.loads(_r.read()) if _r.status != 204 else None

            try:
                _con = duckdb.connect()
                _url = _sales_file.as_posix()
                _before = _con.execute(f"SELECT count(*) FROM '{_url}'").fetchone()[0]
                _created = _call(
                    "POST",
                    "/sales",
                    {
                        "sale_date": "2026-03-01",
                        "product_id": 1,
                        "country_id": 3,
                        "units_sold": 10,
                        "customer_rating": 5,
                    },
                )
                _after = _con.execute(f"SELECT count(*) FROM '{_url}'").fetchone()[0]
                _stored = _con.execute(
                    f"SELECT * FROM '{_url}' WHERE sale_id = {int(_created['sale_id'])}"
                ).df()
                _file_cols = list(_stored.columns)
                _call("DELETE", f"/sales/{int(_created['sale_id'])}")  # leave the file as we found it

                _rows = [
                    {
                        "": "what the FILE keeps",
                        "fields": len(_file_cols),
                        "names of things": "none, only ids",
                        "shape": ", ".join(_file_cols),
                    },
                    {
                        "": "what the API RETURNS",
                        "fields": len(_created),
                        "names of things": "product, category, country, region",
                        "shape": ", ".join(list(_created)),
                    },
                ]
                _note = mo.md(
                    f"""
    **The file grew by one: {_before:,} rows to {_after:,}.**

    The logic tier did not invent a database. It wrote to the same Parquet file you compressed in
    chapter 4 and queried in chapter 5. Your POST travelled all the way down.

    Now compare the two shapes, because this is what a tier is *for*. The **file** keeps
    {len(_file_cols)} columns and stores `product_id 1`, `country_id 3`: ids, no names, every fact
    written exactly once. That is the normalisation the data tier cares about. The **response**
    has {len(_created)} fields, with "Edge Sensor X1", "Germany" and "Europe" spelled out. The
    logic tier did the joining, so the chart in chapter 10 does not have to.

    **One honest callback.** We just read that file while a server might have been writing it.
    Pandas rewrites the whole Parquet file on every change, so a read at the wrong instant could
    catch it half-written. That is precisely the isolation problem from chapter 1, and it is the
    reason a real system puts a database at the bottom of the data tier rather than a file.
                    """
                ).callout(kind="info")
                _output = mo.vstack(
                    [mo.ui.table(_rows, label="Same sale, two tiers, two shapes", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
                )
            except url_error.URLError as _exc:
                _output = mo.md(
                    f"Could not reach `{_base}`. Start the API first: `uvicorn sw03_demo_api:app --reload`. ({_exc})"
                ).callout(kind="danger")
    _output
    return


@app.cell
def _(mo):
    run_two_analysts = mo.ui.button(label="Run the two-analyst test", value=0, on_click=lambda clicks: clicks + 1, kind="success")
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Two People, One Product, Both Click Save"),
            mo.md(
                """
    **Predict first, then run it.**

    Anna and Ben both open product 1 in a browser tab, at the same starting price. Anna applies a
    10% raise. Ben adds a 20 franc surcharge. Both click save. Both see "saved", and both get
    `200 OK` from the API you built.

    **What is the price afterwards?**
                """
            ).callout(kind="info"),
            run_two_analysts,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (run_two_analysts,)


@app.cell
def _(fastapi_base_url, json, mo, run_two_analysts, url_error, url_request):
    if run_two_analysts.value == 0:
        _output = mo.md("Write your prediction down, then click **Run the two-analyst test**.").callout(kind="neutral")
    else:
        _base = fastapi_base_url.value.rstrip("/")

        def _read_price():
            with url_request.urlopen(f"{_base}/products/1", timeout=10) as _r:
                return float(json.loads(_r.read())["price"])

        def _save_price(_new_price):
            _req = url_request.Request(
                f"{_base}/products/1",
                data=json.dumps({"price": _new_price}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            with url_request.urlopen(_req, timeout=10) as _r:
                return _r.status, float(json.loads(_r.read())["price"])

        try:
            _start = _read_price()
            # Both analysts open the page. Two ordinary GETs, nothing concurrent.
            _anna_sees = _read_price()
            _ben_sees = _read_price()
            # Both save, strictly one after the other.
            _anna_status, _after_anna = _save_price(round(_anna_sees * 1.10, 2))
            _ben_status, _after_ben = _save_price(round(_ben_sees + 20, 2))
            _final = _read_price()
            _correct = round(round(_start * 1.10, 2) + 20, 2)

            _steps = [
                {"step": "1. price before anyone touches it", "value": _start, "server said": "-"},
                {"step": "2. Anna opens the product", "value": _anna_sees, "server said": "200 OK"},
                {"step": "3. Ben opens the same product", "value": _ben_sees, "server said": "200 OK"},
                {"step": "4. Anna saves a 10% raise", "value": _after_anna, "server said": f"{_anna_status} OK"},
                {"step": "5. Ben saves a 20 surcharge", "value": _after_ben, "server said": f"{_ben_status} OK"},
                {"step": "6. price afterwards", "value": _final, "server said": "-"},
                {"step": "what it should have been", "value": _correct, "server said": "-"},
            ]
            _lost = round(_correct - _final, 2)
            _note = mo.md(
                f"""
    **Anna's raise is gone. {_lost:.2f} of it, and nobody was told.**

    Look at what did *not* happen. No error. No warning. No conflict. Two `200 OK` responses, two
    users who saw "saved", and a price that is simply wrong.

    Now look back at **chapter 1**. This is the same lost update as the shared counter, the one we
    watched disappear from a text file, and it survived everything we have built since. It is not
    a threading accident either: these six requests ran strictly one after another, so this fails
    identically every single time you click the button. The bug is structural, not a timing fluke.

    Why did the database not save us? Because *there is no transaction around what actually
    happened here*. The read and the write were two separate HTTP requests, minutes apart in real
    life, and the API has no idea they were meant to belong together. Ben's `PUT` carried a price
    computed from a page he opened before Anna saved. Chapter 1's lesson holds exactly as stated:
    a transaction protects the steps you put inside it, and nothing else.

    **The fix is not more locking.** It is to stop sending *the answer* and start sending *the
    change* (`{{"raise_percent": 10}}`), or to make the client say which version it read and let
    the server refuse if that version is stale. This is the one thing the whole day has been
    circling: correctness is a property of the design, not of the tools.
                """
            ).callout(kind="danger")
            _output = mo.vstack(
                [mo.ui.table(_steps, label="Six requests, strictly in order", selection=None, pagination=False, show_download=False, show_search=False), _note], gap=0.6
            )
        except url_error.URLError as _exc:
            _output = mo.md(
                f"Could not reach `{_base}`. Start the API first: `uvicorn sw03_demo_api:app --reload`. ({_exc})"
            ).callout(kind="danger")
    _output
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 9. Frontend Framework Comparison")
    _section
    return


@app.cell
def _(mo):
    _chapter9_guide = mo.md(
        """
    ### Chapter 9 Introduction

    > **Key Question:** What does the frontend need to know about everything behind it?

    *We reach the **presentation tier**. The API from chapter 8 has the data; something has to show it.*

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
    return


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

    **First, what a frontend actually is.** A restaurant has three rooms. The **cold store** holds
    the ingredients and has exactly one job, keeping them correct: that was chapters 1 to 5. The
    **kitchen** holds the recipes and the rules, and nothing leaves without being checked, whether
    the order came from a table, a phone or a delivery app: chapters 6 to 8. The **dining room**
    is what the guest sees, the menu and the plating and the waiter: chapters 9 and 10.

    A frontend is the dining room. It owns no ingredients and no recipes. It writes an order slip,
    which is an HTTP request to a path, hands it through the hatch, and arranges whatever comes
    back so a human can decide something.

    This is the payoff for splitting the tiers at all. Change supplier, Parquet for DuckDB, and no
    guest notices. Rebuild the whole dining room, Streamlit for React, and the kitchen does not
    change one line. **This repo already contains that dining room:** `sw03_demo_streamlit.py`,
    talking to the API you started in chapter 8.

    *Where the picture breaks.* A waiter cannot cook, but a frontend **does** compute: it sorts,
    formats, aggregates and draws every chart in that dashboard. So do not read this as "the
    frontend is dumb". Read it as **the frontend owns no rules**. Anyone can telephone the kitchen
    directly, with `curl` or a script or another team's app, so a rule that lives only in the
    dining room is not a rule at all. That is why this repo deliberately states the same rule
    twice: the Streamlit form sets `min_value=1` for units sold, and the API states it again as
    `units_sold: int = Field(ge=1, ...)`. The dining room may repeat a rule for politeness.
    Never instead.

    Think in terms of trade‑offs (explicit engineering compromises): speed vs. control, Python‑native vs. JS ecosystems, and expected scale.

    A simple framing:

    $$
    \\text{Iteration Speed} \\uparrow \\quad \\Rightarrow \\quad \\text{UI Control} \\downarrow
    $$

    Interpretation:
    - faster iteration often comes with less low-level UI control; more control usually needs more engineering effort

    Useful showcase/example pages:
    - Marimo gallery: https://marimo.io/gallery
    - Dash example gallery: https://dash.gallery/Portal/
    - React community/resources: https://react.dev/community
    - Flask patterns/tutorial examples: https://flask.palletsprojects.com/en/stable/patterns/
            """
    ).callout(kind="neutral")

    _framework_table = mo.ui.table(framework_rows, label="Framework comparison", selection=None, pagination=False, show_download=False, show_search=False)
    _panel = mo.vstack([_framework_note, _framework_table], gap=0.6)
    _panel
    return


@app.cell
def _(mo):
    fw_speed = mo.ui.slider(1, 5, value=5, label="Need fast iteration", show_value=True)
    fw_control = mo.ui.slider(1, 5, value=3, label="Need fine UI control", show_value=True)
    fw_js = mo.ui.slider(1, 5, value=2, label="Team JavaScript strength", show_value=True)
    _note = mo.md(
        """
    Set three numbers about *your team*, not about the frameworks.

    **JavaScript** is the programming language browsers run. Marimo and Streamlit let you
    avoid it and stay in Python; React is written in it. So a low score here is not a
    weakness, it just points at different tools.

    Each framework scores the three inputs with its own weights, and every weight row adds
    up to the same total (3.0) so the scores stay comparable:

    $$
    \\text{fit}_f = w^f_s \\cdot s + w^f_c \\cdot c + w^f_j \\cdot j_f
    \\qquad \\text{with} \\quad w^f_s + w^f_c + w^f_j = 3
    $$

    For the two Python-native tools, $j_f = 6 - j$: they get *more* attractive when the team
    knows *less* JavaScript. For the others $j_f = j$. Heuristic only - validate against
    real team constraints.
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
    # Teaching heuristic, not a recommendation engine. Every weight row sums to 3.0,
    # so no framework wins just by carrying more weight than the others.
    _weights = {
        # framework:   (fast iteration, fine UI control, JavaScript), python_native
        "Marimo":      ((1.4, 0.6, 1.0), True),
        "Streamlit":   ((1.6, 0.4, 1.0), True),
        "Dash":        ((1.0, 1.0, 1.0), False),
        "Flask":       ((0.6, 1.6, 0.8), False),
        "React":       ((0.4, 1.4, 1.2), False),
    }
    # Python-native tools benefit from a team that knows LITTLE JavaScript, hence 6 - j.
    _framework_scores = {
        name: w_s * fw_speed.value
        + w_c * fw_control.value
        + w_j * ((6 - fw_js.value) if python_native else fw_js.value)
        for name, ((w_s, w_c, w_j), python_native) in _weights.items()
    }
    _ranked_frameworks = sorted(_framework_scores.items(), key=lambda x: x[1], reverse=True)
    _fit_table = mo.ui.table(
        [
            {
                "framework": name,
                "score": round(score, 2),
                "weights (speed / control / JS)": " / ".join(str(w) for w in _weights[name][0]),
            }
            for name, score in _ranked_frameworks
        ],
        label="Teaching score (higher = better fit)",
        selection=None, pagination=False, show_download=False, show_search=False,
    )
    _fit_message = mo.md(f"Current top fit: **{_ranked_frameworks[0][0]}**").callout(kind="info")
    _fit_panel = mo.vstack([_fit_table, _fit_message], gap=0.6)
    _fit_panel
    return


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
    return


@app.cell
def _(mo):
    _section = mo.md("## 10. Marimo Charts Lab")
    _section
    return


@app.cell
def _(mo):
    _chapter10_guide = mo.md(
        """
    ### Chapter 10 Introduction

    > **Key Question:** Which pattern is signal, and which is noise?

    *Still in the **presentation tier**, and the last decision of the whole stack: what a chart claims is what people believe.*

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
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### Marimo Charts Lab

    Use the controls below to generate a dataset where **you** set the true slope and the noise,
    then watch what the regression reports back:

    - **XY scatter + linear regression**, with the equation and its $R^2$
    - a verdict that says whether the line means anything at all

    Set the slope to 0 and the noise high. The equation still prints confidently. The $R^2$ is
    what tells you not to believe it. Then the mini-lab below asks the same question of real data
    three different ways, and gets three different answers.
            """
    ).callout(kind="neutral")
    _explanation
    return


@app.cell
def _(mo):
    chart_rows = mo.ui.slider(100, 1000, step=100, value=600, label="Rows (max 1000)", show_value=True)
    chart_seed = mo.ui.slider(1, 999, value=21, label="Seed", show_value=True)
    chart_slope = mo.ui.slider(-3.0, 3.0, step=0.2, value=1.2, label="Trend slope", show_value=True)
    chart_noise = mo.ui.slider(0.2, 5.0, step=0.2, value=1.4, label="Noise level", show_value=True)

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
    alt,
    chart_noise,
    chart_rows,
    chart_seed,
    chart_slope,
    mo,
    pd,
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
        selection=None, pagination=False, show_download=False, show_search=False,
    )

    _df = pd.DataFrame(_rows)

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
        # R^2: the share of the up-and-down in y that the line actually explains.
        _var_y = sum((y - _mean_y) ** 2 for y in ys)
        _r_squared = (_cov * _cov) / (_var_x * _var_y) if _var_y else 0.0
        return _slope, _intercept, _r_squared

    _scatter = (
        alt.Chart(_df)
        .mark_circle(size=60, opacity=0.6, color="#2f6fed")
        .encode(
            x=alt.X("x:Q"),
            y=alt.Y("y:Q"),
            tooltip=[
                alt.Tooltip("x:Q"),
                alt.Tooltip("y:Q"),
            ],
        )
    )
    _scatter_layers = _scatter
    _formula = None
    _lr = _linear_regression(_x_vals, _y_vals)
    if _lr:
        _beta, _alpha, _r2 = _lr
        _x_min = min(_x_vals)
        _x_max = max(_x_vals)
        _reg_df = pd.DataFrame(
            {
                "x": [_x_min, _x_max],
                "y": [_beta * _x_min + _alpha, _beta * _x_max + _alpha],
            }
        )
        _reg_line = alt.Chart(_reg_df).mark_line(color="#f59e0b", strokeWidth=2.5).encode(x=alt.X("x:Q"), y=alt.Y("y:Q"))
        _scatter_layers = _scatter + _reg_line
        # A line can always be drawn. R^2 says whether it means anything.
        if _r2 >= 0.5:
            _verdict = f"R&sup2; = {_r2:.2f} - the line explains most of the spread. This looks like **signal**."
            _verdict_kind = "success"
        elif _r2 >= 0.15:
            _verdict = f"R&sup2; = {_r2:.2f} - the line explains only part of the spread. **Weak** evidence."
            _verdict_kind = "info"
        else:
            _verdict = f"R&sup2; = {_r2:.2f} - the line explains almost nothing. This is **noise**, even though the equation looks confident."
            _verdict_kind = "warn"
        _formula = mo.vstack(
            [
                mo.md(
                    f"Regression: **y = {_alpha:.3f} + {_beta:.3f} x**  \n"
                    f"$\\alpha$ (intercept) = ${_alpha:.3f}$, $\\beta$ (slope) = ${_beta:.3f}$, "
                    f"$R^2$ = ${_r2:.3f}$"
                ).callout(kind="info"),
                mo.md(_verdict).callout(kind=_verdict_kind),
            ],
            gap=0.4,
        )
    else:
        _formula = mo.md("Regression could not be computed for this sample.").callout(kind="warn")

    _scatter_chart = mo.ui.altair_chart(_scatter_layers.properties(height=280))

    _panel = mo.vstack(
        [
            _formula,
            mo.md("#### XY scatter + regression"),
            _scatter_chart,
            _stats_table,
        ],
        gap=0.8,
    )

    _panel
    return


@app.cell
def _(mo):
    honest_view = mo.ui.radio(
        options=[
            "A - aggregate the dots",
            "B - split by category",
            "C - drop one category",
        ],
        value="A - aggregate the dots",
        label="Ask the same question a different way",
    )
    _panel = mo.vstack(
        [
            mo.md("### Mini-lab: Three Ways to Change the Finding Without Changing the Data"),
            mo.md(
                """
    One question, asked of the repo's real 3,360 sales: **does spending more make customers
    happier?** Nothing below adds or removes a single sale. Only the way we look changes.
                """
            ).callout(kind="info"),
            honest_view,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    _panel
    return (honest_view,)


@app.cell
def _(SEED_DIR, duckdb, honest_view, mo, statistics):
    def _fit(_xs, _ys):
        _mx, _my = statistics.mean(_xs), statistics.mean(_ys)
        _vx = sum((_x - _mx) ** 2 for _x in _xs)
        _vy = sum((_y - _my) ** 2 for _y in _ys)
        if not _vx or not _vy:
            return None, None
        _cov = sum((_x - _mx) * (_y - _my) for _x, _y in zip(_xs, _ys))
        return _cov / _vx, (_cov * _cov) / (_vx * _vy)

    _con = duckdb.connect()
    _join = (
        f"FROM '{(SEED_DIR / 'sales.parquet').as_posix()}' s "
        f"JOIN '{(SEED_DIR / 'products.parquet').as_posix()}' p USING (product_id) "
        f"JOIN '{(SEED_DIR / 'categories.parquet').as_posix()}' c USING (category_id)"
    )

    def _measure(_label, _sql):
        _df = _con.execute(_sql).df()
        _slope, _r2 = _fit(_df["x"].tolist(), _df["y"].tolist())
        return {
            "what we plotted": _label,
            "dots (n)": len(_df),
            "slope (rating per CHF 10k)": None if _slope is None else round(_slope * 10000, 3),
            "R²": None if _r2 is None else round(_r2, 3),
        }

    if honest_view.value.startswith("A"):
        _rows = [
            _measure("one dot per sale", f"SELECT total_price x, customer_rating y {_join}"),
            _measure(
                "one dot per product per month",
                f"SELECT avg(total_price) x, avg(customer_rating) y {_join} "
                "GROUP BY p.name, date_trunc('month', s.sale_date)",
            ),
            _measure(
                "one dot per category per month",
                f"SELECT avg(total_price) x, avg(customer_rating) y {_join} "
                "GROUP BY c.name, date_trunc('month', s.sale_date)",
            ),
            _measure(
                "one dot per category",
                f"SELECT avg(total_price) x, avg(customer_rating) y {_join} GROUP BY c.name",
            ),
        ]
        _lesson = """
    **$R^2$ went from "weak" to "publishable" and no new information entered the room.**

    Every row above is the same 3,360 sales. Averaging dots together does not strengthen a
    relationship, it **deletes the disagreement** that was telling you the relationship is weak.
    The last row has three dots and a story you could put on a slide.

    This is why a goodness-of-fit number is meaningless without its sample size. Always read
    $R^2$ and $n$ together, which is why the table prints both.
            """
    elif honest_view.value.startswith("B"):
        _cats = [_r[0] for _r in _con.execute(f"SELECT DISTINCT c.name {_join} ORDER BY 1").fetchall()]
        _rows = [_measure("all sales pooled together", f"SELECT total_price x, customer_rating y {_join}")]
        _rows += [
            _measure(f"only {_c}", f"SELECT total_price x, customer_rating y {_join} WHERE c.name = '{_c}'")
            for _c in _cats
        ]
        _lesson = """
    **The pooled line does not describe any of the groups.**

    Pooled, the slope is positive: spend more, be happier. Look inside Hardware and the slope is
    *negative*. The upward line is not describing customers at all. It is describing the gaps
    **between** categories, because Services happen to be expensive and well rated while Hardware
    is mid-priced and rated worst.

    Three groups' worth of difference, wearing three thousand dots' worth of authority. When a
    relationship reverses inside every subgroup, that has a name: Simpson's paradox.
            """
    else:
        _rows = [
            _measure("all sales", f"SELECT total_price x, customer_rating y {_join}"),
            _measure(
                "every sale except Services",
                f"SELECT total_price x, customer_rating y {_join} WHERE c.name <> 'Services'",
            ),
        ]
        _lesson = """
    **One group out of three decided the direction of the answer.**

    Remove Services and the slope flips sign: the finding reverses completely. Now look at the
    $R^2$ column. It barely moved.

    That is the warning worth leaving this chapter with. $R^2$ tells you how tightly the dots hug
    the line. It never tells you whether the line was the right line to draw, and it will not
    warn you when one group is carrying the entire result.
            """

    _output = mo.vstack(
        [
            mo.ui.table(_rows, label="Same 3,360 sales, same question", selection=None, pagination=False, show_download=False, show_search=False),
            mo.md(_lesson).callout(kind="warn"),
        ],
        gap=0.6,
    )
    _output
    return


@app.cell
def _(mo):
    _transition = mo.md(
        """
    ### Wrap-up

    We built one data product, one tier at a time. This is the map from the start of the notebook,
    now filled in:

    **Data tier — where the bytes rest**

    1. Keep writes correct under concurrency (ch. 1)
    2. Choose efficient serialization formats (ch. 2)
    3. Use columnar layout and compression for analytics (ch. 3-4)
    4. Query files with DuckDB (ch. 5)

    **Logic tier — the rules and the API**

    5. Expose data through REST APIs (ch. 6)
    6. Validate contracts with Pydantic, then serve them with FastAPI (ch. 7-8)

    **Presentation tier — what people actually see**

    7. Choose a frontend and present results in charts (ch. 9-10)

    Each tier only talks to its neighbour. That is what let us swap Parquet for DuckDB without
    touching the API, and what would let you swap Streamlit for React without touching either.

    If students remember one thing: correctness first, then performance, then usability.
            """
    ).callout(kind="neutral")
    _transition
    return


@app.cell
def _(mo):
    _links_section = mo.md("## Some Useful Links")
    _links_section
    return


@app.cell
def _(mo):
    _links = mo.md(
        """
    <div class="section-card">
      <p>Reference material for deeper dives and lookup:</p>
      <ul>
        <li>Marimo documentation: <code>https://marimo.io</code></li>
        <li>Marimo gallery: <code>https://marimo.io/gallery</code></li>
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
        <li>HTTP status code reference: <code>https://en.wikipedia.org/wiki/List_of_HTTP_status_codes</code></li>
        <li>Dash examples: <code>https://dash.plotly.com/examples</code></li>
        <li>React community/resources: <code>https://react.dev/community</code></li>
        <li>Flask patterns/tutorial examples: <code>https://flask.palletsprojects.com/en/stable/patterns/</code></li>
      </ul>
    </div>
            """
    )
    _links
    return


if __name__ == "__main__":
    app.run()
