import marimo

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
            --ink-2: #1f2a44;
            --muted: #4b5b75;
            --border: rgba(11, 18, 32, 0.12);
            --surface: rgba(255, 255, 255, 0.88);
            --surface-strong: rgba(255, 255, 255, 0.96);
            --accent: #2f6fed;
            --accent-2: #14b8a6;
            --accent-3: #f59e0b;
            --shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
          }

          body {
            background:
              radial-gradient(circle at 12% 8%, rgba(47, 111, 237, 0.18), transparent 42%),
              radial-gradient(circle at 85% 18%, rgba(20, 184, 166, 0.16), transparent 40%),
              radial-gradient(circle at 25% 85%, rgba(245, 158, 11, 0.14), transparent 42%),
              linear-gradient(180deg, #f7f9ff 0%, #eef2fb 48%, #f7f9ff 100%);
            color: var(--ink);
            font-family: "Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif;
            background-attachment: fixed;
          }

          main, .marimo-main, .mo-main {
            max-width: 1520px;
            width: min(96vw, 1520px);
            margin: 0 auto;
            padding: 0 24px 60px;
          }

          h1, h2, h3 {
            color: var(--ink);
          }

          h1, .hero-title {
            font-family: "Fraunces", "Space Grotesk", serif;
            letter-spacing: 0.01em;
          }

          pre, code {
            background: rgba(53, 89, 224, 0.08);
            border: 1px solid rgba(53, 89, 224, 0.2);
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
            backdrop-filter: blur(10px);
          }

          .hero {
            position: relative;
            border-radius: 22px;
            padding: 28px 28px 24px 28px;
            background: linear-gradient(120deg, rgba(47, 111, 237, 0.15), rgba(20, 184, 166, 0.12), rgba(245, 158, 11, 0.12));
            border: 1px solid rgba(47, 111, 237, 0.25);
            box-shadow: 0 30px 70px rgba(15, 23, 42, 0.18);
            overflow: hidden;
            animation: float 12s ease-in-out infinite;
          }

          .hero::after {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 20% 20%, rgba(47, 111, 237, 0.35), transparent 45%);
            opacity: 0.9;
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
            font-size: 2.4rem;
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

          @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
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
    <div class="eyebrow">SW03 Lecture Studio</div>
    <div class="hero-title">Data Storage, Serialization, APIs, and Apps</div>
    <div class="hero-subtitle">
      A high‑intensity, hands‑on notebook that connects storage theory to real code:
      race conditions, serialization trade‑offs, columnar analytics, API design, and
      rapid app prototyping.
    </div>
    <div class="hero-pills">
      <span class="pill">ACID & Concurrency</span>
      <span class="pill">Serialization Benchmarks</span>
      <span class="pill">Columnar Analytics</span>
      <span class="pill">APIs & FastAPI</span>
      <span class="pill">Frontend Frameworks</span>
      <span class="pill">Streamlit Studio</span>
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
  <h2>Agenda (Lecture Flow)</h2>
  <div class="grid-2">
    <div>
      <ul>
        <li>File locks and why databases matter (ACID vs. files)</li>
        <li>Serialization & deserialization benchmarks (JSON, Pickle, Arrow, Avro)</li>
        <li>Column‑based vs row‑based storage</li>
        <li>Compression & encoding (Parquet, gzip, compression ratios)</li>
        <li>DuckDB for analytics on files</li>
      </ul>
    </div>
    <div>
      <ul>
        <li>REST APIs (GET, POST, PUT, DELETE)</li>
        <li>Pydantic models for validation</li>
        <li>FastAPI demo + automatic documentation</li>
        <li>Frontend framework comparison (Streamlit, Dash, Flask, React)</li>
        <li>Streamlit in‑depth: build a tiny app</li>
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
    deps = mo.md(
        """
<div class="section-card">
  <h3>Optional Python Packages</h3>
  <p>
    Some demos use optional libraries. If they are missing, the notebook will gracefully skip those parts.
  </p>

```bash
pip install pandas pyarrow fastavro duckdb requests pydantic fastapi uvicorn streamlit dash flask
```
</div>
        """
    ).callout(kind="info")
    deps
    return (deps,)


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
**Takeaway:** File writes can lose updates without locking. Databases provide atomic updates and isolation out of the box.
            """
        ).callout(kind="info")

        _output = mo.vstack([_table, _summary], gap=0.6)

    _output
    return (_output,)


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
    run_duck = mo.ui.button(label="Re-run DuckDB demo", value=1, kind="success")
    run_duck
    return (run_duck,)


@app.cell
def _(
    csv,
    format_ms,
    mo,
    optional_import,
    random,
    run_duck,
    tempfile,
    time,
):
    if run_duck.value == 0:
        _output = mo.md("Click **Run DuckDB demo** to execute.").callout(
            kind="neutral"
        )
    else:
        duckdb = optional_import("duckdb")
        if not duckdb:
            _output = mo.md(
                "DuckDB is not installed. Install with `pip install duckdb` to run this demo."
            ).callout(kind="warn")
        else:
            rng = random.Random(33 + run_duck.value)
            _records = [
                {
                    "region": rng.choice(["EU", "US", "APAC"]),
                    "amount": rng.random() * 1000,
                }
                for _ in range(2000)
            ]

            with tempfile.TemporaryDirectory() as _tmpdir:
                _tmpdir = Path(_tmpdir)
                _csv_path = _tmpdir / "orders.csv"
                with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                    _writer = csv.DictWriter(_f, fieldnames=["region", "amount"])
                    _writer.writeheader()
                    _writer.writerows(_records)

                con = duckdb.connect()
                start = time.perf_counter()
                result = con.execute(
                    "SELECT region, COUNT(*) AS orders, AVG(amount) AS avg_amount "
                    f"FROM read_csv_auto('{_csv_path}') GROUP BY region ORDER BY region"
                ).fetchall()
                _duration = time.perf_counter() - start
                con.close()

            duck_rows = [
                {"region": row[0], "orders": row[1], "avg_amount": round(row[2], 2)}
                for row in result
            ]
            _table = mo.ui.table(duck_rows, label="DuckDB query results")
            _note = mo.md(
                f"Query runtime: **{format_ms(_duration)}** (file scanned + SQL)."
            )

            _output = mo.vstack([_table, _note], gap=0.6)

    _output
    return (_output,)


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
    send = mo.ui.button(label="Send request", value=0, kind="success")

    _controls = mo.vstack(
        [
            mo.hstack([method, base_url], widths="equal"),
            path,
            payload,
            send,
        ],
        gap=0.6,
    ).callout(kind="neutral")

    _controls
    return base_url, method, path, payload, send


@app.cell
def _(base_url, json, method, mo, path, payload, send, url_error, url_request):
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

        if _response_panel is None:
            req = url_request.Request(
                url, data=data_bytes, headers=headers, method=method.value
            )

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
**Status:** `{status}`

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

Run with:

```
uvicorn lecture_api:app --reload
```
        """
    )
    fastapi_code
    return (fastapi_code,)


@app.cell
def _(mo):
    run_fastapi = mo.ui.button(label="Run FastAPI test client", value=1, kind="success")
    run_fastapi
    return (run_fastapi,)


@app.cell
def _(json, mo, optional_import, run_fastapi):
    if run_fastapi.value == 0:
        _output = mo.md("Click **Run FastAPI test client** to execute.").callout(
            kind="neutral"
        )
    else:
        fastapi = optional_import("fastapi")
        if not fastapi:
            _output = mo.md(
                "FastAPI is not installed. Install with `pip install fastapi uvicorn`."
            ).callout(kind="warn")
        else:
            from fastapi import FastAPI
            from pydantic import BaseModel as _FastapiBaseModel

            app = FastAPI()

            class Item(_FastapiBaseModel):
                id: int
                name: str
                price: float

            items = {}

            @app.post("/items")
            def create_item(item: Item):
                items[item.id] = item
                return item

            @app.get("/items/{item_id}")
            def read_item(item_id: int):
                return items.get(item_id, {"error": "not found"})

            try:
                from fastapi.testclient import TestClient
            except Exception as exc:
                _output = mo.md(
                    f"FastAPI TestClient unavailable: `{exc}`"
                ).callout(kind="warn")
            else:
                client = TestClient(app)
                client.post("/items", json={"id": 1, "name": "Notebook", "price": 9.9})
                _response = client.get("/items/1")

                _output = mo.md(
                    f"""
**TestClient response:**

```json
{json.dumps(_response.json(), indent=2)}
```
                    """
                ).callout(kind="success")

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
            "framework": "Streamlit",
            "strengths": "Fast Python dashboards, minimal boilerplate",
            "tradeoffs": "Limited UI control, app-style only",
            "use_case": "Data apps, internal tools",
        },
        {
            "framework": "Dash",
            "strengths": "Plotly integration, component ecosystem",
            "tradeoffs": "Callback complexity for large apps",
            "use_case": "Interactive analytics",
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
    _section = mo.md("## 10. Streamlit In-Depth (Tiny App)")
    _section
    return (_section,)


@app.cell
def _(mo):
    _explanation = mo.md(
        """
### Streamlit in 15 Lines

Streamlit turns a Python script into a web app. Below is a minimal app that:

- loads data  
- lets a user filter  
- renders a chart  
- uses caching  

App logic is just Python, but the UI is reactive:

$$
\\text{UI state} \\rightarrow \\text{recompute} \\rightarrow \\text{render}
$$
        """
    ).callout(kind="neutral")
    _explanation
    return (_explanation,)


@app.cell
def _(mo):
    streamlit_code = """import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Tiny Streamlit App", layout="wide")

st.title("Tiny Streamlit App")
st.caption("A minimal interactive dashboard")

@st.cache_data
def make_data(rows=500):
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        "x": rng.normal(size=rows).cumsum(),
        "y": rng.normal(size=rows).cumsum(),
        "category": rng.choice(["A", "B", "C"], size=rows),
    })

rows = st.slider("Rows", 100, 2000, 500, 100)
category = st.selectbox("Category", ["All", "A", "B", "C"])

df = make_data(rows)
if category != "All":
    df = df[df["category"] == category]

st.line_chart(df[["x", "y"]])
st.dataframe(df.head(10))
"""

    code_block = mo.md(
        f"""
```python
{streamlit_code}
```
        """
    )
    _run_note = mo.md(
        """
Run it locally:

```bash
streamlit run streamlit_app.py
```
        """
    ).callout(kind="info")

    _panel = mo.vstack([code_block, _run_note], gap=0.6)
    _panel
    return _panel, streamlit_code


@app.cell
def _(mo):
    write_app = mo.ui.button(label="Create streamlit_app.py", value=0, kind="success")
    write_app
    return (write_app,)


@app.cell
def _(Path, mo, streamlit_code, write_app):
    if write_app.value == 0:
        _status = mo.md(
            "Click **Create streamlit_app.py** to write the app file in the repo."
        ).callout(kind="neutral")
    else:
        app_path = Path("streamlit_app.py")
        app_path.write_text(streamlit_code, encoding="utf-8")
        _status = mo.md(f"Created `{app_path}`.").callout(kind="success")

    _status
    return (_status,)


@app.cell
def _(mo):
    footer = mo.md(
        """
---

### Next Steps for Students

1. Rerun the experiments with different parameters and discuss the results.
2. Add a new serialization format (e.g., MessagePack) and compare.
3. Extend the FastAPI example with a database backend.
        """
    )
    footer
    return (footer,)


if __name__ == "__main__":
    app.run()
