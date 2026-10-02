# /// script
# [tool.marimo.display]
# theme = "light"
# ///
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium", css_file="sw03_deck.css", html_head_file="sw03_deck_head.html")


@app.cell
def _():
    import csv
    import gzip
    import html
    import io
    import json
    import math
    import os
    import pickle
    import random
    import re
    import sqlite3
    import statistics
    import tempfile
    import threading
    import time
    import timeit
    from pathlib import Path

    import marimo as mo

    return (
        Path,
        csv,
        gzip,
        html,
        io,
        json,
        math,
        mo,
        os,
        pickle,
        random,
        re,
        sqlite3,
        statistics,
        tempfile,
        threading,
        time,
        timeit,
    )


@app.cell
def _(html, mo, re):
    def label_w(text: str) -> float:
        """Width of a box around a 17 px label: about 8.2 px per character (tags do not count) plus 32 px padding."""
        return 32 + 8.2 * len(html.unescape(re.sub(r"<[^>]*>", "", text)))

    def box(x: float, y: float, text: str, *, w: float | None = None, h: float = 44, cls: str = "dg-box") -> str:
        """SVG for a box at (x, y) with `text` centred in it; as wide as label_w(text) unless `w` is given."""
        w = label_w(text) if w is None else w
        return (
            f'<rect class="{cls}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="12"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + h / 2:.0f}" text-anchor="middle" dominant-baseline="central">{text}</text>'
        )

    def diagram(body: str, *, width: int, height: int, label: str, tier: str | None = None):
        """An inline SVG drawn with the dg-* classes of sw03_deck.css; `label` is what a screen reader says.

        1 viewBox unit is 1 px at full size: never wider than `width` px, narrower when its column is.
        `tier` ("data", "logic" or "presentation") colours every dg-tier and dg-dot inside.
        """
        tier_class = f" tier-{tier}" if tier else ""
        # One arrowhead id per drawing: url(#id) takes the first match in the page, which can sit in a
        # hidden copy that marimo keeps of tab and accordion content, and a hidden marker draws nothing.
        arrow = f"dg-arrow-{abs(hash(body))}"
        return mo.Html(
            f'<svg class="dg{tier_class}" viewBox="0 0 {width} {height}"'
            f' style="max-width: {width}px; --dg-arrow: url(#{arrow})" role="img" aria-label="{html.escape(label)}">'
            f'<defs><marker id="{arrow}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5"'
            ' orient="auto-start-reverse"><path class="dg-head" d="M0,0 L10,5 L0,10 z"/></marker></defs>'
            f"{body}</svg>"
        )

    return box, diagram, label_w


@app.cell
def _(mo):
    mo.md("""
    <div class="hero">
      <div class="eyebrow">CIP - SW03 Lecture Studio</div>
      <div class="hero-title">Storage, Serialization, APIs & Apps</div>
      <div class="hero-subtitle">
        One data product, built in <strong>three tiers</strong>: where the data rests,
        what serves it, and what people look at. We build them from the bottom up,
        one chapter per decision.
      </div>
      <div class="hero-pills">
        <span class="pill">Locks & ACID</span>
        <span class="pill">Serialization</span>
        <span class="pill">Row vs Column</span>
        <span class="pill">Compression</span>
        <span class="pill">DuckDB & Indexes</span>
        <span class="pill">REST Contract</span>
        <span class="pill">Pydantic</span>
        <span class="pill">FastAPI</span>
        <span class="pill">Frontends</span>
        <span class="pill">Honest Charts</span>
      </div>
    </div>
    """)
    return


@app.cell
def _(box, diagram, label_w, mo):
    def _tier(y, tier, name, role, chapters):
        """One tier band: name and role on the left, then one chip per chapter."""
        parts = [
            f'<g class="tier-{tier}"><rect class="dg-tier" x="0" y="{y}" width="1060" height="96" rx="16"/>',
            f'<text x="24" y="{y + 40}" font-size="21" font-weight="700">{name}</text>',
            f'<text class="dg-muted" x="24" y="{y + 68}">{role}</text>',
        ]
        x = 230
        for number, topic in chapters:
            chip = f'<tspan font-weight="700">{number}</tspan> {topic}'
            parts.append(box(x, y + 26, chip, cls="dg-tier"))
            x += label_w(chip) + 12
        return "".join(parts) + "</g>"

    # Returned too, so the wrap-up can show the same map again.
    tier_map = diagram(
        '<text x="920" y="22" text-anchor="middle" font-weight="700">request</text>'
        '<text x="1000" y="22" text-anchor="middle" font-weight="700">answer</text>'
        + _tier(40, "presentation", "Presentation tier", "what a person sees", [("9", "frontend"), ("10", "honest charts")])
        + _tier(172, "logic", "Logic tier", "rules and the API", [("6", "contract"), ("7", "validate input"), ("8", "serve over HTTP")])
        + _tier(304, "data", "Data tier", "where bytes rest", [("1", "correct writes"), ("2", "format"), ("3", "layout"), ("4", "compression"), ("5", "query")])
        # one hop per neighbour: down for the request, up for the answer
        + '<path class="dg-edge" d="M920 88 V 166"/><path class="dg-edge" d="M920 220 V 298"/>'
        + '<path class="dg-edge" d="M1000 352 V 274"/><path class="dg-edge" d="M1000 220 V 142"/>'
        + '<circle class="dg-dot" r="9"><animateMotion dur="5s" repeatCount="indefinite" path="M920 88 V 352 H 1000 V 88 Z"/></circle>',
        width=1060,
        height=420,
        label="Three tiers, stacked: presentation (chapters 9 and 10) on logic (6 to 8) on data (1 to 5). "
        "A request travels down one tier at a time and the answer comes back up the same way.",
    )
    _chapters = mo.md("""
    1. **File locks vs databases**: lost updates, locks, ACID, an atomic transfer
    2. **Serialization**: JSON, CSV, Pickle, Arrow, Parquet, Avro
    3. **Row vs column storage**
    4. **Compression & encoding**: lossless vs lossy, Parquet codecs, dictionaries
    5. **DuckDB**: SQL on files, indexes & query plans, schema-on-read vs -write
    6. **REST**: the API contract, four verbs, status codes
    7. **Pydantic**: validation at the trust boundary
    8. **FastAPI live**: the demo API and its automatic `/docs`
    9. **Frontends**: Streamlit, Dash, Flask, React, Marimo
    10. **Honest charts**: a regression lab, one question asked three ways
    """)
    mo.vstack(
        [
            mo.md(f"""
    <div class="section-card">
      <h3>The Map: One Product, Three Tiers</h3>
      {tier_map}
      <p class="vis-caption">Almost every data application has these three tiers. Each talks only to its
      neighbour, so any one can be replaced without rewriting the others.</p>
    </div>
    """),
            mo.accordion({"Every chapter in one line": _chapters}),
        ],
        gap=0.6,
    )
    return (tier_map,)


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>How to Read This Notebook</h3>
      <div class="tiles">
        <div class="tile"><div class="tile-key">?</div><div class="tile-title">Key Question</div>
          <p>Every chapter opens with one, and the tier it lives in.</p></div>
        <div class="tile"><div class="tile-key">&sum;</div><div class="tile-title">Formula</div>
          <p>A quick model of the idea.</p></div>
        <div class="tile"><div class="tile-key">&#9654;</div><div class="tile-title">Mini-lab</div>
          <p>Controls to test the model. Heavy ones wait for their Run button.</p></div>
        <div class="tile"><div class="tile-key">&#8230;</div><div class="tile-title">Discussion</div>
          <p>Questions for the room: click one to reveal the answer.</p></div>
      </div>
    </div>
    """)
    return


@app.cell
def _(os):
    # Kept out of the first cell: the title cells above only need `mo`, so they paint
    # before these heavier libraries finish importing.
    # One BLAS thread: the chapter 4 SVDs are tiny, and extra threads only add multi-second stalls on a busy laptop.
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    import altair as alt
    import duckdb
    import fastavro
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
        alt,
        duckdb,
        fastavro,
        feather,
        np,
        pa,
        pd,
        pq,
        pydantic,
        requests,
    )


@app.cell
def _(Path, mo):
    # Real sales rows (data/seed/) that several labs below read.
    SEED_DIR = Path(mo.notebook_dir()) / "data" / "seed"
    SALES_SEED = SEED_DIR / "sales.parquet"
    return SALES_SEED, SEED_DIR


@app.cell
def _(mo, requests, timeit):
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

    def static_table(rows, label: str, **kwargs):
        """A read-out table: no row selection, paging, search or download buttons. kwargs go to mo.ui.table."""
        return mo.ui.table(rows, label=label, selection=None, pagination=False, show_download=False, show_search=False, **kwargs)

    def best_seconds(fn, *args, repeat=3, number=1):
        """Seconds per fn(*args), fastest of `repeat` bursts of `number` calls: a cold start or a hiccup only adds time."""
        return min(timeit.repeat(lambda: fn(*args), number=number, repeat=repeat)) / number

    def call_api(method: str, url: str, body: dict | None = None) -> tuple[int, object]:
        """One HTTP request -> (status code, parsed JSON or raw text).

        Network failures raise requests.RequestException, so a caller can say "start the API".
        """
        response = requests.request(method, url, json=body, timeout=5)
        try:
            return response.status_code, response.json()
        except requests.JSONDecodeError:
            return response.status_code, response.text

    # ponytail: marimo 0.25 reports theme "system" as light, so on a dark OS those users get light-theme label ink
    _dark = mo.app_meta().theme == "dark"
    # the --tier-* hues of sw03_deck.css, a grey for the bars that are not the point (darker than a hue on dark),
    # and the --red of sw03_deck.css for what broke (the dg-hot of the diagrams)
    TIER = {
        "data": "#2f7fe0",
        "logic": "#c9479f",
        "presentation": "#dd6325",
        "muted": "#626b78" if _dark else "#9aa4b2",
        "hot": "#ff9b8f" if _dark else "#b42318",
    }

    def tier_chart(chart, tier: str):
        """Finish an altair chart: marks in the tier's hue, no background, labels sized for the projector.

        marimo themes the axes for light and dark itself; text marks (value labels) get the page's ink.
        An encoded color (red for "lost", say) still wins over the tier hue.
        """
        ink = "#e8edf4" if _dark else "#0b1220"  # --ink of sw03_deck.css
        return (
            chart.configure(background="transparent")
            .configure_mark(color=TIER[tier])
            .configure_axis(labelFontSize=15, titleFontSize=15, tickCount=5)
            .configure_legend(labelFontSize=15, titleFontSize=15, orient="top")
            .configure_text(color=ink, fontSize=15, fontWeight="bold")
            .configure_view(stroke=None)
        )

    def chart_or_table(chart, rows, label: str):
        """A lab result: the chart that shows the finding, and the exact numbers one click away."""
        return mo.ui.tabs({"Chart": chart, "Table": static_table(rows, label=label)})

    def chapter_intro(tier: str, question: str, context: str):
        """A chapter's opening card: the tier badge, the Key Question in large type, one line of markdown context."""
        return mo.Html(
            f'<div class="key-q tier-{tier}"><span class="tier-badge">{tier} tier</span>'
            f'<p class="key-q-text">{question}</p>{mo.md(context).text}</div>'
        )

    return TIER, best_seconds, call_api, chapter_intro, chart_or_table, format_bytes, format_ms, static_table, tier_chart


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 1. File Locks vs Databases (ACID)"),
            chapter_intro(
                "data",
                "When many users update shared data at the same time, does it stay correct?",
                "The very bottom of the data tier: before a format or a layout, writes have to be correct.",
            ),
            mo.md(
                """
    **ACID**: what a database promises, and what a plain file gives you instead.

    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">A</div><div class="tile-title">Atomicity</div>
        <p>All or nothing.</p><p class="tile-bad">File: a crash leaves half a change.</p></div>
      <div class="tile"><div class="tile-key">C</div><div class="tile-title">Consistency</div>
        <p>Rules hold before and after every change.</p><p class="tile-bad">File: no rules at all.</p></div>
      <div class="tile"><div class="tile-key">I</div><div class="tile-title">Isolation</div>
        <p>Concurrent changes act as if run one at a time.</p><p class="tile-bad">File: writers overwrite each other.</p></div>
      <div class="tile"><div class="tile-key">D</div><div class="tile-title">Durability</div>
        <p>Committed data survives a crash.</p><p class="tile-bad">File: only after flush + fsync.</p></div>
    </div>

    **The signal to watch:** $W$ workers adding $I$ increments each should reach $E = W \\times I$.
    The shortfall is the number of lost updates, $L = E - A$, with $A$ the value actually reached.
                """
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card flow-card">
      <h3>Lost Update: Who Does What, When</h3>
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
          <div class="lu-event">adds 1 to its stale 41</div>
          <div class="lu-state">42</div>

          <div class="lu-step">3</div>
          <div class="lu-event lu-idle">done</div>
          <div class="lu-event lu-stale">writes stale 42</div>
          <div class="lu-state lu-problem">42 (A's +1 overwritten)</div>
        </div>
      </div>
      <div class="flow-note"><strong>Expected after 2 increments: 43.</strong> Observed: 42, so one update was lost.</div>
    </div>
    """)
    return


@app.cell
def _(box, diagram, mo):
    # Three flatmates who ask for the key, one script that never does.
    _workers = "".join(
        box(0, _y, _label, w=300, cls=_cls)
        for _y, _label, _cls in [
            (20, "worker 1 · holds the key", "dg-tier"),
            (92, "worker 2 · waits at the hook", "dg-box"),
            (164, "worker 3 · waits at the hook", "dg-box"),
            (240, "script · never asks for the key", "dg-box dg-hot"),
        ]
    )
    _lock_map = diagram(
        _workers
        + box(410, 64, "one key per file", w=250, h=104, cls="dg-tier")
        + '<text class="dg-muted" x="535" y="194" text-anchor="middle">flock(LOCK_EX): the hook</text>'
        + box(780, 92, "counter.txt", w=200, h=48)
        + '<path class="dg-edge dg-ok" d="M300 42 C 360 42, 350 92, 404 92"/>'
        + '<path class="dg-edge" d="M300 114 H 404"/>'
        + '<path class="dg-edge" d="M300 186 C 360 186, 350 140, 404 140"/>'
        + '<path class="dg-edge dg-ok dg-flow" d="M660 116 H 774"/>'
        + '<path class="dg-edge dg-hot" d="M300 262 H 880 V 146"/>'
        + '<text class="dg-hot" x="590" y="250" text-anchor="middle">no flock call: walks straight in</text>',
        width=980,
        height=290,
        label="Three workers queue for one key on a hook (the OS file lock); only the key holder writes to "
        "counter.txt. A fourth script never asks for the key and writes to the file directly.",
        tier="data",
    )
    _more = mo.md(
        """
    - The OS empties the pockets of anyone who leaves: a program that crashes while holding the
      key does **not** wedge the file forever.
    - There is a second kind of key many may hold at once, for looking but not touching
      (`LOCK_SH`). The lab below asks for the exclusive one, `LOCK_EX`.
    - The hook is in *one* hallway. Two computers sharing a network drive each get their own hook,
      which is why file locks are unreliable across a network filesystem.
    - **Where it breaks:** the rule is only as good as the flatmates. A database does not rely on
      an agreement: every write goes through its lock, whether the program asked or not.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>What a Lock Actually Is</h3>
      <p>Four flatmates, one bathroom, <strong>no lock on the door</strong>: one key on a hook in the
      hall, and a house rule to take it before going in.</p>
      {_lock_map}
      <p class="vis-caption"><strong>A file lock is an agreement, not a door.</strong> The OS hands out
      one key per file and makes everyone else wait. A program that never asks walks straight in.</p>
    </div>
                """
            ),
            mo.accordion({"Where the picture holds, and where it breaks": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    # Checkboxes, not a multiselect: the room sees every strategy and whether it is on.
    STRATEGY_LABELS = {
        "no_lock": "file, no lock",
        "thread_lock": "file + Python lock",
        "file_lock": "file + flock",
        "sqlite_naive": "SQLite: read, +1, write",
        "sqlite": "SQLite: one UPDATE",
    }
    strategies = mo.ui.dictionary(
        {key: mo.ui.checkbox(value=key != "thread_lock", label=label) for key, label in STRATEGY_LABELS.items()}
    )
    workers = mo.ui.slider(2, 8, value=4, label="Workers", show_value=True)
    # Capped so the slowest setting (8 x 120 x 2 ms, paid in a queue by flock) stays near 3 s in all.
    iterations = mo.ui.slider(20, 120, step=20, value=60, label="Increments each", show_value=True)
    jitter = mo.ui.slider(0, 2, value=1, step=1, label="Jitter (ms)", show_value=True)
    run_race = mo.ui.run_button(label="Run counter experiment", kind="success")
    _notes = mo.md(
        """
    - **file, no lock**: plain file writes; nothing stops two workers from overlapping.
    - **file + Python lock**: a `threading.Lock`, which only works inside one process.
    - **file + flock**: the OS key from above, held from the read to the write.
    - **SQLite: read, +1, write**: a real database, used the way most people first use one.
    - **SQLite: one UPDATE**: `UPDATE counter SET value = value + 1` inside a transaction.

    **Jitter** is a pause between the read and the write. It widens the gap the race lives in,
    and a locked strategy pays it one worker at a time.
        """
    )

    mo.vstack(
        [
            mo.md("### Concurrency Demo: File vs Locks vs Database"),
            mo.hstack([workers, iterations, jitter], widths="equal"),
            strategies.hstack(justify="start", gap=1.5, wrap=True),
            mo.accordion({"What each strategy does": _notes}),
            run_race,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return STRATEGY_LABELS, iterations, jitter, run_race, strategies, workers


@app.cell
def _(
    Path,
    STRATEGY_LABELS,
    TIER,
    alt,
    chart_or_table,
    iterations,
    jitter,
    mo,
    pd,
    run_race,
    sqlite3,
    strategies,
    tempfile,
    threading,
    tier_chart,
    time,
    workers,
):
    mo.stop(
        not run_race.value,
        mo.md(
            "**Predict first:** which strategies will reach the dashed target line? "
            "Then click **Run counter experiment**."
        ).callout(kind="neutral"),
    )

    from concurrent.futures import ThreadPoolExecutor as _Pool
    from contextlib import nullcontext as _nullcontext

    try:
        import fcntl as _fcntl
    except ImportError:  # Windows has no flock
        _fcntl = None

    _workers, _increments, _jitter_s = workers.value, iterations.value, jitter.value / 1000

    def _race(worker):
        """Run `worker` in every thread at once; return the seconds until the last one finished."""
        start = time.perf_counter()
        with _Pool(_workers) as pool:
            for future in [pool.submit(worker) for _ in range(_workers)]:
                future.result()  # a worker that crashed raises here instead of passing as a lost update
        return time.perf_counter() - start

    def _file_counter(path, mode):
        # Fixed width: nobody ever reads an empty or half-written number, so the only race
        # left is the read-modify-write gap this demo is about.
        path.write_text(f"{0:010d}")
        guard = threading.Lock() if mode == "thread_lock" else _nullcontext()

        def worker():
            for _ in range(_increments):
                with guard, path.open("r+") as f:
                    if mode == "file_lock" and _fcntl:
                        _fcntl.flock(f, _fcntl.LOCK_EX)  # released when the file closes
                    current = int(f.read())
                    if _jitter_s:
                        time.sleep(_jitter_s)
                    f.seek(0)
                    f.write(f"{current + 1:010d}")

        return _race(worker), int(path.read_text())

    def _sqlite_counter(path, one_statement):
        con = sqlite3.connect(path)
        con.executescript(
            "PRAGMA journal_mode=WAL; CREATE TABLE counter (value INTEGER NOT NULL); INSERT INTO counter VALUES (0);"
        )
        con.close()

        def worker():
            conn = sqlite3.connect(path, timeout=30, isolation_level=None)
            conn.execute("PRAGMA synchronous=OFF")  # this demo is about isolation, not durability
            for _ in range(_increments):
                if one_statement:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute("UPDATE counter SET value = value + 1")
                    conn.execute("COMMIT")
                else:
                    (current,) = conn.execute("SELECT value FROM counter").fetchone()
                    if _jitter_s:
                        time.sleep(_jitter_s)
                    conn.execute("UPDATE counter SET value = ?", (current + 1,))
            conn.close()

        seconds = _race(worker)
        con = sqlite3.connect(path)
        (value,) = con.execute("SELECT value FROM counter").fetchone()
        con.close()
        return seconds, value

    _labels = dict(STRATEGY_LABELS)
    if not _fcntl:
        _labels["file_lock"] = "file, no flock on this OS"
    _expected = _workers * _increments
    _rows = []
    with mo.status.spinner(title="Racing the workers ..."), tempfile.TemporaryDirectory() as _tmp:
        for _key, _label in _labels.items():
            if not strategies.value[_key]:
                continue
            if _key.startswith("sqlite"):
                _seconds, _actual = _sqlite_counter(Path(_tmp) / f"{_key}.db", one_statement=_key == "sqlite")
            else:
                _seconds, _actual = _file_counter(Path(_tmp) / f"{_key}.txt", _key)
            _rows.append(
                {
                    "strategy": _label,
                    "expected": _expected,
                    "actual": _actual,
                    "lost updates": _expected - _actual,
                    "duration (ms)": round(_seconds * 1000, 1),
                }
            )

    _df = pd.DataFrame(_rows)
    _df["verdict"] = [f"{_lost:,} lost" if _lost else "all kept" for _lost in _df["lost updates"]]
    _y = alt.Y("strategy:N", sort=None, title=None)
    _reached = alt.Chart(_df).encode(y=_y, x=alt.X("actual:Q", title="counter reached"))
    _counts = (
        _reached.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.condition("datum['lost updates'] > 0", alt.value(TIER["hot"]), alt.value(TIER["data"]))
        )
        + _reached.mark_text(align="left", dx=6).encode(text="verdict:N")
        + alt.Chart(pd.DataFrame({"target": [_expected]}))
        .mark_rule(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"])
        .encode(x="target:Q")
    ).properties(width="container", height=48 * len(_df), title=f"Counter reached (target {_expected:,})")
    _durations = (
        alt.Chart(_df)
        .encode(y=alt.Y("strategy:N", sort=None, title=None, axis=None), x=alt.X("duration (ms):Q", title=None))
        .mark_bar(cornerRadiusEnd=4, color=TIER["muted"])
        .properties(width="container", height=48 * len(_df), title="Time taken (ms)")
    )

    mo.vstack(
        [
            chart_or_table(
                mo.hstack([tier_chart(_counts, "data"), tier_chart(_durations, "data")], widths=[3, 1], gap=1),
                _rows,
                label="Concurrency results",
            ),
            mo.md(
                "**Compare the two SQLite bars.** Same database, but only the one-statement transaction keeps "
                "every increment: a transaction protects the steps you put inside it, and nothing else."
            ).callout(kind="info"),
            mo.accordion(
                {
                    "Why the unlocked bars stop near one worker's total": mo.md(
                        """
    With jitter, the unlocked workers fall into step: all read the same value, all pause, all write
    the same +1. So they end near *one* worker's total, as if the others never ran. Set jitter to 0
    and the file race turns messy: its count changes from run to run.

    The file lock is correct but slow: writers queue, so every millisecond of jitter is paid one
    worker at a time. The one-statement transaction is quick too: there is no gap for the jitter to
    widen, and the lock is held for microseconds.
                        """
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    interleave_steps = mo.ui.slider(1, 6, value=2, label="Increments per worker", show_value=True, debounce=True)
    interleave_seed = mo.ui.slider(1, 999, value=7, label="Interleaving seed", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md(
                """
    ### Interleaving Simulator: Why Lost Updates Happen

    Each increment is two steps: **read** the shared value, then **write** copy + 1. The seed shuffles
    the order of A's and B's steps. A write from an out-of-date copy is a **stale write**: it erases
    every increment made since that copy was read.
                """
            ),
            mo.hstack([interleave_steps, interleave_seed], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return interleave_seed, interleave_steps


@app.cell
def _(TIER, alt, chart_or_table, interleave_seed, interleave_steps, mo, pd, random, tier_chart):
    _rng = random.Random(interleave_seed.value)
    _ops = {w: ["read", "write"] * interleave_steps.value for w in "AB"}
    _local, _shared, _log = {}, 0, []
    while _ops["A"] or _ops["B"]:
        _worker = _rng.choice([w for w in "AB" if _ops[w]])
        _action = _ops[_worker].pop(0)
        _before = _shared
        if _action == "read":
            _local[_worker] = _shared
        else:
            _shared = _local[_worker] + 1
        _log.append(
            {
                "step": len(_log) + 1,
                "worker": _worker,
                "action": _action,
                "shared before": _before,
                "local copy": _local[_worker],
                "shared after": _shared,
                "note": "stale write" if _action == "write" and _local[_worker] != _before else "",
            }
        )

    _expected = interleave_steps.value * 2
    _df = pd.DataFrame(_log)
    _df["kind"] = [_note or _action for _action, _note in zip(_df["action"], _df["note"], strict=True)]
    # A read shows the value it copied, a write the value it left; short labels once the steps get narrow.
    _short = len(_df) > 12
    _df["label"] = [
        f"{_a[0].upper()}{_v}" if _short else f"{_a} {_v}"
        for _a, _v in zip(_df["action"], _df["shared after"], strict=True)
    ]
    _df["if no update were lost"] = (_df["action"] == "write").cumsum()
    _df["shared counter"] = _df["shared after"]
    _x = alt.X("step:O", title="step", axis=alt.Axis(labelAngle=0))
    _lane = alt.Chart(_df).encode(x=_x, y=alt.Y("worker:N", title=None, axis=alt.Axis(minExtent=40)))
    _lanes = (
        _lane.mark_rect(cornerRadius=8).encode(
            color=alt.Color(
                "kind:N",
                title=None,
                scale=alt.Scale(domain=["read", "write", "stale write"], range=["#cfe0fb", TIER["data"], TIER["hot"]]),
            )
        )
        # fixed text colours: the fills above are the same in both themes
        + _lane.mark_text().encode(
            text="label:N", color=alt.condition("datum.kind == 'read'", alt.value("#0b1220"), alt.value("white"))
        )
    ).properties(width=940, height=110)
    _counter = (
        alt.Chart(_df)
        .transform_fold(["shared counter", "if no update were lost"], as_=["series", "value"])
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=_x,
            y=alt.Y("value:Q", title="counter", axis=alt.Axis(minExtent=40)),
            color=alt.Color(
                "series:N",
                title=None,
                scale=alt.Scale(domain=["shared counter", "if no update were lost"], range=[TIER["data"], TIER["muted"]]),
            ),
            strokeDash=alt.StrokeDash(
                "series:N",
                legend=None,
                scale=alt.Scale(domain=["shared counter", "if no update were lost"], range=[[1, 0], [6, 4]]),
            ),
        )
        .properties(width=940, height=170)
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(_expected, label="expected", bordered=True),
                    mo.stat(_shared, label="actual", bordered=True),
                    mo.stat(_expected - _shared, label="lost updates", bordered=True),
                ],
                widths="equal",
            ),
            chart_or_table(
                tier_chart(alt.vconcat(_lanes, _counter).resolve_scale(color="independent"), "data"),
                _log,
                label="Interleaving trace",
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    atomic_amount = mo.ui.slider(10, 500, step=10, value=150, label="Transfer amount", show_value=True, debounce=True)
    atomic_fail = mo.ui.switch(value=True, label="Crash after the debit")
    mo.vstack(
        [
            mo.md(
                """
    ### Atomicity Demo: a Transfer That Crashes

    Atomicity means **all or nothing**. A transfer must keep $B_{\\text{Alice}} + B_{\\text{Bob}}$
    constant; crash between **debit** and **credit**, and only a transaction puts the money back.
    One transfer, no concurrent writers: flip the switch and watch both totals.
                """
            ),
            mo.hstack([atomic_amount, atomic_fail], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return atomic_amount, atomic_fail


@app.cell
def _(Path, atomic_amount, atomic_fail, chart_or_table, diagram, json, mo, sqlite3, tempfile):
    _initial = {"Alice": 1000, "Bob": 500}
    _expected = sum(_initial.values())
    _amount = atomic_amount.value
    _timeline = []

    def _add_timeline(system, step, state, note):
        _timeline.append({"system": system, "step": step, **state, "total": sum(state.values()), "note": note})

    with tempfile.TemporaryDirectory() as _tmp:
        # File ledger: debit and credit are two separate writes, and nothing ties them together.
        _file_path = Path(_tmp) / "ledger.json"
        _ledger = dict(_initial)
        _file_path.write_text(json.dumps(_ledger))
        _add_timeline("file (JSON)", "start", _ledger, "initial balances")
        _ledger["Alice"] -= _amount
        _file_path.write_text(json.dumps(_ledger))
        _add_timeline("file (JSON)", "debit", _ledger, "Alice debited")
        if atomic_fail.value:
            _add_timeline("file (JSON)", "crash", _ledger, "crash before credit")
        else:
            _ledger["Bob"] += _amount
            _file_path.write_text(json.dumps(_ledger))
            _add_timeline("file (JSON)", "credit", _ledger, "Bob credited")
        _file_total = sum(json.loads(_file_path.read_text()).values())

        # SQLite ledger: both updates inside one transaction.
        _con = sqlite3.connect(Path(_tmp) / "ledger.db", isolation_level=None)
        _con.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER)")
        _con.executemany("INSERT INTO accounts VALUES (?, ?)", _initial.items())

        def _balances():
            return dict(_con.execute("SELECT name, balance FROM accounts ORDER BY name").fetchall())

        _add_timeline("sqlite", "start", _balances(), "initial balances")
        _con.execute("BEGIN")
        _con.execute("UPDATE accounts SET balance = balance - ? WHERE name = 'Alice'", (_amount,))
        _add_timeline("sqlite", "debit (txn)", _balances(), "uncommitted debit")
        try:
            if atomic_fail.value:
                raise RuntimeError("simulated crash after debit")
            _con.execute("UPDATE accounts SET balance = balance + ? WHERE name = 'Bob'", (_amount,))
            _con.execute("COMMIT")
            _add_timeline("sqlite", "commit", _balances(), "transaction committed")
        except RuntimeError:
            _con.execute("ROLLBACK")
            _add_timeline("sqlite", "rollback", _balances(), "transaction rolled back")
        _db_total = sum(_balances().values())
        _con.close()

    # One lane per system, one box per step: the balances after it, and the total at the end.
    _style = {"crash": "dg-box dg-hot", "credit": "dg-box dg-ok", "commit": "dg-box dg-ok", "rollback": "dg-box dg-ok"}

    def _lane(y, system, label, total):
        steps = [_row for _row in _timeline if _row["system"] == system]
        parts = [f'<text x="0" y="{y + 38}" font-weight="700">{label}</text>']
        for _i, _row in enumerate(steps):
            x = 120 + _i * 250
            parts.append(
                f'<rect class="{_style.get(_row["step"], "dg-box")}" x="{x}" y="{y}" width="210" height="72" rx="12"/>'
                f'<text x="{x + 105}" y="{y + 28}" text-anchor="middle" font-weight="700">{_row["step"]}</text>'
                f'<text class="dg-muted" x="{x + 105}" y="{y + 54}" text-anchor="middle">'
                f"Alice {_row['Alice']:,} · Bob {_row['Bob']:,}</text>"
            )
            if _i:
                parts.append(f'<path class="dg-edge" d="M{x - 40} {y + 36} H {x - 6}"/>')
        _ok = total == _expected
        parts.append(
            f'<text class="{"dg-ok" if _ok else "dg-hot"}" x="870" y="{y + 44}" font-size="22">'
            f"{'&#10003;' if _ok else '&#10007;'} total {total:,}</text>"
        )
        return "".join(parts)

    _picture = diagram(
        _lane(20, "file (JSON)", "file", _file_total)
        + '<rect x="356" y="134" width="488" height="92" rx="16" fill="none" stroke="currentColor"'
        ' stroke-dasharray="8 6" opacity="0.45"/>'
        + '<text class="dg-muted" x="593" y="256" text-anchor="middle">one transaction: BEGIN ... COMMIT or ROLLBACK</text>'
        + _lane(144, "sqlite", "SQLite", _db_total),
        width=1080,
        height=270,
        label=f"Transfer of {_amount}: the file keeps a total of {_file_total}, SQLite a total of {_db_total}; "
        f"both should be {_expected}.",
    )

    _file_ok = _file_total == _expected
    _file_callout = mo.md(
        "**File:** debit and credit are two separate writes. "
        + (
            "Both landed, because nothing crashed."
            if _file_ok
            else f"The crash came between them: {_amount:,} left Alice and never reached Bob."
        )
    ).callout(kind="success" if _file_ok else "danger")
    _db_callout = mo.md(
        "**SQLite:** both updates sit in one transaction. "
        + ("The crash rolled the debit back, so the total holds." if atomic_fail.value else "They committed together.")
    ).callout(kind="success" if _db_total == _expected else "danger")

    mo.vstack(
        [
            chart_or_table(_picture, _timeline, label="Step-by-step timeline"),
            mo.hstack([_file_callout, _db_callout], widths="equal"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Atomicity & Concurrency</h3>
      <details>
        <summary><strong>Q1:</strong> With only files (no database), how can a transfer be made all‑or‑nothing?</summary>
        <p><strong>Answer:</strong> Write a small log entry first (a write‑ahead log, WAL), or write a temp file and
        rename it over the old one (an atomic rename). On restart, replay or roll back the log.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> What must always stay true in this system?</summary>
        <p><strong>Answer:</strong> The total balance never changes. Check that invariant after crashes and retries.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Should a system stop on error or allow a temporary mismatch?</summary>
        <p><strong>Answer:</strong> Finance usually fails fast; analytics may accept a temporary mismatch and repair
        it later (eventual consistency). Weigh the cost of wrong data against the cost of downtime.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 1 Conclusion

    - Unsynchronised writes lose updates; a lock or a transaction stops it.
    - A database is not magic: read, +1 in Python, write loses updates in SQLite too. Make the read
      and the write one statement, or one transaction.
    - A transaction makes a multi-step change all-or-nothing: the crashed transfer rolled back.
    - Check invariants (expected vs actual, the total balance) to catch these bugs early.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Correct data still has to be stored and sent, and every byte of it is waited for:

    $$
    \\text{wait} \\approx \\frac{\\text{bytes}}{\\text{throughput}} + \\text{parse time}
    $$

    Better formats cut the wait by shrinking the bytes or speeding up the parse.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Serialization & Deserialization Benchmarks
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 2 Introduction

    > **Key Question:** Which format gives the best trade-off for the workload (actual data + query pattern)?

    *Still in the **data tier**. Chapter 1 made writes correct; now we choose what those bytes look like.*

    Every format trades readability, portability, size and speed differently; the benchmark below
    measures the trade.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    _explanation = mo.md(
        """
    ### Serialization = Bytes on Disk (or Wire)

    Serialization transforms Python objects into bytes so they can be stored or sent.
    Deserialization rebuilds objects from bytes.

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
    **What to compare:**

    - **Speed**: how long writing and reading take  
    - **Size**: how many bytes hit disk  
    - **Interop**: language/tool compatibility  
    - **Type fidelity**: do types round-trip cleanly?  
    - **Schema evolution**: do old files survive a new field?
    - **Safety**: Pickle can execute arbitrary code

    Two words people mix up.

    **Latency** is how long *one* thing takes, end to end. Post a letter to Vienna: two days.

    **Throughput** is how much gets through per unit of time. The van leaving the depot each
    night carries 40,000 letters.

    In the benchmark below, one round trip is a file written and read back, and what gets through
    is records, counted like letters rather than by the weight of the paper:

    $$
    \\text{Latency} = \\text{write time} + \\text{read time}
    \\qquad
    \\text{Throughput} = \\frac{\\text{rows written}}{\\text{write time}}
    $$

    They trade against each other, and this is the part people get wrong. Waiting to fill the van
    raises throughput and *hurts* the latency of the first letter that boarded it. A container
    ship has appalling latency and colossal throughput. When someone says a system is fast, ask
    which one they mean. The benchmark below measures both: check whether they rank the formats
    the same way.

    *Sometimes you get both*, by making the letters smaller. That is what chapter 4 is for.

    **Format quick reference:**  
    - **JSON/CSV**: human‑readable, row‑oriented  
    - **Avro**: row‑oriented, schema‑driven events  
    - **Arrow/Feather**: columnar interchange (fast analytics)  
    - **Parquet**: columnar on‑disk analytics  
    - **Pickle**: Python‑specific (unsafe for untrusted data)
            """
    ).callout(kind="neutral")
    _flow = mo.md(
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
    </div>
            """
    )
    mo.vstack([_explanation, _flow], gap=0.6)
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
    mo.vstack(
        [mo.md("### Mini-lab: Format Decision Assistant"), format_use_case, format_priority, _note],
        gap=0.5,
    ).callout(kind="neutral")
    return format_priority, format_use_case


@app.cell
def _(format_priority, format_use_case, mo):
    _recommendations = {
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
    _choice = _recommendations[(format_use_case.value, format_priority.value)]
    mo.md(
        f"Recommended starting point: **{_choice}**\n\nTreat this as a default, then benchmark on the real workload."
    ).callout(kind="info")
    return


@app.cell
def _(mo):
    serial_rows = mo.ui.slider(200, 3000, step=200, value=800, label="Rows", show_value=True)
    serial_cols = mo.ui.slider(2, 8, value=5, label="Metric columns", show_value=True)
    run_serial = mo.ui.run_button(label="Run serialization benchmark", kind="success")
    mo.vstack(
        [
            mo.hstack([serial_rows, serial_cols], widths="equal"),
            mo.md(
                "Six formats, the same records. Every write and every read runs three times and "
                "the table keeps the fastest, so a one-off start-up cost cannot decide the ranking."
            ),
            run_serial,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return run_serial, serial_cols, serial_rows


@app.cell
def _(
    Path,
    alt,
    best_seconds,
    csv,
    fastavro,
    feather,
    json,
    mo,
    pa,
    pd,
    pickle,
    pq,
    random,
    run_serial,
    serial_cols,
    serial_rows,
    static_table,
    tempfile,
):
    mo.stop(not run_serial.value, mo.md("Click **Run serialization benchmark** to execute.").callout(kind="neutral"))

    _rng = random.Random(42)
    _records = [
        {"id": _i, "city": _rng.choice(["Zurich", "Basel", "Geneva", "Bern", "Lugano"]), "score": round(_rng.random() * 100, 3)}
        | {f"metric_{_c}": round(_rng.random() * 1000, 5) for _c in range(serial_cols.value)}
        for _i in range(serial_rows.value)
    ]
    _avro_schema = {
        "type": "record",
        "name": "Record",
        "fields": [{"name": "id", "type": "int"}, {"name": "city", "type": "string"}]
        + [{"name": _field, "type": "double"} for _field in list(_records[0])[2:]],
    }

    def _csv_write(path):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_records[0])
            writer.writeheader()
            writer.writerows(_records)

    def _csv_read(path):
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _avro_write(path):
        with path.open("wb") as f:
            fastavro.writer(f, _avro_schema, _records)

    def _avro_read(path):
        with path.open("rb") as f:
            return list(fastavro.reader(f))

    _formats = {  # label: (write(path), read(path))
        "JSON": (
            lambda p: p.write_text(json.dumps(_records), encoding="utf-8"),
            lambda p: json.loads(p.read_text(encoding="utf-8")),
        ),
        "Pickle (unsafe)": (
            lambda p: p.write_bytes(pickle.dumps(_records, pickle.HIGHEST_PROTOCOL)),
            lambda p: pickle.loads(p.read_bytes()),
        ),
        "CSV": (_csv_write, _csv_read),
        "Arrow/Feather": (lambda p: feather.write_feather(pa.Table.from_pylist(_records), p), feather.read_table),
        "Parquet": (lambda p: pq.write_table(pa.Table.from_pylist(_records), p), pq.read_table),
        "Avro": (_avro_write, _avro_read),
    }

    _rows = []
    with tempfile.TemporaryDirectory() as _tmp:
        for _label, (_write, _read) in _formats.items():
            _path = Path(_tmp) / _label.replace("/", "_")
            _write_ms = best_seconds(_write, _path) * 1000  # best of 3: only the first call pays the warm-up
            _read_ms = best_seconds(_read, _path) * 1000
            _rows.append(
                {
                    "format": _label,
                    "write (ms)": round(_write_ms, 2),
                    "read (ms)": round(_read_ms, 2),
                    "latency (ms)": round(_write_ms + _read_ms, 2),
                    "size (KB)": round(_path.stat().st_size / 1024, 1),
                    "rows/s written": round(len(_records) / _write_ms * 1000),
                }
            )

    _bars = (
        alt.Chart(pd.DataFrame(_rows))
        .mark_bar()
        .encode(y=alt.Y("format:N", sort=None, title=None))
        .properties(width="container", height=200)  # half the page each, at any screen width
        .configure(background="transparent")  # sit on the page, light or dark
        .configure_axis(labelFontSize=13, titleFontSize=13, tickCount=4)
    )

    mo.vstack(
        [
            static_table(_records[:3], label="Sample records"),
            static_table(_rows, label="Serialization benchmark (best of 3)"),
            mo.md("**Shorter bars win in both charts.**"),
            mo.hstack([_bars.encode(x="size (KB):Q"), _bars.encode(x="latency (ms):Q")], widths="equal", gap=2),
            mo.md(
                "Numbers vary by machine and caching, so compare the formats with each other, not with "
                "another laptop. The reads are not quite like for like: Arrow and Parquet stop at a columnar "
                "table without building Python objects, and CSV hands back strings it never converts to numbers."
            ).callout(kind="info"),
            mo.md(
                "**Security note:** Pickle is not safe for untrusted data. Only load Pickle files from trusted sources."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, mo, pd, static_table, tempfile):
    _src = pd.read_parquet(SALES_SEED, columns=["sale_id", "sale_date", "total_price"]).head(500)
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
        except TypeError as _exc:
            return f"TypeError: {_exc}"

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
    Open the CSV in a text editor and the date is right there: `2024-03-07`. The bytes did not
    lose the date. They lost **the note saying it was a date**, and that note is what your analysis
    was standing on. Parquet stores the date as a plain number and keeps the note in its schema,
    which is why it came back as `datetime64`.

    The first failure shouted. The second did not: the store codes came back as `7, 10, 42`
    with no error, no warning and nothing in the log. That is the one that ends up in a report.
            """
    ).callout(kind="warn")

    mo.vstack(
        [
            static_table(_dtypes, label="Same 500 rows, written two ways and read back"),
            static_table(_answers, label="Now ask the data a question", wrapped_columns=["via CSV"]),
            _note,
        ],
        gap=0.6,
    )
    return


@app.cell
def _(csv, fastavro, io, mo, static_table):
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

    _csv_row = next(csv.DictReader(io.StringIO("sale_id,total_price\n1,4034.91\n")))
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
        "The printed form is not decoration. It is what lets a sheet filled in last year and a "
        "program written this morning still agree. CSV ships without the form, so the agreement "
        "lives only in someone's memory."
    ).callout(kind="info")
    mo.vstack(
        [
            mo.md("### Schema Evolution: the office adds a box to the form"),
            static_table(_rows, label="Same change, three situations", wrapped_columns=["result", "verdict"]),
            _note,
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
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
        <p><strong>Answer:</strong> In staging (a production-like test environment), then confirmed on a canary (the new format serving a small share of real traffic). Compare before/after on the same workload.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 2 Conclusion

    - Format choice is a trade-off between speed, size, interoperability, and safety.
    - Use benchmarks from a representative workload to compare latency and storage cost.
    - CSV keeps values but drops types: dates came back as `str`, store code `007` as `7`.
      Parquet and Avro carry the schema.
    - An Avro reader schema with defaults lets last year's files and this year's code agree.
    - Pickle preserves Python types but should not be used for untrusted data.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
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
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Column-Based vs Row-Based Storage
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 3 Introduction

    > **Key Question:** Is read work spent on data that queries do not need?

    *Still in the **data tier**. Chapter 2 picked a format; now we choose how it is arranged on disk.*

    Storage layout determines read cost:

    - Row store: incurs read cost (I/O + CPU) for whole rows
    - Column store: incurs read cost mainly for selected columns
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Row Store vs Column Store

    **Row stores** keep full records together. Great for OLTP (Online Transaction Processing) and point lookups.  
    **Column stores** group values by column. Great for scans, aggregates, and compression.

    If a query scans only *k* columns out of *C*, the I/O pattern changes:

    $$
    \\text{IO}_{\\text{row}} \\approx N \\times C
    \\qquad
    \\text{IO}_{\\text{col}} \\approx N \\times k
    $$

    Where:
    - $N$: number of rows  
    - $C$: total columns in the dataset  
    - $k$: columns actually needed by the query ($k \\ll C$ for narrow queries)

    A shop keeps its sales two ways.

    **The shoebox.** Every sale is one till receipt: sale number, date, product, country, units,
    price and rating printed together on one slip. To answer *what did we take in January 2026?*
    you pick up all 3,360 slips one at a time, read the date, read the price, and put down the
    other five fields untouched. You handled every field of every sale to use two of them. That
    is a **row store**, and it is exactly the right shape for *show me sale 2,914*: one slip, one grab.

    **The ledger.** The same sales copied into a bookkeeper's ledger, one field per page: a long
    page of dates, a long page of prices, a long page of product codes. The same question now
    means taking down two pages and leaving the other five on the shelf. That is a **column
    store**. It is the wrong shape for *show me sale 2,914*, which is now line 2,914 of seven
    different pages.

    Same sales, same shop. The cost of a question changed because the paper was arranged
    differently.

    *Two things the picture does not show.* The ledger pages are written in shorthand, so they are
    not all the same size, which is chapter 4. And the ledger is not one endless page per field,
    which comes right after the benchmark.

    Below we time both layouts on the same numbers.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card flow-card">
      <h3>Visual: Same Table, Two Physical Layouts</h3>
      <div class="grid-2">
        <div>
          <h4>Row layout (record-oriented)</h4>
          <pre>sale 1: [sale_id, sale_date, total_price, …]
    sale 2: [sale_id, sale_date, total_price, …]
    sale 3: [sale_id, sale_date, total_price, …]
    …</pre>
          <div class="flow-note">Good when each request needs most fields of one row.</div>
        </div>
        <div>
          <h4>Column layout (analytics-oriented)</h4>
          <pre>sale_id:     [1,  2,  3,  …]
    sale_date:   [d1, d2, d3, …]
    total_price: [p1, p2, p3, …]
    …</pre>
          <div class="flow-note">Good when queries touch a few columns across many rows.</div>
        </div>
      </div>
    </div>
    """)
    return


@app.cell
def _(mo):
    n_rows = mo.ui.slider(250, 1000, step=250, value=1000, label="Rows (thousands)", show_value=True)
    run_storage = mo.ui.run_button(label="Run storage benchmark", kind="success")
    mo.hstack([n_rows, run_storage], justify="start", align="center", gap=2).callout(kind="neutral")
    return n_rows, run_storage


@app.cell
def _(best_seconds, mo, n_rows, np, run_storage, static_table):
    mo.stop(not run_storage.value, mo.md("Click **Run storage benchmark** to execute.").callout(kind="neutral"))

    _operations = {
        "Count c0 > 0.75": lambda t: np.count_nonzero(t[:, 0] > 0.75),
        "Sum c0": lambda t: t[:, 0].sum(),
    }
    _results = []
    for _cols in (2, 4, 8, 16):
        # The same numbers stored twice in memory, like the shoebox and the ledger.
        _row_store = np.random.default_rng(7).random((n_rows.value * 1000, _cols))  # C order: each record contiguous
        _col_store = np.asfortranarray(_row_store)  # F order: each column contiguous
        for _operation, _fn in _operations.items():
            # best of 5: each operation is sub-millisecond, so a stray hiccup would dominate
            _row_ms = best_seconds(_fn, _row_store, repeat=5) * 1000
            _col_ms = best_seconds(_fn, _col_store, repeat=5) * 1000
            _results.append(
                {
                    "operation": _operation,
                    "columns (C)": _cols,
                    "row layout (ms)": round(_row_ms, 3),
                    "column layout (ms)": round(_col_ms, 3),
                    "column is faster by": f"{_row_ms / _col_ms:.1f}x",
                }
            )
    _results.sort(key=lambda r: r["operation"])  # stable: each operation's rows stay in column order

    _note = mo.md(
        """
    **Discussion:** The same numbers, stored once record by record and once column by column.
    No file is written, so this is not Avro against Parquet, only the access pattern each one uses.

    Both operations read one column. In the row layout its values sit a whole record apart, and the
    CPU fetches memory in 64-byte cache lines, so it hauls in the neighbouring fields and throws them
    away. In the column layout the values lie side by side and every byte fetched is used.

    **Read down the table:** as the column count grows, the row side slows down while the column
    side stays put. That is $\\text{IO}_{\\text{row}} / \\text{IO}_{\\text{col}} = C/k$ at work with $k = 1$: a direction, not an exact ratio. Parquet
    goes further and never reads the unused columns from disk.
            """
    ).callout(kind="info")

    mo.vstack([static_table(_results, label="Row vs column layout, same numbers"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    mo.md(
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

    Now watch what the index card buys. Someone asks for the average sale in 2026. You read the
    card first and it says:

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
      A section labelled <code style="white-space: nowrap">2024-03-01 .. 2026-02-27</code> must be opened, and may turn out to hold no
      2026 sale at all. Min and max are a rejection test, not a search.
    - This is why the order rows were written in is not cosmetic. Drop the sales into the binder
      in random order and every section's card reads roughly <code style="white-space: nowrap">2024-03-01 .. 2026-02-27</code>. Every
      label spans everything, every label is useless, and you open all eight sections. The
      mechanism did not fail. You gave it nothing to work with. The next cell measures exactly
      that, on the real file.
        """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    run_rowgroup = mo.ui.run_button(label="Run row-group audit", kind="success")
    mo.vstack(
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
    return (run_rowgroup,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, run_rowgroup, static_table, tempfile):
    mo.stop(not run_rowgroup.value, mo.md("Click **Run row-group audit** to read the index card.").callout(kind="neutral"))
    _df = pd.read_parquet(SALES_SEED)
    _cut = "2026-01-01"
    _wanted = ["sale_date", "total_price"]

    with tempfile.TemporaryDirectory() as _td:
        _ordered = Path(_td) / "date_ordered.parquet"
        _shuffled = Path(_td) / "shuffled.parquet"
        _df.sort_values("sale_date").to_parquet(_ordered, index=False, row_group_size=420)
        _df.sample(frac=1, random_state=7).to_parquet(_shuffled, index=False, row_group_size=420)

        _con = duckdb.connect()
        _rows = []
        _ordered_size, _shuffled_size = _ordered.stat().st_size, _shuffled.stat().st_size
        for _label, _path in (("date-ordered", _ordered), ("shuffled", _shuffled)):
            _md = _con.execute(
                "SELECT row_group_id, path_in_schema, total_compressed_size, stats_max "
                f"FROM parquet_metadata('{_path.as_posix()}')"
            ).df()
            _two_cols = _md[_md["path_in_schema"].isin(_wanted)]
            # The index card: a section survives only if its LATEST date reaches the cut-off.
            _dates = _md[_md["path_in_schema"] == "sale_date"]
            _live = _dates[_dates["stats_max"] >= _cut]["row_group_id"]
            _answer = _con.execute(
                f"SELECT round(avg(total_price), 2) FROM '{_path.as_posix()}' WHERE sale_date >= '{_cut}'"
            ).fetchone()[0]
            _rows.append(
                {
                    "file": _label,
                    "A: all columns": int(_md["total_compressed_size"].sum()),
                    "B: 2 columns": int(_two_cols["total_compressed_size"].sum()),
                    "C: 2 columns, open sections": int(
                        _two_cols[_two_cols["row_group_id"].isin(_live)]["total_compressed_size"].sum()
                    ),
                    "opened": f"{len(_live)} of {_md['row_group_id'].nunique()}",
                    "answer": _answer,
                }
            )

    _sorted, _mixed = _rows
    _note = mo.md(
        f"""
    Read the top row left to right. Choosing columns took the read from **{_sorted['A: all columns']:,}**
    bytes to **{_sorted['B: 2 columns']:,}**. That is what this chapter has taught so far. The index card
    then took it from {_sorted['B: 2 columns']:,} to **{_sorted['C: 2 columns, open sections']:,}**, and
    nobody wrote that in the query.

    Now read the second row. Identical data, identical query, rows written in a different order,
    and the index card buys **nothing**: {_mixed['opened']} sections opened, because every
    label spans the whole range. Sorting is not tidying. It is what makes the skipping possible.

    Two honesty notes. These are bytes the engine is *entitled to skip*, computed from the file's
    own footer, not bytes measured leaving the disk. And the shuffled file is also
    {_shuffled_size / _ordered_size - 1:.0%} larger ({_shuffled_size:,} against {_ordered_size:,} bytes)
    from the very same rows, which is a preview of chapter 4: order is itself a form of compression.
    Both files return the same answer, which is the point.
            """
    ).callout(kind="info")
    mo.vstack([static_table(_rows, label="Bytes the query must read"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    mo.md("""
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
        <summary><strong>Q3:</strong> Why does write order matter for Parquet?</summary>
        <p><strong>Answer:</strong> Min/max can only exclude a row group whose range misses the filter. Sorted data gives narrow ranges; shuffled data gives every group the full range.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 3 Conclusion

    - Row layouts favour transactional record-level access; column layouts favour scans and aggregates.
    - Reading only required columns cuts I/O and typically improves analytics performance.
    - Parquet keeps min/max per row group in its footer. Sorted by date, the footer lets the query
      skip 7 of 8 row groups; shuffled, none.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Columnar data puts similar values together, and similar values are easier to compress.
    Next we measure how much size reduction we can actually get.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 4. Compression & Encoding (Parquet, Gzip)
    """)
    return


@app.cell
def _(mo):
    mo.md(
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
    T_{\\text{total}} \\approx T_{\\text{io}} + T_{\\text{decompress}} + T_{\\text{compute}}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Compression & Encoding

    Compression ratio (lower is better):

    $$
    r = \\frac{\\text{compressed size}}{\\text{original size}}
    \\qquad
    \\text{savings} = 1 - r
    $$

    We compare JSON/CSV to gzip and Parquet with different codecs.

    **Compression level.** gzip takes a level from 1 (fast, saves less) to 9 (slow, saves most).
    The `gzip` tool and zlib default to 6; Python's `gzip.compress` defaults to 9. Going from 6
    to 9 buys almost nothing while the CPU cost roughly doubles. Watch the level rows in the
    benchmark and the timing lab below.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    budget_size_gb = mo.ui.slider(1, 500, value=120, label="Raw dataset size (GB)", show_value=True, debounce=True)
    budget_ratio = mo.ui.slider(0.1, 1.0, step=0.05, value=0.35, label="Compression ratio", show_value=True, debounce=True)
    budget_scans_day = mo.ui.slider(1, 80, value=18, label="Full scans/day", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Mini-lab: Compression Cost Impact"),
            mo.hstack([budget_size_gb, budget_ratio], widths="equal"),
            budget_scans_day,
            mo.md("Set the compression ratio and scan frequency to estimate the I/O saved per day. A first-order estimate, not a benchmark.").callout(kind="info"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return budget_ratio, budget_scans_day, budget_size_gb


@app.cell
def _(budget_ratio, budget_scans_day, budget_size_gb, mo):
    _on_disk = budget_size_gb.value * budget_ratio.value
    _saved = budget_size_gb.value - _on_disk
    mo.hstack(
        [
            mo.stat(f"{_on_disk:,.1f} GB", label="On disk after compression", bordered=True),
            mo.stat(f"{_saved:,.1f} GB", label="Less to read per full scan", bordered=True),
            mo.stat(f"{_saved * budget_scans_day.value:,.1f} GB", label="Less I/O per day", bordered=True),
        ],
        widths="equal",
    )
    return


@app.cell
def _(mo):
    mo.Html(
        """
    <div class="disclaimer-red">
      Disclaimer: PCA will be discussed in depth in the <strong>Machine Learning 2</strong> module.
      Here it is only used as a simple example to illustrate compression ideas.
    </div>
            """
    )
    return


@app.cell
def _(mo):
    image_demo_rank = mo.ui.slider(4, 90, value=26, step=2, label="Components kept (rank k)", show_value=True, debounce=True)
    image_demo_width = mo.ui.slider(200, 360, value=280, step=20, label="Image width (px)", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Mini-lab: Visual Compression with PCA (Cat Image)"),
            mo.hstack([image_demo_rank, image_demo_width], widths="equal"),
            mo.md(
                "Left is the original cat. Right is rebuilt from only the top `k` singular vectors per colour channel "
                "(rank-k SVD, the maths behind PCA)."
            ).callout(kind="info"),
            mo.md("Further details: [Principal Component Analysis (PCA)](https://en.wikipedia.org/wiki/Principal_component_analysis)").callout(kind="neutral"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return image_demo_rank, image_demo_width


@app.cell
def _(Image, ImageDraw, image_demo_width, np):
    # Drawn here, so the lab needs no image file. This cell reads only the width: dragging k
    # reuses the SVD below instead of redoing it.
    _w = image_demo_width.value
    _h = int(_w * 0.74)
    _img = Image.new("RGB", (_w, _h))
    _d = ImageDraw.Draw(_img)
    for _y in range(_h):  # soft vertical gradient
        _t = _y / (_h - 1)
        _d.line([(0, _y), (_w, _y)], fill=(int(218 + 18 * _t), int(229 + 14 * _t), int(242 + 10 * _t)))
    _step = max(6, _w // 45)  # a checker texture, so compression artefacts show
    for _x in range(0, _w, _step):
        for _y in range(0, _h, _step):
            if (_x // _step + _y // _step) % 2 == 0:
                _d.rectangle([_x, _y, min(_w - 1, _x + _step), min(_h - 1, _y + _step)], fill=(225, 232, 245))

    _cx, _cy = _w // 2, int(_h * 0.56)
    _r = int(min(_w, _h) * 0.24)

    def _p(_fx, _fy):
        """The point (fx, fy) face radii away from the centre of the face."""
        return _cx + int(_fx * _r), _cy + int(_fy * _r)

    _fur, _dark, _line = (220, 192, 158), (96, 74, 56), (88, 67, 54)
    _ex, _ey = int(0.50 * _r), _cy - int(0.14 * _r)
    _ew, _eh = int(0.25 * _r), int(0.18 * _r)
    _pw, _ph, _sp = max(4, int(0.08 * _r)), max(7, int(0.20 * _r)), max(3, int(0.05 * _r))
    for _s in (-1, 1):  # ears; every feature but the face and nose comes in a mirrored pair
        _d.polygon([_p(_s * 0.82, -0.52), _p(_s * 0.40, -1.35), _p(_s * 0.03, -0.58)], fill=_fur, outline=_dark, width=3)
        _d.polygon([_p(_s * 0.70, -0.56), _p(_s * 0.40, -1.16), _p(_s * 0.12, -0.62)], fill=(246, 186, 198))
    _d.ellipse([_cx - _r, _cy - _r, _cx + _r, _cy + _r], fill=_fur, outline=_dark, width=3)
    _d.ellipse([_p(-0.45, 0.05), _p(0.45, 0.62)], fill=(236, 214, 190))
    for _s in (-1, 1):  # eyes, pupils, sparkles
        _x = _cx + _s * _ex
        _d.ellipse([(_x - _ew, _ey - _eh), (_x + _ew, _ey + _eh)], fill=(143, 198, 128), outline=(40, 40, 40), width=2)
        _d.ellipse([(_x - _pw, _ey - _ph), (_x + _pw, _ey + _ph)], fill=(18, 22, 20))
        _d.ellipse([(_x - _sp, _ey - _sp), (_x + _sp, _ey + _sp)], fill=(255, 255, 255))
    _ny = _cy + int(0.13 * _r)
    _d.polygon([(_cx, _ny), (_cx - int(0.13 * _r), _ny + int(0.15 * _r)), (_cx + int(0.13 * _r), _ny + int(0.15 * _r))], fill=(234, 150, 165), outline=(120, 74, 86))
    _d.line([(_cx, _ny + int(0.15 * _r)), _p(0, 0.48)], fill=_line, width=2)
    for _s in (-1, 1):  # mouth, cheeks, forehead marks, whiskers
        _d.arc([_p(min(0, _s * 0.24), 0.38), _p(max(0, _s * 0.24), 0.62)], start=200, end=340, fill=_line, width=2)
        _d.ellipse([_p(min(_s * 0.70, _s * 0.44), 0.16), _p(max(_s * 0.70, _s * 0.44), 0.36)], fill=(247, 178, 186))
        _d.line([_p(0, -0.34), _p(_s * 0.11, -0.48)], fill=(187, 151, 118), width=2)
        for _o in (-1, 0, 1):
            _dy = _o * int(0.13 * _r)
            _d.line([(_cx + _s * int(0.12 * _r), _cy + int(0.28 * _r) + _dy), (_cx + _s * int(0.95 * _r), _cy + int(0.13 * _r) + _dy)], fill=_line, width=2)

    ch4_cat = np.asarray(_img)
    # One SVD per colour channel, run as a batch of three. It is the slow step, so once per width.
    ch4_cat_svd = np.linalg.svd(ch4_cat.transpose(2, 0, 1) / 255.0, full_matrices=False)
    return ch4_cat, ch4_cat_svd


@app.cell
def _(ch4_cat, ch4_cat_svd, gzip, image_demo_rank, io, mo, np, static_table):
    _k = image_demo_rank.value
    _u, _s, _vt = ch4_cat_svd
    _u, _s, _vt = _u[:, :, :_k], _s[:, :_k], _vt[:, :_k]
    _rebuilt = np.rint(np.clip((_u * _s[:, None]) @ _vt, 0, 1) * 255).astype(np.uint8).transpose(1, 2, 0)
    _pca = io.BytesIO()  # what the lossy method has to store: the kept factors, as float16
    np.savez_compressed(_pca, *(_m.astype(np.float16) for _m in (_u, _s, _vt)))
    _gz = gzip.compress(ch4_cat.tobytes(), 6)
    _gz_back = np.frombuffer(gzip.decompress(_gz), np.uint8).reshape(ch4_cat.shape)

    _table = static_table(
        [
            {
                "method": _method,
                "bytes": _size,
                "ratio (compressed/raw)": round(_size / ch4_cat.nbytes, 4),
                "identical to the original?": "yes" if np.array_equal(_back, ch4_cat) else "no",
                "worst pixel off by (of 255)": int(np.abs(_back.astype(int) - ch4_cat).max()),
            }
            for _method, _size, _back in (
                ("gzip (lossless method)", len(_gz), _gz_back),
                (f"PCA k={_k} (lossy method)", len(_pca.getvalue()), _rebuilt),
            )
        ],
        label=f"Same {ch4_cat.nbytes:,}-byte image, two kinds of compression",
    )
    _note = mo.md(
        """
    **Two different promises, and confusing them is expensive.**

    **Lossless** is a letter folded to fit an envelope. Every word is still there; unfold it and
    you get the original back exactly, byte for byte. gzip, PNG and Parquet are lossless. This is
    the only kind you may use on money.

    **Lossy** is a summary. Usually much smaller, still useful, and the original is gone forever.
    PCA here, JPEG and MP3 in the world. Fine for a photo, where nobody can tell. Never fine for a
    price.

    The last two columns are the whole difference: gzip *promises* an exact copy, PCA only a
    close one (push `k` high enough and close can round to exact, but nothing promised it). Notice
    which row is actually smaller, too. On this image the lossless method wins, because a smooth
    drawing repeats itself enormously and repetition is exactly what lossless compression removes.
            """
    ).callout(kind="info")
    _pipeline = mo.Html(
        """
    <div class="section-card flow-card">
      <div class="flow-diagram">
        <div class="flow-box">Image as 3 matrices (R, G, B)</div>
        <div class="flow-arrow">&rarr;</div>
        <div class="flow-box">Keep the top k components</div>
        <div class="flow-arrow">&rarr;</div>
        <div class="flow-box">Rebuilt image</div>
      </div>
    </div>
        """
    )
    _images = mo.hstack(
        [
            mo.image(ch4_cat, width="100%", caption="Original"),
            mo.image(_rebuilt, width="100%", caption=f"Rebuilt from k={_k} components"),
        ],
        widths="equal",
        gap=0.8,
    )
    mo.vstack([_pipeline, _images, _table, _note], gap=0.6)
    return


@app.cell
def _(mo):
    run_lossy_money = mo.ui.run_button(label="Run lossy vs lossless on money", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: The Cat Trick, Applied to Sales Prices"),
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
    return (run_lossy_money,)


@app.cell
def _(SALES_SEED, io, mo, pd, run_lossy_money, static_table):
    mo.stop(
        not run_lossy_money.value,
        mo.md("Write your prediction down, then click **Run lossy vs lossless on money**.").callout(kind="neutral"),
    )
    _src = pd.read_parquet(SALES_SEED, columns=["sale_id", "total_price"])
    _truth = round(float(_src["total_price"].sum()), 2)
    _rows = []
    for _label, _digits, _codec in (
        ("exact (lossless)", None, "snappy"),
        ("exact + gzip (lossless)", None, "gzip"),
        ("rounded to the franc (lossy)", 0, "gzip"),
        ("rounded to 10 francs (lossy)", -1, "gzip"),
        ("rounded to 100 francs (lossy)", -2, "gzip"),
    ):
        _stored = _src if _digits is None else _src.assign(total_price=_src["total_price"].round(_digits))
        _blob = _stored.to_parquet(index=False, compression=_codec)  # no path: the file's bytes
        _total = round(float(pd.read_parquet(io.BytesIO(_blob))["total_price"].sum()), 2)
        _rows.append(
            {
                "how the prices are stored": _label,
                "bytes": len(_blob),
                "total revenue it reports": _total,
                "off by": round(_total - _truth, 2),
            }
        )
    _exact, _exact_gz, *_, _hundred = (_row["bytes"] for _row in _rows)

    _note = mo.md(
        f"""
    **The lossy files really are smaller.** Rounding to the nearest 100 francs cuts another
    {1 - _hundred / _exact_gz:.0%} off the gzipped file, a bigger win than gzip itself managed on
    the exact data ({1 - _exact_gz / _exact:.0%}).

    **And the last column is why nobody does this.** The true total is
    `{_truth:,.2f}`. Every lossy row reports a different number, and none of them is flagged: the
    file loads cleanly, the column is still a decimal, every tool downstream is perfectly happy.

    This is the same trick that was completely acceptable on the cat. The difference is not the
    technique, it is **what the numbers mean**. Nobody minds a cat whose pixels are a few shades
    off on average. Every accountant can see a total that is off by hundreds of francs, and by
    then the original is gone.

    So the rule is not "lossy compression is bad". It is: **lossy compression is a decision about
    whether an approximation of this particular value is still the truth you need.** For a photo,
    usually yes. For money, an identifier or a date, never.
            """
    ).callout(kind="danger")
    mo.vstack([static_table(_rows, label=f"Same {len(_src):,} prices, stored five ways"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    compress_rows = mo.ui.slider(500, 10_000, step=500, value=2_000, label="Rows", show_value=True)
    compress_cols = mo.ui.slider(3, 10, value=6, label="Numeric columns", show_value=True)
    ch4_compress_repeat = mo.ui.switch(label="Only 5 distinct values per column")
    run_compress = mo.ui.run_button(label="Run compression benchmark", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Which Format Is Smallest?"),
            mo.md(
                "**Predict first.** JSON, CSV, gzip or Parquet: which one wins? "
                "Would your answer change if every column held only five different values?"
            ).callout(kind="info"),
            mo.hstack([compress_rows, compress_cols], widths="equal"),
            ch4_compress_repeat,
            run_compress,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return ch4_compress_repeat, compress_cols, compress_rows, run_compress


@app.cell
def _(
    ch4_compress_repeat,
    compress_cols,
    compress_rows,
    csv,
    gzip,
    io,
    json,
    mo,
    pa,
    pq,
    random,
    run_compress,
    static_table,
):
    mo.stop(not run_compress.value, mo.md("Click **Run compression benchmark** to execute.").callout(kind="neutral"))
    _rng = random.Random(11)  # fixed seed: the same settings always give the same table
    _pool = [round(_rng.random() * 1000, 5) for _ in range(5)]

    def _measurement():
        return _rng.choice(_pool) if ch4_compress_repeat.value else round(_rng.random() * 1000, 5)

    _records = [
        {"id": _i, "category": _rng.choice("ABCD"), **{f"metric_{_c}": _measurement() for _c in range(compress_cols.value)}}
        for _i in range(compress_rows.value)
    ]
    _csv = io.StringIO()
    _writer = csv.DictWriter(_csv, fieldnames=_records[0])
    _writer.writeheader()
    _writer.writerows(_records)

    # Sizes measured in memory: the bytes a file would hold, without writing one.
    _texts = {"JSON": json.dumps(_records).encode(), "CSV": _csv.getvalue().encode()}
    _sizes = {_name: len(_blob) for _name, _blob in _texts.items()}
    # Level 1 is fastest, 9 squeezes hardest (Python's default), 6 is zlib's default.
    _sizes |= {f"{_name}+gzip (level {_lvl})": len(gzip.compress(_blob, _lvl)) for _name, _blob in _texts.items() for _lvl in (1, 6, 9)}
    _table = pa.Table.from_pylist(_records)
    for _codec in ("snappy", "gzip", "zstd", "brotli"):
        _buf = io.BytesIO()
        pq.write_table(_table, _buf, compression=_codec)
        _sizes[f"Parquet ({_codec})"] = len(_buf.getvalue())

    _smallest = min(_sizes.values())
    _best = " and ".join(_name for _name, _size in _sizes.items() if _size == _smallest)  # ties happen: gzip 6 and 9
    _note = mo.md(
        f"""
    **Smallest here: {_best}**, at {_smallest / _sizes['JSON']:.0%} of the JSON bytes.

    The `ratio vs JSON` column is size ÷ JSON size: 0.25 means a quarter of the bytes to read from disk or network.

    **And why the ranking is not a law.** Compression removes **repetition**, so the winner
    depends on your columns, not on the format's reputation. Distinct 5-decimal measurements
    hold almost none: Parquet stores each one as 8 bytes of float64, while gzipped text pays only
    for the digits you wrote. Five repeated values per column are exactly what Parquet's
    dictionary encoding lives on. At the default 2,000 rows x 6 columns, flipping the switch moves
    the win from gzipped CSV to Parquet.

    Nothing about Parquet changed. Before you pick a format, look at your columns.
        """
    ).callout(kind="info")
    mo.vstack(
        [
            static_table(
                [{"format": _name, "size (bytes)": _size, "ratio vs JSON": round(_size / _sizes["JSON"], 4)} for _name, _size in _sizes.items()],
                label="Compression ratios (baseline: JSON size)",
            ),
            _note,
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    run_ctime = mo.ui.run_button(label="Run compression timing", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Does Compression Make the Query *Faster*?"),
            mo.md(
                "This chapter opened by asking whether compression cuts total query time, not just "
                "file size. So far we have only measured size. Now we time the whole job on the sales "
                "file already in memory: unpack it if needed, parse it, and sum one column. "
                "Every time is the best of 5 bursts."
            ).callout(kind="info"),
            run_ctime,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_ctime,)


@app.cell
def _(SALES_SEED, best_seconds, gzip, io, mo, pd, run_ctime, static_table):
    mo.stop(not run_ctime.value, mo.md("Click **Run compression timing** to measure it.").callout(kind="neutral"))

    _raw = pd.read_parquet(SALES_SEED).to_csv(index=False).encode("utf-8")

    def _ms(_fn, _calls=20):
        """Milliseconds per call, fastest of 5 bursts. A burst averages out sub-millisecond noise."""
        return best_seconds(_fn, repeat=5, number=_calls) * 1000

    def _answer(_csv_bytes):
        return pd.read_csv(io.BytesIO(_csv_bytes))["total_price"].sum()

    _plain = _ms(lambda: _answer(_raw))
    _rows = [{"variant": "plain CSV", "bytes": len(_raw), "read + parse + sum (ms)": round(_plain, 2), "vs plain": "1.00x", "compress (ms)": "-", "decompress (ms)": "-"}]
    for _level in (1, 6, 9):
        _blob = gzip.compress(_raw, _level)
        _read = _ms(lambda _b=_blob: _answer(gzip.decompress(_b)))
        _rows.append(
            {
                "variant": f"gzip level {_level}",
                "bytes": len(_blob),
                "read + parse + sum (ms)": round(_read, 2),
                "vs plain": f"{_read / _plain:.2f}x",
                "compress (ms)": round(_ms(lambda _lv=_level: gzip.compress(_raw, _lv), 2), 2),
                "decompress (ms)": round(_ms(lambda _b=_blob: gzip.decompress(_b)), 2),
            }
        )
    _plain_row, _l1, _l6, _l9 = _rows
    if min(_row["read + parse + sum (ms)"] for _row in (_l1, _l6, _l9)) > _plain_row["read + parse + sum (ms)"]:
        _verdict = (
            f"**The answer is no, not here.** The gzipped file is {_l6['bytes'] / len(_raw):.0%} of the size "
            "and still takes *longer* to answer the same question."
        )
    else:
        _verdict = "**Here it is a wash:** unpacking costs about as much as the smaller file saves."

    _note = mo.md(
        f"""
    {_verdict}

    Compression trades CPU for I/O. Here the file already sits in memory, so there is no I/O to
    save: the extra bytes cost nothing to read, while unpacking them costs CPU on every query.
    Send the same file across a network and the trade flips, which is why compression is normal
    for transfer and a judgement call on a local disk.

    Look at levels 6 and 9 too. They land {abs(_l6['bytes'] - _l9['bytes']):,} bytes apart, and
    level 9 spent {_l9['compress (ms)'] / _l6['compress (ms)']:.1f}x the CPU to find them.
    Decompression costs about the same at every level, so **the level you pick is a decision
    about writing, not reading.**
        """
    ).callout(kind="warn")
    mo.vstack([static_table(_rows, label="Same question, four ways to store the file"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    dict_rows = mo.ui.slider(1000, 200000, step=1000, value=20000, label="Rows", show_value=True, debounce=True)
    dict_unique = mo.ui.slider(2, 1000, step=1, value=20, label="Unique values", show_value=True, debounce=True)
    dict_value_bytes = mo.ui.slider(1, 40, step=1, value=10, label="Average bytes per original value", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Dictionary Encoding Intuition (Toy Model)"),
            mo.hstack([dict_rows, dict_unique], widths="equal"),
            dict_value_bytes,
            mo.md(
                "We estimate storage two ways: (1) store every value in full, or (2) store a dictionary "
                "of the unique values plus a compact integer code per row."
            ).callout(kind="info"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return dict_rows, dict_unique, dict_value_bytes


@app.cell
def _(dict_rows, dict_unique, dict_value_bytes, math, mo, static_table):
    _code_bits = math.ceil(math.log2(dict_unique.value))
    _raw_bytes = dict_rows.value * dict_value_bytes.value
    _dictionary_bytes = dict_unique.value * dict_value_bytes.value
    _index_bytes = dict_rows.value * _code_bits / 8
    _ratio = (_dictionary_bytes + _index_bytes) / _raw_bytes

    _table = static_table(
        [
            {"metric": "Raw storage (no dictionary)", "formula": "rows x bytes_per_value", "value": _raw_bytes},
            {"metric": "Dictionary storage", "formula": "unique_values x bytes_per_value", "value": _dictionary_bytes},
            {"metric": "Code size per row", "formula": "ceil(log2(unique_values)) bits", "value": _code_bits},
            {"metric": "Encoded indexes storage", "formula": "rows x code_bits/8", "value": round(_index_bytes, 2)},
            {"metric": "Estimated encoded/raw ratio", "formula": "(dictionary + indexes) / raw", "value": round(_ratio, 4)},
            {"metric": "Estimated savings", "formula": "1 - ratio", "value": f"{(1 - _ratio) * 100:.2f}%"},
        ],
        label="Dictionary encoding intuition (toy calculation)",
    )
    _note = mo.md(
        """
    Interpretation:

    - Lower `unique values` usually means fewer bits per code and better compression.
    - If almost every row has a different value, dictionary encoding helps less.
    - Columnar formats often benefit because repeated values are common in a column.
            """
    ).callout(kind="info")
    mo.vstack([_table, _note], gap=0.6)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 4 Conclusion

    - Lossless (gzip, Parquet codecs) gives back every byte; lossy (PCA, rounding) gives back an
      approximation: fine for a picture, never for prices, ids or dates.
    - Compression feeds on repetition: five distinct values per column handed Parquet the win,
      distinct measurements handed it to gzipped CSV.
    - Smaller is not automatically faster: on a file already in memory, unpacking costs CPU on
      every query and saves no I/O. The gzip level is a cost paid when writing.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Smaller files help, but analytics runtime is not only about file size.
    We also need a query engine that avoids unnecessary work.

    $$
    \\text{query time} \\approx \\text{I/O time} + \\text{compute time}
    $$

    DuckDB cuts both: it reads only the columns and row groups a query needs, then runs the maths
    on whole columns at once.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 5. DuckDB Example (SQL on Files)"),
            chapter_intro(
                "data",
                "How can DuckDB answer a query while reading much less data?",
                "Last stop in the data tier: chapters 1-4 built the files, now something reads them back.",
            ),
            mo.md(
                """
    **DuckDB**: an embedded analytical database, fast because it reads less.

    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">import</div><div class="tile-title">Embedded</div>
        <p>Runs inside your Python process. No server.</p></div>
      <div class="tile"><div class="tile-key">GROUP BY</div><div class="tile-title">Analytical</div>
        <p>Scans, filters, joins and aggregates over many rows, column by column.</p></div>
      <div class="tile"><div class="tile-key">WHERE</div><div class="tile-title">Predicate pushdown</div>
        <p>Filters inside the scan; skips blocks whose min/max rule out a match.</p>
        <p><em>Chapter 3's index card.</em></p></div>
      <div class="tile"><div class="tile-key">SELECT</div><div class="tile-title">Projection pushdown</div>
        <p>Only the columns the query names are read.</p>
        <p><em>Chapter 3's ledger.</em></p></div>
    </div>
                """
            ),
            mo.Html(
                '<div class="disclaimer-red">Databases get their own module later: '
                "<strong>Database Management for Data Scientists (DBM)</strong>. Here: intuition only.</div>"
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    push_rows = mo.ui.slider(10_000, 5_000_000, step=10_000, value=400_000, label="Rows (N)", show_value=True, debounce=True)
    push_selectivity = mo.ui.slider(0.001, 1.0, step=0.001, value=0.08, label="Filter selectivity (fraction of rows kept)", show_value=True, debounce=True)
    push_cols_total = mo.ui.slider(4, 80, value=24, label="Total columns", show_value=True, debounce=True)
    push_cols_needed = mo.ui.slider(1, 24, value=5, label="Columns used by query", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md(
                "### Mini-lab: Pushdown Intuition (What Work Gets Skipped?)\n\n"
                "A toy model: $\\text{cells read} \\approx N \\times \\text{selectivity} \\times C_{\\text{needed}}$"
            ),
            mo.hstack([push_rows, push_selectivity], widths="equal"),
            mo.hstack([push_cols_total, push_cols_needed], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return push_cols_needed, push_cols_total, push_rows, push_selectivity


@app.cell
def _(diagram, mo, push_cols_needed, push_cols_total, push_rows, push_selectivity):
    _n, _kept, _total = push_rows.value, push_selectivity.value, push_cols_total.value
    _needed = min(push_cols_needed.value, _total)  # a query cannot use more columns than the table has
    _without, _with = _n * _total, _n * _kept * _needed
    _tall = 220  # px for all N rows

    def _grid(x, title, sub, read_height):
        """The table as one strip per column, N rows tall: cells read in the tier hue, cells skipped grey."""
        step = 440 / _total
        width = step - (2 if step > 8 else 1)
        parts = [f'<text x="{x + 220}" y="22" text-anchor="middle" font-weight="700">{title}</text>']
        for column in range(_total):
            cx = x + column * step
            parts.append(
                f'<rect x="{cx:.1f}" y="40" width="{width:.1f}" height="{_tall}"'
                ' style="fill: color-mix(in srgb, var(--ink) 9%, transparent)"/>'
            )
            if height := read_height(column):
                parts.append(f'<rect x="{cx:.1f}" y="40" width="{width:.1f}" height="{height:.1f}" style="fill: var(--tier)"/>')
        parts.append(f'<text class="dg-muted" x="{x + 220}" y="{_tall + 68}" text-anchor="middle">{sub}</text>')
        return "".join(parts)

    _picture = diagram(
        _grid(0, "without pushdown", f"{_n:,} rows × {_total} columns", lambda _c: _tall)
        + '<text class="dg-muted" x="490" y="138" text-anchor="middle">pushdown</text>'
        + '<path class="dg-edge" d="M452 150 H 526"/>'
        # at least a sliver, so a selectivity of 0.001 still shows where the work is
        + _grid(
            540,
            "with pushdown",
            f"{_kept:.1%} of the rows × {_needed} of {_total} columns",
            lambda _c: max(_tall * _kept, 1.5) if _c < _needed else 0,
        ),
        width=980,
        height=300,
        label=f"The table as {_total} column strips. Without pushdown every cell is read; with pushdown only "
        f"the {_needed} needed columns of the {_kept:.1%} of rows the filter keeps.",
        tier="data",
    )
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(f"{_without:,}", label="cells read without pushdown", bordered=True),
                    mo.stat(f"{round(_with):,}", label="cells read with pushdown", bordered=True),
                    mo.stat(f"{_without / _with:,.1f}x", label="less work", bordered=True),
                ],
                widths="equal",
            ),
            _picture,
            mo.Html(
                '<p class="vis-caption"><strong>Blue: cells read. Grey: work skipped.</strong> The kept rows are drawn '
                "at the top; in a real file they are scattered.</p>"
            ),
            mo.accordion(
                {
                    "Where the toy model is too kind": mo.md(
                        """
    It counts only the needed columns of the kept rows. The filter column itself is still read
    for every row, unless whole blocks can be skipped by their min/max, and that needs the data
    sorted or clustered on that column (chapter 3). It shows what *can* be skipped, not a
    runtime: the next mini-lab times a real query.
                        """
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    duck_rows = mo.ui.slider(2_000, 50_000, step=2_000, value=12_000, label="Rows", show_value=True)
    duck_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Amount threshold", show_value=True)
    run_duck = mo.ui.run_button(label="Run DuckDB demo", kind="success")
    mo.vstack(
        [
            mo.md(
                "### Mini-lab: One Query, Three Sources\n\n"
                "One `GROUP BY` (orders and average amount per region above the threshold) on three sources. "
                "DuckDB reads a file by its name: `FROM 'orders.csv'`."
            ),
            mo.hstack([duck_rows, duck_threshold], widths="equal"),
            run_duck,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return duck_rows, duck_threshold, run_duck


@app.cell
def _(
    Path,
    TIER,
    alt,
    best_seconds,
    chart_or_table,
    duck_rows,
    duck_threshold,
    duckdb,
    format_bytes,
    format_ms,
    mo,
    np,
    pd,
    run_duck,
    static_table,
    tempfile,
    tier_chart,
):
    mo.stop(
        not run_duck.value,
        mo.md(
            "**Predict first:** which source answers fastest, and which file is the smallest? Then click **Run DuckDB demo**."
        ).callout(kind="neutral"),
    )

    _n = duck_rows.value
    _rng = np.random.default_rng(33)
    _orders = pd.DataFrame(
        {
            "order_id": np.arange(_n),
            "region": _rng.choice(["EU", "US", "APAC"], _n),
            "segment": _rng.choice(["consumer", "enterprise", "startup"], _n),
            "amount": _rng.uniform(0, 1000, _n).round(2),
            "day": _rng.integers(1, 31, _n),
        }
    )
    _sql = (
        "SELECT region, count(*) AS orders, round(avg(amount), 2) AS avg_amount "
        "FROM {} WHERE amount > ? GROUP BY region ORDER BY region"
    )
    with tempfile.TemporaryDirectory() as _td:
        _csv, _parquet, _db = (Path(_td) / _name for _name in ("orders.csv", "orders.parquet", "analytics.duckdb"))
        _orders.to_csv(_csv, index=False)
        _orders.to_parquet(_parquet, index=False)
        with duckdb.connect(_db) as _con:

            def _best(sql, params):  # best of 3, so a cold first run does not decide the ranking
                return best_seconds(lambda: _con.execute(sql, params).fetchall())

            _load_csv = _best("CREATE OR REPLACE TABLE orders AS FROM read_csv(?)", [str(_csv)])
            _load_parquet = _best("CREATE OR REPLACE TABLE orders AS FROM read_parquet(?)", [str(_parquet)])
            _query_csv = _best(_sql.format("read_csv(?)"), [str(_csv), duck_threshold.value])
            _query_parquet = _best(_sql.format("read_parquet(?)"), [str(_parquet), duck_threshold.value])
            _query_table = _best(_sql.format("orders"), [duck_threshold.value])
            _result = _con.execute(_sql.format("orders"), [duck_threshold.value]).df()
            _block = _con.execute("SELECT block_size FROM pragma_database_size()").fetchone()[0]
        _csv_size, _parquet_size, _db_size = (_p.stat().st_size for _p in (_csv, _parquet, _db))

    _sources = [
        # name, file, size, per query, load into a table once
        ("CSV file", "orders.csv", _csv_size, _query_csv, _load_csv),
        ("Parquet file", "orders.parquet", _parquet_size, _query_parquet, _load_parquet),
        ("DuckDB table", "analytics.duckdb", _db_size, _query_table, None),
    ]
    _rows = [
        {
            "source": f"{_name} ({_file})",
            "size": format_bytes(_size),
            "per query": format_ms(_query),
            "load into a table, once": format_ms(_load) if _load else "-",
        }
        for _name, _file, _size, _query, _load in _sources
    ]
    _names = [_source[0] for _source in _sources]
    _order = ["per query", "load into a table, once"]
    _costs = pd.DataFrame(
        [
            {"source": _name, "cost": _cost, "ms": _seconds * 1000}
            for _name, _file, _size, *_times in _sources
            for _cost, _seconds in zip(_order, _times, strict=True)
            if _seconds is not None
        ]
    )
    _costs["label"] = [f"{_ms:,.1f} ms" for _ms in _costs["ms"]]
    _timed = alt.Chart(_costs).encode(
        y=alt.Y("source:N", sort=_names, title=None),
        yOffset=alt.YOffset("cost:N", sort=_order),
        x=alt.X("ms:Q", title="milliseconds", scale=alt.Scale(domain=[0, _costs["ms"].max() * 1.3])),
    )
    _time = (
        _timed.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("cost:N", title=None, sort=_order, scale=alt.Scale(domain=_order, range=[TIER["data"], TIER["muted"]]))
        )
        + _timed.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width=500, height=250, title="Time (best of 3 runs)")
    _sized = alt.Chart(
        pd.DataFrame({"source": _names, "bytes": [_s[2] for _s in _sources], "label": [format_bytes(_s[2]) for _s in _sources]})
    ).encode(
        y=alt.Y("source:N", sort=_names, title=None, axis=None),
        x=alt.X("bytes:Q", axis=None, scale=alt.Scale(domain=[0, max(_s[2] for _s in _sources) * 1.6])),
    )
    _size = (
        _sized.mark_bar(cornerRadiusEnd=4, color=TIER["muted"]) + _sized.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width=240, height=250, title="File size")

    _size_note = (
        "Push Rows up and the CSV overtakes it." if _db_size > _csv_size else "At this size the CSV is already the bigger file."
    )
    mo.vstack(
        [
            chart_or_table(tier_chart(alt.hconcat(_time, _size, spacing=40), "data"), _rows, label="One query, three sources (best of 3 runs)"),
            mo.md(
                f"**Here the gap is mostly parsing:** CSV is text, re-converted on every query; Parquet and the "
                f"table are typed columns. Loading the CSV once cost {_load_csv / _query_csv:.1f} CSV queries' worth."
            ).callout(kind="info"),
            mo.accordion(
                {
                    "Why pushdown skips little here, and why the DuckDB file can be the biggest": mo.md(
                        f"""
    Predicate pushdown has next to nothing to skip: the amounts are random, so every block spans
    roughly 0 to 1000 and none can be ruled out by its min/max.

    DuckDB grows `analytics.duckdb` in {_block // 1024} KiB blocks, so a small table still fills
    whole blocks. {_size_note}
                        """
                    ),
                    "The query and its answer": mo.vstack(
                        [
                            mo.md(f"```sql\n{_sql.format('orders')}\n```"),
                            static_table(_result.to_dict("records"), label=f"Query result (amount > {duck_threshold.value})"),
                        ]
                    ),
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    idx_rows = mo.ui.slider(20_000, 200_000, step=20_000, value=80_000, label="Rows", show_value=True)
    idx_selectivity = mo.ui.slider(0.05, 0.9, step=0.05, value=0.2, label="Share of category = 'C'", show_value=True)
    idx_threshold = mo.ui.slider(0, 1000, step=50, value=600, label="Value threshold", show_value=True)
    idx_seed = mo.ui.slider(1, 999, value=17, label="Seed", show_value=True)
    run_index = mo.ui.run_button(label="Run indexing demo", kind="success")
    mo.vstack(
        [
            mo.md(
                """
    ### Indexing Demo: Full Scan vs Indexed Search

    An **index** avoids the scan: a sorted copy of some columns, to jump to the matching rows.
    DuckDB keeps min/max zone maps instead, so this lab uses SQLite.
                """
            ),
            mo.hstack([idx_rows, idx_selectivity], widths="equal"),
            mo.hstack([idx_threshold, idx_seed], widths="equal"),
            run_index,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return idx_rows, idx_seed, idx_selectivity, idx_threshold, run_index


@app.cell
def _(
    TIER,
    alt,
    best_seconds,
    chart_or_table,
    idx_rows,
    idx_seed,
    idx_selectivity,
    idx_threshold,
    mo,
    pd,
    random,
    run_index,
    sqlite3,
    tier_chart,
):
    mo.stop(
        not run_index.value,
        mo.md(
            "**Predict first:** no index, `(category)` or `(category, value)`: which is fastest? "
            "Then click **Run indexing demo**."
        ).callout(kind="neutral"),
    )

    _rng = random.Random(idx_seed.value)
    _con = sqlite3.connect(":memory:")  # in memory, so the timings measure SQLite and not the disk
    _con.execute("CREATE TABLE events (id INTEGER, category TEXT, value REAL)")
    _con.executemany(
        "INSERT INTO events VALUES (?, ?, ?)",
        (
            (_i, "C" if _rng.random() < idx_selectivity.value else _rng.choice("ABD"), round(_rng.random() * 1000, 2))
            for _i in range(idx_rows.value)
        ),
    )
    _query = "SELECT count(*), round(avg(value), 2) FROM events WHERE category = 'C' AND value > ?"
    _params = [idx_threshold.value]
    _states, _answers = {}, set()
    for _state, _ddl in (
        ("no index", None),
        ("index on (category)", "CREATE INDEX idx_cat ON events(category)"),
        ("index on (category, value)", "CREATE INDEX idx_cat_val ON events(category, value)"),
    ):
        _build = best_seconds(_con.execute, _ddl, repeat=1) if _ddl else 0.0
        _plan = _con.execute(f"EXPLAIN QUERY PLAN {_query}", _params).fetchone()[-1]
        _states[_state] = (_build, best_seconds(lambda: _con.execute(_query, _params).fetchall(), repeat=5), _plan)
        _answers.add(_con.execute(_query, _params).fetchone())
    _con.close()
    ((_count, _avg),) = _answers  # one answer, whichever plan SQLite picked

    _scan = _states["no index"][1]
    _narrow = _scan / _states["index on (category)"][1]
    _rows = [
        {
            "state": _state,
            "build (ms)": round(_build * 1000, 1),
            "query (ms)": round(_query_s * 1000, 3),
            "speed-up vs scan": f"{_scan / _query_s:.1f}x",
            "SQLite plan": _plan,
        }
        for _state, (_build, _query_s, _plan) in _states.items()
    ]
    _df = pd.DataFrame(_rows)
    _df["speed-up"] = _scan / (_df["query (ms)"] / 1000)
    _df["label"] = [
        f"{_ms:.2f} ms (the scan)" if _state == "no index" else f"{_ms:.2f} ms · {_up:.1f}x"
        for _state, _ms, _up in zip(_df["state"], _df["query (ms)"], _df["speed-up"], strict=True)
    ]
    _df["kind"] = ["scan" if _state == "no index" else ("slower" if _up < 1 else "faster") for _state, _up in zip(_df["state"], _df["speed-up"], strict=True)]
    _y = alt.Y("state:N", sort=None, title=None)
    _timed = alt.Chart(_df).encode(y=_y, x=alt.X("query (ms):Q", title=None, scale=alt.Scale(domain=[0, _df["query (ms)"].max() * 1.45])))
    _query_chart = (
        _timed.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color(
                "kind:N", legend=None, scale=alt.Scale(domain=["scan", "faster", "slower"], range=[TIER["muted"], TIER["data"], TIER["hot"]])
            )
        )
        + _timed.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width=480, height=180, title="Query time (ms), best of 5")
    _built = alt.Chart(_df).encode(
        y=alt.Y("state:N", sort=None, title=None, axis=None),
        x=alt.X("build (ms):Q", title=None, scale=alt.Scale(domain=[0, max(_df["build (ms)"].max(), 1) * 1.5])),
    )
    _build_chart = (
        _built.mark_bar(cornerRadiusEnd=4, color=TIER["muted"])
        + _built.mark_text(align="left", dx=6).encode(text=alt.Text("build (ms):Q", format=".1f"))
    ).properties(width=200, height=180, title="Build, once (ms)")

    if round(_narrow, 1) < 1:
        _planner = f"Here <code>(category)</code> ran at {_narrow:.1f}x, slower than the scan, and still USING INDEX."
    elif round(idx_selectivity.value, 2) < 0.7:
        _planner = "Set the share of C to 0.7 or more and run again: <code>(category)</code> drops below 1.0x."
    else:
        _planner = f"Here <code>(category)</code> just held on ({_narrow:.1f}x); timings wobble, so run again."
    _wide_build = _states["index on (category, value)"][0] * 1000
    _tiles = mo.md(
        f"""
    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">+1</div><div class="tile-title">It is not free</div>
        <p>Built here in {_wide_build:.0f} ms, then paid again on <strong>every insert, update and delete</strong>.
        Six indexes: every write does seven pieces of work.</p></div>
      <div class="tile"><div class="tile-key">COVERING</div><div class="tile-title">Width matters</div>
        <p><code>(category)</code> finds the C rows, then fetches each <code>value</code> from the table.
        <code>(category, value)</code> holds both: its plan says COVERING INDEX, the table is never touched.</p></div>
      <div class="tile"><div class="tile-key">?</div><div class="tile-title">The planner guesses</div>
        <p>SQLite assumes few rows match and takes the index even when a scan is faster.</p>
        <p>{_planner}</p></div>
    </div>
        """
    )
    mo.vstack(
        [
            chart_or_table(
                tier_chart(alt.hconcat(_query_chart, _build_chart, spacing=40), "data"),
                _rows,
                label=f"What the index costs, and what it buys (all three return {_count:,} rows, average {_avg})",
            ),
            _tiles,
            mo.md(
                "**The honest rule:** an index pays when it holds what the query asks for, and the query asks for **few** rows."
            ).callout(kind="info"),
            mo.accordion(
                {
                    "The plan SQLite chose for each state": mo.md(
                        "\n".join(f"- **{_state}:** `{_plan}`" for _state, (_b, _q, _plan) in _states.items())
                        + "\n\nSQLite cannot know how many rows are C: even `ANALYZE` stores only averages."
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    def ch5_card(x, y, title, sub, cls="dg-box", w=235, h=72):
        """SVG for a two-line box at (x, y): a bold title over a muted line."""
        return (
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 29}" text-anchor="middle" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="{x + w / 2:.0f}" y="{y + 53}" text-anchor="middle">{sub}</text>'
        )

    mo.md(
        """
    ### Schema-on-Read vs Schema-on-Write

    A CSV file has no types. **Schema-on-read** guesses them while reading; **schema-on-write**
    declares the blank form first and loads into it. What differs is **when the check happens,
    and who gets told**. The file: 400 real sales, 5% of `total_price` broken like real exports
    (`n/a`, empty, `1 234,50`, `EUR 900`).
        """
    ).callout(kind="neutral")
    return (ch5_card,)


@app.cell
def _(Path, SALES_SEED, ch5_card, diagram, duckdb, html, mo, pd, random, re, static_table, tempfile):
    _src = pd.read_parquet(SALES_SEED).head(400)
    _export = _src[["sale_id", "sale_date", "product_id", "units_sold", "total_price"]].astype({"total_price": str})
    _bad_rows = random.Random(5).sample(range(len(_export)), 20)
    _export.loc[_bad_rows, "total_price"] = ["", "1 234,50", "EUR 900", "n/a"] * 5

    with tempfile.TemporaryDirectory() as _td:
        _csv = str(Path(_td) / "sales_export.csv")
        _export.to_csv(_csv, index=False)
        _con = duckdb.connect()

        # Lane 1: let DuckDB guess the types, then do what a student would do next.
        _inferred = dict(_row[:2] for _row in _con.execute("DESCRIBE FROM read_csv(?)", [_csv]).fetchall())["total_price"]
        _rows, _parsed, _revenue = _con.execute(
            "SELECT count(*), count(TRY_CAST(total_price AS DOUBLE)), "
            "round(sum(TRY_CAST(total_price AS DOUBLE)), 2) FROM read_csv(?)",
            [_csv],
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
            _con.execute("INSERT INTO sales_clean FROM read_csv(?)", [_csv])
            _told, _refused = "loaded without complaint", ("loaded", "no complaint")
        except duckdb.Error as _exc:
            _lines = str(_exc).splitlines()
            _told = f"{type(_exc).__name__}: {_lines[0]}. {_lines[2]}"
            _line = re.search(r"Line: (\d+)", _told)
            _value = re.search(r'string "([^"]*)"', _told)
            _refused = (
                "INSERT refused",
                f'line {_line[1]}: "{_value[1]}"' if _line and _value else type(_exc).__name__,
            )
        _loaded = _con.execute("SELECT count(*) FROM sales_clean").fetchone()[0]

    _true = _src["total_price"].sum()
    _low = 1 - _revenue / _true
    _lanes = diagram(
        '<rect class="dg-box" x="0" y="72" width="190" height="156" rx="12"/>'
        '<text x="95" y="122" text-anchor="middle" font-weight="700">sales_export.csv</text>'
        f'<text class="dg-muted" x="95" y="152" text-anchor="middle">{_rows:,} rows</text>'
        f'<text class="dg-hot" x="95" y="180" text-anchor="middle">{len(_bad_rows)} bad prices</text>'
        '<path class="dg-edge" d="M190 120 C 215 120, 215 76, 234 76"/>'
        '<path class="dg-edge" d="M190 180 C 215 180, 215 226, 234 226"/>'
        '<text x="240" y="24" font-weight="700">schema-on-read: <tspan class="dg-muted" font-weight="400">guess the type, find out later (or never)</tspan></text>'
        + ch5_card(240, 40, "DuckDB guesses", f"total_price: {html.escape(_inferred)}")
        + ch5_card(505, 40, "TRY_CAST to DOUBLE", f"{_parsed:,} of {_rows:,} rows survive")
        + ch5_card(770, 40, f"revenue {_revenue:,.0f}", f"{_low:.1%} too low · no warning", cls="dg-box dg-hot")
        + '<text x="240" y="174" font-weight="700">schema-on-write: <tspan class="dg-muted" font-weight="400">declare the form, reject at the door</tspan></text>'
        + ch5_card(240, 190, "declared first", "DOUBLE NOT NULL CHECK (&gt; 0)")
        + ch5_card(505, 190, _refused[0], html.escape(_refused[1]), cls="dg-box dg-ok")
        + ch5_card(770, 190, f"{_loaded:,} rows loaded", "a problem you know about", cls="dg-box dg-ok")
        + '<path class="dg-edge" d="M475 76 H 499"/><path class="dg-edge" d="M740 76 H 764"/>'
        + '<path class="dg-edge" d="M475 226 H 499"/><path class="dg-edge" d="M740 226 H 764"/>',
        width=1010,
        height=270,
        label=f"One messy CSV, two lanes. Schema-on-read guesses {_inferred}, keeps {_parsed} of {_rows} rows and reports "
        f"a revenue {_low:.1%} too low without a warning. Schema-on-write refuses the load and names the bad line.",
        tier="data",
    )
    _read, _write = "schema-on-read (guess the types)", "schema-on-write (declare, then load)"
    _table = static_table(
        {
            "": ["type of total_price", "rows in the file", "rows that reached the answer", "what you are told", "revenue reported"],
            _read: [_inferred, f"{_rows:,}", f"{_parsed:,}", "nothing at all", f"{_revenue:,.2f} (true total: {_true:,.2f})"],
            _write: ["DOUBLE NOT NULL CHECK (> 0)", f"{_rows:,}", f"{_loaded:,}", _told, "none, the load stopped"],
        },
        label="One messy export, two lanes",
        wrapped_columns=[_read, _write],
        column_widths={_read: 400, _write: 440},
    )
    mo.vstack(
        [
            mo.ui.tabs({"Diagram": _lanes, "Table": _table}),
            mo.md(
                f"**Same file, same {len(_bad_rows)} bad values.** Read gave a wrong number that looks ordinary. "
                "Write gave no number: a problem you know about, not an answer you trust by mistake."
            ).callout(kind="warn"),
            mo.accordion(
                {
                    "Where the rows went, and which lane to use when": mo.md(
                        f"""
    `TRY_CAST` turns anything it cannot convert into `NULL`, and `SUM` skips nulls: {_rows - _parsed}
    of {_rows} rows silently left the total. Nothing raised, nothing warned.

    Neither lane is correct in the abstract. Schema-on-read is right for exploring a file you have
    just been handed; schema-on-write is right for anything a decision rests on.
                        """
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Mini-lab: Add One Column, Then Read Last Year's Files

    Chapter 2's changed form, one level up: one file per year. `sales_2024.parquet` predates
    `customer_rating`; the 2025 and 2026 files have it.
        """
    ).callout(kind="neutral")
    return


@app.cell
def _(Path, SALES_SEED, ch5_card, diagram, duckdb, html, mo, pd, static_table, tempfile):
    _all = pd.read_parquet(SALES_SEED)
    with tempfile.TemporaryDirectory() as _td:
        _dir = Path(_td).as_posix()
        _files = {}
        for _year, _part in _all.groupby(_all["sale_date"].dt.year):
            _files[_year] = f"{_dir}/sales_{_year}.parquet"
            # customer_rating joined the form in 2025, so the 2024 file never had it
            (_part.drop(columns="customer_rating") if _year < 2025 else _part).to_parquet(_files[_year], index=False)
        _sizes = _all.groupby(_all["sale_date"].dt.year).size()
        _con = duckdb.connect()

        def _read(sql, params):
            """What one reading of the folder gives back: (dg class, outcome, the same in words for the table)."""
            try:
                _df = _con.execute(sql, params).df()
            except duckdb.Error as _exc:
                _text = f"{type(_exc).__name__}: {str(_exc).splitlines()[0].replace(_dir + '/', '')}"
                return "dg-box", f"refused: {type(_exc).__name__}", _text
            if "customer_rating" not in _df:
                _text = f"{len(_df):,} rows, {_df.shape[1]} columns, no customer_rating, no error"
                return "dg-box dg-hot", f"{len(_df):,} rows, customer_rating gone", _text
            _rated = _df["customer_rating"]
            _text = f"{len(_df):,} rows, rating on {_rated.count():,}, average {_rated.mean():.3f}"
            return "dg-box dg-ok", f"{len(_df):,} rows, {_rated.count():,} rated, average {_rated.mean():.2f}", _text

        _glob = f"{_dir}/sales_*.parquet"
        _readings = [
            (
                "read_parquet('sales_*.parquet')",
                "the glob reads A to Z: 2024 first",
                _read("FROM read_parquet(?)", [_glob]),
                "the oldest file sets the shape: the new column is dropped",
            ),
            (
                "the same files, newest first",
                "2026 first: it has the column",
                _read("FROM read_parquet(?)", [list(_files.values())[::-1]]),
                "the first file has the column and a later one does not",
            ),
            (
                "read_parquet(..., union_by_name = true)",
                "match columns by name",
                _read("FROM read_parquet(?, union_by_name = true)", [_glob]),
                "missing columns are filled with NULL",
            ),
        ]

    _files_row = "".join(
        ch5_card(
            _i * 345,
            0,
            f"sales_{_year}.parquet",
            f"{_sizes[_year]:,} rows · " + ("no customer_rating" if _year < 2025 else "+ customer_rating"),
            cls="dg-box" if _year < 2025 else "dg-tier",
            w=320,
        )
        for _i, _year in enumerate(_files)
    )
    _reading_rows = "".join(
        f'<text x="0" y="{_y + 30}" style="font-family: var(--monospace-font, monospace); font-size: 15px">{html.escape(_how)}</text>'
        f'<text class="dg-muted" x="0" y="{_y + 54}">{_hint}</text>'
        f'<path class="dg-edge" d="M440 {_y + 36} H 494"/>'
        + ch5_card(500, _y, html.escape(_outcome), _why, cls=_cls, w=510)
        for _y, (_how, _hint, (_cls, _outcome, _text), _why) in zip((120, 210, 300), _readings, strict=True)
    )
    _picture = diagram(
        _files_row + _reading_rows,
        width=1010,
        height=380,
        label="Three yearly files, only the newer two with customer_rating, read three ways: the glob silently drops "
        "the column, newest first is refused, union_by_name keeps every row and fills the gap with NULL.",
        tier="data",
    )
    _table = static_table(
        [
            {"how you read the folder": _how, "what happens": _text, "why": _why}
            for _how, _hint, (_cls, _outcome, _text), _why in _readings
        ],
        label="One folder, two file shapes, three readings",
        wrapped_columns=["how you read the folder", "what happens", "why"],
        column_widths={"how you read the folder": 250, "what happens": 480, "why": 330},
    )
    mo.vstack(
        [
            mo.ui.tabs({"Diagram": _picture, "Table": _table}),
            mo.md(
                "**Only the third reading is right.** The first is the dangerous one: nothing failed, and "
                "`customer_rating` quietly vanished. When a folder's files grew columns, say so when you read it."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — DuckDB & Schema</h3>
      <details>
        <summary><strong>Q1:</strong> When is loading data into DuckDB better than scanning files each time?</summary>
        <p><strong>Answer:</strong> When the same queries or joins run repeatedly: the file is parsed once at load instead of on every query, as the three-sources lab showed (materialisation = storing structured intermediate data for reuse).</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> What risk appears with schema-on-read?</summary>
        <p><strong>Answer:</strong> Bad values slip through silently: they turn into <code>NULL</code>s and totals come out wrong without any error.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> How can data drift be detected over time?</summary>
        <p><strong>Answer:</strong> Track inferred types, null rates, and value distributions; alert when they change (data drift = statistical change in incoming data over time).</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 5 Conclusion

    - DuckDB runs SQL on files; typed columns (Parquet, a table) beat CSV, re-parsed every query.
    - Pushdown reads only the rows and columns a query needs.
    - An index pays when it covers the query and few rows match; every write pays for it.
    - Schema-on-read fails silently later; schema-on-write rejects at the door.
    - A folder whose files grew columns: `union_by_name = true`, or the first file sets the shape.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    So far everything ran locally. Next, other programs ask for the data over an API: a
    **request** goes out, a **response** comes back.

    $$
    \\text{API latency} = \\text{network} + \\text{server processing}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 6. REST API Demo (GET, POST, PUT, DELETE)"),
            chapter_intro(
                "logic",
                "Did the client and server agree on the same contract?",
                "Up to the logic tier: the data tier is finished, now other programs ask for its data.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, mo):
    _labels = [
        # (x, y, text): the names of the parts, above the request and below the response
        (225, 56, "verb"),
        (330, 56, "path"),
        (600, 56, "payload (JSON)"),
        (280, 148, "endpoint = verb + path"),
        (255, 240, "status code"),
        (575, 240, "the resource, as JSON"),
    ]
    _message = diagram(
        '<rect class="dg-box" x="0" y="40" width="150" height="190" rx="12"/>'
        '<text x="75" y="130" text-anchor="middle" font-weight="700">client</text>'
        '<text class="dg-muted" x="75" y="156" text-anchor="middle">script or app</text>'
        '<rect class="dg-tier" x="850" y="40" width="150" height="190" rx="12"/>'
        '<text x="925" y="130" text-anchor="middle" font-weight="700">API</text>'
        '<text class="dg-muted" x="925" y="156" text-anchor="middle">sw03_demo_api</text>'
        '<path class="dg-edge" d="M150 90 H 844"/><path class="dg-edge" d="M850 190 H 156"/>'
        # an opaque strip under each message, so the arrow does not show through its see-through boxes
        '<rect x="176" y="64" width="638" height="52" style="fill: var(--surface)"/>'
        '<rect x="176" y="164" width="638" height="52" style="fill: var(--surface)"/>'
        + box(180, 68, "POST", w=90, cls="dg-tier")
        + box(280, 68, "/sales", w=100, cls="dg-tier")
        + box(390, 68, '{"product_id": 1, "units_sold": 2, ...}', w=420)
        + '<path d="M182 118 V 126 H 378 V 118" fill="none" stroke="currentColor" opacity="0.45"/>'
        + box(180, 168, "201 Created", w=150, cls="dg-box dg-ok")
        + box(340, 168, '{"sale_id": 3361, "total_price": 390.0, ...}', w=470)
        + "".join(f'<text class="dg-muted" x="{_x}" y="{_y}" text-anchor="middle">{_t}</text>' for _x, _y, _t in _labels),
        width=1000,
        height=250,
        label="A request travels from client to API: the verb POST, the path /sales and a JSON payload. "
        "The response travels back: the status code 201 Created and the new sale as JSON.",
        tier="logic",
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>One Request, One Response</h3>
      {_message}
      <p class="vis-caption">An API is a <strong>contract</strong>. Most API bugs break it: a wrong
      path, a wrong payload shape, or a status code the client did not handle.</p>
    </div>
                """
            ),
            mo.accordion(
                {
                    "Resource, path, endpoint, payload: the four words": mo.md(
                        """
    - A **resource** is one thing the server knows about, like a product or a sale.
    - A **path** is the address of a resource, like `/products/8`.
    - An **endpoint** is one path combined with one verb, like `GET /products/8`.
    - A **payload** is the data sent along with a request, written as JSON. In a JSON API the
      payload is the resource's *representation*: the same thing, written down to travel.
    - **HTTP** is the message protocol of the web; **HTTPS** is HTTP with encryption (TLS), the
      secure default. Same API idea either way.
                        """
                    )
                }
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md(
                """
    ### REST Principles

    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">GET</div><div class="tile-title">fetch</div>
        <p>Idempotent: a lift button.</p></div>
      <div class="tile"><div class="tile-key">POST</div><div class="tile-title">create</div>
        <p class="tile-bad">Not idempotent: a ticket dispenser.</p></div>
      <div class="tile"><div class="tile-key">PUT</div><div class="tile-title">replace</div>
        <p>Idempotent. Ours also takes only the changed fields (the standard's PATCH).</p></div>
      <div class="tile"><div class="tile-key">DELETE</div><div class="tile-title">remove</div>
        <p>Idempotent.</p></div>
    </div>

    **Idempotent**: pressing twice changes nothing more than pressing once. Jab a lift button ten
    times, one lift comes; press a ticket dispenser ten times, you hold ten tickets. So a POST that
    timed out is frightening to retry: you cannot tell whether the server acted.

    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">&#8709;</div><div class="tile-title">Stateless</div>
        <p>The server forgets the conversation, never the data.</p></div>
      <div class="tile"><div class="tile-key">=</div><div class="tile-title">Uniform interface</div>
        <p>The same four verbs on every resource.</p></div>
      <div class="tile"><div class="tile-key">&#8635;</div><div class="tile-title">Cacheable</div>
        <p>An answer may say "valid for a while" and be reused.</p></div>
      <div class="tile"><div class="tile-key">&#8801;</div><div class="tile-title">Layered</div>
        <p>The client talks to the next layer only: the tier map, on the network.</p></div>
    </div>
                """
            ),
            mo.accordion(
                {
                    "Idempotent does not mean nothing happens": mo.md(
                        """
    The second press really is sent and really is processed. Idempotent means the **end state**
    is the same, not that the work is skipped, and not even that the answer is the same: DELETE a
    sale twice and you get **204**, then **404**. Still idempotent, because after one press or ten
    the sale is gone. Our partial PUT is idempotent too: setting the rating to 5 twice leaves it at 5.
                        """
                    ),
                    "Why these four constraints let REST scale": mo.md(
                        """
    - **Stateless**: the server keeps no memory of *you* between requests: not where you are in a
      conversation, what you asked last, or which page you were on. Every request carries
      everything needed to answer it. It does remember your **data**, which is what the whole data
      tier was for. Session state no, resource state yes: that is what lets a second copy of the
      server answer your next request without anyone noticing.
    - **Uniform interface**: once you can read one endpoint, you can read them all.
    - **Cacheable**: a reused answer is one the server did not have to recompute.
    - **Layered**: the tier idea from the start of this notebook, applied to the network.
                        """
                    ),
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, mo):
    def _stage(x, title, sub, cls):
        return (
            f'<rect class="{cls}" x="{x}" y="10" width="210" height="80" rx="12"/>'
            f'<text x="{x + 105}" y="44" text-anchor="middle" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="{x + 105}" y="70" text-anchor="middle">{sub}</text>'
        )

    def _exit(x, code, meaning, example):
        return (
            f'<rect class="dg-box dg-hot" x="{x}" y="190" width="220" height="100" rx="12"/>'
            f'<text x="{x + 110}" y="220" text-anchor="middle" font-weight="700">{code}</text>'
            f'<text class="dg-muted" x="{x + 110}" y="245" text-anchor="middle">{meaning}</text>'
            f'<text class="dg-muted" x="{x + 110}" y="270" text-anchor="middle">{example}</text>'
        )

    _gates = diagram(
        _stage(0, "request", "you send", "dg-box")
        + _stage(260, "the door", "the model's rules", "dg-tier")
        + _stage(520, "endpoint code", "checks the data", "dg-tier")
        + _stage(780, "201 Created", "a valid sale", "dg-box dg-ok")
        + '<path class="dg-edge" d="M210 50 H 254"/><path class="dg-edge" d="M470 50 H 514"/>'
        + '<path class="dg-edge" d="M730 50 H 774"/>'
        + _exit(255, "422 Unprocessable", "broke a written rule", "rating 9 · total_price")
        + _exit(505, "404 Not Found", "nothing lives there", "GET /sales/999999")
        + _exit(755, "400 Bad Request", "asks the impossible", "region_id 999")
        + '<path class="dg-edge dg-hot" d="M365 90 V 184"/>'
        + '<path class="dg-edge dg-hot" d="M615 90 V 184"/>'
        + '<path class="dg-edge dg-hot" d="M700 90 C 700 140, 865 130, 865 184"/>',
        width=1000,
        height=300,
        label="Where each status code comes from. A request first meets the door, the model's rules: breaking one "
        "answers 422 and the endpoint never runs. Past the door the endpoint code checks the data: no such sale "
        "answers 404, a region that does not exist answers 400. A valid sale answers 201 Created.",
        tier="logic",
    )
    mo.md(
        f"""
    ### Four Real Answers From Our Own API

    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">2xx</div><div class="tile-title">Done</div>
        <p>It worked; 201: a new thing now exists.</p></div>
      <div class="tile"><div class="tile-key">4xx</div><div class="tile-title">Fix your request</div>
        <p>Resending the same request gets the same answer.</p></div>
      <div class="tile"><div class="tile-key">5xx</div><div class="tile-title">The server broke</div>
        <p>A retry may work (blindly only for the lift-button verbs).</p></div>
    </div>

    <div class="section-card" style="margin-top: 14px">
      {_gates}
      <p class="vis-caption"><strong>400 or 422 is where students trip.</strong> 422: turned away at
      the door (chapter 7), the endpoint's code never ran. 400: passed the door, then broke a rule
      only the data can check. The mini-lab below sends all four.</p>
    </div>
        """
    )
    return


@app.cell
def _(mo):
    # One box for chapters 6 and 8: chapter 8 shows this same element again, and both copies stay in sync.
    api_base_url = mo.ui.text(value="http://127.0.0.1:8000", label="API base URL", full_width=True)
    _sale = {"sale_date": "2026-09-01", "product_id": 1, "country_id": 3, "units_sold": 2, "customer_rating": 4}
    ch6_preset = mo.ui.dropdown(
        options={
            "GET /sales/1": ("GET", "/sales/1", None),
            "POST /sales with a valid sale": ("POST", "/sales", _sale),
            "GET /sales/999999": ("GET", "/sales/999999", None),
            "POST /countries with region_id 999": ("POST", "/countries", {"name": "Atlantis", "region_id": 999}),
            "POST /sales with customer_rating 9": ("POST", "/sales", _sale | {"customer_rating": 9}),
            "POST /sales that sends total_price": ("POST", "/sales", _sale | {"total_price": 1.0}),
            "POST /countries named three spaces": ("POST", "/countries", {"name": "   ", "region_id": 1}),
            "PUT /sales/1 with only a new rating": ("PUT", "/sales/1", {"customer_rating": 5}),
            "DELETE /sales/1": ("DELETE", "/sales/1", None),
        },
        value="GET /sales/1",
        label="Request",
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Ask Our API

    Start the API in a terminal first: `uvicorn sw03_demo_api:app`, without `--reload` today.
    Send the POST, the PUT and the DELETE twice each: which leave the server where the first
    press left it?
                """
            ),
            mo.hstack([ch6_preset, api_base_url], widths="equal", align="end"),
            mo.accordion(
                {
                    "What uvicorn is, and why no --reload": mo.md(
                        """
    **uvicorn** is the program that listens on the port and hands each request to the FastAPI
    code; `sw03_demo_api` is the file and `app` the variable inside it. `--reload` also restarts
    the server whenever marimo saves a notebook in this folder, and every restart resets `data/`:
    the API restores it from `data/seed/` each time it starts, so nothing you change or delete
    here is permanent.
                        """
                    )
                }
            ),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return api_base_url, ch6_preset


@app.cell
def _(ch6_preset, json, mo):
    _method, _path, _body = ch6_preset.value
    ch6_method = mo.ui.dropdown(["GET", "POST", "PUT", "DELETE"], value=_method, label="Method")
    ch6_path = mo.ui.text(value=_path, label="Path")
    ch6_body = mo.ui.text_area(
        value=json.dumps(_body, indent=2) if _body else "", rows=8, label="JSON body (sent with POST and PUT)", full_width=True
    )
    ch6_send = mo.ui.run_button(label="Send request", kind="success")
    mo.vstack([mo.hstack([ch6_method, ch6_path], justify="start", gap=2), ch6_body, ch6_send], gap=0.6).callout(kind="neutral")
    return ch6_body, ch6_method, ch6_path, ch6_send


@app.cell
def _(
    api_base_url,
    call_api,
    ch6_body,
    ch6_method,
    ch6_path,
    ch6_send,
    html,
    json,
    mo,
    requests,
):
    from http.client import responses as _phrases

    mo.stop(
        not ch6_send.value,
        mo.md("**Predict first:** which status code comes back? Then click **Send request**.").callout(kind="neutral"),
    )

    _url = api_base_url.value.rstrip("/") + "/" + ch6_path.value.lstrip("/")
    try:
        _body = json.loads(ch6_body.value) if ch6_method.value in {"POST", "PUT"} else None
    except json.JSONDecodeError as _exc:
        mo.stop(True, mo.md(f"The body is not valid JSON: {_exc}").callout(kind="danger"))
    try:
        _status, _answer = call_api(ch6_method.value, _url, _body)
    except requests.RequestException:
        mo.stop(True, mo.md(f"No answer from `{_url}`. Start the API in a terminal, then send again: `uvicorn sw03_demo_api:app`").callout(kind="danger"))

    # JSON as a code block, not mo.json: its tree view squeezes a name of three spaces to one
    if isinstance(_answer, list):  # GET /sales is thousands of rows: show a taste, not a wall
        _shown = mo.md(f"*{len(_answer):,} items, the first 3 shown*\n\n```json\n{json.dumps(_answer[:3], indent=2)}\n```")
    elif isinstance(_answer, dict):
        _shown = mo.md(f"```json\n{json.dumps(_answer, indent=2)}\n```")
    elif _answer:
        _shown = mo.plain_text(str(_answer))  # not JSON, e.g. a 500 "Internal Server Error"
    else:
        _shown = mo.md("*No body: 204 means done, nothing to send back.*")
    _kind, _colour, _meaning = {
        2: ("success", "var(--teal)", "done"),
        4: ("warn", "var(--amber)", "fix your request: resending it gets the same answer"),
    }.get(_status // 100, ("danger", "var(--red)", "the server broke: a retry may work"))
    _badge = mo.Html(
        '<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px">'
        f'<span style="color: {_colour}; font-size: 3rem; font-weight: 700; line-height: 1">{_status}</span>'
        f'<span style="font-size: 1.4rem; font-weight: 700">{_phrases.get(_status, "(no standard name)")}</span>'
        f'<span style="color: var(--ink-soft); font-size: 1.1rem">{_meaning}</span></div>'
        f"<p><code>{html.escape(ch6_method.value)} {html.escape(_url)}</code></p>"
    )
    mo.vstack([_badge, _shown], gap=0.5).callout(kind=_kind)
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — APIs</h3>
      <details>
        <summary><strong>Q1:</strong> When is a POST safe to retry?</summary>
        <p><strong>Answer:</strong> Only when the server can recognise the repeat: the client sends a unique key
        (an idempotency key, or an id it chose) and the server refuses to create a second record with that key.
        Our API picks <code>sale_id</code> itself, so a retried POST books a second sale (the mini-lab above and chapter 8 show it).</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> How can an API evolve without breaking clients?</summary>
        <p><strong>Answer:</strong> Add optional fields, version endpoints when needed, and deprecate slowly with clear timelines (backward compatibility).</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 6 Conclusion

    - The first digit says who must act: 2xx done, 4xx fix your request, 5xx the server broke.
    - 422: broke a written rule at the door. 404: nothing lives there. 400: asks the impossible.
    - GET, PUT and DELETE are idempotent; POST is not, so a timed-out POST cannot be blindly retried.
    - Stateless: the server forgets the conversation, never the data.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Every 422 above was the request's *shape* failing a check before any endpoint code ran.
    Pydantic is that door. Chapter 7 shows why the second arrow fails:

    $$
    \\text{valid request} \\Rightarrow \\text{schema checks pass} \\quad\\text{but}\\quad \\text{schema checks pass} \\nRightarrow \\text{valid request}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 7. Pydantic Models"),
            chapter_intro(
                "logic",
                "Which inputs are allowed into the trusted system boundary?",
                "Chapter 6 wrote the contract; now we enforce it.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(diagram, mo):
    def _card(x, y, title, sub, cls, w=280, h=130):
        return (
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 - 6}" text-anchor="middle" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="{x + w / 2}" y="{y + h / 2 + 20}" text-anchor="middle">{sub}</text>'
        )

    _boundary = diagram(
        '<path d="M680 0 V 200" fill="none" stroke="currentColor" stroke-dasharray="6 6" opacity="0.45"/>'
        '<text class="dg-muted" x="668" y="20" text-anchor="end">untrusted</text>'
        '<text class="dg-muted" x="692" y="20">trusted</text>'
        + _card(0, 50, "JSON from outside", "request body, form, CSV row", "dg-box", w=250)
        + _card(330, 50, "Pydantic model", "the door: types and rules", "dg-tier")
        + _card(720, 50, "typed Python object", "nothing behind it re-checks", "dg-box dg-ok")
        + _card(330, 230, "422: a list of errors", "one entry per broken rule", "dg-box dg-hot", h=70)
        + '<path class="dg-edge" d="M250 115 H 324"/><path class="dg-edge dg-ok" d="M610 115 H 714"/>'
        + '<path class="dg-edge dg-hot" d="M470 180 V 224"/>',
        width=1000,
        height=300,
        label="Untrusted JSON enters a Pydantic model, the door. What passes becomes a typed Python object on the "
        "trusted side; what breaks a rule is turned away as a 422 with one error per broken rule.",
        tier="logic",
    )
    mo.md(
        f"""
    <div class="section-card">
      <h3>Pydantic: Check Once, at the Door</h3>
      {_boundary}
      <p class="vis-caption">A <strong>type hint</strong> (<code>name: str</code>) is only documentation
      to plain Python; Pydantic <em>enforces</em> it.</p>
    </div>
        """
    )
    return


@app.cell
def _(mo):
    ch7_preset = mo.ui.dropdown(
        options={
            "valid → should pass": {"id": 1, "name": "Ada", "gpa": 3.8, "email": "ada@example.com"},
            "missing_email → should fail": {"id": 2, "name": "Lin", "gpa": 3.4},
            "gpa_out_of_range → should fail": {"id": 3, "name": "Mira", "gpa": 5.2, "email": "mira@example.com"},
            "wrong_type → should fail": {"id": "not-an-int", "name": "Sam", "gpa": "high", "email": "sam@example.com"},
            # Every field is the declared type and inside its declared range. Every field is also nonsense.
            "garbage_that_passes → ???": {"id": -7, "name": "   ", "gpa": 0.0, "email": "definitely not an email"},
            # Two numbers arrive as text, and nothing is rejected either.
            "silently_coerced → ???": {"id": "42", "name": "Ada", "gpa": "3.5", "email": "ada@example.com"},
        },
        value="valid → should pass",
        label="Preset payload",
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Interactive Payload Validation

    ```python
    class Student(BaseModel):            # types and one range
        id: int
        name: str
        gpa: float = Field(ge=0.0, le=4.0)
        email: str

    class StrictStudent(Student):        # the same, plus the rules written down
        model_config = ConfigDict(str_strip_whitespace=True, strict=True)
        id: int = Field(gt=0)
        name: str = Field(min_length=1)  # counted after the strip
        email: str = Field(pattern=".+@.+")
    ```

    Pick a preset, or edit the JSON. Guess both verdicts first: **the last two presets are the point.**
                """
            ),
            ch7_preset,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (ch7_preset,)


@app.cell
def _(ch7_preset, json, mo):
    ch7_json = mo.ui.text_area(value=json.dumps(ch7_preset.value, indent=2), rows=7, label="Student JSON", full_width=True)
    ch7_json
    return (ch7_json,)


@app.cell
def _(ch7_json, html, json, mo, pydantic):
    class _Student(pydantic.BaseModel):
        id: int
        name: str
        gpa: float = pydantic.Field(ge=0.0, le=4.0)
        email: str

    class _StrictStudent(_Student):
        model_config = pydantic.ConfigDict(str_strip_whitespace=True, strict=True)
        id: int = pydantic.Field(gt=0)
        name: str = pydantic.Field(min_length=1)
        email: str = pydantic.Field(pattern=".+@.+")

    try:
        _sent = json.loads(ch7_json.value)
    except json.JSONDecodeError:
        _sent = None  # Pydantic reports it too, as one error on the whole input

    def _code(value):
        # no-break spaces, so a name of three spaces does not collapse to one
        return f"<code>{html.escape(repr(value)).replace(' ', '&nbsp;')}</code>"

    def _row(colour, field, sent, verdict):
        return (
            f'<div style="margin-top: 8px; padding: 8px 12px; border-left: 4px solid {colour}; border-radius: 8px;'
            f' background: color-mix(in srgb, {colour} 12%, transparent)"><strong>{field}</strong> {sent} {verdict}</div>'
        )

    def _column(title, model):
        """One model's verdict: a tile with one row per field, ok in teal and broken in red; and the raw output."""
        try:
            student = model.model_validate_json(ch7_json.value)  # parse + validate in one step
            errors, raw = {}, student.model_dump_json(indent=2)
        except pydantic.ValidationError as exc:
            student, errors, raw = None, {}, exc.json(indent=2, include_url=False)
            for _e in exc.errors():
                errors.setdefault(".".join(map(str, _e["loc"])) or "JSON", []).append(_e["msg"])
        fields = [*model.model_fields, *(_f for _f in errors if _f not in model.model_fields)] if isinstance(_sent, dict) else list(errors)
        rows = []
        for field in fields:
            sent = _code(_sent[field]) if isinstance(_sent, dict) and field in _sent else "<em>(missing)</em>"
            if field in errors:
                rows.append(_row("var(--red)", field, sent, "&#10007; " + html.escape("; ".join(errors[field]))))
            elif student is None:
                rows.append(_row("var(--teal)", field, sent, "&#10003;"))
            else:
                kept = getattr(student, field)
                changed = isinstance(_sent, dict) and repr(kept) != repr(_sent.get(field))
                rows.append(_row("var(--teal)", field, sent, "&#10003;" + (f" became {_code(kept)}" if changed else "")))
        ok = student is not None
        verdict = "accepted" if ok else f"rejected, {sum(map(len, errors.values()))} error(s)"
        tile = (
            f'<div class="tile" style="--tier: var({"--teal" if ok else "--red"})">'
            f'<div class="tile-key">{"&#10003;" if ok else "&#10007;"}</div>'
            f'<div class="tile-title">{title}: {verdict}</div>{"".join(rows)}</div>'
        )
        return tile, mo.md(f"**{title}**\n\n```json\n{raw}\n```")

    _loose, _loose_raw = _column("Student", _Student)
    _strict, _strict_raw = _column("StrictStudent", _StrictStudent)
    mo.ui.tabs(
        {
            "Per field": mo.Html(f'<div class="grid-2" style="font-size: 16px">{_loose}{_strict}</div>'),
            "Raw output": mo.vstack([_loose_raw, _strict_raw]),  # stacked: a long error line would push a twin off screen
        }
    )
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md(
                """
    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">&ne;</div><div class="tile-title">Shape, not truth</div>
        <p>A negative id, a blank name, no real email: right types, in range, so <code>Student</code>
        accepts it.</p></div>
      <div class="tile"><div class="tile-key">"&nbsp;&nbsp;&nbsp;"</div><div class="tile-title">Strip, then count</div>
        <p><code>min_length=1</code> alone lets three spaces through; <code>str_strip_whitespace</code>
        trims first. Our API's <code>Input</code> base does both, plus <code>extra="forbid"</code>.</p></div>
      <div class="tile"><div class="tile-key">"42"</div><div class="tile-title">Lax or strict</div>
        <p>Lax, the default, turns <code>"42"</code> into 42; <code>strict=True</code> refuses it.
        Our API stays lax.</p></div>
    </div>
                """
            ),
            mo.md("**Validation is only as good as the rules you wrote.**").callout(kind="info"),
            mo.accordion(
                {
                    "A real email check": mo.md(
                        'The `pattern` above is a cheap check. `EmailStr` is the real one, after `pip install "pydantic[email]"`.'
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Validation</h3>
      <details>
        <summary><strong>Q1:</strong> Where should validation happen: client, server, or both?</summary>
        <p><strong>Answer:</strong> Both. The client gives fast feedback; the server must enforce the rules (server-side validation),
        because anyone can skip your client and call the API directly, as chapter 6 just did.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> Should <code>"42"</code> count as a valid <code>int</code>?</summary>
        <p><strong>Answer:</strong> It depends on who sends it. Lax mode (the default) is kind to forms and CSV files, where
        everything arrives as text; strict mode catches a client that sends the wrong type by mistake. Choose deliberately.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 7 Conclusion

    - A model checks shape, not truth.
    - Lax by default: `"42"` becomes 42 and three spaces pass as a name, unless a rule says no.
    - A rejection lists every broken rule: FastAPI's 422.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    FastAPI turns these models into validation, endpoints and docs:

    $$
    \\text{Python types + models} \\rightarrow \\text{OpenAPI schema} \\rightarrow \\text{interactive docs}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 8. FastAPI Demo + Automatic Docs"),
            chapter_intro(
                "logic",
                "How do we keep implementation and API documentation in sync?",
                "Last stop in the logic tier: the rules from chapter 7 become a running server.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, mo):
    def _menu_item(y, title, note):
        """One thing FastAPI prints from the type hints, with its edge from the FastAPI box."""
        return (
            f'<rect class="dg-box" x="600" y="{y}" width="396" height="58" rx="12"/>'
            f'<text x="620" y="{y + 24}" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="620" y="{y + 46}">{note}</text>'
            f'<path class="dg-edge" d="M500 150 C 550 150, 550 {y + 29}, 594 {y + 29}"/>'
        )

    _menu = diagram(
        '<rect class="dg-tier" x="0" y="60" width="340" height="180" rx="16"/>'
        '<text x="20" y="94" font-weight="700">the recipe, written once</text>'
        '<text x="20" y="134" font-family="monospace" font-size="15">Rating = Annotated[int,</text>'
        '<text x="44" y="158" font-family="monospace" font-size="15">Field(ge=1, le=5)]</text>'
        '<text class="dg-muted" x="20" y="196">used by SaleCreate, SaleUpdate</text>'
        '<text class="dg-muted" x="20" y="220">and the rating filters</text>'
        '<path class="dg-edge" d="M340 150 H 374"/>'
        + box(380, 122, "FastAPI", w=120, h=56, cls="dg-tier")
        + '<text class="dg-muted" x="440" y="204" text-anchor="middle">reads the hints</text>'
        + _menu_item(0, "422 for a rating of 9", "the rule, enforced before your code runs")
        + _menu_item(76, "/openapi.json", "the menu, for programs to read")
        + _menu_item(152, "/redoc", "the menu, as a reference manual")
        + _menu_item(228, "/docs (Swagger UI)", "the menu, with Try it out buttons")
        + '<rect class="dg-box dg-hot" x="0" y="300" width="340" height="64" rx="12"/>'
        '<text x="20" y="326">docstring: "recomputes total_price"</text>'
        '<text class="dg-muted" x="20" y="350">a behaviour, not a type</text>'
        '<path class="dg-edge dg-hot" d="M340 332 H 800 V 292"/>'
        '<text class="dg-hot" x="570" y="322" text-anchor="middle">typed by hand: nothing checks it</text>',
        width=1000,
        height=370,
        label="One line, Rating = Annotated[int, Field(ge=1, le=5)], goes into FastAPI, which prints four things from it: "
        "the 422 for a rating of 9, /openapi.json, /redoc and /docs. A hand-written docstring about recomputing "
        "total_price reaches /docs too, but nothing checks it.",
        tier="logic",
    )
    _more = mo.md(
        """
    - **OpenAPI** (`/openapi.json`) is a standard file format that describes every endpoint an API
      has, for other programs to read. FastAPI writes it for you.
    - **Swagger UI** (`/docs`) reads that file and turns it into buttons: open it and press *Try it out*.
    - **ReDoc** (`/redoc`) reads the same file and renders it as a reference manual.
    - The rating rule is written once in `sw03_demo_api.py` and used for new sales, for edits and for
      the `min_rating`/`max_rating` filters. The schema can say `units_sold` must be at least 1; it
      cannot say that changing it recomputes `total_price`.
    - The server is the one you started for chapter 6 with `uvicorn sw03_demo_api:app`. While you
      *edit* the API, `--reload` restarts it on every save; during the lecture, leave it out.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>FastAPI = Type Hints → OpenAPI</h3>
      <p>A hand-written menu starts lying the day the kitchen changes a recipe. FastAPI prints the menu from the recipes.</p>
      {_menu}
      <p class="vis-caption"><strong>Change the 5 to a 10 and all four change together</strong>, because there is
      only one 5. A rule about behaviour is not a type: it reaches <code>/docs</code> only as hand-written text.</p>
    </div>
                """
            ),
            mo.accordion({"The three doc pages, and the server behind them": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, html, mo):
    _cw = 9.6  # px per character of 16 px monospace; textLength pins every piece of code to it

    def _code(y, parts):
        """One line of code from (text, label) pieces: a labelled piece gets a bracket and its label below it."""
        svg, col = [], 0
        for text, label in parts:
            x, w = col * _cw, len(text) * _cw
            svg.append(
                f'<text x="{x:.0f}" y="{y}" font-family="monospace" font-size="16" textLength="{w:.0f}"'
                f' lengthAdjust="spacingAndGlyphs" style="white-space: pre">{html.escape(text)}</text>'
            )
            if label:
                svg.append(
                    f'<path style="fill: none; stroke: var(--tier); stroke-width: 2.5"'
                    f' d="M{x + 2:.0f} {y + 9} v 8 H {x + w - 2:.0f} v -8"/>'
                    f'<text class="dg-muted" x="{x + w / 2:.0f}" y="{y + 40}" text-anchor="middle">{label}</text>'
                )
            col += len(text)
        return "".join(svg)

    _sentence = diagram(
        _code(
            24,
            [
                ("@app.post", "verb"),
                ("(", None),
                ('"/sales"', "path"),
                (", ", None),
                ("response_model=Sale", "the answer's shape"),
                (", ", None),
                ("status_code=201", "code on success"),
                (", ", None),
                ('tags=["Sales"]', "group in /docs"),
                (", ", None),
                ("responses=BAD_REQUEST", "the errors it adds"),
                (")", None),
            ],
        )
        + _code(
            114,
            [
                ("def create_sale(", None),
                ("payload: SaleCreate", "the model the client fills: checked first, 422 if not"),
                (") -> dict[str, Any]:", None),
            ],
        )
        + _code(
            204,
            [
                ("    ", None),
                ('"""Record a sale. The server computes total_price as units_sold x the product\'s price."""',
                 "its description in /docs, written by hand"),
            ],
        ),
        width=940,
        height=260,
        label="The decorator of POST /sales read as a sentence: verb, path, the shape of the answer, the status code "
        "on success, its group in /docs and the errors it adds. The payload's type is the model checked first; "
        "the docstring becomes the description in /docs.",
        tier="logic",
    )
    _source = mo.md("""
    ```python
    # file: sw03_demo_api.py (abridged)
    # Every rule is written once, here, and reused wherever the field appears.
    Rating = Annotated[int, Field(ge=1, le=5)]


    class Input(BaseModel):
        "\""What a client may send: stray whitespace is trimmed, unknown fields are refused (422)."\""

        model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


    class SaleCreate(Input):
        "\""A new sale. There is no total_price: the server computes it from units_sold and the product's price."\""

        sale_date: SaleDate
        product_id: Ref
        country_id: Ref
        units_sold: Units
        customer_rating: Rating


    @app.post("/sales", response_model=Sale, status_code=201, tags=["Sales"], responses=BAD_REQUEST)
    def create_sale(payload: SaleCreate) -> dict[str, Any]:
        "\""Record a sale. The server computes total_price as units_sold x the product's price."\""
        ...


    @app.put("/sales/{sale_id}", response_model=Sale, tags=["Sales"], responses=NOT_FOUND | BAD_REQUEST)
    def update_sale(sale_id: SaleId, payload: SaleUpdate) -> dict[str, Any]:
        "\""Update a sale. Fields you leave out keep their current value (the HTTP standard would call this PATCH).

        total_price is recomputed only when units_sold or product_id actually change, so editing just
        the rating keeps the stored total.
        "\""
        ...
    ```

    The second docstring is the hand-written recompute rule from the drawing above. Sales are the
    resource this chapter follows, so every verb is written out; the four lookup tables (regions,
    countries, categories, products) share one generic set of five endpoints, registered by
    `add_lookup_endpoints`. Nothing else had to be written to get documentation.
    """)
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Read a Decorator as a Sentence</h3>
      {_sentence}
      <p class="vis-caption">Everything <code>/docs</code> shows about this endpoint comes from these three lines.
      <code>SaleCreate</code> has no <code>total_price</code>, so a client cannot set its own price.</p>
    </div>
                """
            ),
            mo.accordion({"The abridged source: the model and two endpoints": _source}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    fastapi_check = mo.ui.run_button(label="1) Check API status")
    fastapi_payload = mo.ui.text_area(
        value='{"name": "Lecture Demo Widget", "price": 99.9, "description": "Created live in Chapter 8", "category_id": 1}',
        label="POST /products payload (JSON)",
        rows=3,
        full_width=True,
    )
    fastapi_post = mo.ui.run_button(label="2) POST /products", kind="success")
    fastapi_item_id = mo.ui.number(start=1, step=1, value=1, label="Product id")
    fastapi_get = mo.ui.run_button(label="3) GET /products/{id}")
    return fastapi_check, fastapi_get, fastapi_item_id, fastapi_payload, fastapi_post


@app.cell
def _(api_base_url, fastapi_check, fastapi_get, fastapi_item_id, fastapi_payload, fastapi_post, mo):
    # Display only, so editing the shared URL re-renders these widgets instead of rebuilding them.
    mo.vstack(
        [
            mo.md(
                "### Live API Workflow\n\n"
                "Start the API (`uvicorn sw03_demo_api:app`), then press the buttons in order. Press **2)** "
                "twice: the name is taken, so the second answer is `400`."
            ),
            mo.hstack([api_base_url, fastapi_check], widths=[5, 1], align="end"),
            fastapi_payload,
            mo.hstack([fastapi_post, fastapi_item_id, fastapi_get], justify="start", align="end", gap=2),
        ],
        gap=0.8,
    ).callout(kind="neutral")
    return


@app.cell
def _(api_base_url, call_api, mo, requests):
    from http.client import responses as ch8_phrases  # 201 -> "Created", for the answers below

    def ch8_api(method, path, body=None):
        """call_api against the base URL above. Stops the cell with a hint if nothing answers, or not with JSON."""
        base = api_base_url.value.rstrip("/")
        try:
            status, answer = call_api(method, base + path, body)
        except requests.RequestException:
            mo.stop(
                True,
                mo.md(f"Could not reach `{base}`. Start the API first: `uvicorn sw03_demo_api:app`.").callout(kind="danger"),
            )
        if answer and isinstance(answer, str):  # HTML or plain text, e.g. the Streamlit dashboard's port
            mo.stop(
                True,
                mo.md(f"`{base}{path}` answered `{status}`, but not with JSON. Is that the sales API?").callout(kind="danger"),
            )
        return status, answer

    # The sale the chapter 8 labs send: 10 units of product 1, sold in country 3.
    sale_slip = {"sale_date": "2026-03-01", "product_id": 1, "country_id": 3, "units_sold": 10, "customer_rating": 5}
    return ch8_api, ch8_phrases, sale_slip


@app.cell
def _(api_base_url, box, ch8_api, diagram, fastapi_check, mo):
    mo.stop(
        not fastapi_check.value,
        mo.md("Start `uvicorn sw03_demo_api:app` in a terminal, then click **1) Check API status**.").callout(kind="neutral"),
    )
    _base = api_base_url.value.rstrip("/")
    _status, _schema = ch8_api("GET", "/openapi.json")
    mo.stop(
        _status != 200,
        mo.md(f"`{_base}/openapi.json` answered `{_status}`. Is that the sales API?").callout(kind="danger"),
    )
    # The API describes itself: one row per path this chapter uses, one box per verb it accepts.
    _paths = {_p: _ops for _p, _ops in _schema["paths"].items() if _p.startswith(("/products", "/sales"))}
    _verbs = ("get", "post", "put", "delete")
    _parts = [
        f'<text x="{300 + _j * 120}" y="20" text-anchor="middle" font-weight="700">{_v.upper()}</text>'
        for _j, _v in enumerate(_verbs)
    ]
    for _i, (_path, _ops) in enumerate(_paths.items()):
        _y = 40 + _i * 52
        _parts.append(
            f'<text x="0" y="{_y + 20}" font-family="monospace" dominant-baseline="central">{_path}</text>'
        )
        for _j, _v in enumerate(_verbs):
            if _v in _ops:
                _parts.append(box(248 + _j * 120, _y, "&#10003;", w=104, h=40, cls="dg-tier"))
            else:
                _parts.append(
                    f'<rect x="{248 + _j * 120}" y="{_y}" width="104" height="40" rx="12" fill="none"'
                    ' stroke="currentColor" stroke-dasharray="6 6" opacity="0.3"/>'
                )
    _matrix = diagram(
        "".join(_parts),
        width=720,
        height=40 + 52 * len(_paths),
        label="The paths this chapter uses and the verbs each accepts, read from /openapi.json: "
        + "; ".join(f"{_p}: {', '.join(_o).upper()}" for _p, _o in _paths.items()),
        tier="logic",
    )
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(f"{_status} OK", label="GET /openapi.json", caption=f"{_schema['info']['title']} "
                            f"{_schema['info']['version']} is running", bordered=True),
                    mo.stat(len(_schema["paths"]), label="paths it describes", bordered=True),
                    mo.md(f"**[Open {_base}/docs]({_base}/docs)**"),
                ],
                widths=[2, 1, 2],
                align="center",
            ),
            _matrix,
        ],
        gap=0.8,
    ).callout(kind="success")
    return


@app.cell
def _(ch8_api, ch8_phrases, fastapi_payload, fastapi_post, json, mo):
    mo.stop(not fastapi_post.value, mo.md("Edit the payload, then click **2) POST /products**.").callout(kind="neutral"))
    try:
        _payload = json.loads(fastapi_payload.value)
    except json.JSONDecodeError as _exc:
        mo.stop(True, mo.md(f"The payload is not valid JSON: `{_exc}`").callout(kind="danger"))
    _status, _answer = ch8_api("POST", "/products", _payload)
    mo.md(
        f"`POST /products` → **{_status} {ch8_phrases.get(_status, '')}**\n\n```json\n{json.dumps(_answer, indent=2)}\n```"
    ).callout(kind="success" if _status < 400 else "danger")
    return


@app.cell
def _(ch8_api, ch8_phrases, fastapi_get, fastapi_item_id, json, mo):
    mo.stop(not fastapi_get.value, mo.md("Pick a product id, then click **3) GET /products/{id}**.").callout(kind="neutral"))
    _path = f"/products/{fastapi_item_id.value}"
    _status, _answer = ch8_api("GET", _path)
    mo.md(
        f"`GET {_path}` → **{_status} {ch8_phrases.get(_status, '')}**\n\n```json\n{json.dumps(_answer, indent=2)}\n```"
    ).callout(kind="success" if _status < 400 else "danger")
    return


@app.cell
def _(mo):
    run_gates = mo.ui.run_button(label="Send seven slips through both gates", kind="success")
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Seven Sale Slips, One Model, Two Gates

    What does a server add? **Gate 1** is the API's own `SaleCreate`, run right here in the
    notebook. **Gate 2** is the running API.
                """
            ),
            run_gates,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_gates,)


@app.cell
def _(box, ch8_api, diagram, mo, pydantic, run_gates, sale_slip, static_table):
    mo.stop(
        not run_gates.value,
        mo.md(
            "**Predict first:** which slips does your laptop catch, and which only the server? "
            "Then click **Send seven slips through both gates**."
        ).callout(kind="neutral"),
    )
    from sw03_demo_api import SaleCreate as _SaleCreate  # gate 1: the server's own model, no network

    _ok = sale_slip
    _slips = {
        "a good sale": _ok,
        "rating of 9": {**_ok, "customer_rating": 9},
        "zero units sold": {**_ok, "units_sold": 0},
        "date as 01/03/2026": {**_ok, "sale_date": "01/03/2026"},
        "no country at all": {_k: _v for _k, _v in _ok.items() if _k != "country_id"},
        "its own total_price of 0.01": {**_ok, "total_price": 0.01},
        "product 9999": {**_ok, "product_id": 9999},
    }
    _rows, _cells, _good = [], [], None
    for _name, _slip in _slips.items():
        try:
            _SaleCreate.model_validate(_slip)
            _gate1, _short1 = "passes", "&#10003; passes"
        except pydantic.ValidationError as _exc:
            _err = _exc.errors()[0]
            _gate1, _short1 = f"rejected: {_err['loc'][0]} — {_err['msg']}", f"&#10007; {_err['loc'][0]}"
        _status, _answer = ch8_api("POST", "/sales", _slip)
        mo.stop(
            not (isinstance(_answer, dict) and ("detail" in _answer or "sale_id" in _answer)),
            mo.md(f"`POST /sales` answered `{_status}`: `{_answer}`. Is that the sales API?").callout(kind="danger"),
        )
        if _status == 201:
            _good = _answer
            ch8_api("DELETE", f"/sales/{_good['sale_id']}")  # leave the file as we found it
            _gate2, _short2 = f"201 created — {len(_good)} fields back, total_price {_good['total_price']}", "&#10003; 201 created"
        else:
            _detail = _answer["detail"]
            _why = _detail if isinstance(_detail, str) else _detail[0]["msg"]
            _gate2 = f"{_status} — {_why}"
            _short2 = f"&#10007; {_status} " + (_why if isinstance(_detail, str) else _detail[0]["loc"][-1])
        _rows.append({"the slip": _name, "gate 1: your laptop": _gate1, "gate 2: the server": _gate2})
        _cells.append((_name, _gate1 == "passes", _short1, _status, _short2))
    mo.stop(_good is None, mo.md("Even the good sale was refused. Restart the API to reseed its data.").callout(kind="danger"))

    # One row per slip, one box per gate: teal got through, red was turned away.
    _svg = [
        '<text x="430" y="16" text-anchor="middle" font-weight="700">gate 1: your laptop</text>'
        '<text x="805" y="16" text-anchor="middle" font-weight="700">gate 2: the server</text>'
    ]
    for _i, (_name, _pass1, _short1, _status, _short2) in enumerate(_cells):
        _y = 36 + _i * 48
        _svg.append(
            f'<text x="250" y="{_y + 20}" text-anchor="end" dominant-baseline="central">{_name}</text>'
            + box(270, _y, _short1, w=320, h=40, cls="dg-box dg-ok" if _pass1 else "dg-box dg-hot")
            + box(610, _y, _short2, w=386, h=40, cls="dg-box dg-ok" if _status == 201 else "dg-box dg-hot")
        )
    _matrix = diagram(
        "".join(_svg),
        width=1000,
        height=36 + 48 * len(_cells),
        label="Seven slips, each checked by the model on the laptop and by the running server. "
        + "; ".join(f"{_r['the slip']}: {_r['gate 1: your laptop']}, then {_r['gate 2: the server']}" for _r in _rows),
    )
    _table = static_table(
        _rows,
        label="The same seven slips, checked twice",
        wrapped_columns=["gate 1: your laptop", "gate 2: the server"],  # the messages are the point
        column_widths={"gate 1: your laptop": 410, "gate 2: the server": 410},
    )

    def _count(status):
        n = sum(1 for _c in _cells if _c[3] == status)
        return f"{n} slip{'' if n == 1 else 's'}"

    _tiles = mo.md(
        f"""
    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">422</div><div class="tile-title">{_count(422)}: the wrong shape</div>
        <p>Caught at both gates with the same message: both run the same model.</p></div>
      <div class="tile"><div class="tile-key">400</div><div class="tile-title">{_count(400)}: a fact</div>
        <p>A well-formed id. Only the server can open the filing cabinet and find no product 9999.</p></div>
      <div class="tile"><div class="tile-key">201</div><div class="tile-title">{_count(201)}: booked</div>
        <p>{len(_ok)} fields sent, {len(_good)} back. The server computed <code>total_price</code> =
        {_good["units_sold"]} &times; {_good["total_price"] / _good["units_sold"]:.2f} itself.</p></div>
    </div>
        """
    )
    _why = mo.md(
        """
    A price the client is allowed to invent is a price the client can lie about. `SaleCreate` has no
    `total_price` field, and `Input` refuses fields it does not know, so the slip that brought its
    own `total_price` was refused at both gates.
        """
    )
    mo.vstack(
        [
            mo.ui.tabs({"Chart": _matrix, "Table": _table}),
            _tiles,
            mo.accordion({"Why the client may not send total_price": _why}),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    run_twice = mo.ui.run_button(label="Press every verb twice", kind="success")
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Press It Twice

    The lift button or the ticket dispenser? All four verbs go to the running API **twice in a
    row**, against one sale.
                """
            ),
            run_twice,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_twice,)


@app.cell
def _(box, ch8_api, chart_or_table, diagram, mo, run_twice, sale_slip):
    mo.stop(
        not run_twice.value,
        mo.md(
            "**Predict first:** which verb changes the world again on the second press? "
            "Then click **Press every verb twice**."
        ).callout(kind="neutral"),
    )

    _post1, _first = ch8_api("POST", "/sales", sale_slip)
    mo.stop(_post1 != 201, mo.md(f"`POST /sales` answered `{_post1}`: `{_first}`").callout(kind="danger"))
    _post2, _second = ch8_api("POST", "/sales", sale_slip)
    _one = f"/sales/{_first['sale_id']}"
    _put1, _ = ch8_api("PUT", _one, {"units_sold": 25})
    _put2, _ = ch8_api("PUT", _one, {"units_sold": 25})
    _get1, _got = ch8_api("GET", _one)
    _get2, _ = ch8_api("GET", _one)
    _del1, _ = ch8_api("DELETE", _one)
    _del2, _ = ch8_api("DELETE", _one)
    ch8_api("DELETE", f"/sales/{_second['sale_id']}")  # tidy up the duplicate

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
            "what changed in the world": f"two different sales booked: #{_first['sale_id']} and #{_second['sale_id']}",
            "lift button?": "NO",
        },
        {
            "verb": "PUT",
            "first press": _put1,
            "second press": _put2,
            "what changed in the world": f"units_sold is {_got['units_sold']} either way",
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
    # One row per verb: the two status codes, then what the world looks like after both presses.
    _svg = [
        '<text x="235" y="20" text-anchor="middle" font-weight="700">first press</text>'
        '<text x="405" y="20" text-anchor="middle" font-weight="700">second press</text>'
        '<text x="748" y="20" text-anchor="middle" font-weight="700">what changed in the world</text>'
    ]
    for _i, _row in enumerate(_rows):
        _y, _lift = 40 + _i * 58, _row["lift button?"] == "yes"
        _svg.append(
            f'<text x="0" y="{_y + 20}" font-weight="700">{_row["verb"]}</text>'
            f'<text class="dg-muted" x="0" y="{_y + 42}">{"lift button" if _lift else "ticket dispenser"}</text>'
            + box(160, _y, str(_row["first press"]), w=150, h=48)
            + box(330, _y, str(_row["second press"]), w=150, h=48, cls="dg-box" if _lift else "dg-box dg-hot")
            + box(500, _y, _row["what changed in the world"], w=496, h=48, cls="dg-box dg-ok" if _lift else "dg-box dg-hot")
        )
    _matrix = diagram(
        "".join(_svg),
        width=1000,
        height=40 + 58 * len(_rows),
        label="Each verb sent twice. "
        + "; ".join(
            f"{_r['verb']}: {_r['first press']} then {_r['second press']}, {_r['what changed in the world']}" for _r in _rows
        ),
    )
    _more = mo.md(
        """
    That is exactly why a checkout page begs you not to hit refresh, and why a payment that times
    out is frightening in a way a profile edit is not.

    Idempotence is a promise the API author makes, not something HTTP enforces. A carelessly
    written `PUT` can behave exactly like `POST`. It holds here because this server updates a row
    you named by id, not because the word PUT is magic.
        """
    )
    mo.vstack(
        [
            chart_or_table(_matrix, _rows, label="Each verb, sent twice"),
            mo.md(
                f"**GET, PUT and DELETE are lift buttons:** the world ends up the same. **POST is a ticket "
                f"dispenser:** the second press booked a second sale. The second DELETE's `{_del2}` changes "
                "nothing: idempotent is about the effect, not the status code."
            ).callout(kind="info"),
            mo.accordion({"Idempotence is a promise, not a law": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    run_follow = mo.ui.run_button(label="Follow the sale into the file", kind="success")
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Where Does a POST Actually Go?

    POST one sale, watch `data/sales.parquet` grow, and compare the stored row with the JSON
    answer. Needs the API started from this folder.
                """
            ),
            run_follow,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_follow,)


@app.cell
def _(Path, box, ch8_api, chart_or_table, diagram, duckdb, mo, run_follow, sale_slip):
    mo.stop(
        not run_follow.value,
        mo.md(
            "**Predict first:** does the file store the product's name, or only its id? "
            "Then click **Follow the sale into the file**."
        ).callout(kind="neutral"),
    )
    _sales_file = Path(mo.notebook_dir()) / "data" / "sales.parquet"
    mo.stop(
        not _sales_file.exists(),
        mo.md("Needs a running API (which creates `data/sales.parquet`).").callout(kind="warn"),
    )
    _con = duckdb.connect()
    _count = f"SELECT count(*) FROM '{_sales_file.as_posix()}'"
    _before = _con.sql(_count).fetchone()[0]
    _status, _created = ch8_api("POST", "/sales", sale_slip)
    mo.stop(_status != 201, mo.md(f"`POST /sales` answered `{_status}`: `{_created}`").callout(kind="danger"))
    try:
        _after = _con.sql(_count).fetchone()[0]
        _stored = _con.execute(
            f"SELECT * FROM '{_sales_file.as_posix()}' WHERE sale_id = ?", [_created["sale_id"]]
        ).df()
    finally:
        ch8_api("DELETE", f"/sales/{_created['sale_id']}")  # leave the file as we found it
    mo.stop(
        _stored.empty,
        mo.md(
            f"Sale {_created['sale_id']} never reached `{_sales_file}`: the API at the base URL writes "
            "to another `data/` folder. Start it from this notebook's folder."
        ).callout(kind="warn"),
    )

    _file_row = _stored.iloc[0].to_dict()
    _rows = [
        {"field": _k, "in the file": str(_file_row.get(_k, "—")), "in the API answer": str(_v)}
        for _k, _v in _created.items()
    ]

    def _band(y, tier, name, note):
        return (
            f'<g class="tier-{tier}"><rect class="dg-tier" x="2" y="{y}" width="996" height="88" rx="16"/>'
            f'<text x="20" y="{y + 38}" font-weight="700">{name}</text>'
            f'<text class="dg-muted" x="20" y="{y + 62}">{note}</text></g>'
        )

    # The request goes down the left column, the answer comes back up the right, like the tier map.
    _trip = diagram(
        _band(0, "presentation", "client", "this notebook")
        + _band(120, "logic", "logic tier", "sw03_demo_api.py")
        + _band(240, "data", "data tier", "data/sales.parquet")
        + '<text x="402" y="110" class="dg-muted">request</text>'
        + '<text x="822" y="110" class="dg-muted">answer</text>'
        + box(220, 20, f"POST /sales · {len(sale_slip)} fields, no price", w=340, h=48)
        + box(220, 140, "check · price it · lock · append", w=340, h=48)
        + box(220, 260, f"{_before:,} rows &#8594; {_after:,} rows", w=340, h=48)
        + box(640, 260, f"row stored: {len(_stored.columns)} columns, ids only", w=340, h=48)
        + box(640, 140, "joins product, country, region names", w=340, h=48)
        + box(640, 20, f"{_status} · {len(_created)} fields, names spelled out", w=340, h=48)
        + '<path class="dg-edge" d="M390 68 V 134"/><path class="dg-edge" d="M390 188 V 254"/>'
        + '<path class="dg-edge" d="M560 284 H 634"/>'
        + '<path class="dg-edge" d="M810 260 V 194"/><path class="dg-edge" d="M810 140 V 74"/>',
        width=1000,
        height=330,
        label=f"The POST goes down: the notebook sends {len(sale_slip)} fields, the API checks, prices and appends it, "
        f"and the file grows from {_before:,} to {_after:,} rows. The answer comes up: the stored row has "
        f"{len(_stored.columns)} columns of ids, the API joins the names and answers {_status} with {len(_created)} fields.",
        tier="logic",
    )
    _caption = mo.md(
        f"""
    <p class="vis-caption">The <strong>file</strong> keeps <code>product_id {_created["product_id"]}</code> and
    <code>country_id {_created["country_id"]}</code>: ids, every fact written once. The <strong>answer</strong> spells
    out "{_created["product_name"]}", "{_created["country_name"]}" and "{_created["region_name"]}": the logic tier
    did the joining, so the dashboard does not have to.</p>
        """
    )
    _more = mo.md(
        """
    The logic tier did not invent a database. It wrote to `data/sales.parquet`, a working copy of
    the file you compressed in chapter 4 and queried in chapter 5 (the API copies `data/seed/` into
    `data/` on every start). Even the date changes shape: the file keeps a timestamp, the API sends a
    plain date.

    **One honest callback.** We just read that file behind the API's back. The API takes a lock
    around every write, but like the key on the hook in chapter 1, a lock only protects those who ask
    for it. Pandas rewrites the whole Parquet file on every change, so a read at the wrong instant
    could catch it half-written. That is chapter 1's isolation problem, and the reason a real system
    puts a database at the bottom of the data tier rather than a file.
        """
    )
    mo.vstack(
        [
            chart_or_table(mo.vstack([_trip, _caption], gap=0.4), _rows, label="Same sale, two tiers, two shapes"),
            mo.accordion({"Where the file came from, and one honest callback": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    run_two_analysts = mo.ui.run_button(label="Run the two-analyst test", kind="success")
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Two People, One Product, Both Click Save

    Anna and Ben open product 1 at the same price. Anna saves a **10% raise**, Ben a
    **CHF 20 surcharge**. Both get `200 OK`.
                """
            ),
            run_two_analysts,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_two_analysts,)


@app.cell
def _(ch8_api, chart_or_table, mo, run_two_analysts):
    mo.stop(
        not run_two_analysts.value,
        mo.md(
            "**Predict first:** what is the price afterwards? Write it down, then click **Run the two-analyst test**."
        ).callout(kind="neutral"),
    )

    def _price(method, body=None):
        """GET or PUT product 1 and return its price. Anything but 200 OK stops the cell."""
        status, answer = ch8_api(method, "/products/1", body)
        mo.stop(status != 200, mo.md(f"`{method} /products/1` answered `{status}`: `{answer}`").callout(kind="danger"))
        return answer["price"]

    _start = _price("GET")
    try:
        # Both analysts open the page. Two ordinary GETs, nothing concurrent.
        _anna_sees = _price("GET")
        _ben_sees = _price("GET")
        # Both save, strictly one after the other.
        _anna_sends = round(_anna_sees * 1.10, 2)
        _ben_sends = round(_ben_sees + 20, 2)
        _after_anna = _price("PUT", {"price": _anna_sends})
        _after_ben = _price("PUT", {"price": _ben_sends})
        _final = _price("GET")
    finally:
        ch8_api("PUT", "/products/1", {"price": _start})  # put the price back, like the other labs tidy up
    _correct = round(round(_start * 1.10, 2) + 20, 2)

    _steps = [
        {"step": "1. price before anyone touches it", "price": _start, "server said": "-"},
        {"step": "2. Anna opens the product", "price": _anna_sees, "server said": "200 OK"},
        {"step": "3. Ben opens the same product", "price": _ben_sees, "server said": "200 OK"},
        {"step": "4. Anna saves a 10% raise", "price": _after_anna, "server said": "200 OK"},
        {"step": "5. Ben saves a CHF 20 surcharge", "price": _after_ben, "server said": "200 OK"},
        {"step": "6. price afterwards", "price": _final, "server said": "-"},
        {"step": "what it should have been", "price": _correct, "server said": "-"},
    ]
    # Chapter 1's lost-update grid, with people instead of workers and a price instead of a counter.
    _grid = mo.Html(
        f"""
    <div class="section-card flow-card">
      <div class="lost-update-wrap">
        <div class="lost-update-grid">
          <div class="lu-header">Step</div>
          <div class="lu-header">Anna</div>
          <div class="lu-header">Ben</div>
          <div class="lu-header">Price on the server</div>

          <div class="lu-step">1</div>
          <div class="lu-event lu-read">GET: sees {_anna_sees:.2f}</div>
          <div class="lu-event lu-read">GET: sees {_ben_sees:.2f}</div>
          <div class="lu-state">{_start:.2f}</div>

          <div class="lu-step">2</div>
          <div class="lu-event lu-write">PUT {_anna_sends:.2f} (+10%): 200 OK</div>
          <div class="lu-event">adds CHF 20 to his stale {_ben_sees:.2f}</div>
          <div class="lu-state">{_after_anna:.2f}</div>

          <div class="lu-step">3</div>
          <div class="lu-event lu-idle">done</div>
          <div class="lu-event lu-stale">PUT stale {_ben_sends:.2f}: 200 OK</div>
          <div class="lu-state lu-problem">{_after_ben:.2f} (Anna's raise overwritten)</div>
        </div>
      </div>
      <div class="flow-note"><strong>Should be {_correct:.2f}.</strong> Observed: {_final:.2f}, and both saves
      answered 200 OK.</div>
    </div>
        """
    )
    _more = mo.md(
        """
    Every write in `sw03_demo_api.py` runs inside one `lock`, chapter 1's own fix, so each single
    request is safe. But *there is no lock around what actually happened here*. The read and the
    write were two separate HTTP requests, minutes apart in real life, and the API has no idea they
    were meant to belong together. Ben's `PUT` carried a price computed from a page he opened
    before Anna saved. Chapter 1's lesson holds exactly as stated: a lock, like a transaction,
    protects the steps you put inside it, and nothing else. Correctness is a property of the
    design, not of the tools.
        """
    )
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(f"{_correct:.2f}", label="should be", bordered=True),
                    mo.stat(f"{_final:.2f}", label="is", bordered=True),
                    mo.stat(f"{_correct - _final:.2f}", label="lost, and nobody was told", bordered=True),
                ],
                widths="equal",
            ),
            chart_or_table(_grid, _steps, label=f"Six requests, strictly in order (then the price goes back to {_start:.2f})"),
            mo.md(
                "**Chapter 1's lost update, over HTTP.** No error, two `200 OK`s. The requests ran one after "
                "another, so it fails on every click: a design bug, not a timing fluke."
            ).callout(kind="danger"),
            mo.accordion({"Why the API's lock did not save Anna": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — FastAPI</h3>
      <details>
        <summary><strong>Q1:</strong> Gate 1 already checked the slip on your laptop. Why check it again at the server?</summary>
        <p><strong>Answer:</strong> Anyone can bypass this notebook and post directly with <code>curl</code>.
        Validating on the laptop is a courtesy to the user, instant feedback with no round trip, never a
        substitute for the server's check.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> Is the split between 422 and 400 a law of HTTP?</summary>
        <p><strong>Answer:</strong> No, it is this API's convention. FastAPI produces the 422 automatically from
        the model; the 400s are business rules somebody wrote by hand.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> How should Ben's save have failed?</summary>
        <p><strong>Answer:</strong> Loudly. Send <em>the change</em> (<code>{"raise_percent": 10}</code>) instead of
        the answer, so both changes apply. Or make the client say which version it read (<code>If-Match</code>
        with an ETag) and let the server refuse a stale write with <code>412 Precondition Failed</code>.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 8 Conclusion

    - One model drives validation, endpoint and `/docs`: the docs cannot drift. A hand-written docstring can.
    - Shape is checked anywhere (422), facts only at the server (400). Only the server computes `total_price`.
    - GET, PUT and DELETE are safe to press twice; POST books a second sale.
    - A lock per request cannot stop a lost update split over two requests: send the change, or `If-Match`.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Next: the interface people actually use, and what each frontend trades away.

    $$
    \\text{user value} = \\text{backend correctness} \\times \\text{frontend usability}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 9. Frontend Framework Comparison"),
            chapter_intro(
                "presentation",
                "What does the frontend need to know about everything behind it?",
                "The API from chapter 8 has the data; something has to show it.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, mo):
    def _room(x, tier, name, note, file, rule=None, why=None):
        """One room of the restaurant: its tier colour, what it holds, and the units rule if it states one."""
        parts = [
            f'<g class="tier-{tier}"><rect class="dg-tier" x="{x}" y="110" width="280" height="220" rx="16"/></g>',
            f'<text x="{x + 20}" y="144" font-size="20" font-weight="700">{name}</text>',
            f'<text class="dg-muted" x="{x + 20}" y="170">{note}</text>',
            box(x + 20, 188, file, w=240, h=44),
        ]
        if rule:
            parts.append(
                f'<rect class="dg-box" x="{x + 20}" y="250" width="240" height="62" rx="12"/>'
                f'<text x="{x + 140}" y="276" text-anchor="middle" font-family="monospace" font-size="15">{rule}</text>'
                f'<text class="dg-muted" x="{x + 140}" y="300" text-anchor="middle">{why}</text>'
            )
        return "".join(parts)

    _restaurant = diagram(
        _room(2, "presentation", "dining room", "ch. 9-10: what the guest sees", "sw03_demo_streamlit.py",
              "min_value=1", "repeated for politeness")
        + _room(360, "logic", "kitchen", "ch. 6-8: recipes and rules", "sw03_demo_api.py",
                "ge=1, le=100_000", "the rule")
        + _room(718, "data", "cold store", "ch. 1-5: ingredients", "data/*.parquet", "sales, products, ...", "five tables, ids only")
        # the hatches: a request goes right, the answer comes back left
        + '<path class="dg-edge" d="M284 206 H 354"/><path class="dg-edge" d="M358 250 H 288"/>'
        + '<path class="dg-edge" d="M642 206 H 712"/><path class="dg-edge" d="M716 250 H 646"/>'
        + '<text class="dg-muted" x="321" y="196" text-anchor="middle">request</text>'
        + '<text class="dg-muted" x="321" y="274" text-anchor="middle">answer</text>'
        + '<text class="dg-muted" x="679" y="196" text-anchor="middle">query</text>'
        + '<text class="dg-muted" x="679" y="274" text-anchor="middle">rows</text>'
        # the phone line: anyone can call the kitchen without passing the dining room
        + box(340, 10, "curl · a script · another team's app", w=320, h=48, cls="dg-box dg-hot")
        + '<path class="dg-edge dg-hot" d="M500 58 V 104"/>'
        + '<text class="dg-hot" x="512" y="88">no dining room in between</text>',
        width=1000,
        height=340,
        label="Three rooms: the dining room (Streamlit, chapters 9 and 10) sends requests to the kitchen (the API, "
        "chapters 6 to 8), which queries the cold store (Parquet files, chapters 1 to 5). The units rule sits in the "
        "kitchen; the form repeats only its lower bound. curl, a script or another app can call the kitchen directly.",
    )
    _more = mo.md(
        """
    - **The payoff for splitting the tiers.** Change supplier, Parquet for DuckDB, and no guest
      notices. Rebuild the whole dining room, Streamlit for React, and the kitchen does not change one line.
    - **What a frontend does.** It writes an order slip, an HTTP request to a path, hands it through
      the hatch, and arranges whatever comes back so a human can decide something.
    - **Where the picture breaks.** A waiter cannot cook, but a frontend *does* compute: it sorts,
      formats, aggregates and draws every chart in the dashboard. So do not read this as "the frontend
      is dumb". Read it as **the frontend owns no rules**.
    - **The same rule, twice, on purpose.** The Streamlit form sets `min_value=1` for units sold; the API
      states `Units = Annotated[int, Field(ge=1, le=100_000)]`. The form does not even repeat the upper
      limit: only the kitchen knows it.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>A Frontend Is the Dining Room</h3>
      {_restaurant}
      <p class="vis-caption"><strong>The frontend owns no rules.</strong> Anyone can phone the kitchen directly,
      so a rule that lives only in the dining room is not a rule at all. The dining room may repeat a rule for
      politeness. Never instead.</p>
    </div>
                """
            ),
            mo.accordion({"Where the restaurant picture holds, and where it breaks": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, mo):
    # Ordered by the fit assistant's iteration-speed weight, fastest first.
    _frameworks = [
        ("Streamlit", "Py", "Dashboards, internal tools", "Fastest prototyping, simple widgets", "Less layout and state control in big apps"),
        ("Marimo", "Py", "Labs, teaching, analysis apps", "Reactive notebooks, data + UI in one loop", "Notebook-first, not for big web apps"),
        ("Dash", "Py", "Interactive analytics", "Plotly charts, component ecosystem", "Callbacks get tangled in big apps"),
        ("Flask", "Py+JS", "Custom web apps + APIs", "Full control, templates + APIs", "More setup, no built-in UI"),
        ("React", "JS", "Production web apps", "Flexible, modern UI patterns", "Needs a JS/TS stack and tooling"),
    ]
    _tiles = "".join(
        f'<div class="tile"><div class="tile-key">{_lang}</div><div class="tile-title">{_name}</div>'
        f"<p><strong>{_use}</strong></p><p>{_good}</p><p class=\"tile-bad\">{_bad}</p></div>"
        for _name, _lang, _use, _good, _bad in _frameworks
    )
    _tradeoff = diagram(
        '<text x="0" y="26" font-weight="700">faster iteration</text>'
        '<path class="dg-edge" d="M400 20 H 150"/>'
        '<text class="dg-muted" x="500" y="26" text-anchor="middle">the usual trade-off</text>'
        '<path class="dg-edge" d="M600 20 H 850"/>'
        '<text x="1000" y="26" text-anchor="end" font-weight="700">more UI control</text>',
        width=1000,
        height=40,
        label="The usual trade-off: the further left, the faster you iterate; the further right, the more UI control you get.",
    )
    mo.md(
        f"""
    <div class="section-card">
      <h3>Choosing a Frontend Stack</h3>
      {_tradeoff}
      <div class="tiles tier-presentation" style="grid-template-columns: repeat(5, 1fr); margin-top: 12px">{_tiles}</div>
      <p class="vis-caption">Py: Python only. JS: JavaScript, the language browsers run.
      Showcases: <a href="https://marimo.io/gallery">Marimo gallery</a> ·
      <a href="https://dash.gallery/Portal/">Dash gallery</a> ·
      <a href="https://react.dev/community">React community</a> ·
      <a href="https://flask.palletsprojects.com/en/stable/patterns/">Flask patterns</a></p>
    </div>
        """
    )
    return


@app.cell
def _(mo):
    fw_speed = mo.ui.slider(1, 5, value=5, label="Need fast iteration", show_value=True, debounce=True)
    fw_control = mo.ui.slider(1, 5, value=3, label="Need fine UI control", show_value=True, debounce=True)
    fw_js = mo.ui.slider(1, 5, value=2, label="Team JavaScript strength", show_value=True, debounce=True)
    _more = mo.md(
        """
    **JavaScript** is the programming language browsers run. Marimo, Streamlit and Dash let you stay
    in Python; React is written in JavaScript, and a Flask app needs some as soon as a page has to
    react. So a low score here is not a weakness, it just points at different tools.

    Each framework scores the three inputs with its own weights, and every weight row adds up to the
    same total (3.0), so no framework wins just by carrying more weight. For the three Python-native
    tools $j_f = 6 - j$: they get *more* attractive when the team knows *less* JavaScript. For Flask
    and React $j_f = j$. Heuristic only: validate it against real team constraints.
        """
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Framework Fit Assistant

    Set three numbers about **your team**, not about the frameworks.

    $$
    \\text{fit}_f = w^f_s \\cdot s + w^f_c \\cdot c + w^f_j \\cdot j_f
    \\qquad \\text{with} \\quad w^f_s + w^f_c + w^f_j = 3
    $$
                """
            ),
            mo.vstack([fw_speed, fw_control, fw_js], gap=0.4),
            mo.accordion({"How the score works": _more}),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return fw_control, fw_js, fw_speed


@app.cell
def _(TIER, alt, chart_or_table, fw_control, fw_js, fw_speed, pd, tier_chart):
    # Teaching heuristic, not a recommendation engine. Every weight row sums to 3.0,
    # so no framework wins just by carrying more weight than the others.
    _weights = {
        # framework:   (fast iteration, fine UI control, JavaScript), python_native
        "Marimo":      ((1.3, 0.5, 1.2), True),
        "Streamlit":   ((1.6, 0.4, 1.0), True),
        "Dash":        ((1.0, 1.0, 1.0), True),
        "Flask":       ((0.6, 1.6, 0.8), False),
        "React":       ((0.4, 1.4, 1.2), False),
    }
    # Python-native tools benefit from a team that knows LITTLE JavaScript, hence 6 - j.
    # Rounded like the table, so two scores that look equal are equal.
    _scores = {
        name: round(w_s * fw_speed.value + w_c * fw_control.value + w_j * (6 - fw_js.value if python_native else fw_js.value), 2)
        for name, ((w_s, w_c, w_j), python_native) in _weights.items()
    }
    _ranked = sorted(_scores.items(), key=lambda item: item[1], reverse=True)
    _top = [name for name, score in _ranked if score == _ranked[0][1]]
    _rows = [
        {"framework": name, "score": score, "weights (speed / control / JS)": " / ".join(map(str, _weights[name][0]))}
        for name, score in _ranked
    ]
    _df = pd.DataFrame(_rows)
    _df["best"] = _df["framework"].isin(_top)
    _bars = alt.Chart(_df).encode(
        y=alt.Y("framework:N", sort=None, title=None),
        x=alt.X("score:Q", title="teaching score (higher = better fit)", scale=alt.Scale(domain=[0, 15])),
        tooltip=["framework:N", "score:Q", "weights (speed / control / JS):N"],
    )
    _chart = (
        _bars.mark_bar(cornerRadiusEnd=4, size=28).encode(
            color=alt.condition("datum.best", alt.value(TIER["presentation"]), alt.value(TIER["muted"]))
        )
        + _bars.mark_text(align="left", dx=6).encode(text=alt.Text("score:Q", format=".2f"))
    ).properties(
        width="container",
        height=46 * len(_df),
        title=f"Best fit: {' / '.join(_top)}" + (" (a tie)" if len(_top) > 1 else ""),
    )
    chart_or_table(tier_chart(_chart, "presentation"), _rows, label="Teaching score (higher = better fit)")
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Frontends</h3>
      <details>
        <summary><strong>Q1:</strong> The Streamlit form already refuses 0 units. Why does the API check again?</summary>
        <p><strong>Answer:</strong> Anyone can phone the kitchen directly, with <code>curl</code>, a script or
        another team's app. A rule that lives only in the dining room is not a rule. The form repeats it for
        politeness: instant feedback, no round trip.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> The fit assistant says Streamlit. Is that the decision?</summary>
        <p><strong>Answer:</strong> No, it is a teaching heuristic with hand-picked weights. Check it against
        real constraints: how much layout and state control the product needs, who will maintain it, and
        what the team already knows.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 9 Conclusion

    - A frontend sends requests and arranges the answers. It owns no rules, so the API enforces
      every rule again.
    - Choose by your team's skills and how much UI control the product needs: fast iteration
      usually costs control.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Charts show patterns faster than tables, including patterns that are not there.

    $$
    \\text{what you plot} = \\text{signal} + \\text{noise}
    $$
    """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 10. Honest Charts (Signal vs Noise)"),
            chapter_intro(
                "presentation",
                "Which pattern is signal, and which is noise?",
                "The last decision of the whole stack: what a chart claims is what people believe.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    _more = mo.md(
        """
    - $\\alpha$ is the baseline level, the value of y where x is 0; $\\beta$ is the change in y for one
      unit of x. The margin of error is two standard errors, about 95% confidence.
    - **Slope 0, noise high:** the equation still prints confidently, and the ± tells you not to
      believe it. About 1 seed in 20 still clears the bar at slope 0: that is what 95% means.
    - **Noise 1.4, slope 0.4:** $R^2$ calls the line nearly useless, yet the slope is clearly real.
    - **More rows** shrink the ±, but they do not push $R^2$ up. $R^2$ measures how predictable single
      points are, not whether a trend exists.
        """
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Lab: Signal or Noise?

    The regression $y = \\alpha + \\beta x$ gives two separate answers:

    <div class="tiles tier-presentation">
      <div class="tile"><div class="tile-key">&beta; &plusmn; 2 SE</div><div class="tile-title">Trend: is there a slope?</div>
        <p>If the range includes 0, the data cannot tell the slope from zero.</p></div>
      <div class="tile"><div class="tile-key">R&sup2;</div><div class="tile-title">Fit: how close are the points?</div>
        <p>How well the line predicts a <em>single</em> point: the share of the spread it explains.</p></div>
    </div>

    **Try:** slope 0 with noise 5 · slope 0.4 with noise 1.4 · then more rows.
                """
            ),
            mo.accordion({"What each experiment shows": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    chart_slope = mo.ui.slider(-3.0, 3.0, step=0.2, value=1.2, label="True slope", show_value=True, debounce=True)
    chart_noise = mo.ui.slider(0.2, 5.0, step=0.2, value=1.4, label="Noise level", show_value=True, debounce=True)
    chart_rows = mo.ui.slider(100, 1000, step=100, value=600, label="Rows", show_value=True, debounce=True)
    chart_seed = mo.ui.slider(1, 999, value=21, label="Seed", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.hstack([chart_slope, chart_noise], widths="equal"),
            mo.hstack([chart_rows, chart_seed], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return chart_noise, chart_rows, chart_seed, chart_slope


@app.cell
def _(
    TIER,
    alt,
    chart_noise,
    chart_or_table,
    chart_rows,
    chart_seed,
    chart_slope,
    mo,
    pd,
    random,
    statistics,
    tier_chart,
):
    _rng = random.Random(chart_seed.value)
    _xs = [_rng.gauss(0, 1) for _ in range(chart_rows.value)]
    _ys = [chart_slope.value * _x + _rng.gauss(0, chart_noise.value) for _x in _xs]
    _beta, _alpha = statistics.linear_regression(_xs, _ys)
    _r2 = statistics.correlation(_xs, _ys) ** 2
    # Standard error of the slope: how far beta would wander if you drew the sample again.
    _se = ((1 - _r2) / (len(_xs) - 2)) ** 0.5 * statistics.stdev(_ys) / statistics.stdev(_xs)
    _nonzero = abs(_beta) > 2 * _se  # the ± range below excludes 0

    _trend = (
        "clearly **not zero**: the data rule out a flat line."
        if _nonzero
        else "**indistinguishable from zero**: this is noise, however confident the equation looks."
    )
    _fit = (
        "most of the spread: single points sit close to the line"
        if _r2 >= 0.5
        else "part of the spread: a trend with plenty of scatter around it"
        if _r2 >= 0.15
        else "almost none of the spread: single points are hard to predict"
    )
    _verdict = mo.md(
        f"$y = {_alpha:.2f} {_beta:+.2f}\\,x$ &nbsp; (you set the slope to {chart_slope.value:g})  \n"
        f"**Trend:** $\\beta = {_beta:.2f} \\pm {2 * _se:.2f}$, {_trend}  \n"
        f"**Fit:** $R^2 = {_r2:.2f}$, the line explains {_fit}."
    ).callout(kind="success" if _nonzero else "warn")

    # The fan: every line whose slope lies in beta ± 2 SE, pivoting on the centre of the data.
    _xbar, _ybar = statistics.fmean(_xs), statistics.fmean(_ys)
    _grid = [min(_xs) + (max(_xs) - min(_xs)) * _i / 40 for _i in range(41)]
    _ends = [((_beta - 2 * _se) * (_g - _xbar), (_beta + 2 * _se) * (_g - _xbar)) for _g in _grid]
    _fan = pd.DataFrame(
        {
            "x": _grid,
            "low": [_ybar + min(_e) for _e in _ends],
            "high": [_ybar + max(_e) for _e in _ends],
            "flat": _ybar,
        }
    )
    _x = alt.X("x:Q").axis(tickCount=8)
    _points = (
        alt.Chart(pd.DataFrame({"x": _xs, "y": _ys}))
        .mark_circle(size=36, opacity=0.45, color=TIER["muted"])
        .encode(x=_x, y="y:Q")
    )
    _band = alt.Chart(_fan).mark_area(opacity=0.25, color=TIER["presentation"]).encode(x=_x, y=alt.Y("low:Q", title="y"), y2="high:Q")
    _flat = alt.Chart(_fan).mark_line(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"]).encode(x=_x, y=alt.Y("flat:Q", title="y"))
    _line = _points.transform_regression("x", "y").mark_line(color=TIER["presentation"], strokeWidth=4)
    _chart = (_band + _points + _flat + _line).properties(width="container", height=320)
    _summary = [
        {"quantity": "slope you set", "value": chart_slope.value},
        {"quantity": "fitted slope β", "value": round(_beta, 3)},
        {"quantity": "margin of error (2 SE)", "value": round(2 * _se, 3)},
        {"quantity": "intercept α", "value": round(_alpha, 3)},
        {"quantity": "R²", "value": round(_r2, 3)},
        {"quantity": "rows (n)", "value": len(_xs)},
    ]
    mo.vstack(
        [
            _verdict,
            chart_or_table(tier_chart(_chart, "presentation"), _summary, label="Regression summary"),
            mo.md(
                '<p class="vis-caption">Orange fan: every slope inside &beta; &plusmn; 2 SE. If the dashed flat '
                "line fits inside it, the data cannot rule out zero.</p>"
            ),
        ],
        gap=0.6,
    )
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
        inline=True,
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: Three Ways to Change the Finding Without Changing the Data

    One question of the repo's real 3,360 sales: **does spending more make customers happier?**
    Every view uses every sale; only the way we look changes.
                """
            ),
            honest_view,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (honest_view,)


@app.cell
def _(SEED_DIR, TIER, alt, chart_or_table, duckdb, honest_view, mo, tier_chart):
    _con = duckdb.connect()
    _con.execute(
        f"""
        CREATE VIEW sales AS
        SELECT c.name AS category, p.name AS product, date_trunc('month', s.sale_date) AS month,
               s.total_price AS x, s.customer_rating AS y
        FROM '{(SEED_DIR / "sales.parquet").as_posix()}' s
        JOIN '{(SEED_DIR / "products.parquet").as_posix()}' p USING (product_id)
        JOIN '{(SEED_DIR / "categories.parquet").as_posix()}' c USING (category_id)
        """
    )

    def _measure(label, source="sales", *params):
        # DuckDB fits the line itself: regr_slope and regr_r2 are ordinary least squares.
        _n, _slope, _r2 = _con.execute(
            f"SELECT count(*), regr_slope(y, x) * 10000, regr_r2(y, x) FROM {source}", params
        ).fetchone()
        return {"what we plotted": label, "dots (n)": _n, "slope (rating per CHF 10k)": round(_slope, 3), "R²": round(_r2, 3)}

    def _averaged(group_by):
        return f"(SELECT avg(x) AS x, avg(y) AS y FROM sales GROUP BY {group_by})"

    if honest_view.value.startswith("A"):
        _views = [
            ("one dot per sale", "sales", ()),
            ("per product per month", _averaged("product, month"), ()),
            ("per category per month", _averaged("category, month"), ()),
            ("per category", _averaged("category"), ()),
        ]
    elif honest_view.value.startswith("B"):
        _cats = [_c for (_c,) in _con.execute("SELECT DISTINCT category FROM sales ORDER BY 1").fetchall()]
        _views = [("all sales pooled", "sales", ())] + [(f"only {_c}", "sales WHERE category = ?", (_c,)) for _c in _cats]
    else:
        _views = [("all sales", "sales", ()), ("every sale except Services", "sales WHERE category <> 'Services'", ())]
    _rows = [_measure(_label, _source, *_params) for _label, _source, _params in _views]

    def _panel(i, row, source, params):
        """Small multiple i: the dots and their least-squares line, red when it slopes down."""
        df = _con.execute(f"SELECT x, y FROM {source}", params).df()
        dots = (
            alt.Chart(df)
            .mark_circle(size=18 if len(df) > 1000 else 60, opacity=0.15 if len(df) > 1000 else 0.7, color=TIER["muted"])
            .encode(
                x=alt.X("x:Q", title="CHF spent", axis=alt.Axis(format="~s", tickCount=4)),
                y=alt.Y("y:Q", title="rating" if i == 0 else None, scale=alt.Scale(domain=[1, 5])),
            )
        )
        slope = row["slope (rating per CHF 10k)"]
        line = dots.transform_regression("x", "y").mark_line(
            strokeWidth=4, color=TIER["hot"] if slope < 0 else TIER["presentation"]
        )
        return (dots + line).properties(
            width=190 if len(_views) > 2 else 430,
            height=230,
            title=alt.TitleParams(
                row["what we plotted"],
                subtitle=f"n {row['dots (n)']:,} · R² {row['R²']:.2f} · slope {slope:+.2f}",
                fontSize=15,
                subtitleFontSize=14,
            ),
        )

    _panels = alt.hconcat(*[_panel(_i, _row, _view[1], _view[2]) for _i, (_row, _view) in enumerate(zip(_rows, _views, strict=True))])

    if honest_view.value.startswith("A"):
        _lesson = (
            f"**$R^2$ climbed from {_rows[0]['R²']:.2f} to {_rows[-1]['R²']:.2f} and no new information entered "
            f"the room.** The last panel has {_rows[-1]['dots (n)']} dots and a story you could put on a slide."
        )
        _more = mo.md(
            f"""
    Every panel is the same {_rows[0]["dots (n)"]:,} sales. Averaging dots together does not
    strengthen a relationship, it **deletes the disagreement** that was telling you the
    relationship is weak.

    This is why a goodness-of-fit number is meaningless without its sample size. Always read $R^2$
    and $n$ together, which is why every panel prints both. The dashboard's *What goes with a good
    rating?* chart offers the same choice: compare *Sale* with *Category (monthly)*.
            """
        )
    elif honest_view.value.startswith("B"):
        _down = [_c for _c, _row in zip(_cats, _rows[1:], strict=True) if _row["slope (rating per CHF 10k)"] < 0]
        _up = [_c for _c in _cats if _c not in _down]
        _lesson = (
            f"**The pooled line does not describe the groups.** Pooled, the slope is positive. Inside "
            f"{' and '.join(_down)} it points the other way (red); only {' and '.join(_up)} still slopes upward."
        )
        _more = mo.md(
            f"""
    The upward pooled line is mostly describing the gaps **between** categories: Services happen to
    be expensive and well rated, while Hardware is mid-priced and rated worst.

    When a trend reverses inside *every* group it was built from, that is Simpson's paradox. Here it
    reverses in {len(_down)} of {len(_cats)} groups: not the textbook case, but the same trap. Three
    groups' worth of difference, wearing three thousand dots' worth of authority.
            """
        )
    else:
        _lesson = (
            "**One group out of three decided the direction of the answer.** Remove Services and the slope "
            "flips sign, and $R^2$ barely moves."
        )
        _more = mo.md(
            """
    $R^2$ tells you how tightly the dots hug the line. It never tells you whether the line was the
    right line to draw, and it will not warn you when one group is carrying the entire result.
            """
        )

    mo.vstack(
        [
            chart_or_table(
                tier_chart(_panels, "presentation"), _rows, label=f"Same {_rows[0]['dots (n)']:,} sales, same question"
            ),
            mo.md(_lesson).callout(kind="warn"),
            mo.accordion(
                {
                    "Why it happens": mo.vstack(
                        [
                            _more,
                            mo.md(
                                "*The lab reads the seed files directly, a notebook shortcut past the API; "
                                "the dashboard asks the API.*"
                            ),
                        ]
                    )
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Honest Charts</h3>
      <details>
        <summary><strong>Q1:</strong> A slide shows a tight line and a high R². What do you ask first?</summary>
        <p><strong>Answer:</strong> What one dot is, and how many there are. View A turns the same sales from a
        weak per-sale relationship into a tight line of category averages, with no new information.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> When is it fair to drop a category?</summary>
        <p><strong>Answer:</strong> When the reason is stated before you look at the result (a different
        business, a data error), and both answers are shown. Dropping a group because it spoils the story is
        exactly how view C reverses the finding.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 10 Conclusion

    - Read a slope with its ± range, and $R^2$ with its $n$.
    - $R^2$ says how close single points sit, not whether a trend exists.
    - Averaging, splitting or dropping a group can reverse a finding without changing one row: say which you did.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo, tier_map):
    _more = mo.md(
        """
    Move the sales from Parquet files into a DuckDB database and only the storage code in
    `sw03_demo_api.py` changes (the file names in `TABLES` and `reset`, `read`, `write`), not one
    endpoint. Swap Streamlit for React and neither lower tier notices.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Wrap-up: the Map, Filled In</h3>
      {tier_map}
      <p class="vis-caption">Each tier only talks to its neighbour, so any one can be replaced without
      rewriting the others.</p>
      <div class="tiles">
        <div class="tile"><div class="tile-key">1</div><div class="tile-title">Correctness</div>
          <p>Designed in, not bought with a tool. Get it first.</p></div>
        <div class="tile"><div class="tile-key">2</div><div class="tile-title">Performance</div>
          <p>Then make it fast.</p></div>
        <div class="tile"><div class="tile-key">3</div><div class="tile-title">Usability</div>
          <p>Then make it clear, and honest.</p></div>
      </div>
    </div>
                """
            ),
            mo.accordion({"What replacing one tier would touch": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("## Some Useful Links"),
            mo.md("""
    <div class="tiles">
      <div class="tile tier-data"><div class="tile-title">Data tier</div>
        <p><a href="https://duckdb.org/docs">DuckDB</a> · <a href="https://www.sqlite.org/docs.html">SQLite</a> ·
        <a href="https://parquet.apache.org">Apache&nbsp;Parquet</a> · <a href="https://arrow.apache.org">Arrow</a> ·
        <a href="https://avro.apache.org">Avro</a></p></div>
      <div class="tile tier-logic"><div class="tile-title">Logic tier</div>
        <p><a href="https://fastapi.tiangolo.com">FastAPI</a> · <a href="https://docs.pydantic.dev">Pydantic</a> ·
        <a href="https://spec.openapis.org/oas/latest.html">OpenAPI&nbsp;spec</a> ·
        <a href="https://www.rfc-editor.org/rfc/rfc9110.html">HTTP semantics, RFC&nbsp;9110</a> ·
        <a href="https://en.wikipedia.org/wiki/List_of_HTTP_status_codes">HTTP&nbsp;status&nbsp;codes</a></p></div>
      <div class="tile tier-presentation"><div class="tile-title">Presentation tier</div>
        <p><a href="https://docs.marimo.io">marimo&nbsp;docs</a> · <a href="https://marimo.io/gallery">gallery</a> ·
        <a href="https://docs.streamlit.io">Streamlit</a> · <a href="https://dash.gallery/Portal/">Dash&nbsp;gallery</a> ·
        <a href="https://react.dev/community">React&nbsp;community</a> ·
        <a href="https://flask.palletsprojects.com/en/stable/patterns/">Flask&nbsp;patterns</a></p></div>
    </div>
            """),
        ],
        gap=1,
    )
    return


if __name__ == "__main__":
    app.run()
