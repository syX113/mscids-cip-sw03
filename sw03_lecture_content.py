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
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 2. Serialization & Deserialization Benchmarks"),
            chapter_intro(
                "data",
                "Which format gives the best trade-off for this workload: this data, these queries?",
                "Chapter 1 made the writes correct; now we choose what those bytes look like.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, fastavro, html, io, json, mo):
    _record = {"sale_id": 1, "sale_date": "2024-03-07", "total_price": 4034.91}
    # The bytes in the middle are the real start of this record's JSON.
    _hex = json.dumps(_record).encode()[:24].hex(" ").upper()

    def _object(x, title, cls):
        lines = "".join(
            f'<text x="{x + 125}" y="{104 + _i * 26}" text-anchor="middle">{_k} <tspan font-weight="700">{_v}</tspan></text>'
            for _i, (_k, _v) in enumerate(_record.items())
        )
        return (
            f'<rect class="{cls}" x="{x}" y="30" width="250" height="140" rx="12"/>'
            f'<text x="{x + 125}" y="64" text-anchor="middle" font-weight="700">{title}</text>{lines}'
        )

    def _arrow(x, verb, word):
        return (
            f'<path class="dg-edge dg-flow" d="M{x} 100 H {x + 122}"/>'
            f'<text x="{x + 60}" y="86" text-anchor="middle" font-weight="700">{verb}</text>'
            f'<text class="dg-muted" x="{x + 60}" y="126" text-anchor="middle">{word}</text>'
        )

    _pipeline = diagram(
        _object(0, "Python object", "dg-tier")
        + _arrow(258, "serialize", "write")
        + '<rect class="dg-box" x="390" y="30" width="260" height="140" rx="12"/>'
        + '<text x="520" y="64" text-anchor="middle" font-weight="700">bytes</text>'
        + "".join(
            f'<text x="520" y="{104 + _i * 26}" text-anchor="middle" font-family="monospace">{_hex[_i * 24 : _i * 24 + 23]}</text>'
            for _i in range(3)
        )
        + _arrow(660, "deserialize", "read")
        + _object(790, "Python object", "dg-tier")
        + '<text class="dg-muted" x="520" y="200" text-anchor="middle">'
        "on disk or on the wire: files, API payloads, queues, caches</text>",
        width=1040,
        height=212,
        label="A Python record is serialized into bytes for a file or the network, and deserialized back into a Python record.",
        tier="data",
    )

    # The pre-printed form refuses an answer that does not fit its box: the real error from the Avro writer.
    try:
        fastavro.writer(io.BytesIO(), {"type": "record", "name": "Sale", "fields": [{"name": "total_price", "type": "double"}]}, [{"total_price": "about forty"}])
        _refusal = "accepted"
    except (TypeError, ValueError) as _exc:
        _refusal = f"{type(_exc).__name__}: {str(_exc).split(': ')[0]}"

    def _sheet(y, sale_id, date, price):
        return (
            f'<rect class="dg-box" x="0" y="{y}" width="470" height="70" rx="8"/>'
            f'<text x="18" y="{y + 28}" font-family="monospace">{{"sale_id": {sale_id}, "sale_date": "{date}",</text>'
            f'<text x="18" y="{y + 54}" font-family="monospace"> "total_price": {price}}}</text>'
        )

    _form_cells = [("sale_id: int", 130), ("sale_date: date", 170), ("total_price: double", 200)]

    def _form_row(y, values, cls):
        x, parts = 540, []
        for (_, w), value in zip(_form_cells, values, strict=True):
            parts.append(box(x, y, value, w=w - 8, h=40, cls=cls))
            x += w
        return "".join(parts)

    _forms = diagram(
        '<text x="0" y="22" font-weight="700">JSON: longhand on blank paper</text>'
        + _sheet(40, 1, "2024-03-07", "4034.91")
        + _sheet(124, 2, "2024-03-08", '<tspan class="dg-hot">"about forty"</tspan>')
        + '<text class="dg-muted" x="0" y="222">every sheet writes the labels out again</text>'
        + '<text class="dg-hot" x="0" y="248">and nothing stops "about forty" in the price box</text>'
        + '<text x="540" y="22" font-weight="700">Avro: a pre-printed form</text>'
        + _form_row(40, [_label for _label, _ in _form_cells], "dg-tier")
        + _form_row(92, ["1", "2024-03-07", "4034.91"], "dg-box")
        + _form_row(140, ["2", "2024-03-08", '<tspan class="dg-hot" text-decoration="line-through">about forty</tspan>'], "dg-box")
        + '<text class="dg-muted" x="540" y="222">labels printed once; sheets hold only answers</text>'
        + f'<text class="dg-hot" x="540" y="248" font-size="15">refused: {html.escape(_refusal, quote=False)}</text>'
        + '<text x="0" y="306" font-weight="700">The form comes back:</text>'
        + '<g class="tier-data"><rect class="dg-tier" x="190" y="282" width="250" height="40" rx="12"/>'
        '<text x="315" y="307" text-anchor="middle">5 · DuckDB <tspan font-weight="700">guesses</tspan> it</text></g>'
        + '<g class="tier-logic"><rect class="dg-tier" x="456" y="282" width="270" height="40" rx="12"/>'
        '<text x="591" y="307" text-anchor="middle">7 · Pydantic <tspan font-weight="700">enforces</tspan> it</text>'
        '<rect class="dg-tier" x="742" y="282" width="270" height="40" rx="12"/>'
        '<text x="877" y="307" text-anchor="middle">8 · FastAPI <tspan font-weight="700">publishes</tspan> it</text></g>',
        width=1040,
        height=330,
        label="Left: JSON sheets repeat every label, and one has 'about forty' in the price box. Right: an Avro form "
        "prints the labels once, each row holds only the answers, and the writer refuses 'about forty'. "
        "The same form returns in chapters 5, 7 and 8.",
        tier="data",
    )
    _breaks = mo.md(
        """
    - A paper form is inseparable from its answers: true for Avro, which stores the form in the
      file, and false for JSON and CSV. There the form exists only in the mind of whoever reads the
      file, which is why two teams can disagree about what the same sheet means. That is the reason
      chapter 7 exists.
    - **Schema evolution** is what happens when the office adds a box to the form: do last year's
      sheets, printed on the old form, still get read? The last lab of this chapter tests exactly that.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Serialization = Bytes on Disk (or Wire)</h3>
      {_pipeline}
    </div>
                """
            ),
            mo.md(
                f"""
    <div class="section-card">
      <h3>The Schema Is the Blank Form</h3>
      <p>Not the answers, the printed boxes: which fields, in what order, what kind of thing goes in each.</p>
      {_forms}
    </div>
                """
            ),
            mo.accordion({"Where the picture breaks, and what schema evolution means": _breaks}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, mo):
    def _envelope(x, y, w, h):
        return (
            f'<rect class="dg-box" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>'
            f'<path d="M{x} {y} L{x + w / 2:.0f} {y + h * 0.6:.0f} L{x + w} {y}" fill="none" stroke="currentColor" opacity="0.5"/>'
        )

    # Letters handed in through the day; the van leaves with all of them at 22:00.
    _hours = [8, 10, 12, 14, 16, 18, 20]

    def _at(hour):
        return 60 + (hour - 8) * 60

    _post = diagram(
        '<text x="0" y="24" font-weight="700">Latency: how long one thing takes</text>'
        + _envelope(10, 60, 90, 60)
        + '<path class="dg-edge" d="M112 90 H 330"/>'
        + '<text x="220" y="78" text-anchor="middle" font-weight="700">2 days</text>'
        + box(338, 66, "Vienna", w=110, h=48)
        + '<text x="560" y="24" font-weight="700">Throughput: how much gets through per night</text>'
        + '<rect class="dg-tier" x="570" y="46" width="230" height="78" rx="10"/>'
        + '<text x="685" y="91" text-anchor="middle" font-weight="700">40,000 letters</text>'
        + '<path class="dg-tier" d="M800 72 H 846 L 872 98 V 124 H 800 Z"/>'
        + '<circle class="dg-box" cx="620" cy="128" r="14"/><circle class="dg-box" cx="836" cy="128" r="14"/>'
        # the trade: the van waits for the last letter, so the first one waits longest
        + '<text x="0" y="214" font-weight="700">They trade:</text>'
        + f'<path d="M{_at(8)} 262 H {_at(22) - 50}" stroke="currentColor" opacity="0.35" stroke-width="2"/>'
        + "".join(
            _envelope(_at(_h) - 14, 236, 28, 20)
            + f'<text class="dg-muted" x="{_at(_h)}" y="284" text-anchor="middle">{_h:02d}:00</text>'
            for _h in _hours
        )
        + f'<rect class="dg-tier" x="{_at(22) - 50}" y="226" width="100" height="40" rx="10"/>'
        + f'<text x="{_at(22)}" y="251" text-anchor="middle">van 22:00</text>'
        + f'<path class="dg-edge dg-hot" d="M{_at(8)} 304 H {_at(22) - 54}"/>'
        + f'<text class="dg-hot" x="{(_at(8) + _at(22)) / 2:.0f}" y="330" text-anchor="middle">'
        "the first letter waits 14 hours</text>",
        width=1040,
        height=344,
        label="Latency: one letter takes two days to Vienna. Throughput: a van carries 40,000 letters a night. "
        "Letters handed in from 08:00 all wait for the 22:00 van, so filling the van raises throughput and "
        "makes the first letter wait 14 hours.",
        tier="data",
    )
    _more = mo.md(
        """
    - A container ship has appalling latency and colossal throughput.
    - In the benchmark, one round trip is a file written and read back, and what gets through is
      records, counted like letters rather than by the weight of the paper.
    - *Sometimes you get both*, by making the letters smaller. That is what chapter 4 is for.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Latency vs Throughput</h3>
      {_post}
      <p class="vis-caption"><strong>Filling the van raises throughput and hurts the first letter's latency.</strong>
      Ask which one "fast" means.</p>
    </div>
                """
            ),
            mo.md(
                """
    In the benchmark below:
    $\\text{Latency} = \\text{write time} + \\text{read time}$ and
    $\\text{Throughput} = \\text{rows written} / \\text{write time}$.
                """
            ),
            mo.accordion({"Container ships, and how to get both": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    _criteria = mo.md(
        """
    - **Speed**: how long writing and reading take
    - **Size**: how many bytes hit the disk
    - **Interop**: which languages and tools can read it
    - **Type fidelity**: do dates and codes come back as dates and codes?
    - **Schema evolution**: do old files survive a new field?
    - **Safety**: can loading a file run someone else's code?
        """
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Format Quick Reference

    **Compare on:** speed · size · interop · type fidelity · schema evolution · safety

    <div class="tiles tier-data" style="grid-template-columns: repeat(5, 1fr)">
      <div class="tile"><div class="tile-key">JSON</div><div class="tile-title">Text, row by row</div>
        <p>JSON and CSV: every tool reads them.</p></div>
      <div class="tile"><div class="tile-key">Avro</div><div class="tile-title">Rows + a schema</div>
        <p>Event streams.</p></div>
      <div class="tile"><div class="tile-key">Arrow</div><div class="tile-title">Columns in memory</div>
        <p>Arrow / Feather: hand-over between tools.</p></div>
      <div class="tile"><div class="tile-key">Parquet</div><div class="tile-title">Columns on disk</div>
        <p>Analytics files.</p></div>
      <div class="tile"><div class="tile-key">Pickle</div><div class="tile-title">Python objects</div>
        <p class="tile-bad">Loading it can run code.</p></div>
    </div>
                """
            ),
            mo.accordion({"What each criterion asks": _criteria}),
        ],
        gap=0.6,
    )
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
    mo.vstack(
        [mo.md("### Mini-lab: Format Decision Assistant"), mo.hstack([format_use_case, format_priority], justify="start", gap=2)],
        gap=0.5,
    ).callout(kind="neutral")
    return format_priority, format_use_case


@app.cell
def _(format_priority, format_use_case, mo):
    # one row per use case, one entry per priority in the order of the priority dropdown
    _recommendations = {
        "Public API payload": ["JSON", "JSON, or MessagePack if both sides speak it", "Compressed JSON or a binary protocol", "JSON with strict schema validation"],
        "Internal Python checkpoint": ["Parquet / Arrow", "Pickle (trusted data only)", "Parquet or compressed Pickle", "Parquet / JSON, no untrusted Pickle"],
        "Analytics table": ["Parquet", "Parquet or Arrow", "Parquet + zstd / snappy", "Parquet with schema checks"],
        "Streaming event log": ["Avro / JSON", "Avro", "Avro with compression", "Avro + schema registry"],
    }
    _priorities = list(format_priority.options)
    _pick = (format_use_case.value, _priorities.index(format_priority.value))
    def _cell(text, chosen):
        """A grey grid cell; the chosen use case, priority and recommendation stand out as tiles."""
        return f'<div class="tile"><strong>{text}</strong></div>' if chosen else f'<div class="focus-item">{text}</div>'

    _grid = [_cell("", False)] + [_cell(f"<strong>{_p}</strong>", _p == format_priority.value) for _p in _priorities]
    for _use, _row in _recommendations.items():
        _grid.append(_cell(f"<strong>{_use}</strong>", _use == _pick[0]))
        _grid += [_cell(_r, (_use, _i) == _pick) for _i, _r in enumerate(_row)]
    mo.md(
        f"""
    <div class="section-card tier-data">
      <div style="display: grid; grid-template-columns: 190px repeat(4, 1fr); gap: 6px; font-size: 15px; line-height: 1.3">
        {"".join(_grid)}
      </div>
      <p class="vis-caption">Starting point: <strong>{_recommendations[_pick[0]][_pick[1]]}</strong>.
      A default to benchmark, not a rule.</p>
    </div>
        """
    )
    return


@app.cell
def _(mo):
    serial_rows = mo.ui.slider(200, 3000, step=200, value=800, label="Rows", show_value=True)
    serial_cols = mo.ui.slider(2, 8, value=5, label="Metric columns", show_value=True)
    run_serial = mo.ui.run_button(label="Run serialization benchmark", kind="success")
    mo.vstack(
        [
            mo.md("### Benchmark: Six Formats, the Same Records"),
            mo.hstack([serial_rows, serial_cols], widths="equal"),
            run_serial,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return run_serial, serial_cols, serial_rows


@app.cell
def _(
    Path,
    TIER,
    alt,
    best_seconds,
    chart_or_table,
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
    tier_chart,
):
    mo.stop(
        not run_serial.value,
        mo.md(
            "**Predict first:** is the smallest file also the fastest? Then click **Run serialization benchmark**."
        ).callout(kind="neutral"),
    )

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

    _df = pd.DataFrame(_rows)
    _df["unsafe"] = _df["format"].str.startswith("Pickle")
    # Two points close together: the smaller file's label goes to the left, so the labels do not collide.
    _dx, _dy = 0.15 * _df["size (KB)"].max(), 0.08 * _df["latency (ms)"].max()
    _df["left"] = [
        any(
            _o is not _r and 0 <= _o["size (KB)"] - _r["size (KB)"] < _dx and abs(_o["latency (ms)"] - _r["latency (ms)"]) < _dy
            for _o in _rows
        )
        for _r in _rows
    ]
    _color = alt.condition("datum.unsafe", alt.value(TIER["hot"]), alt.value(TIER["data"]))
    _tooltip = list(_rows[0])
    _base = alt.Chart(_df).encode(
        x=alt.X("size (KB):Q", title="file size (KB)", scale=alt.Scale(zero=True)),
        y=alt.Y("latency (ms):Q", title="write + read (ms)", scale=alt.Scale(zero=True)),
        tooltip=_tooltip,
    )
    _scatter = (
        _base.mark_circle(size=260, opacity=1).encode(color=_color)
        + _base.transform_filter("!datum.left").mark_text(align="left", dx=14).encode(text="format:N")
        + _base.transform_filter("datum.left").mark_text(align="right", dx=-14).encode(text="format:N")
    ).properties(width=470, height=300, title="Size vs latency: the bottom-left corner wins")
    _speed = alt.Chart(_df).encode(
        y=alt.Y("format:N", sort="-x", title=None),
        x=alt.X(
            "rows/s written:Q",
            axis=None,
            scale=alt.Scale(domain=[0, _df["rows/s written"].max() * 1.3]),
        ),
        tooltip=_tooltip,
    )
    _throughput = (
        _speed.mark_bar(cornerRadiusEnd=4).encode(color=_color)
        + _speed.mark_text(align="left", dx=6).encode(text=alt.Text("rows/s written:Q", format=".2s"))
    ).properties(width=250, height=300, title="Throughput: rows written per second")

    mo.vstack(
        [
            chart_or_table(
                tier_chart(alt.hconcat(_scatter, _throughput, spacing=40), "data"),
                _rows,
                label="Serialization benchmark (best of 3)",
            ),
            mo.md("**Do latency and throughput rank the formats the same way?**"),
            mo.accordion(
                {
                    "The records being saved, and why the reads are not quite like for like": mo.vstack(
                        [
                            static_table(_records[:3], label="Sample records"),
                            mo.md(
                                "Numbers vary by machine and caching, so compare the formats with each other, not with "
                                "another laptop. Arrow and Parquet stop at a columnar table without building Python "
                                "objects, and CSV hands back strings it never converts to numbers."
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
def _(Path, SALES_SEED, box, diagram, mo, pd, tempfile):
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

    # One row per column: the type written, then the type each file hands back, ticked where it matches.
    _xs = {"wrote": 190, "back from CSV": 470, "back from Parquet": 750}
    _parts = [f'<text x="{_x + 130}" y="22" text-anchor="middle" font-weight="700">{_name}</text>' for _name, _x in _xs.items()]
    for _i, _c in enumerate(_src.columns):
        _y = 40 + _i * 56
        _wrote = str(_src[_c].dtype)
        _parts.append(f'<text x="0" y="{_y + 27}" font-family="monospace" font-weight="700">{_c}</text>')
        _parts.append(box(_xs["wrote"], _y, _wrote, w=260))
        for _x, _back_df in ((_xs["back from CSV"], _from_csv), (_xs["back from Parquet"], _from_pq)):
            _back = str(_back_df[_c].dtype)
            if _back == _wrote:
                _parts.append(box(_x, _y, f"&#10003; {_back}", w=260, cls="dg-box dg-ok"))
            else:
                _parts.append(box(_x, _y, f'<tspan class="dg-hot">&#10007; {_back}</tspan>', w=260, cls="dg-box dg-hot"))
    _types = diagram(
        "".join(_parts),
        width=1010,
        height=270,
        label="The same four columns written to CSV and to Parquet and read back. Parquet returns every type it was given; "
        "CSV returns sale_date as text and store_code as a whole number.",
    )

    def _span(_df):
        try:
            return str(_df["sale_date"].max() - _df["sale_date"].min())
        except TypeError as _exc:
            return f"TypeError: {_exc}"

    def _ask(name, df, kind):
        return mo.md(
            f"""
    **Ask the {name} copy**

    - How long did sales run? `{_span(df)}`
    - First three store codes: `{df["store_code"].head(3).tolist()}`
            """
        ).callout(kind=kind)

    _why = mo.md(
        """
    Open the CSV in a text editor and the date is right there: `2024-03-07`. The bytes did not lose the
    date. They lost **the note saying it was a date**, and that note is what your analysis was standing
    on. Parquet stores the date as a plain number and keeps the note in its schema, which is why it came
    back as `datetime64`.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Same 500 Sales, Written Two Ways and Read Back</h3>
      {_types}
    </div>
                """
            ),
            mo.hstack([_ask("Parquet", _from_pq, "success"), _ask("CSV", _from_csv, "danger")], widths="equal", gap=1),
            mo.md(
                "The date failure shouted; the store codes failed silently. **That one ends up in a report.**"
            ).callout(kind="warn"),
            mo.accordion({"What the CSV actually lost": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(csv, diagram, fastavro, html, io, mo):
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

    def _card(x, y, w, title, sub, cls="dg-box"):
        return (
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="64" rx="12"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 26}" text-anchor="middle" font-weight="700">{html.escape(title, quote=False)}</text>'
            f'<text class="dg-muted" x="{x + w / 2:.0f}" y="{y + 50}" text-anchor="middle">{sub}</text>'
        )

    def _fields(record):
        return " · ".join(f"{_k} {_v}" for _k, _v in record.items())

    _lanes = [
        ("last year's Avro file", "old form", "this year's code", "new form: + channel",
         _fields(_old_by_new[0]), "&#10003; the reader filled in the default", "dg-box dg-ok"),
        ("this year's Avro file", "new form", "the old program", "old form",
         _fields(_new_by_old[0]), "&#10003; the extra box is skipped", "dg-box dg-ok"),
        ("last year's CSV file", "no form inside", "this year's code", "expects channel",
         _csv_result, "&#10007; only fix: change every reader", "dg-box dg-hot"),
    ]
    _parts = [
        '<text x="120" y="20" text-anchor="middle" font-weight="700">the file</text>'
        '<text x="390" y="20" text-anchor="middle" font-weight="700">read by</text>'
        '<text x="790" y="20" text-anchor="middle" font-weight="700">what comes back</text>'
    ]
    for _i, (_file, _file_sub, _reader, _reader_sub, _result, _verdict, _cls) in enumerate(_lanes):
        _y = 36 + _i * 84
        _parts += [
            _card(0, _y, 240, _file, _file_sub),
            f'<path class="dg-edge" d="M246 {_y + 32} H 284"/>',
            _card(290, _y, 200, _reader, _reader_sub, "dg-tier"),
            f'<path class="dg-edge" d="M496 {_y + 32} H 534"/>',
            _card(540, _y, 500, _result, _verdict, _cls),
        ]
    _lanes_svg = diagram(
        "".join(_parts),
        width=1040,
        height=290,
        label="Avro: last year's file read by this year's code gets the default channel; this year's file read by the "
        "old program skips the channel. CSV: last year's file read by this year's code raises a KeyError.",
        tier="data",
    )
    mo.md(
        f"""
    <div class="section-card">
      <h3>Schema Evolution: the Office Adds a Box to the Form</h3>
      <p>A <code>channel</code> box is added (default <code>in-store</code>), while old files and one old
      program live on.</p>
      {_lanes_svg}
      <p class="vis-caption">CSV ships without the form, so the agreement lives only in someone's memory.</p>
    </div>
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Serialization Choices</h3>
      <details>
        <summary><strong>Q1:</strong> JSON, Avro or Parquet: how do you choose?</summary>
        <p><strong>Answer:</strong> JSON for the widest tool support, Avro for event streams whose schema
        changes, Parquet for analytics.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> Who can send this data, and can they be malicious?</summary>
        <p><strong>Answer:</strong> If so, never unpickle it, and validate it strictly.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Where should size vs speed trade‑offs be measured?</summary>
        <p><strong>Answer:</strong> In staging, then on a canary: the new format serving a small share of
        real traffic.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 2 Conclusion

    - Formats trade speed, size, interop and safety: benchmark on your workload.
    - CSV keeps values, drops types (`str` dates, `007` as `7`); Parquet and Avro carry the schema.
    - Avro reader defaults let old files and new code agree.
    - Never load Pickle from a source you do not trust.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Next: **lay the bytes out** on disk, by row or by column.

    $$
    \\text{read work} \\propto \\text{rows read} \\times \\text{columns touched}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 3. Column-Based vs Row-Based Storage"),
            chapter_intro(
                "data",
                "Is read work spent on data the query does not need?",
                "Chapter 2 picked a format; now we choose how its bytes are arranged on disk.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    ch3_query = mo.ui.radio(
        options=["Show me sale 2,914", "Total revenue", "Revenue in January 2026"],
        value="Total revenue",
        label="Ask the shop:",
        inline=True,
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Row Store vs Column Store: the Shoebox and the Ledger

    A shop keeps its sales twice: a **shoebox** of till receipts, one slip per sale, and a **ledger**
    with one page per field. Pick a question and watch what each one has to read.
                """
            ),
            ch3_query,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (ch3_query,)


@app.cell
def _(ch3_query, diagram, mo):
    _fields = ["id", "date", "product", "country", "units", "price", "rating"]
    _sales = list(range(2911, 2919))
    # (sales the question needs, fields it needs); a filter on the date needs the date of every sale
    _rows, _cols = {
        "Show me sale 2,914": ([2914], _fields),
        "Total revenue": (_sales, ["price"]),
        "Revenue in January 2026": (_sales, ["date", "price"]),
    }[ch3_query.value]
    _cls = {"used": "dg-tier", "wasted": "dg-hot", "idle": "dg-box"}

    def _cell(x, y, state):
        opacity = ' opacity="0.45"' if state == "idle" else ""
        return f'<rect class="{_cls[state]}" x="{x}" y="{y}" width="52" height="26" rx="4"{opacity}/>'

    # The shoebox: one slip per sale. A slip is picked up whole, so every field on it is read.
    _box = ['<text x="0" y="20" font-weight="700">Shoebox: row layout</text>']
    _box += [f'<text class="dg-muted" x="{88 + _j * 56}" y="54" text-anchor="middle">{_f}</text>' for _j, _f in enumerate(_fields)]
    for _i, _sale in enumerate(_sales):
        _y = 66 + _i * 38
        _picked = _sale in _rows
        _box.append(f'<rect class="{"dg-tier" if _picked else "dg-box"}" x="58" y="{_y}" width="400" height="34" rx="6" fill-opacity="0.35"/>')
        _box.append(f'<text class="dg-muted" x="50" y="{_y + 22}" text-anchor="end">{_sale}</text>')
        _box += [
            _cell(62 + _j * 56, _y + 4, ("used" if _f in _cols else "wasted") if _picked else "idle")
            for _j, _f in enumerate(_fields)
        ]

    # The ledger: one page per field. Only the pages the question needs come down, at the lines it needs.
    _ledger = ['<text x="560" y="20" font-weight="700">Ledger: column layout</text>']
    for _j, _f in enumerate(_fields):
        _x = 600 + _j * 64
        _taken = _f in _cols
        _ledger.append(f'<text class="dg-muted" x="{_x + 29}" y="54" text-anchor="middle">{_f}</text>')
        _ledger.append(f'<rect class="{"dg-tier" if _taken else "dg-box"}" x="{_x}" y="62" width="58" height="248" rx="6" fill-opacity="0.35"/>')
        _ledger += [_cell(_x + 3, 66 + _i * 30, "used" if _taken and _sale in _rows else "idle") for _i, _sale in enumerate(_sales)]
    _ledger += [f'<text class="dg-muted" x="590" y="{84 + _i * 30}" text-anchor="end">{_sale}</text>' for _i, _sale in enumerate(_sales)]

    _used = len(_rows) * len(_cols)
    _row_read, _col_read = len(_rows) * len(_fields), _used

    def _tally(x, grabbed, read):
        hot = ' class="dg-hot"' if read > _used else ""
        return (
            f'<text x="{x}" y="400">{grabbed} · reads <tspan font-weight="700"{hot}>{read} fields</tspan>'
            f" to use {_used}</text>"
        )

    _legend = "".join(
        f'<rect class="{_cls[_state]}" x="{_x}" y="424" width="22" height="16" rx="3"/>'
        f'<text class="dg-muted" x="{_x + 30}" y="437">{_label}</text>'
        for _x, _state, _label in [(0, "used", "needed"), (130, "wasted", "read, not needed"), (330, "idle", "left alone")]
    )
    _picture = diagram(
        "".join(_box + _ledger)
        + _tally(0, f"picks up {len(_rows)} slip{'s' if len(_rows) > 1 else ''}", _row_read)
        + _tally(560, f"takes down {len(_cols)} page{'s' if len(_cols) > 1 else ''}", _col_read)
        + _legend,
        width=1060,
        height=450,
        label=f"{ch3_query.value}: the shoebox picks up {len(_rows)} slips and reads {_row_read} fields; "
        f"the ledger takes down {len(_cols)} pages and reads {_col_read} fields; the question needs {_used}.",
        tier="data",
    )
    _story = mo.md(
        """
    **The shoebox.** Every sale is one till receipt: sale number, date, product, country, units,
    price and rating printed together on one slip. To answer *what did we take in January 2026?*
    you pick up all 3,360 slips one at a time, read the date, read the price, and put down the
    other five fields untouched. That is a **row store**, and it is exactly the right shape for
    *show me sale 2,914*: one slip, one grab. Row stores suit OLTP (Online Transaction
    Processing): point lookups and updates of whole records.

    **The ledger.** The same sales copied into a bookkeeper's ledger, one field per page. The same
    question now means taking down two pages and leaving the other five on the shelf. That is a
    **column store**: right for scans, aggregates and compression, wrong for *show me sale 2,914*,
    which is now line 2,914 of seven different pages.

    *Two things the picture does not show.* The ledger pages are written in shorthand, so they are
    not all the same size, which is chapter 4. And the ledger is not one endless page per field,
    which comes right after the benchmark.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      {_picture}
      <p class="vis-caption">Same sales, same shop: <strong>the cost of a question depends on how the paper
      is arranged.</strong></p>
    </div>
                """
            ),
            mo.md(
                "A scan of $N$ rows that needs $k$ of $C$ columns reads "
                "$\\text{IO}_{\\text{row}} \\approx N \\times C$ in a row store, "
                "$\\text{IO}_{\\text{col}} \\approx N \\times k$ in a column store."
            ),
            mo.accordion({"The shoebox and the ledger, told in full": _story}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    n_rows = mo.ui.slider(250, 1000, step=250, value=1000, label="Rows (thousands)", show_value=True)
    run_storage = mo.ui.run_button(label="Run storage benchmark", kind="success")
    mo.vstack(
        [
            mo.md("### Benchmark: One Column, Two Layouts"),
            mo.md("The same random numbers kept twice in memory, record by record and column by column."),
            mo.hstack([n_rows, run_storage], justify="start", align="center", gap=2),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return n_rows, run_storage


@app.cell
def _(TIER, alt, best_seconds, chart_or_table, mo, n_rows, np, pd, run_storage, tier_chart):
    mo.stop(
        not run_storage.value,
        mo.md(
            "**Predict first:** give every record more columns. Which layout slows down when you sum one of them? "
            "Then click **Run storage benchmark**."
        ).callout(kind="neutral"),
    )

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

    _df = pd.DataFrame(_results)
    _long = _df.melt(
        id_vars=["operation", "columns (C)"], value_vars=["row layout (ms)", "column layout (ms)"], var_name="layout", value_name="ms"
    )
    _long["layout"] = _long["layout"].str.removesuffix(" (ms)")
    _x = alt.X("columns (C):O", title="columns per record (C)", axis=alt.Axis(labelAngle=0))
    _charts = []
    for _operation in _operations:
        _lines = (
            alt.Chart(_long[_long["operation"] == _operation])
            .mark_line(point=alt.OverlayMarkDef(size=90), strokeWidth=3)
            .encode(
                x=_x,
                y=alt.Y("ms:Q", title="ms"),
                color=alt.Color(
                    "layout:N", title=None, scale=alt.Scale(domain=["row layout", "column layout"], range=[TIER["hot"], TIER["data"]])
                ),
                tooltip=["layout:N", "columns (C):O", "ms:Q"],
            )
        )
        # over each row-layout point: how many times faster the column layout was
        _speedup = (
            alt.Chart(_df[_df["operation"] == _operation])
            .mark_text(align="right", dx=-8, dy=-12)
            .encode(x=_x, y="row layout (ms):Q", text="column is faster by:N")
        )
        _charts.append((_lines + _speedup).properties(width=400, height=260, title=_operation))

    _why = mo.md(
        """
    No file is written, so this is not Avro against Parquet, only the access pattern each one uses.
    Both operations read one column. In the row layout its values sit a whole record apart, and the
    CPU fetches memory in 64-byte cache lines, so it hauls in the neighbouring fields and throws them
    away. In the column layout the values lie side by side and every byte fetched is used. Parquet
    goes further and never reads the unused columns from disk.
        """
    )
    mo.vstack(
        [
            chart_or_table(tier_chart(alt.hconcat(*_charts, spacing=40), "data"), _results, label="Row vs column layout, same numbers"),
            mo.md(
                "Labels: how many times faster the column layout was. As $C$ grows the row layout slows and the "
                "column layout stays put: $\\text{IO}_{\\text{row}} / \\text{IO}_{\\text{col}} = C/k$ with $k = 1$, "
                "a direction, not an exact ratio."
            ),
            mo.accordion({"Why: cache lines, and what Parquet adds": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SALES_SEED, box, diagram, mo, pd):
    # The real sales in date order, cut into 420-sale sections like the audit below writes them.
    _dates = pd.read_parquet(SALES_SEED, columns=["sale_date"])["sale_date"].sort_values().reset_index(drop=True)
    _sections = [(_dates[_i : _i + 420].min(), _dates[_i : _i + 420].max()) for _i in range(0, len(_dates), 420)]
    _cut = pd.Timestamp("2026-01-01")
    _open = [_hi >= _cut for _lo, _hi in _sections]
    _wanted = [1, 5]  # the date and price pages of the seven

    _parts = [box(0, 0, "avg(total_price) WHERE sale_date &gt;= '2026-01-01'", cls="dg-tier")]
    def _rect(x, y, w, h, lit):
        """A section or a page: tier-coloured when the query opens it, faded when it stays shut."""
        return f'<rect class="{"dg-tier" if lit else "dg-box"}" x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="3" opacity="{1 if lit else 0.45}"/>'

    for _s, _lit in enumerate(_open):
        _x = _s * 78
        _parts.append(f'<text class="dg-muted" x="{_x + 34}" y="88" text-anchor="middle">section {_s}</text>')
        _parts.append(_rect(_x, 98, 68, 190, _lit))
        # seven pages per section; in an opened section only the two the query needs come out
        _parts += [_rect(_x + 5 + _p * 8.5, 106, 7, 174, _lit and _p in _wanted) for _p in range(7)]
    # the index card: one line per section, smallest and largest date
    _parts.append('<rect class="dg-box" x="680" y="60" width="380" height="252" rx="10"/>')
    _parts.append('<text x="700" y="88" font-weight="700">index card (Parquet: footer)</text>')
    for _s, (_lo, _hi) in enumerate(_sections):
        _y = 116 + _s * 24
        _parts.append(f'<text x="700" y="{_y}" font-family="monospace" font-size="15">{_s}  {_lo:%Y-%m-%d} .. {_hi:%Y-%m-%d}</text>')
        _parts.append(
            f'<text class="{"dg-ok" if _open[_s] else "dg-muted"}" x="1044" y="{_y}" text-anchor="end">'
            f'{"open" if _open[_s] else "skip"}</text>'
        )
    _first_open = _open.index(True)
    _parts.append('<path class="dg-edge" d="M406 22 H 870 V 54"/>')
    _parts.append('<text class="dg-muted" x="640" y="14" text-anchor="middle">read the card first</text>')
    _parts.append(f'<path class="dg-edge dg-ok" d="M676 {110 + _first_open * 24} H {_first_open * 78 + 74}"/>')
    _parts.append(
        f'<text class="dg-muted" x="0" y="314">{_open.count(False)} sections stay closed; '
        f"each opened one gives up 2 of its 7 pages</text>"
    )
    _binder = diagram(
        "".join(_parts),
        width=1060,
        height=326,
        label=f"A binder of {len(_sections)} sections of 420 sales, seven pages each. The index card lists each "
        f"section's first and last date; only sections whose last date reaches 2026 are opened, and only their "
        f"date and price pages are taken out.",
        tier="data",
    )
    _fences = mo.md(
        """
    - The card can prove a section is **hopeless**. It can never prove a section is **useful**. A
      section labelled <code style="white-space: nowrap">2024-03-01 .. 2026-02-27</code> must be opened,
      and may hold no 2026 sale at all. Min and max are a rejection test, not a search.
    - Sections 0 to 6 are skipped not *probably* but **provably**: their latest date is earlier than
      your earliest, so no page inside them can hold a 2026 sale.
    - The order rows were written in is not cosmetic. Drop the sales into the binder in random order
      and every section's card spans everything, every label is useless, and you open all eight. The
      mechanism did not fail; you gave it nothing to work with. The next lab measures exactly that.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>The Binder and the Index Card</h3>
      <p>The ledger is really a <strong>binder</strong>: sections of 420 sales (Parquet: <strong>row groups</strong>),
      one page per field in each, and an <strong>index card</strong> at the back with each section's smallest
      and largest value (Parquet: <strong>column statistics</strong>).</p>
      {_binder}
      <p class="vis-caption"><strong>That is how a program skips data it never read: it read the index card.</strong>
      The card can only say "no match here", so the order the rows were written in decides how much it can skip.</p>
    </div>
                """
            ),
            mo.accordion({"Two fences: what the card can and cannot prove": _fences}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, TIER, alt, chart_or_table, diagram, duckdb, format_bytes, mo, pd, tempfile, tier_chart):
    _df = pd.read_parquet(SALES_SEED)
    _cut = "2026-01-01"
    _wanted = ["sale_date", "total_price"]
    _steps = ["A: all columns", "B: 2 columns", "C: 2 columns, open sections"]

    with tempfile.TemporaryDirectory() as _td:
        _ordered = Path(_td) / "date_ordered.parquet"
        _shuffled = Path(_td) / "shuffled.parquet"
        _df.sort_values("sale_date").to_parquet(_ordered, index=False, row_group_size=420)
        _df.sample(frac=1, random_state=7).to_parquet(_shuffled, index=False, row_group_size=420)

        _con = duckdb.connect()
        _rows, _cards = [], {}
        _ordered_size, _shuffled_size = _ordered.stat().st_size, _shuffled.stat().st_size
        for _label, _path in (("date-ordered", _ordered), ("shuffled", _shuffled)):
            _md = _con.execute(
                "SELECT row_group_id, path_in_schema, total_compressed_size, stats_min, stats_max "
                f"FROM parquet_metadata('{_path.as_posix()}')"
            ).df()
            _two_cols = _md[_md["path_in_schema"].isin(_wanted)]
            # The index card: a section survives only if its LATEST date reaches the cut-off.
            _dates = _md[_md["path_in_schema"] == "sale_date"].sort_values("row_group_id")
            _live = _dates[_dates["stats_max"] >= _cut]["row_group_id"]
            _cards[_label] = list(zip(_dates["stats_min"].str[:7], _dates["stats_max"].str[:7], _dates["stats_max"] >= _cut))
            _answer = _con.execute(
                f"SELECT round(avg(total_price), 2) FROM '{_path.as_posix()}' WHERE sale_date >= '{_cut}'"
            ).fetchone()[0]
            _rows.append(
                {
                    "file": _label,
                    _steps[0]: int(_md["total_compressed_size"].sum()),
                    _steps[1]: int(_two_cols["total_compressed_size"].sum()),
                    _steps[2]: int(_two_cols[_two_cols["row_group_id"].isin(_live)]["total_compressed_size"].sum()),
                    "opened": f"{len(_live)} of {_md['row_group_id'].nunique()}",
                    "answer": _answer,
                }
            )
        _con.close()

    # One strip per file: every section with its date range, opened (tier) or skipped (grey).
    _strip = []
    for _r, (_label, _card) in enumerate(_cards.items()):
        _y = _r * 76
        _opened = sum(_open for *_, _open in _card)
        _strip.append(f'<text x="0" y="{_y + 24}" font-weight="700">{_label}</text>')
        _strip.append(
            f'<text class="{"dg-hot" if _opened == len(_card) else "dg-ok"}" x="0" y="{_y + 48}">opened {_opened} of {len(_card)}</text>'
        )
        for _s, (_lo, _hi, _open) in enumerate(_card):
            _x = 170 + _s * 111
            _strip.append(
                f'<rect class="{"dg-tier" if _open else "dg-box"}" x="{_x}" y="{_y}" width="104" height="60" rx="10"/>'
                f'<text x="{_x + 52}" y="{_y + 25}" text-anchor="middle">{_lo}</text>'
                f'<text class="dg-muted" x="{_x + 52}" y="{_y + 49}" text-anchor="middle">to {_hi}</text>'
            )
    _strip_svg = diagram(
        "".join(_strip),
        width=1060,
        height=136,
        label=f"Date-ordered file: sections each span three months and {_rows[0]['opened']} are opened. "
        f"Shuffled file: every section spans the whole range and {_rows[1]['opened']} are opened.",
        tier="data",
    )

    _bars = pd.DataFrame([{"file": _r["file"], "read": _s, "bytes": _r[_s]} for _r in _rows for _s in _steps])
    _bars["label"] = [format_bytes(_b) for _b in _bars["bytes"]]
    # red where the index card bought nothing: step C still reads everything step B read
    _bars["nothing skipped"] = [
        _s == _steps[2] and _r[_steps[2]] == _r[_steps[1]] for _r in _rows for _s in _steps
    ]
    _x = alt.X("bytes:Q", title=None, axis=None, scale=alt.Scale(domain=[0, _bars["bytes"].max() * 1.3]))
    _charts = []
    for _i, _file in enumerate(["date-ordered", "shuffled"]):
        _base = alt.Chart(_bars[_bars["file"] == _file]).encode(
            y=alt.Y("read:N", sort=None, title=None, axis=alt.Axis(labelLimit=260) if _i == 0 else None),
            x=_x,
            tooltip=["file:N", "read:N", "bytes:Q"],
        )
        _charts.append(
            (
                _base.mark_bar(cornerRadiusEnd=4).encode(
                    color=alt.condition("datum['nothing skipped']", alt.value(TIER["hot"]), alt.value(TIER["data"]))
                )
                + _base.mark_text(align="left", dx=6).encode(text="label:N")
            ).properties(width=300, height=150, title=f"{_file} file: bytes the query must read")
        )
    _sorted, _mixed = _rows
    _notes = mo.md(
        f"""
    - These are bytes the engine is *entitled to skip*, computed from the file's own footer, not
      bytes measured leaving the disk.
    - The shuffled file is also {_shuffled_size / _ordered_size - 1:.0%} larger ({_shuffled_size:,} against
      {_ordered_size:,} bytes) from the very same rows: a preview of chapter 4, where order is itself a
      form of compression.
        """
    )
    mo.vstack(
        [
            mo.md(
                f"""
    ### Mini-lab: Which Sections Did We Open?

    The 3,360 real sales written twice in 420-row sections, in date order and shuffled. Each file's own
    index card says what `avg(total_price) WHERE sale_date >= '{_cut}'` may skip.
                """
            ),
            _strip_svg,
            chart_or_table(tier_chart(alt.hconcat(*_charts, spacing=30), "data"), _rows, label="Bytes the query must read"),
            mo.md(
                f"Choosing columns took the date-ordered read from **{_sorted[_steps[0]]:,}** to "
                f"**{_sorted[_steps[1]]:,}** bytes; the index card took it to **{_sorted[_steps[2]]:,}**, and nobody "
                f"wrote that in the query. Shuffled, the card buys **nothing**: {_mixed['opened']} opened. "
                f"Both answer **{_sorted['answer']:,.2f}**."
            ).callout(kind="info"),
            mo.accordion({"Two honesty notes": _notes}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Row vs Column Storage</h3>
      <details>
        <summary><strong>Q1:</strong> When is a row store the better choice?</summary>
        <p><strong>Answer:</strong> Point lookups, frequent updates, and transactions on whole records (OLTP,
        Online Transaction Processing).</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> How does reading only the needed columns help?</summary>
        <p><strong>Answer:</strong> Unused columns are never read, so scans move less data. This is projection
        pushdown: the column choice applied as early as possible.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Why does write order matter for Parquet?</summary>
        <p><strong>Answer:</strong> Min/max can only exclude a row group whose range misses the filter. Sorted
        data gives narrow ranges; shuffled data gives every group the full range.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 3 Conclusion

    - Row layouts suit record-level transactions; column layouts suit scans and aggregates.
    - Reading only the columns you need cuts I/O.
    - Parquet keeps min/max per row group in its footer: sorted by date, the query skips 7 of 8 row
      groups; shuffled, none.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    A column puts similar values side by side, and similar values compress well. Next: how much
    smaller does it get, and at what cost?
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
def _(mo):
    mo.md("""
    ## 5. DuckDB Example (SQL on Files)
    """)
    return


@app.cell
def _(mo):
    mo.Html(
        """
    <div class="disclaimer-red">
      Disclaimer: Databases will be discussed in depth later in the semester in the
      <strong>Database Management for Data Scientists (DBM)</strong> module.
      Here we focus only on practical intuition for analytics workflows.
    </div>
            """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 5 Introduction

    > **Key Question:** How can DuckDB answer a query while reading much less data?

    *Last stop in the **data tier**. Chapters 1-4 built the files; now something has to read them back.*

    Two ideas you already met in chapter 3, the index card and the ledger, by their proper names:

    - **Predicate pushdown**: the filter runs inside the scan, so non-matching rows are dropped
      before any other work, and whole blocks whose min/max rule out a match are not read at all.
    - **Projection pushdown**: only the columns the query needs are read; the others are skipped.

    Main idea:

    $$
    \\text{work units} \\approx N \\times \\text{selectivity} \\times C_{\\text{needed}}
    $$

    Lower selectivity and fewer needed columns usually mean less total work. It is a toy model:
    the filter column itself is still read for every row unless whole blocks can be skipped, which
    needs data sorted or clustered on that column.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### DuckDB: SQL on Files, Zero Server

    DuckDB is an **embedded analytical database**:

    - **Embedded**: it runs inside your Python process, like a library. There is no server to start.
    - **Analytical**: it is built for scans, filters, `GROUP BY`, joins and aggregates over many
      rows, stored column by column.

    It is fast because it reads less, pushing the filter and the column list into the scan as
    defined above. The first mini-lab estimates how much that can skip; the second times one real
    query on three sources.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    push_rows = mo.ui.slider(10_000, 5_000_000, step=10_000, value=400_000, label="Rows (N)", show_value=True, debounce=True)
    push_selectivity = mo.ui.slider(0.001, 1.0, step=0.001, value=0.08, label="Filter selectivity (fraction of rows kept)", show_value=True, debounce=True)
    push_cols_total = mo.ui.slider(4, 80, value=24, label="Total columns", show_value=True, debounce=True)
    push_cols_needed = mo.ui.slider(1, 24, value=5, label="Columns used by query", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Mini-lab: Pushdown Intuition (What Work Gets Skipped?)"),
            mo.hstack([push_rows, push_selectivity], widths="equal"),
            mo.hstack([push_cols_total, push_cols_needed], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return push_cols_needed, push_cols_total, push_rows, push_selectivity


@app.cell
def _(
    mo,
    push_cols_needed,
    push_cols_total,
    push_rows,
    push_selectivity,
    static_table,
):
    _n, _kept, _total = push_rows.value, push_selectivity.value, push_cols_total.value
    _needed = min(push_cols_needed.value, _total)  # a query cannot use more columns than the table has
    _without, _with = _n * _total, _n * _kept * _needed
    mo.vstack(
        [
            static_table(
                [
                    {
                        "estimate": "without pushdown",
                        "rows (N)": _n,
                        "share of rows kept": 1.0,
                        "columns read": _total,
                        "work units": _without,
                    },
                    {
                        "estimate": "with pushdown",
                        "rows (N)": _n,
                        "share of rows kept": _kept,
                        "columns read": _needed,
                        "work units": round(_with),
                    },
                ],
                label="Predicate + projection pushdown estimate (toy model, not a runtime)",
            ),
            mo.md(
                f"Reduction factor: **{_without / _with:,.1f}x** less work. The bigger it is, the more "
                "there is for pushdown to skip. The next mini-lab times a real query."
            ).callout(kind="info"),
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
                "DuckDB can query a file by its name: `SELECT ... FROM 'orders.csv'`. The same "
                "`GROUP BY` (orders and average amount per region, above the threshold) runs on a "
                "CSV file, a Parquet file and a table loaded into DuckDB. Compare what each costs "
                "per query and what loading costs once."
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
    best_seconds,
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
):
    mo.stop(not run_duck.value, mo.md("Click **Run DuckDB demo** to time one query on three sources.").callout(kind="neutral"))

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

    _timings = static_table(
        [
            {
                "source": "CSV file (orders.csv)",
                "size": format_bytes(_csv_size),
                "per query": format_ms(_query_csv),
                "load into a table, once": format_ms(_load_csv),
            },
            {
                "source": "Parquet file (orders.parquet)",
                "size": format_bytes(_parquet_size),
                "per query": format_ms(_query_parquet),
                "load into a table, once": format_ms(_load_parquet),
            },
            {
                "source": "DuckDB table (analytics.duckdb)",
                "size": format_bytes(_db_size),
                "per query": format_ms(_query_table),
                "load into a table, once": "-",
            },
        ],
        label="One query, three sources (best of 3 runs)",
    )
    _size_note = (
        "Push Rows up and the CSV overtakes it." if _db_size > _csv_size else "At this size the CSV is already the bigger file."
    )
    _note = mo.md(
        f"""
    **Here the gap is mostly parsing.** CSV is text, so every query re-reads and re-converts it;
    Parquet and the DuckDB table are already typed columns. Predicate pushdown has next to
    nothing to skip: the amounts are random, so every block spans roughly 0 to 1000.

    Loading the CSV into a table cost {format_ms(_load_csv)}, about
    {_load_csv / _query_csv:.1f} CSV queries' worth. Every query after that runs at table speed,
    which is the case for loading data you query again and again.

    **Why can `analytics.duckdb` be bigger than the CSV?** DuckDB grows its file in
    {_block // 1024} KiB blocks, so a small table still fills whole blocks. {_size_note}
            """
    ).callout(kind="info")
    mo.vstack([_timings, static_table(_result.to_dict("records"), label=f"Query result (amount > {duck_threshold.value})"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Indexing Demo: Full Scan vs Indexed Search

    Pushdown skips work *during* a scan; an index avoids the scan: a sorted copy of some columns
    that lets the engine jump to the matching rows. DuckDB relies on automatic min/max zone maps
    rather than hand-made indexes, so we switch to SQLite, the row-store database Python ships
    with. One query, three states of the same table: no index, an index on `category`, an index on
    `(category, value)`, plus the plan SQLite chose for each.
            """
    ).callout(kind="neutral")
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
            mo.hstack([idx_rows, idx_selectivity], widths="equal"),
            mo.hstack([idx_threshold, idx_seed], widths="equal"),
            run_index,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return idx_rows, idx_seed, idx_selectivity, idx_threshold, run_index


@app.cell
def _(
    best_seconds,
    idx_rows,
    idx_seed,
    idx_selectivity,
    idx_threshold,
    mo,
    random,
    run_index,
    sqlite3,
    static_table,
):
    mo.stop(not run_index.value, mo.md("Click **Run indexing demo** to time one query on three states of the same table.").callout(kind="neutral"))

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
    _table = static_table(
        [
            {
                "state": _state,
                "build (ms)": round(_build * 1000, 1),
                "query (ms)": round(_query_s * 1000, 3),
                "speed-up vs scan": f"{_scan / _query_s:.1f}x",
                "SQLite plan": _plan,
            }
            for _state, (_build, _query_s, _plan) in _states.items()
        ],
        label=f"What the index costs, and what it buys (all three return {_count:,} rows, average {_avg})",
        wrapped_columns=["SQLite plan"],
    )
    if round(_narrow, 1) < 1:
        _planner = (
            f"Here that is exactly what happened: the `(category)` row is at {_narrow:.1f}x, slower than "
            "the scan, and the plan still says USING INDEX."
        )
    elif round(idx_selectivity.value, 2) < 0.7:
        _planner = (
            "Push the share of C to 0.7 or more and run again: the `(category)` row drops below 1.0x "
            "and the plan still says USING INDEX."
        )
    else:
        _planner = (
            f"At this share the narrow index still just held on ({_narrow:.1f}x); timings wobble, so run "
            "again and it drops below 1.0x while the plan still says USING INDEX."
        )
    _note = mo.md(
        f"""
    **An index is not a speed setting.** It is a second copy of some of your columns, and this
    table shows three consequences.

    - **It is not free.** Look at the build column. That cost is paid once here, but in a real
      system it is paid again on **every insert, update and delete**, forever. A table with six
      indexes is a table where every write does seven pieces of work.
    - **Width matters more than existence.** The narrow index knows only the category, so once it
      has found the matching rows it must still visit the table to read each `value`. The wide one
      contains both columns the query asked for, so the answer never touches the table at all.
      Watch the plan say **COVERING INDEX**: that word is the whole difference.
    - **The planner guesses.** SQLite does not know how many rows are C (even `ANALYZE` only
      stores averages), so it assumes an equality match is rare and takes the index even when
      that is slower than scanning. {_planner}

    So the honest rule is not "add an index to make it fast". It is: an index pays when it holds
    what the query asks for, and the query asks for **few** rows.
            """
    ).callout(kind="info")
    mo.vstack([_table, _note], gap=0.6)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Schema-on-Read vs Schema-on-Write (DuckDB)
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    Two ways to deal with the fact that a file has no types of its own.

    **Schema-on-read** means you point a tool at the file and let it guess. DuckDB looks at the
    values and picks `BIGINT`, `DOUBLE`, `DATE` or `VARCHAR`. Fast to start, and forgiving: one
    bad value in a column and the whole column becomes text.

    **Schema-on-write** means you declare the blank form *first*, with its types and its rules,
    and then load into it. Slower to start, and unforgiving on purpose.

    The difference is not which one uses a cast. It is **when the check happens, and who gets
    told.** Below, the same messy export goes down both lanes. Watch what each one reports.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    run_schema = mo.ui.run_button(label="Run schema demo", kind="success")
    mo.vstack(
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
    return (run_schema,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, random, run_schema, static_table, tempfile):
    mo.stop(not run_schema.value, mo.md("Click **Run schema demo** to send one messy file down both lanes.").callout(kind="neutral"))

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
            _told = "loaded without complaint"
        except duckdb.Error as _exc:
            _lines = str(_exc).splitlines()
            _told = f"{type(_exc).__name__}: {_lines[0]}. {_lines[2]}"
        _loaded = _con.execute("SELECT count(*) FROM sales_clean").fetchone()[0]

    _true = _src["total_price"].sum()
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
    _note = mo.md(
        f"""
    **Same file. Same {len(_bad_rows)} bad values. Two completely different days at work.**

    Schema-on-read gave you a number, and it is wrong: {1 - _revenue / _true:.1%} below the true
    total. {_rows - _parsed} of {_rows} rows were silently discarded, because `TRY_CAST` turns
    anything it cannot convert into `NULL` and `SUM` skips nulls. Nothing raised, nothing warned.
    The figure looks completely ordinary and would go straight into a report.

    Schema-on-write refused to load and named the line it choked on. You have no number yet, and
    that is the point: you have a **problem you know about** instead of an answer you trust by
    mistake.

    Neither lane is correct in the abstract. Schema-on-read is right for exploring a file you
    have just been handed. Schema-on-write is right for anything a decision rests on.
            """
    ).callout(kind="warn")
    mo.vstack([_table, _note], gap=0.6)
    return


@app.cell
def _(mo):
    run_evolution = mo.ui.run_button(label="Run schema evolution demo", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Add One Column, Then Read Last Year's Files"),
            mo.md(
                "Chapter 2 showed a *format* handling a changed form. This is the same problem one "
                "level up: a folder with one file per year, read together. "
                "We split the real sales by year: `sales_2024.parquet` was written **before** anyone "
                "thought of `customer_rating`; `sales_2025.parquet` and `sales_2026.parquet` have it."
            ).callout(kind="info"),
            run_evolution,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_evolution,)


@app.cell
def _(Path, SALES_SEED, duckdb, mo, pd, run_evolution, static_table, tempfile):
    mo.stop(not run_evolution.value, mo.md("Click **Run schema evolution demo** to read one folder three ways.").callout(kind="neutral"))

    _all = pd.read_parquet(SALES_SEED)
    with tempfile.TemporaryDirectory() as _td:
        _dir = Path(_td).as_posix()
        _files = []
        for _year, _part in _all.groupby(_all["sale_date"].dt.year):
            _files.append(f"{_dir}/sales_{_year}.parquet")
            # customer_rating joined the form in 2025, so the 2024 file never had it
            (_part.drop(columns="customer_rating") if _year < 2025 else _part).to_parquet(_files[-1], index=False)
        _con = duckdb.connect()

        def _read(sql, params):
            try:
                _df = _con.execute(sql, params).df()
            except duckdb.Error as _exc:
                return f"{type(_exc).__name__}: {str(_exc).splitlines()[0].replace(_dir + '/', '')}"
            if "customer_rating" not in _df:
                return f"{len(_df):,} rows, {_df.shape[1]} columns, no customer_rating, no error"
            return f"{len(_df):,} rows, rating on {_df['customer_rating'].count():,}, average {_df['customer_rating'].mean():.3f}"

        _glob = f"{_dir}/sales_*.parquet"
        _rows = [
            {
                "how you read the folder": "read_parquet('sales_*.parquet')",
                "what happens": _read("FROM read_parquet(?)", [_glob]),
                "why": "the glob lists files alphabetically, so the oldest file sets the shape and the newer column is dropped",
            },
            {
                "how you read the folder": "the same files, newest first",
                "what happens": _read("FROM read_parquet(?)", [_files[::-1]]),
                "why": "now the first file has the column and a later one does not, so the read is refused",
            },
            {
                "how you read the folder": "read_parquet('sales_*.parquet', union_by_name = true)",
                "what happens": _read("FROM read_parquet(?, union_by_name = true)", [_glob]),
                "why": "columns are matched by name, and the missing ones are filled with NULL",
            },
        ]

    _note = mo.md(
        """
    **Same folder, three readings, and only one is right.**

    The first is the dangerous one. Nothing failed: you read the folder and `customer_rating` had
    quietly vanished, because the first file read decided what the shape was. The second at least
    had the decency to shout. Only the third gives the honest answer, over the rows that actually
    have a rating.

    This is what "schema evolution" means once your data lives in more than one file. The rule to
    take away: **when a folder of files has grown new columns over time, say so when you read
    it.** The default is not to guess kindly.
            """
    ).callout(kind="warn")
    mo.vstack(
        [
            static_table(
                _rows,
                label="One folder, two file shapes, three readings",
                wrapped_columns=["how you read the folder", "what happens", "why"],
                column_widths={"how you read the folder": 250, "what happens": 480, "why": 330},
            ),
            _note,
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

    - DuckDB runs SQL directly on files; typed columns (Parquet, a loaded table) answer far faster
      than CSV, which is re-parsed on every query.
    - Schema-on-write catches type issues earlier; schema-on-read is flexible but riskier.
    - An index is a second copy of some columns: it pays when it covers the query and the query
      asks for few rows, and every write pays for it.
    - Reading a folder whose files grew columns: say `union_by_name=true`, or the first file
      decides the shape.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
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
    return


@app.cell
def _(mo):
    mo.md("""
    ## 6. REST API Demo (GET, POST, PUT, DELETE)
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 6 Introduction

    > **Key Question:** Did the client and server agree on the same contract?

    *We move up to the **logic tier**. The data tier is finished; now other programs need to ask for that data.*

    An API is a contract between systems.
    Most API bugs are contract mismatches: wrong path, wrong payload shape, or wrong status handling.

    Quick basics:

    - **HTTP** is the message protocol used by clients and servers on the web.
    - **HTTPS** is HTTP with encryption (TLS), so data is protected in transit.
    - In practice: same API idea, but HTTPS is the secure default.

    Keep this mapping in mind:

    - 2xx: success
    - 4xx: client-side issue
    - 5xx: server-side issue
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### REST Principles

    First the four words this whole chapter is built from:

    - A **resource** is one thing the server knows about, like a product or a sale.
    - A **path** is the address of a resource, like `/products/8`.
    - An **endpoint** is one path combined with one verb, like `GET /products/8`.
    - A **payload** is the data you send along with a request, written as JSON.

    The four verbs say what you want done to a resource:

    - **GET**: fetch a resource
    - **POST**: create a new resource
    - **PUT**: replace a resource with the version you send. Our API also accepts just the
      fields you change, which the HTTP standard calls **PATCH**; its `/docs` page says so.
    - **DELETE**: remove a resource

    One more word, because the mini-lab below and chapter 8's *Press It Twice* lab turn on it.
    **Idempotent** means pressing it twice changes nothing more than pressing it once. The button
    to call a lift is idempotent: jab it ten times, one lift comes. A ticket dispenser is not:
    press it ten times and you are holding ten tickets.

    GET, PUT and DELETE are lift buttons. POST is a ticket dispenser. That is the whole reason a
    failed POST is frightening to retry and a failed PUT is not: when the network drops before
    the answer arrives, you cannot tell whether the server acted, and only for POST does guessing
    wrong cost you a duplicate.

    *The lift button suggests nothing happens on the second press, and something does.* The
    request really is sent and really is processed. Idempotent means the **end state** is the
    same, not that the work is skipped, and not even that the answer is the same: DELETE a sale
    twice and you get **204**, then **404**. Still idempotent, because after one press or ten the
    sale is gone. Our partial PUT is idempotent too: setting the rating to 5 twice leaves it at 5.

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
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Four Real Answers From Our Own API

    Not a lookup table. These are the actual replies `sw03_demo_api.py` gives, and the difference
    between the three failures is the part worth learning. The mini-lab below sends each of them.

    | You send | You get | Why |
    | :--- | :--- | :--- |
    | `POST /sales` with a valid sale | **201 Created** | it worked, and a new thing now exists |
    | `GET /sales/999999` | **404 Not Found** | the address is fine, nothing lives there |
    | `POST /countries` with `region_id: 999` | **400 Bad Request** | well formed, but it asks for the impossible |
    | `POST /sales` with `customer_rating: 9` | **422 Unprocessable Content** | it breaks a rule written in the model (1 to 5), so the endpoint's code never ran |

    All three failures are **4xx**, and that first digit is the instruction: *you* must change
    something; resending the same request gets the same answer. A **5xx** is the opposite
    message: the server broke, so retrying may well work (blindly only for the lift-button verbs).

    400 or 422 is where students trip. **422**: the request broke a rule in the model (missing
    field, wrong type, rating 9, a name of only spaces, an unknown field such as `total_price`,
    which the server computes itself), so it was turned away at the door (chapter 7). **400**: it
    passed the door, then broke a rule only the data can check, like a region that does not exist.
        """
    ).callout(kind="neutral")
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

    Start the API in a terminal first: `uvicorn sw03_demo_api:app`. **uvicorn** is the program
    that listens on the port and hands each request to the FastAPI code; `sw03_demo_api` is the
    file and `app` the variable inside it. Leave out `--reload` today: it also restarts the server
    whenever marimo saves a notebook in this folder, and every restart resets `data/`.

    Pick a request, **guess the status code**, then press **Send request**. Send the POST, the PUT and the DELETE twice each:
    which of them leave the server where the first press left it? The API restores `data/` from
    `data/seed/` every time it starts, so nothing you change or delete here is permanent.
                """
            ),
            mo.hstack([ch6_preset, api_base_url], widths="equal", align="end"),
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
    json,
    mo,
    requests,
):
    from http.client import responses as _phrases

    mo.stop(not ch6_send.value, mo.md("Pick a request, guess the status code, then click **Send request**.").callout(kind="neutral"))

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
    mo.vstack(
        [mo.md(f"`{ch6_method.value} {_url}` → **{_status} {_phrases.get(_status, '(no standard name)')}**"), _shown],
        gap=0.5,
    ).callout(kind={2: "success", 4: "warn"}.get(_status // 100, "danger"))
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
    - 404, 400 and 422 are three different client mistakes: nothing lives there, the request asks
      for the impossible, the request breaks a written rule.
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

    Every 422 above was the request's *shape* failing a check. Pydantic is that checkpoint:
    required fields, types and ranges are checked before any endpoint code runs.

    $$
    \\text{valid request} \\Rightarrow \\text{schema checks pass} \\quad\\text{but}\\quad \\text{schema checks pass} \\nRightarrow \\text{valid request}
    $$

    Chapter 7 shows why the second arrow fails.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 7. Pydantic Models
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 7 Introduction

    > **Key Question:** Which inputs are allowed into the trusted system boundary?

    *Still in the **logic tier**. Chapter 6 agreed on a contract; now we enforce it.*

    Validation decides which inputs may cross into the trusted part of the system. Check once at
    the door, and every function behind it can stop re-checking.

    $$
    \\text{accepted input} = \\{\\, x \\in \\text{untrusted input} \\mid x \\text{ passes every rule you wrote} \\,\\}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
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

    Example constraint: $0 \\le \\text{gpa} \\le 4$ (grade-point average).

    In the mini-lab below, pick a preset or edit the JSON and watch the errors appear.
    **Then run the last two presets, which are the point of this chapter.**

    `garbage_that_passes` sends a negative id, a name of three spaces, a gpa of 0.0 and
    `"definitely not an email"`. Every field is the declared type and inside its declared range,
    so `Student` **accepts all of it**.

    `silently_coerced` sends `"42"` and `"3.5"` as text. Pydantic does not reject them; it
    converts them and hands you numbers.

    So validation checks **shape**, not **truth**: a bouncer with a list of rules, not a person who
    knows whether the answer makes sense. A negative id and a blank name are shaped correctly and
    still garbage; only a written rule stops them, as in `StrictStudent` in the lab. Two of its
    rules are subtle:

    - `min_length=1` alone lets three spaces through (three characters).
      `str_strip_whitespace=True` trims first, then counts. Every request model of our API
      inherits this from its `Input` base, plus `extra="forbid"` against unknown fields.
    - `strict=True` refuses `"42"` for an int instead of converting it. Our API leaves it off:
      `"2"` for `units_sold` becomes 2.

    Validation is exactly as good as the rules you thought to write. (The email `pattern` is a
    cheap check; `EmailStr` is the real one, after `pip install "pydantic[email]"`.)
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    ch7_preset = mo.ui.dropdown(
        options={
            "valid → should pass": {"id": 1, "name": "Ada", "gpa": 3.8, "email": "ada@example.com"},
            "missing_email → should fail (missing field)": {"id": 2, "name": "Lin", "gpa": 3.4},
            "gpa_out_of_range → should fail (gpa > 4.0)": {"id": 3, "name": "Mira", "gpa": 5.2, "email": "mira@example.com"},
            "wrong_type → should fail (type mismatch)": {"id": "not-an-int", "name": "Sam", "gpa": "high", "email": "sam@example.com"},
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
            mo.md("### Mini-lab: Interactive Payload Validation"),
            ch7_preset,
            mo.md(
                """
    ```python
    from pydantic import BaseModel, ConfigDict, Field

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

    Guess what each model says, then click **Validate with Pydantic**. Each error line is one
    entry of the list FastAPI sends back as the body of a 422.
                """
            ),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (ch7_preset,)


@app.cell
def _(ch7_preset, json, mo):
    ch7_json = mo.ui.text_area(value=json.dumps(ch7_preset.value, indent=2), rows=7, label="Student JSON", full_width=True)
    ch7_validate = mo.ui.run_button(label="Validate with Pydantic", kind="success")
    mo.vstack([ch7_json, ch7_validate], gap=0.6).callout(kind="neutral")
    return ch7_json, ch7_validate


@app.cell
def _(ch7_json, ch7_validate, mo, pydantic):
    mo.stop(not ch7_validate.value, mo.md("Guess the verdict, then click **Validate with Pydantic**.").callout(kind="neutral"))

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

    def _verdict(title, model):
        try:
            student = model.model_validate_json(ch7_json.value)  # parse + validate in one step
        except pydantic.ValidationError as exc:
            lines = [
                f"- `{'.'.join(map(str, e['loc'])) or 'JSON'}`: {e['msg']}"
                # no-break spaces, so three spaces do not collapse to one in the rendered code span
                + ("" if e["type"] in {"missing", "json_invalid"} else f" (you sent `{repr(e['input']).replace(' ', '\u00a0')}`)")
                for e in exc.errors()
            ]
            return mo.md(f"**{title}: rejected**\n\n" + "\n".join(lines)).callout(kind="danger")
        # a code block, not mo.json: its tree view would squeeze a name of three spaces to one
        return mo.md(f"**{title}: accepted**\n\n```json\n{student.model_dump_json(indent=2)}\n```").callout(kind="success")

    mo.hstack([_verdict("Student", _Student), _verdict("StrictStudent", _StrictStudent)], widths="equal")
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Validation</h3>
      <details>
        <summary><strong>Q1:</strong> Where should validation happen: client, server, or both?</summary>
        <p><strong>Answer:</strong> Both. Clients give fast feedback, but servers must enforce rules to protect data (server-side validation):
        anyone can skip your client and call the API directly, as chapter 6 just did.</p>
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

    - A model checks shape (fields, types, ranges), not truth: it is only as good as the rules you wrote.
    - Pydantic converts `"42"` to 42 and accepts a name of three spaces unless you say otherwise
      (`strict`; `str_strip_whitespace` plus `min_length=1`).
    - A rejection is a precise list of errors, and FastAPI sends that list back as a 422.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
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
    return


@app.cell
def _(mo):
    mo.md("""
    ## 8. FastAPI Demo + Automatic Docs
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 8 Introduction

    > **Key Question:** How do we keep implementation and API documentation in sync?

    *Last stop in the **logic tier**. We turn the rules from chapter 7 into a running server.*

    FastAPI turns validated models into running endpoints *and* the documentation for them, so
    the two drift apart far less.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### FastAPI = Type Hints → OpenAPI

    Most restaurants write the menu by hand. Then the kitchen changes a recipe and the menu
    quietly starts lying, and every customer who orders from it is disappointed. FastAPI does not
    let that happen, because **the menu is printed from the recipes**. `sw03_demo_api.py` writes
    the rating rule exactly once, `Rating = Annotated[int, Field(ge=1, le=5)]`, and uses it for new
    sales, for edits and for the `min_rating`/`max_rating` filters. That one line becomes the
    machine-readable menu, the buttons a human clicks, and the rule the server enforces. Change
    the 5 to a 10 and all of them change together, because there is only one 5.

    *What the menu cannot enforce* is behaviour. The schema can say `units_sold` must be at least
    1; it cannot say that changing it recomputes `total_price`. That rule reaches `/docs` only
    because somebody wrote it into a docstring by hand, and nothing checks that the docstring is
    still true.

    - **OpenAPI** (`/openapi.json`) is a standard file format that describes every endpoint
      an API has, in a way other programs can read. FastAPI writes it for you.
    - **Swagger UI** (`/docs`) is a web page that reads that file and turns it into buttons
      you can click to try each endpoint. Open it and press *Try it out*.
    - **ReDoc** (`/redoc`) reads the same file and renders it as a reference manual instead.

    The server is the one you started for chapter 6 with `uvicorn sw03_demo_api:app`. While you
    *edit* the API, `--reload` restarts it on every save; during the lecture, leave it out.
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
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

    Read each decorator as a sentence: *verb*, *path*, the shape of the answer, and the errors it
    can return. The docstring under each function becomes its description in `/docs`; the second
    one is the hand-written recompute rule from above. `SaleCreate` has no `total_price`, and
    `Input` refuses fields it does not know, so a client cannot set its own price.

    Sales are the resource this chapter follows, so every verb is written out. The four lookup
    tables (regions, countries, categories, products) share one generic set of five endpoints,
    registered by `add_lookup_endpoints`. Nothing else had to be written to get documentation.
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Live API Workflow

    1. Start the API in a terminal: `uvicorn sw03_demo_api:app`
    2. Click **1) Check API status** to verify the server is reachable.
    3. Edit the JSON payload and click **2) POST /products**. Click it again: the name is taken
       now, so the server answers `400` (the widget stays until the API restarts).
    4. Choose a product id and click **3) GET /products/{id}** to compare results.
            """
    ).callout(kind="info")
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
            mo.hstack([api_base_url, fastapi_check], widths=[5, 1], align="end"),
            fastapi_payload,
            mo.hstack([fastapi_post, fastapi_item_id, fastapi_get], justify="start", align="end", gap=2),
        ],
        gap=0.8,
    ).callout(kind="neutral")
    return


@app.cell
def _(api_base_url, call_api, mo, requests):
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
    return ch8_api, sale_slip


@app.cell
def _(api_base_url, ch8_api, fastapi_check, mo):
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
    _routes = [
        f"- `{_path}`: {', '.join(_verb.upper() for _verb in _ops)}"
        for _path, _ops in _schema["paths"].items()
        if _path.startswith(("/products", "/sales"))
    ]
    mo.md(
        "\n".join(
            [
                f"**{_schema['info']['title']} {_schema['info']['version']} is running.** "
                f"Docs: [{_base}/docs]({_base}/docs)",
                "",
                f"The paths this chapter uses, read from `/openapi.json` ({len(_schema['paths'])} paths in all):",
                "",
                *_routes,
            ]
        )
    ).callout(kind="success")
    return


@app.cell
def _(ch8_api, fastapi_payload, fastapi_post, json, mo):
    mo.stop(not fastapi_post.value, mo.md("Edit the payload, then click **2) POST /products**.").callout(kind="neutral"))
    try:
        _payload = json.loads(fastapi_payload.value)
    except json.JSONDecodeError as _exc:
        mo.stop(True, mo.md(f"The payload is not valid JSON: `{_exc}`").callout(kind="danger"))
    _status, _answer = ch8_api("POST", "/products", _payload)
    mo.md(f"`POST /products` answered `{_status}`.\n\n```json\n{json.dumps(_answer, indent=2)}\n```").callout(
        kind="success" if _status < 400 else "danger"
    )
    return


@app.cell
def _(ch8_api, fastapi_get, fastapi_item_id, json, mo):
    mo.stop(not fastapi_get.value, mo.md("Pick a product id, then click **3) GET /products/{id}**.").callout(kind="neutral"))
    _path = f"/products/{fastapi_item_id.value}"
    _status, _answer = ch8_api("GET", _path)
    mo.md(f"`GET {_path}` answered `{_status}`.\n\n```json\n{json.dumps(_answer, indent=2)}\n```").callout(
        kind="success" if _status < 400 else "danger"
    )
    return


@app.cell
def _(mo):
    run_gates = mo.ui.run_button(label="Send seven slips through both gates", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Seven Sale Slips, One Model, Two Gates"),
            mo.md(
                """
    Chapter 7 validated a payload on your laptop with no network at all, because Pydantic is just
    Python. This chapter put the very same kind of model on a server. So what is the difference?

    **Gate 1** is the API's own `SaleCreate`, imported from `sw03_demo_api.py` and run right here
    in the notebook. **Gate 2** is the running API. Seven slips go through both. Read the table
    across.
                """
            ).callout(kind="info"),
            run_gates,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_gates,)


@app.cell
def _(ch8_api, mo, pydantic, run_gates, sale_slip, static_table):
    mo.stop(not run_gates.value, mo.md("Click **Send seven slips through both gates** to compare them.").callout(kind="neutral"))
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
    _rows, _good = [], None
    for _name, _slip in _slips.items():
        try:
            _SaleCreate.model_validate(_slip)
            _gate1 = "passes"
        except pydantic.ValidationError as _exc:
            _err = _exc.errors()[0]
            _gate1 = f"rejected: {_err['loc'][0]} — {_err['msg']}"
        _status, _answer = ch8_api("POST", "/sales", _slip)
        mo.stop(
            not (isinstance(_answer, dict) and ("detail" in _answer or "sale_id" in _answer)),
            mo.md(f"`POST /sales` answered `{_status}`: `{_answer}`. Is that the sales API?").callout(kind="danger"),
        )
        if _status == 201:
            _good = _answer
            ch8_api("DELETE", f"/sales/{_good['sale_id']}")  # leave the file as we found it
            _gate2 = f"201 created — {len(_good)} fields back, total_price {_good['total_price']}"
        else:
            _detail = _answer["detail"]
            _gate2 = f"{_status} — {_detail if isinstance(_detail, str) else _detail[0]['msg']}"
        _rows.append({"the slip": _name, "gate 1: your laptop": _gate1, "gate 2: the server": _gate2})
    mo.stop(_good is None, mo.md("Even the good sale was refused. Restart the API to reseed its data.").callout(kind="danger"))

    _note = mo.md(
        f"""
    **Read the last column down.** Five slips die at gate 1 and die again at gate 2, with `422`
    and the *same message*, because both gates run the same model. One slip, `product 9999`,
    passes gate 1 and dies at gate 2 with `400`. And one gets `201`.

    That difference is the whole lesson. Gate 1 can check **shape**: is this a date, is the rating
    between 1 and 5. Only gate 2 can check **facts**, because only the server can open the filing
    cabinet and discover there is no product 9999. Your laptop had no way to know.

    **Then look at the successful row.** We sent {len(_ok)} fields and got {len(_good)} back, and we never
    sent `total_price`: the server computed {_good["units_sold"]} x
    {_good["total_price"] / _good["units_sold"]:.2f} itself. The slip that brought its own
    `total_price` was refused at both gates, because `SaleCreate` has no such field and refuses
    fields it does not know. A price the client is allowed to invent is a price the client can
    lie about, so this API does not allow one.

    Two fences. Validating on the laptop is a **courtesy** to the user, instant feedback with no
    round trip, and never a substitute for the server's check, because anyone can bypass this
    notebook and post directly with `curl`. And the split between 422 and 400 is this API's
    convention, not a law of HTTP: FastAPI produces the 422 automatically from the model, while
    the 400s are business rules somebody wrote by hand.
            """
    ).callout(kind="info")
    _table = static_table(
        _rows,
        label="The same seven slips, checked twice",
        wrapped_columns=["gate 1: your laptop", "gate 2: the server"],  # the messages are the point
        column_widths={"gate 1: your laptop": 410, "gate 2: the server": 410},
    )
    mo.vstack([_table, _note], gap=0.6)
    return


@app.cell
def _(mo):
    run_twice = mo.ui.run_button(label="Press every verb twice", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Press It Twice"),
            mo.md(
                "The lift button or the ticket dispenser? Chapter 6 had you press them by hand; here "
                "all four verbs go to the running API **twice in a row**, against one sale, side by "
                "side. Needs the running API."
            ).callout(kind="info"),
            run_twice,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_twice,)


@app.cell
def _(ch8_api, mo, run_twice, sale_slip, static_table):
    mo.stop(not run_twice.value, mo.md("Click **Press every verb twice** to test it against the running API.").callout(kind="neutral"))

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
    _note = mo.md(
        """
    **GET, PUT and DELETE are safe to press twice. The world ends up the same.** POST is not: the
    second press booked a second sale. That is exactly why a checkout page begs you not to hit
    refresh, and why a payment that times out is frightening in a way a profile edit is not.

    **The 404 from chapter 6 is back.** The second DELETE answered `404`, not `204`, and the sale
    is just as gone. Idempotent is a promise about the **effect on the world**, not about the
    status code; only the answer to "did *you* delete it" changed.

    One more honest note: idempotence is a promise the API author makes, not something HTTP
    enforces. A carelessly written `PUT` can behave exactly like `POST`. It holds here because
    this server updates a row you named by id, not because the word PUT is magic.
        """
    ).callout(kind="info")
    mo.vstack([static_table(_rows, label="Each verb, sent twice"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    run_follow = mo.ui.run_button(label="Follow the sale into the file", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Where Does a POST Actually Go?"),
            mo.md(
                "We count the rows in `data/sales.parquet`, POST one sale through the API, count "
                "again, and then put the row that landed in the file next to the JSON that came "
                "back. Needs the running API, started from this folder."
            ).callout(kind="info"),
            run_follow,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_follow,)


@app.cell
def _(Path, ch8_api, duckdb, mo, run_follow, sale_slip, static_table):
    mo.stop(not run_follow.value, mo.md("Click **Follow the sale into the file** to watch the tiers hand over.").callout(kind="neutral"))
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
    _note = mo.md(
        f"""
    **The file grew by one: {_before:,} rows to {_after:,}.**

    The logic tier did not invent a database. It wrote to `data/sales.parquet`, a working copy of
    the file you compressed in chapter 4 and queried in chapter 5 (the API copies `data/seed/`
    into `data/` on every start). Your POST travelled all the way down.

    Now read the table across, because this is what a tier is *for*. The **file** keeps
    {len(_stored.columns)} columns and stores `product_id {_created["product_id"]}`,
    `country_id {_created["country_id"]}`: ids, no names, every fact written exactly once. That is
    the normalisation the data tier cares about. The **response** has {len(_created)} fields, with
    "{_created["product_name"]}", "{_created["country_name"]}" and "{_created["region_name"]}"
    spelled out. The logic tier did the joining, so the dashboard in `sw03_demo_streamlit.py` does not have to. Even
    the date changes shape: the file keeps a timestamp, the API sends a plain date.

    **One honest callback.** We just read that file behind the API's back. The API takes a lock
    around every write, but like the key on the hook in chapter 1, a lock only protects those who
    ask for it. Pandas rewrites the whole Parquet file on every change, so a read at the wrong
    instant could catch it half-written. That is precisely the isolation problem from chapter 1,
    and it is the reason a real system puts a database at the bottom of the data tier rather than
    a file.
        """
    ).callout(kind="info")
    mo.vstack([static_table(_rows, label="Same sale, two tiers, two shapes"), _note], gap=0.6)
    return


@app.cell
def _(mo):
    run_two_analysts = mo.ui.run_button(label="Run the two-analyst test", kind="success")
    mo.vstack(
        [
            mo.md("### Mini-lab: Two People, One Product, Both Click Save"),
            mo.md(
                """
    **Predict first, then run it.**

    Anna and Ben both open product 1 in a browser tab, at the same starting price. Anna applies a
    10% raise. Ben adds a 20-franc surcharge. Both click save. Both see "saved", and both get
    `200 OK` from the API you built.

    **What is the price afterwards?**
                """
            ).callout(kind="info"),
            run_two_analysts,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_two_analysts,)


@app.cell
def _(ch8_api, mo, run_two_analysts, static_table):
    mo.stop(
        not run_two_analysts.value,
        mo.md("Write your prediction down, then click **Run the two-analyst test**.").callout(kind="neutral"),
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
        _after_anna = _price("PUT", {"price": round(_anna_sees * 1.10, 2)})
        _after_ben = _price("PUT", {"price": round(_ben_sees + 20, 2)})
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
    _note = mo.md(
        f"""
    **Anna's raise is gone. {_correct - _final:.2f} of it, and nobody was told.**

    Look at what did *not* happen. No error. No warning. No conflict. Two `200 OK` responses, two
    users who saw "saved", and a price that is simply wrong.

    Now look back at **chapter 1**. This is the same lost update as the shared counter, the one we
    watched disappear from a text file, and it survived everything we have built since. It is not
    a threading accident either: these six requests ran strictly one after another, so this fails
    identically every single time you click the button. The bug is structural, not a timing fluke.

    Why did the lock not save us? Every write in `sw03_demo_api.py` runs inside one `lock`,
    chapter 1's own fix, so each single request is safe. But *there is no lock around what
    actually happened here*. The read and the write were two separate HTTP requests, minutes apart
    in real life, and the API has no idea they were meant to belong together. Ben's `PUT` carried
    a price computed from a page he opened before Anna saved. Chapter 1's lesson holds exactly as
    stated: a lock, like a transaction, protects the steps you put inside it, and nothing else.

    **The fix is not more locking.** It is to stop sending *the answer* and start sending *the
    change* (`{{"raise_percent": 10}}`), or to make the client say which version it read and let
    the server refuse if that version is stale. HTTP has that second option built in: `If-Match`
    with an ETag, answered by `412 Precondition Failed`. Correctness is a property of the design,
    not of the tools.
        """
    ).callout(kind="danger")
    mo.vstack(
        [static_table(_steps, label=f"Six requests, strictly in order (then the price goes back to {_start:.2f})"), _note],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 8 Conclusion

    - One model drives the validation, the endpoint and `/docs`, so the documentation cannot drift
      from the rules. A hand-written docstring still can.
    - Shape can be checked anywhere, on your laptop or at the server (422); facts only at the
      server (400). Only the server computes `total_price`.
    - GET, PUT and DELETE are safe to press twice; POST books a second sale.
    - A lock per request cannot stop a lost update split over two requests: send the change, or
      make the client say which version it read (`If-Match`).
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Backend answers are useful, but users still need a clear interface.
    Next we compare frontend options and what each one trades away: speed, control or simplicity.

    $$
    \\text{user value} = \\text{backend correctness} \\times \\text{frontend usability}
    $$
            """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 9. Frontend Framework Comparison
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 9 Introduction

    > **Key Question:** What does the frontend need to know about everything behind it?

    *We reach the **presentation tier**. The API from chapter 8 has the data; something has to show it.*

    Framework choice is a product decision, not a matter of taste: match the tool to your team's skills and
    to how much UI control the product needs. The usual trade-off:

    $$
    \\text{Iteration Speed} \\uparrow \\;\\Rightarrow\\; \\text{UI Control} \\downarrow
    $$
    """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo, static_table):
    _framework_note = mo.md(
        """
    ### Choosing a Frontend Stack

    **First, what a frontend actually is.** A restaurant has three rooms. The **cold store** holds
    the ingredients, keeps them correct and gets them out fast: chapters 1 to 5. The
    **kitchen** holds the recipes and the rules, and nothing leaves without being checked, whether
    the order came from a table, a phone or a delivery app: chapters 6 to 8. The **dining room**
    is what the guest sees, the tables, the plating and the waiter: chapters 9 and 10.

    A frontend is the dining room. It owns no ingredients and no recipes. It writes an order slip,
    which is an HTTP request to a path, hands it through the hatch, and arranges whatever comes
    back so a human can decide something.

    This is the payoff for splitting the tiers at all. Change supplier, Parquet for DuckDB, and no
    guest notices. Rebuild the whole dining room, Streamlit for React, and the kitchen does not
    change one line. **This repo already contains that dining room:** `sw03_demo_streamlit.py`,
    talking to the API you started in chapter 6.

    *Where the picture breaks.* A waiter cannot cook, but a frontend **does** compute: it sorts,
    formats, aggregates and draws every chart in that dashboard. So do not read this as "the
    frontend is dumb". Read it as **the frontend owns no rules**. Anyone can telephone the kitchen
    directly, with `curl` or a script or another team's app, so a rule that lives only in the
    dining room is not a rule at all. That is why this repo deliberately states the same rule
    twice: the Streamlit form sets `min_value=1` for units sold, and the API states it again as
    `Units = Annotated[int, Field(ge=1, le=100_000)]`. The form does not even repeat the upper
    limit; only the kitchen knows it. The dining room may repeat a rule for politeness. Never instead.

    Showcases: [Marimo gallery](https://marimo.io/gallery) ·
    [Dash gallery](https://dash.gallery/Portal/) ·
    [React community](https://react.dev/community) ·
    [Flask patterns](https://flask.palletsprojects.com/en/stable/patterns/)
    """
    ).callout(kind="neutral")
    _columns = ("framework", "you write", "strengths", "trade-offs", "use case")
    _frameworks = [
        ("Marimo", "Python", "Reactive notebooks, data + UI in one loop", "Notebook-first, not for big web apps", "Labs, teaching, analysis apps"),
        ("Dash", "Python", "Plotly charts, component ecosystem", "Callbacks get tangled in big apps", "Interactive analytics"),
        ("Streamlit", "Python", "Fastest prototyping, simple widgets", "Less layout and state control in big apps", "Dashboards, internal tools"),
        ("Flask", "Python + HTML templates, some JS", "Full control, templates + APIs", "More setup, no built-in UI", "Custom web apps + APIs"),
        ("React", "JavaScript / TypeScript", "Flexible, modern UI patterns", "Needs a JS/TS stack and tooling", "Production web apps"),
    ]
    _framework_table = static_table(
        [dict(zip(_columns, _row, strict=True)) for _row in _frameworks], label="Framework comparison"
    )
    mo.vstack([_framework_note, _framework_table], gap=0.6)
    return


@app.cell
def _(mo):
    fw_speed = mo.ui.slider(1, 5, value=5, label="Need fast iteration", show_value=True, debounce=True)
    fw_control = mo.ui.slider(1, 5, value=3, label="Need fine UI control", show_value=True, debounce=True)
    fw_js = mo.ui.slider(1, 5, value=2, label="Team JavaScript strength", show_value=True, debounce=True)
    _note = mo.md(
        """
    Set three numbers about *your team*, not about the frameworks.

    **JavaScript** is the programming language browsers run. Marimo, Streamlit and Dash let you
    stay in Python; React is written in JavaScript, and a Flask app needs some as soon as a page
    has to react. So a low score here is not a weakness, it just points at different tools.

    Each framework scores the three inputs with its own weights, and every weight row adds
    up to the same total (3.0) so the scores stay comparable:

    $$
    \\text{fit}_f = w^f_s \\cdot s + w^f_c \\cdot c + w^f_j \\cdot j_f
    \\qquad \\text{with} \\quad w^f_s + w^f_c + w^f_j = 3
    $$

    For the three Python-native tools, $j_f = 6 - j$: they get *more* attractive when the team
    knows *less* JavaScript. For Flask and React $j_f = j$. Heuristic only: validate it against
    real team constraints.
    """
    ).callout(kind="info")
    mo.vstack(
        [mo.md("### Mini-lab: Framework Fit Assistant"), fw_speed, fw_control, fw_js, _note],
        gap=0.6,
    ).callout(kind="neutral")
    return fw_control, fw_js, fw_speed


@app.cell
def _(fw_control, fw_js, fw_speed, mo, static_table):
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
    mo.vstack(
        [
            static_table(
                [
                    {
                        "framework": name,
                        "score": score,
                        "weights (speed / control / JS)": " / ".join(map(str, _weights[name][0])),
                    }
                    for name, score in _ranked
                ],
                label="Teaching score (higher = better fit)",
            ),
            mo.md(f"Current top fit: **{' / '.join(_top)}**" + (" (a tie)" if len(_top) > 1 else "")).callout(kind="info"),
        ],
        gap=0.6,
    )
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

    Tables show exact values; charts show patterns faster, including patterns that are not there.
    We close by asking when a chart deserves to be believed.

    $$
    \\text{what you plot} = \\text{signal} + \\text{noise}
    $$
    """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## 10. Honest Charts (Signal vs Noise)
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 10 Introduction

    > **Key Question:** Which pattern is signal, and which is noise?

    *Still in the **presentation tier**, and the last decision of the whole stack: what a chart claims is what people believe.*

    Charts help humans detect patterns quickly. A linear regression summarises a trend with two numbers:

    $$
    y = \\alpha + \\beta x
    $$

    - $\\alpha$: baseline level, the value of y where x is 0
    - $\\beta$: change in y for one unit change in x
    """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Lab: Signal or Noise?

    Generate a dataset where **you** set the true slope and the noise, then watch what the
    regression reports back. It gives two separate answers:

    - **Trend:** $\\beta$ plus or minus its margin of error (two standard errors, about 95%
      confidence). If that range includes 0, the data cannot tell the slope from zero.
    - **Fit:** $R^2$, the share of the up-and-down in y that the line explains: how well it
      predicts a *single* point.

    Set the slope to 0 and the noise high: the equation still prints confidently, and the ± tells
    you not to believe it. Still, about 1 seed in 20 clears the bar at slope 0: that is what
    95% means.

    Then put the noise back to 1.4 and set the slope to 0.4: $R^2$ calls the line nearly useless,
    yet the slope is clearly real. More rows shrink the ±, but they do not push $R^2$ up. $R^2$ measures
    how predictable single points are, not whether a trend exists.

    The mini-lab below then asks one question of real data three different ways, and gets three
    different answers.
    """
    ).callout(kind="neutral")
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

    _points = (
        alt.Chart(pd.DataFrame({"x": _xs, "y": _ys}))
        .mark_circle(size=40, opacity=0.6, color="#3b82f6")
        .encode(x=alt.X("x:Q").axis(tickCount=8), y="y:Q")
    )
    _line = _points.transform_regression("x", "y").mark_line(color="#f59e0b", strokeWidth=4)
    _chart = (
        (_points + _line)
        .properties(width="container", height=320)
        .configure_axis(labelFontSize=13, titleFontSize=14)
    )
    mo.vstack([_verdict, _chart], gap=0.8)
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
    mo.vstack(
        [
            mo.md("### Mini-lab: Three Ways to Change the Finding Without Changing the Data"),
            mo.md(
                """
    One question, asked of the repo's real 3,360 sales: **does spending more make customers
    happier?** Nothing below adds or removes a single sale. Only the way we look changes.
    (The lab reads the seed files directly, a notebook shortcut past the API; the dashboard asks the API.)
    """
            ).callout(kind="info"),
            honest_view,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (honest_view,)


@app.cell
def _(SEED_DIR, duckdb, honest_view, mo, static_table):
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
        _rows = [
            _measure("one dot per sale"),
            _measure("one dot per product per month", _averaged("product, month")),
            _measure("one dot per category per month", _averaged("category, month")),
            _measure("one dot per category", _averaged("category")),
        ]
        _lesson = f"""
    **$R^2$ climbed from {_rows[0]["R²"]:.2f} to {_rows[-1]["R²"]:.2f} and no new information entered the room.**

    Every row above is the same {_rows[0]["dots (n)"]:,} sales. Averaging dots together does not
    strengthen a relationship, it **deletes the disagreement** that was telling you the
    relationship is weak. The last row has {_rows[-1]["dots (n)"]} dots and a story you could put on a slide.

    This is why a goodness-of-fit number is meaningless without its sample size. Always read
    $R^2$ and $n$ together, which is why the table prints both. The dashboard's *What goes with a
    good rating?* chart offers the same choice: compare *Sale* with *Category (monthly)*.
    """
    elif honest_view.value.startswith("B"):
        _cats = [_c for (_c,) in _con.execute("SELECT DISTINCT category FROM sales ORDER BY 1").fetchall()]
        _rows = [_measure("all sales pooled together")]
        _rows += [_measure(f"only {_c}", "sales WHERE category = ?", _c) for _c in _cats]
        _down = [_c for _c, _row in zip(_cats, _rows[1:], strict=True) if _row["slope (rating per CHF 10k)"] < 0]
        _up = [_c for _c in _cats if _c not in _down]
        _lesson = f"""
    **The pooled line does not describe any of the groups.**

    Pooled, the slope is positive: spend more, be happier. Inside {" and ".join(_down)} it points
    the other way, and only {" and ".join(_up)} still slopes upward. The upward pooled line is mostly
    describing the gaps **between** categories: Services happen to be expensive and well rated,
    while Hardware is mid-priced and rated worst.

    When a trend reverses inside *every* group it was built from, that is Simpson's paradox. Here
    it reverses in {len(_down)} of {len(_cats)} groups: not the textbook case, but the same trap.
    Three groups' worth of difference, wearing three thousand dots' worth of authority.
    """
    else:
        _rows = [
            _measure("all sales"),
            _measure("every sale except Services", "sales WHERE category <> 'Services'"),
        ]
        _lesson = """
    **One group out of three decided the direction of the answer.**

    Remove Services and the slope flips sign: the finding reverses completely. Now look at the
    $R^2$ column. It barely moved.

    That is the warning worth leaving this chapter with. $R^2$ tells you how tightly the dots hug
    the line. It never tells you whether the line was the right line to draw, and it will not
    warn you when one group is carrying the entire result.
    """

    mo.vstack(
        [
            static_table(_rows, label=f"Same {_rows[0]['dots (n)']:,} sales, same question"),
            mo.md(_lesson).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Wrap-up

    We built one data product, one tier at a time. The map from the start, filled in:

    - **Data tier, where the bytes rest:** keep writes correct (ch. 1), pick a format (ch. 2),
      choose a layout (ch. 3), shrink it (ch. 4), query it with DuckDB (ch. 5).
    - **Logic tier, the rules and the API:** agree on a contract (ch. 6), check what comes in
      with Pydantic (ch. 7), serve it with FastAPI (ch. 8).
    - **Presentation tier, what people see:** choose a frontend (ch. 9), show the numbers
      honestly (ch. 10).

    Each tier only talks to its neighbour. Move the sales from Parquet files into a DuckDB
    database and only the storage code in `sw03_demo_api.py` changes (the file names in `TABLES`
    and `reset`, `read`, `write`), not one endpoint. Swap Streamlit for React and neither lower
    tier notices.

    If you remember one thing: correctness is designed in, not bought with a tool. Get it first,
    then performance, then usability.
    """
    ).callout(kind="neutral")
    return


@app.cell
def _(mo):
    mo.md("""
    ## Some Useful Links
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    - [marimo docs](https://docs.marimo.io) · [gallery](https://marimo.io/gallery)
    - [DuckDB](https://duckdb.org/docs) · [SQLite](https://www.sqlite.org/docs.html)
    - [Apache Parquet](https://parquet.apache.org) · [Arrow](https://arrow.apache.org) ·
      [Avro](https://avro.apache.org)
    - [FastAPI](https://fastapi.tiangolo.com) · [Pydantic](https://docs.pydantic.dev) ·
      [Streamlit](https://docs.streamlit.io)
    - [OpenAPI spec](https://spec.openapis.org/oas/latest.html) ·
      [HTTP semantics, RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) ·
      [HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
    - [Dash gallery](https://dash.gallery/Portal/) · [React community](https://react.dev/community) ·
      [Flask patterns](https://flask.palletsprojects.com/en/stable/patterns/)
    """)
    return


if __name__ == "__main__":
    app.run()
