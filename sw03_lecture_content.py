# /// script
# [tool.marimo.display]
# theme = "light"
# ///
import marimo

__generated_with = "0.25.0"
# The deck is shown as slides (layouts/): every cell with an output is one slide, shown whole; a cell
# without output (definitions, a lab's controls) is skipped. So a slide is built as one cell's output.
app = marimo.App(
    width="medium",
    css_file="sw03_deck.css",
    html_head_file="sw03_deck_head.html",
    layout_file="layouts/sw03_lecture_content.slides.json",
)


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

        1 viewBox unit is 1 px at `width`: it grows to 1.3x that in a wide column (a 4K window), so it fills
        more of the screen without its labels outgrowing the text; narrower when its column is.
        `tier` ("data", "logic" or "presentation") colours every dg-tier and dg-dot inside.
        """
        tier_class = f" tier-{tier}" if tier else ""
        # One arrowhead id per drawing: url(#id) takes the first match in the page, which can sit in a
        # hidden copy that marimo keeps of tab and accordion content, and a hidden marker draws nothing.
        arrow = f"dg-arrow-{abs(hash(body))}"
        return mo.Html(
            f'<svg class="dg{tier_class}" viewBox="0 0 {width} {height}"'
            f' style="max-width: {width * 1.3:.0f}px; --dg-arrow: url(#{arrow})" role="img" aria-label="{html.escape(label)}">'
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
        <strong>EdgeWorks</strong> sells sensors, software and services in eight countries. Its head of
        sales, Mia, wants a sales dashboard she can trust. Today we are EdgeWorks' data team, and we
        build it from the bottom up: where the data rests, what serves it, and what people look at.
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
def _(in_plain, mia_asks, mo, shop_sales, static_table):
    _months = shop_sales["sale_date"].dt.to_period("M").nunique()
    _sample = shop_sales.sort_values("sale_id").head(4)[
        ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"]
    ]
    mo.vstack(
        [
            mo.md("## Meet EdgeWorks"),
            mia_asks("I want one dashboard for our sales. Numbers I can trust, fast, and on my laptop."),
            mo.hstack(
                [
                    mo.stat(f"{len(shop_sales):,}", label="sales", caption=f"over {_months} months", bordered=True),
                    mo.stat(f"CHF {shop_sales['total_price'].sum() / 1e6:,.1f} M", label="revenue", bordered=True),
                    mo.stat(shop_sales["product"].nunique(), label="products sold", caption="hardware, software, services", bordered=True),
                    mo.stat(shop_sales["country"].nunique(), label="countries", caption="in 4 regions", bordered=True),
                ],
                widths="equal",
            ),
            static_table(
                _sample.assign(sale_date=_sample["sale_date"].dt.date).to_dict("records"),
                label="Every sale is one row like these (data/seed/sales.parquet)",
            ),
            in_plain(
                "Every example today uses these real rows. When something goes wrong in a lab, it goes wrong "
                "on EdgeWorks' sales, in numbers Mia would see."
            ),
        ],
        gap=0.8,
    )
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
        + _tier(40, "presentation", "Presentation tier", "Mia's dashboard", [("9", "frontend"), ("10", "honest charts")])
        + _tier(172, "logic", "Logic tier", "the sales API", [("6", "contract"), ("7", "validate input"), ("8", "serve over HTTP")])
        + _tier(304, "data", "Data tier", "the sales files", [("1", "correct writes"), ("2", "format"), ("3", "layout"), ("4", "compression"), ("5", "query")])
        # one hop per neighbour: down for the request, up for the answer
        + '<path class="dg-edge" d="M920 88 V 166"/><path class="dg-edge" d="M920 220 V 298"/>'
        + '<path class="dg-edge" d="M1000 352 V 274"/><path class="dg-edge" d="M1000 220 V 142"/>'
        + '<circle class="dg-dot" r="9"><animateMotion dur="5s" repeatCount="indefinite" path="M920 88 V 352 H 1000 V 88 Z"/></circle>',
        width=1060,
        height=420,
        label="Three tiers, stacked: presentation (chapters 9 and 10) on logic (6 to 8) on data (1 to 5). "
        "A request travels down one tier at a time and the answer comes back up the same way.",
    )
    mo.md(f"""
    <div class="section-card">
      <h3>The Map: Mia's Dashboard Is Three Tiers</h3>
      {tier_map}
      <p class="vis-caption">The <strong>data tier</strong> keeps the sales files
      (<code>data/*.parquet</code>), the <strong>logic tier</strong> is the sales API
      (<code>sw03_demo_api.py</code>), the <strong>presentation tier</strong> is the dashboard Mia
      opens (<code>sw03_demo_streamlit.py</code>). Each talks only to its neighbour, so any one can be
      replaced without rewriting the others.</p>
    </div>
    """)
    return (tier_map,)


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Ten Questions Mia Will Ask Today</h3>
      <ol class="mia-list">
        <li class="tier-data"><strong>Locks</strong>: two reps booked an order at the same moment. Why is today's order count too low?</li>
        <li class="tier-data"><strong>Formats</strong>: we send sales files to partners. Which format, and why did the CSV turn store code 007 into 7?</li>
        <li class="tier-data"><strong>Layout</strong>: "total revenue" reads one column. Why does it read the whole file?</li>
        <li class="tier-data"><strong>Compression</strong>: the sales history fills the disk. Can we shrink it without losing a cent?</li>
        <li class="tier-data"><strong>DuckDB</strong>: can I get revenue per region straight from the files, with no database server?</li>
        <li class="tier-logic"><strong>REST</strong>: the dashboard and the partners' scripts both need the sales. How do they ask for them?</li>
        <li class="tier-logic"><strong>Pydantic</strong>: someone sent a sale with rating 9 and 0 units. How do we stop it at the door?</li>
        <li class="tier-logic"><strong>FastAPI</strong>: how do partners learn what our API accepts, without emailing us?</li>
        <li class="tier-presentation"><strong>Frontends</strong>: what should we build the dashboard with?</li>
        <li class="tier-presentation"><strong>Honest charts</strong>: does spending more make customers happier? Mia wants a chart for the board.</li>
      </ol>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>How to Read This Notebook</h3>
      <div class="tiles">
        <div class="tile"><div class="tile-key">?</div><div class="tile-title">Mia asks</div>
          <p>Every chapter starts with a real question from EdgeWorks' head of sales.</p></div>
        <div class="tile"><div class="tile-key">=</div><div class="tile-title">In plain words</div>
          <p>Every idea in one or two everyday sentences, before any formula.</p></div>
        <div class="tile"><div class="tile-key">&#9654;</div><div class="tile-title">Try it</div>
          <p>A lab on EdgeWorks' sales. Slow ones wait for their Run button: guess first, then run.</p></div>
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

    # Charts as SVG, not canvas: the slides are zoomed to fit the screen, and a canvas bitmap zoomed up blurs.
    # Assigned, so the cell shows nothing (an output would become a slide of its own).
    _ = alt.renderers.set_embed_options(renderer="svg")

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
def _(SEED_DIR, pd):
    def _table(file, **renames):
        return pd.read_parquet(SEED_DIR / f"{file}.parquet").rename(columns=renames)

    # EdgeWorks' sales with the names joined in: every example in the deck is about these rows.
    # Shared by many cells, so a cell that changes it works on a copy: shop_sales.copy().
    shop_sales = (
        _table("sales")
        .merge(_table("products", name="product", price="list_price")[["product_id", "product", "list_price", "category_id"]], on="product_id")
        .merge(_table("categories", name="category")[["category_id", "category"]], on="category_id")
        .merge(_table("countries", name="country")[["country_id", "country", "region_id"]], on="country_id")
        .merge(_table("sales_regions", name="region")[["region_id", "region"]], on="region_id")
        .sort_values("sale_id", ignore_index=True)
    )
    return (shop_sales,)


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

    def mia_asks(question: str):
        """Mia, EdgeWorks' head of sales, asking the question a chapter or a lab answers (markdown)."""
        return mo.Html(f'<div class="mia-asks"><span class="mia-who">Mia, head of sales</span>{mo.md(question).text}</div>')

    def in_plain(text: str):
        """The idea in one or two everyday sentences (markdown), shown before any formula."""
        return mo.Html(f'<div class="in-plain"><span class="in-plain-label">In plain words</span>{mo.md(text).text}</div>')

    def chapter_intro(tier: str, question: str, context: str):
        """A chapter's opening card: the tier badge, Mia's question in large type, one line of markdown context."""
        return mo.Html(
            f'<div class="key-q tier-{tier}"><span class="tier-badge">{tier} tier</span>'
            f'<span class="mia-who key-q-who">Mia asks</span>'
            f'<p class="key-q-text">{question}</p>{mo.md(context).text}</div>'
        )

    return (
        TIER,
        best_seconds,
        call_api,
        chapter_intro,
        chart_or_table,
        format_bytes,
        format_ms,
        in_plain,
        mia_asks,
        static_table,
        tier_chart,
    )


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
    # No mo.status.spinner here: as a slide, a cell whose output blanks while it runs drops into marimo's edit preview.
    with tempfile.TemporaryDirectory() as _tmp:
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
    ).properties(width="container", height=110)
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
        .properties(width="container", height=170)
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
                mo.vstack([tier_chart(_lanes, "data"), tier_chart(_counter, "data")]),
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
def _(diagram, json, mo):
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
    mo.md(
        f"""
    <div class="section-card">
      <h3>Serialization = Bytes on Disk (or Wire)</h3>
      {_pipeline}
    </div>
        """
    )
    return


@app.cell
def _(box, diagram, fastavro, html, io, mo):
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
    ).properties(width="container", height=300, title="Size vs latency: the bottom-left corner wins")
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
    ).properties(width="container", height=300, title="Throughput: rows written per second")

    mo.vstack(
        [
            chart_or_table(
                mo.hstack([tier_chart(_scatter, "data"), tier_chart(_throughput, "data")], widths=[3, 2], gap=2),
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
        _charts.append((_lines + _speedup).properties(width="container", height=260, title=_operation))

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
            chart_or_table(mo.hstack([tier_chart(_c, "data") for _c in _charts], widths="equal", gap=2), _results, label="Row vs column layout, same numbers"),
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
            ).properties(width="container", height=150, title=f"{_file} file: bytes the query must read")
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
            chart_or_table(mo.hstack([tier_chart(_c, "data") for _c in _charts], widths="equal", gap=2), _rows, label="Bytes the query must read"),
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
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 4. Compression & Encoding (Parquet, Gzip)"),
            chapter_intro(
                "data",
                "Will compression cut total query time, not only file size?",
                "Chapter 3 put similar values side by side, which is exactly what makes them squeeze well.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(diagram, mo):
    # A sketch of the timing model, not a measurement: segment lengths only show which term grows.
    _amber = ' style="fill: color-mix(in srgb, var(--amber) 22%, transparent); stroke: var(--amber); stroke-width: 1.5"'
    _kinds = {"read": ' class="dg-tier"', "unpack": _amber, "compute": ' class="dg-box"'}

    def _bar(y, name, parts, verdict=""):
        x, out = 190, [f'<text x="0" y="{y + 25}">{name}</text>']
        for kind, w in parts:
            out.append(f'<rect{_kinds[kind]} x="{x}" y="{y}" width="{w}" height="38" rx="6"/>')
            if w >= 70:
                out.append(f'<text x="{x + w / 2:.0f}" y="{y + 25}" text-anchor="middle">{kind}</text>')
            x += w + 3
        return "".join(out) + verdict.format(x=x + 12, y=y + 25)

    _faster = '<text class="dg-ok" x="{x}" y="{y}">&#10003; faster</text>'
    _slower = '<text class="dg-hot" x="{x}" y="{y}">&#10007; slower</text>'
    _sketch = diagram(
        '<text x="0" y="20" font-weight="700">slow disk or network: reading bytes dominates</text>'
        + _bar(36, "plain", [("read", 520), ("compute", 120)])
        + _bar(82, "compressed", [("read", 190), ("unpack", 110), ("compute", 120)], _faster)
        + '<text x="0" y="160" font-weight="700">file already in memory, or the CPU already busy</text>'
        + _bar(176, "plain", [("read", 40), ("compute", 120)])
        + _bar(222, "compressed", [("read", 16), ("unpack", 110), ("compute", 120)], _slower),
        width=1000,
        height=270,
        label="A sketch: with a slow disk or network, compression shrinks the read time more than unpacking adds, so the "
        "total shrinks. With the file already in memory there is little read time to save, and unpacking makes it slower.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>What Compression Trades</h3>
      {_sketch}
      <p class="vis-caption">A sketch, not a measurement: <strong>compression trades CPU for I/O</strong>,
      and pays only when moving bytes is expensive.</p>
    </div>
                """
            ),
            mo.md(
                """
    $T_{\\text{total}} \\approx T_{\\text{io}} + T_{\\text{decompress}} + T_{\\text{compute}}$, and the
    compression ratio $r = \\text{compressed size} / \\text{original size}$ (savings $= 1 - r$).

    **gzip levels:** 1 is fast and saves less, 9 slow and saves most. The `gzip` tool and zlib default
    to 6, Python's `gzip.compress` to 9.
                """
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    budget_size_gb = mo.ui.slider(1, 500, value=120, label="Raw dataset size (GB)", show_value=True, debounce=True)
    budget_ratio = mo.ui.slider(0.1, 1.0, step=0.05, value=0.35, label="Compression ratio r", show_value=True, debounce=True)
    budget_scans_day = mo.ui.slider(1, 80, value=18, label="Full scans/day", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Mini-lab: Compression Cost Impact (an Estimate)"),
            mo.hstack([budget_size_gb, budget_ratio, budget_scans_day], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return budget_ratio, budget_scans_day, budget_size_gb


@app.cell
def _(TIER, alt, budget_ratio, budget_scans_day, budget_size_gb, mo, pd, tier_chart):
    _on_disk = budget_size_gb.value * budget_ratio.value
    _saved = budget_size_gb.value - _on_disk
    _day = pd.DataFrame(
        {
            "stored": ["plain", "compressed"],
            "GB read per day": [budget_size_gb.value * budget_scans_day.value, _on_disk * budget_scans_day.value],
        }
    )
    _day["label"] = [f"{_gb:,.0f} GB" for _gb in _day["GB read per day"]]
    _base = alt.Chart(_day).encode(
        y=alt.Y("stored:N", sort=None, title=None),
        x=alt.X("GB read per day:Q", title="GB read per day", scale=alt.Scale(domain=[0, _day["GB read per day"].max() * 1.2])),
        tooltip=["stored:N", "GB read per day:Q"],
    )
    _bars = (
        _base.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("stored:N", legend=None, scale=alt.Scale(domain=["plain", "compressed"], range=[TIER["muted"], TIER["data"]]))
        )
        + _base.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=110)
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(f"{_on_disk:,.1f} GB", label="On disk after compression", bordered=True),
                    mo.stat(f"{_saved:,.1f} GB", label="Less to read per full scan", bordered=True),
                    mo.stat(f"{_saved * budget_scans_day.value:,.1f} GB", label="Less I/O per day", bordered=True),
                ],
                widths="equal",
            ),
            tier_chart(_bars, "data"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch4_k_range = (4, 90, 2)  # first, last, step: the slider below and the curve the lab draws
    image_demo_rank = mo.ui.slider(*ch4_k_range, value=26, label="Components kept (rank k)", show_value=True, debounce=True)
    image_demo_width = mo.ui.slider(200, 360, value=280, step=20, label="Image width (px)", show_value=True, debounce=True)
    mo.vstack(
        [
            mo.md("### Mini-lab: Visual Compression with PCA (Cat Image)"),
            mo.hstack([image_demo_rank, image_demo_width], widths="equal"),
            mo.md(
                "Rebuilt from the top `k` singular vectors per colour channel: rank-k SVD, the maths behind "
                "[PCA](https://en.wikipedia.org/wiki/Principal_component_analysis). *PCA itself is covered in "
                "Machine Learning 2; here it only illustrates compression.*"
            ),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return ch4_k_range, image_demo_rank, image_demo_width


@app.cell
def _(Image, ImageDraw, ch4_k_range, image_demo_width, io, np):
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

    # Every k the slider offers, done once per width: what PCA has to store (the kept factors as float16,
    # compressed) and how far the rebuilt pixels land from the original on average.
    _u, _s, _vt = ch4_cat_svd
    _first, _last, _step_k = ch4_k_range
    ch4_cat_curve = []
    for _k in range(_first, _last + 1, _step_k):
        _kept = (_u[:, :, :_k], _s[:, :_k], _vt[:, :_k])
        _buf = io.BytesIO()
        np.savez_compressed(_buf, *(_m.astype(np.float16) for _m in _kept))
        _back = np.rint(np.clip((_kept[0] * _kept[1][:, None]) @ _kept[2], 0, 1) * 255)
        ch4_cat_curve.append(
            {
                "k": _k,
                "PCA bytes": _buf.getbuffer().nbytes,
                "average pixel off by": round(float(np.abs(_back - ch4_cat.transpose(2, 0, 1)).mean()), 2),
            }
        )
    return ch4_cat, ch4_cat_curve, ch4_cat_svd


@app.cell
def _(TIER, alt, box, ch4_cat, ch4_cat_curve, ch4_cat_svd, chart_or_table, diagram, gzip, image_demo_rank, mo, np, pd, tier_chart):
    _k = image_demo_rank.value
    _u, _s, _vt = ch4_cat_svd
    _rebuilt = np.rint(np.clip((_u[:, :, :_k] * _s[:, None, :_k]) @ _vt[:, :_k], 0, 1) * 255).astype(np.uint8).transpose(1, 2, 0)
    _pca_bytes = next(_row["PCA bytes"] for _row in ch4_cat_curve if _row["k"] == _k)
    _gz = gzip.compress(ch4_cat.tobytes(), 6)
    _gz_back = np.frombuffer(gzip.decompress(_gz), np.uint8).reshape(ch4_cat.shape)

    _rows = [
        {
            "method": _method,
            "bytes": _size,
            "ratio (compressed/raw)": round(_size / ch4_cat.nbytes, 4),
            "identical to the original?": "yes" if np.array_equal(_back, ch4_cat) else "no",
            "worst pixel off by (of 255)": int(np.abs(_back.astype(int) - ch4_cat).max()),
        }
        for _method, _size, _back in (
            ("gzip (lossless method)", len(_gz), _gz_back),
            (f"PCA k={_k} (lossy method)", _pca_bytes, _rebuilt),
        )
    ]

    _curve = pd.DataFrame(ch4_cat_curve)
    _x = alt.X("k:Q", title="components kept (k)")
    _here = _curve[_curve["k"] == _k]

    def _panel(field, title, dy, *extra):
        """One curve over k, with today's k as a dot labelled dy px above (-) or below (+) it."""
        line = alt.Chart(_curve).mark_line(strokeWidth=3).encode(x=_x, y=alt.Y(f"{field}:Q", title=None), tooltip=["k:Q", f"{field}:Q"])
        dot = alt.Chart(_here).mark_circle(size=220, opacity=1).encode(x=_x, y=f"{field}:Q")
        label = alt.Chart(_here).mark_text(align="left", dx=12, dy=dy).encode(x=_x, y=f"{field}:Q", text=alt.value(f"k = {_k}"))
        return alt.layer(line, dot, label, *extra).properties(width="container", height=220, title=title)

    _gzip_line = alt.Chart(pd.DataFrame({"bytes": [len(_gz)], "text": [f"gzip, lossless: {len(_gz):,} bytes"]}))
    _gzip_rule = _gzip_line.mark_rule(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"]).encode(y="bytes:Q") + _gzip_line.mark_text(
        align="right", x="width", dy=-8
    ).encode(y="bytes:Q", text="text:N")
    _charts = mo.hstack(
        [
            tier_chart(_panel("PCA bytes", "Bytes PCA has to store", 16, _gzip_rule), "data"),
            tier_chart(_panel("average pixel off by", "Average pixel off by (of 255)", -14), "data"),
        ],
        widths="equal",
        gap=2,
    )

    _pipeline = diagram(
        box(0, 8, "image: 3 matrices (R, G, B)")
        + '<path class="dg-edge" d="M262 30 H 318"/>'
        + box(324, 8, f"keep the top k = {_k} components", cls="dg-tier")
        + f'<path class="dg-edge" d="M{324 + 300} 30 H {324 + 356}"/>'
        + box(686, 8, "rebuilt image"),
        width=860,
        height=60,
        label=f"The image as three colour matrices, of which only the top {_k} components are kept, then rebuilt.",
        tier="data",
    )
    _pca_wins = _pca_bytes < len(_gz)
    # Shown on the next slide: what this k costs, against every other k.
    ch4_pca_result = mo.vstack(
        [
            mo.md(f"### What k = {_k} Costs: Bytes Against Pixel Error"),
            mo.md(
                """
    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">=</div><div class="tile-title">Lossless: a folded letter</div>
        <p>Unfold it: every word is back. gzip, PNG, Parquet. The only kind for money.</p></div>
      <div class="tile"><div class="tile-key">&asymp;</div><div class="tile-title">Lossy: a summary</div>
        <p>Smaller, still useful, the original gone. PCA, JPEG, MP3. Never for a price.</p></div>
    </div>
                """
            ),
            chart_or_table(_charts, _rows, label=f"Same {ch4_cat.nbytes:,}-byte image, two kinds of compression"),
            mo.md(
                f"**At k = {_k} the {'PCA' if _pca_wins else 'gzip'} file is smaller**"
                + (
                    ", but only gzip gives back the exact image."
                    if _pca_wins
                    else ": a smooth drawing repeats itself, and lossless compression removes repetition."
                )
            ),
        ],
        gap=0.6,
    )
    mo.vstack(
        [
            _pipeline,
            mo.hstack(
                [
                    mo.image(ch4_cat, width="100%", caption="Original"),
                    mo.image(_rebuilt, width="100%", caption=f"Rebuilt from k={_k} components"),
                ],
                widths="equal",
                gap=0.8,
            ),
        ],
        gap=0.6,
    )
    return (ch4_pca_result,)


@app.cell
def _(ch4_pca_result):
    ch4_pca_result
    return


@app.cell
def _(SALES_SEED, TIER, alt, chart_or_table, io, mo, pd, tier_chart):
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

    _df = pd.DataFrame(_rows)
    _df["verdict"] = [f"total off by {_off:+,.2f}" if _off else "exact total" for _off in _df["off by"]]
    _base = alt.Chart(_df).encode(
        y=alt.Y("how the prices are stored:N", sort=None, title=None, axis=alt.Axis(labelLimit=280)),
        x=alt.X("bytes:Q", title="file size (bytes)", scale=alt.Scale(domain=[0, _df["bytes"].max() * 1.6])),
        tooltip=list(_rows[0]),
    )
    _chart = (
        _base.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.condition("datum['off by'] != 0", alt.value(TIER["hot"]), alt.value(TIER["data"]))
        )
        + _base.mark_text(align="left", dx=6).encode(text="verdict:N")
    ).properties(width="container", height=48 * len(_df), title="Smaller files, wrong totals")

    _more = mo.md(
        f"""
    **The lossy files really are smaller.** Rounding to the nearest 100 francs cuts another
    {1 - _hundred / _exact_gz:.0%} off the gzipped file, a bigger win than gzip itself managed on the exact
    data ({1 - _exact_gz / _exact:.0%}). The true total is `{_truth:,.2f}`; every lossy row reports a
    different number, the file loads cleanly, the column is still a decimal, and every tool downstream is
    perfectly happy. Nobody minds a cat whose pixels are a few shades off; every accountant sees a total
    that is off by hundreds of francs, and by then the original is gone.
        """
    )
    mo.vstack(
        [
            mo.md(
                """
    ### Mini-lab: The Cat Trick, Applied to Sales Prices

    Store the real prices less precisely. **Which file is smallest, and which still adds up?**
                """
            ),
            chart_or_table(tier_chart(_chart, "data"), _rows, label=f"Same {len(_src):,} prices, stored five ways"),
            mo.md(
                "**Same trick, different meaning.** Is an approximation of *this* value still the truth you need? "
                "For a photo, usually. For money, an identifier or a date, never."
            ).callout(kind="danger"),
            mo.accordion({"How much smaller, and why nobody notices": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    compress_rows = mo.ui.slider(500, 10_000, step=500, value=2_000, label="Rows", show_value=True, debounce=True)
    compress_cols = mo.ui.slider(3, 10, value=6, label="Numeric columns", show_value=True, debounce=True)
    ch4_compress_repeat = mo.ui.switch(label="Only 5 distinct values per column")
    mo.vstack(
        [
            mo.md("### Mini-lab: Which Format Is Smallest?"),
            mo.md(
                "**Predict first:** JSON, CSV, gzip or Parquet? And if every column held only five values? Flip the switch."
            ),
            mo.hstack([compress_rows, compress_cols, ch4_compress_repeat], widths="equal", align="center"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return ch4_compress_repeat, compress_cols, compress_rows


@app.cell
def _(TIER, alt, ch4_compress_repeat, chart_or_table, compress_cols, compress_rows, csv, gzip, io, json, mo, pa, pd, pq, random, tier_chart):
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
    _rows = [{"format": _name, "size (bytes)": _size, "ratio vs JSON": round(_size / _sizes["JSON"], 4)} for _name, _size in _sizes.items()]
    _df = pd.DataFrame(_rows)
    _df["smallest"] = _df["size (bytes)"] == _smallest
    _df["label"] = [f"{_r:.1%} of JSON" for _r in _df["ratio vs JSON"]]
    _base = alt.Chart(_df).encode(
        y=alt.Y("format:N", sort=None, title=None),
        x=alt.X("size (bytes):Q", title="bytes", scale=alt.Scale(domain=[0, _df["size (bytes)"].max() * 1.25])),
        tooltip=list(_rows[0]),
    )
    _chart = (
        _base.mark_bar(cornerRadiusEnd=4).encode(color=alt.condition("datum.smallest", alt.value(TIER["data"]), alt.value(TIER["muted"])))
        + _base.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=30 * len(_df), title="Same records, twelve ways")

    _why = mo.md(
        """
    Distinct 5-decimal measurements hold almost no repetition: Parquet stores each one as 8 bytes of
    float64, while gzipped text pays only for the digits you wrote. Five repeated values per column are
    exactly what Parquet's dictionary encoding lives on. At the default 2,000 rows x 6 columns, flipping
    the switch moves the win from gzipped CSV to Parquet. Nothing about Parquet changed.
        """
    )
    mo.vstack(
        [
            chart_or_table(tier_chart(_chart, "data"), _rows, label="Compression ratios (baseline: JSON size)"),
            mo.md(
                f"**Smallest here: {_best}**, at {_smallest / _sizes['JSON']:.0%} of the JSON bytes. Compression removes "
                "**repetition**: the winner depends on your columns, not the format's reputation."
            ).callout(kind="info"),
            mo.accordion({"Why the ranking flips": _why}),
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
                "Unpack, parse and sum one column of the sales file, already in memory. Best of 5 bursts."
            ),
            run_ctime,
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return (run_ctime,)


@app.cell
def _(SALES_SEED, TIER, alt, best_seconds, chart_or_table, gzip, io, mo, pd, run_ctime, tier_chart):
    mo.stop(
        not run_ctime.value,
        mo.md(
            "**Predict first:** the gzipped file is far smaller. Is the query on it faster or slower? "
            "Then click **Run compression timing**."
        ).callout(kind="neutral"),
    )

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

    _df = pd.DataFrame(_rows)
    _df["slower"] = _df["read + parse + sum (ms)"] > _plain_row["read + parse + sum (ms)"]
    _query = alt.Chart(_df).encode(
        y=alt.Y("variant:N", sort=None, title=None),
        x=alt.X("read + parse + sum (ms):Q", title="ms", scale=alt.Scale(domain=[0, _df["read + parse + sum (ms)"].max() * 1.3])),
        tooltip=["variant:N", "bytes:Q", "read + parse + sum (ms):Q", "vs plain:N"],
    )
    _answer_chart = (
        _query.mark_bar(cornerRadiusEnd=4).encode(color=alt.condition("datum.slower", alt.value(TIER["hot"]), alt.value(TIER["data"])))
        + _query.mark_text(align="left", dx=6).encode(text="vs plain:N")
        + alt.Chart(pd.DataFrame({"ms": [_plain]})).mark_rule(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"]).encode(x="ms:Q")
    ).properties(width="container", height=200, title="Time to answer (vs plain CSV)")
    _levels = pd.DataFrame(_rows[1:])
    _write = alt.Chart(_levels).encode(
        y=alt.Y("variant:N", sort=None, title=None),
        x=alt.X("compress (ms):Q", title="ms", scale=alt.Scale(domain=[0, _levels["compress (ms)"].max() * 1.3])),
        tooltip=["variant:N", "bytes:Q", "compress (ms):Q", "decompress (ms):Q"],
    )
    _write_chart = (
        _write.mark_bar(cornerRadiusEnd=4, color=TIER["muted"]) + _write.mark_text(align="left", dx=6).encode(text=alt.Text("compress (ms):Q", format=".1f"))
    ).properties(width="container", height=150, title="Compress once (ms)")

    _note = mo.md(
        f"""
    Here the file already sits in memory, so there is no I/O to save: the extra bytes cost nothing to
    read, while unpacking them costs CPU on every query. Send the same file across a network and the
    trade flips, which is why compression is normal for transfer and a judgement call on a local disk.
    Levels 6 and 9 land {abs(_l6['bytes'] - _l9['bytes']):,} bytes apart, and level 9 spent
    {_l9['compress (ms)'] / _l6['compress (ms)']:.1f}x the CPU to find them.
        """
    )
    mo.vstack(
        [
            chart_or_table(mo.hstack([tier_chart(_answer_chart, "data"), tier_chart(_write_chart, "data")], widths=[3, 2], gap=2), _rows, label="Same question, four files"),
            mo.md(
                f"{_verdict} Unpacking costs about the same at every level: **the level is a decision about writing, not reading.**"
            ).callout(kind="warn"),
            mo.accordion({"Why: CPU for I/O, and the price of level 9": _note}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, mo):
    dict_rows = mo.ui.slider(1000, 200000, step=1000, value=20000, label="Rows", show_value=True, debounce=True)
    dict_unique = mo.ui.slider(2, 1000, step=1, value=20, label="Unique values", show_value=True, debounce=True)
    dict_value_bytes = mo.ui.slider(1, 40, step=1, value=10, label="Bytes per value", show_value=True, debounce=True)
    # One small column, encoded: each distinct value once, then a short code per row.
    _column = ["Zurich", "Basel", "Zurich", "Geneva", "Zurich", "Basel"]
    _codes = {_v: _i for _i, _v in enumerate(dict.fromkeys(_column))}
    _drawing = diagram(
        '<text x="0" y="30">as written</text>'
        + "".join(box(150 + _i * 118, 8, _v, w=110) for _i, _v in enumerate(_column))
        + '<path class="dg-edge" d="M480 60 V 92"/>'
        + '<text x="0" y="122">dictionary</text>'
        + "".join(box(150 + _c * 150, 100, f"{_c} = {_v}", w=140, cls="dg-tier") for _v, _c in _codes.items())
        + '<text x="0" y="192">codes</text>'
        + "".join(box(150 + _i * 58, 170, str(_codes[_v]), w=50, cls="dg-tier") for _i, _v in enumerate(_column))
        + '<text class="dg-muted" x="510" y="197">2 bits each instead of 5 or 6 bytes</text>',
        width=1000,
        height=226,
        label="The column Zurich, Basel, Zurich, Geneva, Zurich, Basel becomes a dictionary of three values "
        "and the codes 0, 1, 0, 2, 0, 1.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Dictionary Encoding (Toy Model)"),
            _drawing,
            mo.hstack([dict_rows, dict_unique, dict_value_bytes], widths="equal"),
        ],
        gap=0.6,
    ).callout(kind="neutral")
    return dict_rows, dict_unique, dict_value_bytes


@app.cell
def _(TIER, alt, chart_or_table, dict_rows, dict_unique, dict_value_bytes, format_bytes, math, mo, pd, tier_chart):
    _code_bits = math.ceil(math.log2(dict_unique.value))
    _raw_bytes = dict_rows.value * dict_value_bytes.value
    _dictionary_bytes = dict_unique.value * dict_value_bytes.value
    _index_bytes = dict_rows.value * _code_bits / 8
    _ratio = (_dictionary_bytes + _index_bytes) / _raw_bytes

    _rows = [
        {"metric": "Raw storage (no dictionary)", "formula": "rows x bytes_per_value", "value": _raw_bytes},
        {"metric": "Dictionary storage", "formula": "unique_values x bytes_per_value", "value": _dictionary_bytes},
        {"metric": "Code size per row", "formula": "ceil(log2(unique_values)) bits", "value": _code_bits},
        {"metric": "Encoded indexes storage", "formula": "rows x code_bits/8", "value": round(_index_bytes, 2)},
        {"metric": "Estimated encoded/raw ratio", "formula": "(dictionary + indexes) / raw", "value": round(_ratio, 4)},
        {"metric": "Estimated savings", "formula": "1 - ratio", "value": f"{(1 - _ratio) * 100:.2f}%"},
    ]
    _parts = pd.DataFrame(
        {
            "stored": ["every value in full", "dictionary + codes", "dictionary + codes"],
            "part": ["values in full", "dictionary", "codes"],
            "bytes": [_raw_bytes, _dictionary_bytes, _index_bytes],
            "order": [0, 0, 1],
        }
    )
    _totals = pd.DataFrame(
        {
            "stored": ["every value in full", "dictionary + codes"],
            "bytes": [_raw_bytes, _dictionary_bytes + _index_bytes],
            "label": [format_bytes(_raw_bytes), f"{format_bytes(_dictionary_bytes + _index_bytes)}, ratio {_ratio:.2f}"],
        }
    )
    _y = alt.Y("stored:N", sort=None, title=None)
    _x = alt.X("bytes:Q", title="bytes", stack="zero", scale=alt.Scale(domain=[0, _totals["bytes"].max() * 1.35]))
    _chart = (
        alt.Chart(_parts)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            y=_y,
            x=_x,
            order="order:Q",
            color=alt.Color(
                "part:N",
                title=None,
                scale=alt.Scale(domain=["values in full", "dictionary", "codes"], range=[TIER["muted"], TIER["data"], "#8fb4ea"]),
            ),
            tooltip=["stored:N", "part:N", "bytes:Q"],
        )
        + alt.Chart(_totals).mark_text(align="left", dx=6).encode(y=_y, x="bytes:Q", text="label:N")
    ).properties(width="container", height=130)
    mo.vstack(
        [
            chart_or_table(tier_chart(_chart, "data"), _rows, label="Dictionary encoding (toy calculation)"),
            mo.md(
                f"Fewer unique values, fewer bits per code (here **{_code_bits}**). All unique, and the dictionary is the whole column."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Compression</h3>
      <details>
        <summary><strong>Q1:</strong> A 2 GB CSV crosses the network every minute. Compress it?</summary>
        <p><strong>Answer:</strong> Probably: over a network, moving bytes dominates. Time it on the real link.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> May sensor readings be rounded to save space?</summary>
        <p><strong>Answer:</strong> Only to the sensor's own precision, noted in the schema. Prices, ids, dates: never.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Why did the shuffled Parquet file in chapter 3 come out larger?</summary>
        <p><strong>Answer:</strong> Sorting puts equal values next to each other; dictionary and run-length encoding
        (a value stored once, with its repeat count) feed on that.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Chapter 4 Conclusion

    - Lossless gives back every byte; lossy an approximation, never for prices, ids or dates.
    - Compression feeds on repetition: five values per column handed Parquet the win.
    - Smaller is not automatically faster: in memory, unpacking costs CPU and saves no I/O.
            """
    ).callout(kind="success")
    return


@app.cell
def _(mo):
    mo.md(
        """
    ### Bridge to Next Chapter

    Smaller files help; the engine must also skip work:
    $\\text{query time} \\approx \\text{I/O time} + \\text{compute time}$.
    DuckDB reads only the columns and row groups a query needs, and computes on whole columns.
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
    ).properties(width="container", height=250, title="Time (best of 3 runs)")
    _sized = alt.Chart(
        pd.DataFrame({"source": _names, "bytes": [_s[2] for _s in _sources], "label": [format_bytes(_s[2]) for _s in _sources]})
    ).encode(
        y=alt.Y("source:N", sort=_names, title=None, axis=None),
        x=alt.X("bytes:Q", axis=None, scale=alt.Scale(domain=[0, max(_s[2] for _s in _sources) * 1.6])),
    )
    _size = (
        _sized.mark_bar(cornerRadiusEnd=4, color=TIER["muted"]) + _sized.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=250, title="File size")

    _size_note = (
        "Push Rows up and the CSV overtakes it." if _db_size > _csv_size else "At this size the CSV is already the bigger file."
    )
    mo.vstack(
        [
            chart_or_table(mo.hstack([tier_chart(_time, "data"), tier_chart(_size, "data")], widths=[2, 1], gap=2), _rows, label="One query, three sources (best of 3 runs)"),
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
    ).properties(width="container", height=180, title="Query time (ms), best of 5")
    _built = alt.Chart(_df).encode(
        y=alt.Y("state:N", sort=None, title=None, axis=None),
        x=alt.X("build (ms):Q", title=None, scale=alt.Scale(domain=[0, max(_df["build (ms)"].max(), 1) * 1.5])),
    )
    _build_chart = (
        _built.mark_bar(cornerRadiusEnd=4, color=TIER["muted"])
        + _built.mark_text(align="left", dx=6).encode(text=alt.Text("build (ms):Q", format=".1f"))
    ).properties(width="container", height=180, title="Build, once (ms)")

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
                mo.hstack([tier_chart(_query_chart, "data"), tier_chart(_build_chart, "data")], widths=[5, 2], gap=2),
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
        value=json.dumps(_body) if _body else "", rows=3, label="JSON body (sent with POST and PUT)", full_width=True
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
    ch7_json = mo.ui.text_area(value=json.dumps(ch7_preset.value, indent=2), rows=6, label="Student JSON", full_width=True)
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
            mo.md("### What the Two Verdicts Teach"),
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
                "How do partners learn what our API accepts, without emailing us?",
                "They open `/docs`, a manual FastAPI writes from the same code that checks every request, so "
                "it cannot go out of date. Then we run the API live and see what a server adds.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo):
    def _page(y, title, note):
        """One thing FastAPI writes from the type hints, with its edge from the FastAPI box."""
        return (
            f'<rect class="dg-box" x="600" y="{y}" width="396" height="58" rx="12"/>'
            f'<text x="620" y="{y + 24}" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="620" y="{y + 46}">{note}</text>'
            f'<path class="dg-edge" d="M500 150 C 550 150, 550 {y + 29}, 594 {y + 29}"/>'
        )

    _manual = diagram(
        '<rect class="dg-tier" x="0" y="60" width="340" height="180" rx="16"/>'
        '<text x="20" y="94" font-weight="700">the rule, written once</text>'
        '<text x="20" y="134" font-family="monospace" font-size="15">Rating = Annotated[int,</text>'
        '<text x="44" y="158" font-family="monospace" font-size="15">Field(ge=1, le=5)]</text>'
        '<text class="dg-muted" x="20" y="196">used by SaleCreate, SaleUpdate</text>'
        '<text class="dg-muted" x="20" y="220">and the rating filters</text>'
        '<path class="dg-edge" d="M340 150 H 374"/>'
        + box(380, 122, "FastAPI", w=120, h=56, cls="dg-tier")
        + '<text class="dg-muted" x="440" y="204" text-anchor="middle">reads the hints</text>'
        + _page(0, "422 for a rating of 9", "the rule, enforced before our code runs")
        + _page(76, "/openapi.json", "the manual, for partners' programs")
        + _page(152, "/redoc", "the manual, to read like a reference")
        + _page(228, "/docs (Swagger UI)", "the manual, with Try it out buttons")
        + '<rect class="dg-box dg-hot" x="0" y="300" width="340" height="64" rx="12"/>'
        '<text x="20" y="326">docstring: "recomputes total_price"</text>'
        '<text class="dg-muted" x="20" y="350">a behaviour, not a type</text>'
        '<path class="dg-edge dg-hot" d="M340 332 H 800 V 292"/>'
        '<text class="dg-hot" x="570" y="322" text-anchor="middle">typed by hand: nothing checks it</text>',
        width=1000,
        height=370,
        label="One line, Rating = Annotated[int, Field(ge=1, le=5)], goes into FastAPI, which writes four things from it: "
        "the 422 for a rating of 9, /openapi.json, /redoc and /docs. A hand-written docstring about recomputing "
        "total_price reaches /docs too, but nothing checks it.",
        tier="logic",
    )
    _more = mo.md(
        """
    - **OpenAPI** (`/openapi.json`) is a standard file format that lists every path an API has, what
      each one accepts and what it answers, for programs to read. A partner's script can be generated from it.
    - **Swagger UI** (`/docs`) reads that file and turns it into a page of buttons: open it and press *Try it out*.
    - **ReDoc** (`/redoc`) reads the same file and lays it out as a reference manual.
    - The rating rule is written once in `sw03_demo_api.py` and used for new sales, for edits and for
      the `min_rating`/`max_rating` filters. The schema can say `units_sold` must be at least 1; it
      cannot say that changing it recomputes `total_price`.
    - The server is the one you started for chapter 6 with `uvicorn sw03_demo_api:app`. While you
      *edit* the API, `--reload` restarts it on every save; during the lecture, leave it out.
        """
    )
    mo.vstack(
        [
            mo.md("### Where the Partners' Manual Comes From"),
            in_plain(
                "A **type hint** is a label on a field in our code: `customer_rating: Rating`, where `Rating` means "
                "a whole number from 1 to 5. FastAPI reads these labels twice: to turn away a sale with rating 9 "
                "(status **422**: the request has the wrong shape), and to write the manual partners open at "
                "`/docs`. One rule, two uses, so the manual cannot disagree with the check."
            ),
            _manual,
            mo.md(
                "**What to notice:** change the 5 to a 10 and all four boxes on the right change together, because "
                "there is only one 5. The red box is different: a docstring is typed by hand, and nothing checks it."
            ),
            mo.accordion({"The three manual pages, and the server behind them": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, html, in_plain, mo):
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

    The second docstring is the hand-written recompute rule from the previous slide. Sales are the
    resource this chapter follows, so every verb is written out; the four lookup tables (regions,
    countries, categories, products) share one generic set of five endpoints, registered by
    `add_lookup_endpoints`. Nothing else had to be written to get documentation.
    """)
    mo.vstack(
        [
            mo.md("### Read a Decorator as a Sentence"),
            in_plain(
                "A **decorator** is the `@` line above a function. It tells FastAPI which request runs the "
                "function: here a `POST` to `/sales`, where every new order from a sales rep arrives. Read it "
                "left to right like a sentence. Every piece of it also appears in `/docs`."
            ),
            _sentence,
            mo.md(
                "**What to notice:** `SaleCreate` has no `total_price`, so a rep cannot type in their own price: "
                "the server computes units × list price. Only the docstring on the last line is written by hand."
            ),
            mo.accordion({"The abridged source: the model and two endpoints": _source}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(api_base_url, call_api, mo, requests):
    from http.client import responses as ch8_phrases  # 201 -> "Created", for the answers below

    def ch8_stop(top, message):
        """Stop the cell with a red hint below `top`, the slide's heading and controls, so the slide keeps its buttons."""
        mo.stop(True, mo.vstack([top, mo.md(message).callout(kind="danger")], gap=0.6))

    def ch8_api(top, method, path, body=None):
        """call_api against the base URL. If nothing answers, or not with JSON, stops the cell via ch8_stop."""
        base = api_base_url.value.rstrip("/")
        try:
            status, answer = call_api(method, base + path, body)
        except requests.RequestException:
            ch8_stop(top, f"Could not reach `{base}`. Start the API first: `uvicorn sw03_demo_api:app`.")
        if answer and isinstance(answer, str):  # HTML or plain text, e.g. the Streamlit dashboard's port
            ch8_stop(top, f"`{base}{path}` answered `{status}`, but not with JSON. Is that the sales API?")
        return status, answer

    # The order the chapter 8 labs send: a rep in Germany (country 3) books 10 Edge Sensor X1 (product 1).
    sale_slip = {"sale_date": "2026-03-01", "product_id": 1, "country_id": 3, "units_sold": 10, "customer_rating": 5}
    return ch8_api, ch8_phrases, ch8_stop, sale_slip


@app.cell
def _(SEED_DIR, mo, pd):
    # Every chapter 8 control. Shown by the slides below, so this cell has no output (no slide of its own).
    fastapi_check = mo.ui.run_button(label="Is it running?", kind="success")
    # EdgeWorks launches a new sensor live. The API numbers it one past the last product in the seed files.
    _next_id = int(pd.read_parquet(SEED_DIR / "products.parquet")["product_id"].max()) + 1
    fastapi_payload = mo.ui.text_area(
        value='{"name": "Edge Sensor X2", "price": 245.0, "description": "Next-generation telemetry sensor", "category_id": 1}',
        label="The new product (JSON)",
        rows=2,
        full_width=True,
    )
    fastapi_post = mo.ui.run_button(label="1) POST /products", kind="success")
    fastapi_item_id = mo.ui.number(start=1, step=1, value=_next_id, label="Product id")
    fastapi_get = mo.ui.run_button(label="2) GET /products/{id}")
    # The latest answer to each button, so the slide shows both even though each click reruns it.
    ch8_answers, ch8_set_answers = mo.state({})
    run_gates = mo.ui.run_button(label="Send seven slips through both gates", kind="success")
    run_twice = mo.ui.run_button(label="Press every verb twice", kind="success")
    run_follow = mo.ui.run_button(label="Follow the order into the file", kind="success")
    run_two_analysts = mo.ui.run_button(label="Run the two-analyst test", kind="success")
    return (
        ch8_answers,
        ch8_set_answers,
        fastapi_check,
        fastapi_get,
        fastapi_item_id,
        fastapi_payload,
        fastapi_post,
        run_follow,
        run_gates,
        run_twice,
        run_two_analysts,
    )


@app.cell
def _(api_base_url, box, ch8_api, ch8_stop, diagram, fastapi_check, in_plain, mo):
    _base = api_base_url.value.rstrip("/")
    _top = mo.vstack(
        [
            mo.md("### Live: Is Our API Running?"),
            in_plain(
                "The API is a program of its own; the **base URL** is its address. We ask it for "
                "`/openapi.json`, the manual written for programs. If it answers, the API is up, and the "
                "answer lists every path it serves and every verb each path accepts."
            ),
            mo.hstack([api_base_url, fastapi_check], widths=[5, 1], align="end"),
        ],
        gap=0.6,
    )
    mo.stop(
        not fastapi_check.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "Start the API in a terminal (`uvicorn sw03_demo_api:app`), then click **Is it running?**"
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )
    _status, _schema = ch8_api(_top, "GET", "/openapi.json")
    if _status != 200:
        ch8_stop(_top, f"`{_base}/openapi.json` answered `{_status}`. Is that the sales API?")
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
            _top,
            mo.hstack(
                [
                    mo.stat(f"{_status} OK", label="GET /openapi.json", caption=f"{_schema['info']['title']} "
                            f"{_schema['info']['version']} is running", bordered=True),
                    mo.stat(len(_schema["paths"]), label="paths in the manual", bordered=True),
                    mo.md(f"**[Open {_base}/docs]({_base}/docs)**, the page partners read"),
                ],
                widths=[2, 1, 2],
                align="center",
            ),
            _matrix,
            mo.md(
                "**What to notice:** nobody typed this table. The API read it from its own code, and a partner "
                "sees the same paths and verbs at `/docs`."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(
    ch8_answers,
    ch8_api,
    ch8_phrases,
    ch8_set_answers,
    ch8_stop,
    fastapi_get,
    fastapi_item_id,
    fastapi_payload,
    fastapi_post,
    in_plain,
    json,
    mo,
):
    _top = mo.vstack(
        [
            mo.md("### Live: EdgeWorks Launches a New Sensor"),
            in_plain(
                "**POST** sends the new product; the API checks it, gives it the next free id and answers "
                "**201 Created**. **GET** with that id reads it back. Then press POST again: the name is taken "
                "now, so the answer is **400 Bad Request**, a fact about our data that no type hint can see."
            ),
            fastapi_payload,
            mo.hstack([fastapi_post, fastapi_item_id, fastapi_get], justify="start", align="end", gap=2),
        ],
        gap=0.6,
    )
    _answers = dict(ch8_answers())
    if fastapi_post.value:
        try:
            _payload = json.loads(fastapi_payload.value)
        except json.JSONDecodeError as _exc:
            ch8_stop(_top, f"The payload is not valid JSON: `{_exc}`")
        _answers["post"] = ("POST /products", *ch8_api(_top, "POST", "/products", _payload))
    if fastapi_get.value:
        _path = f"/products/{fastapi_item_id.value}"
        _answers["get"] = (f"GET {_path}", *ch8_api(_top, "GET", _path))
    ch8_set_answers(_answers)  # keeps both answers for the next click; this cell does not rerun itself

    def _answer(key, waiting):
        """The latest answer to one button, or what to do before there is one."""
        if key not in _answers:
            return mo.md(waiting).callout(kind="neutral")
        request, status, answer = _answers[key]
        return mo.md(
            f"`{request}` → **{status} {ch8_phrases.get(status, '')}**\n\n```json\n{json.dumps(answer, indent=2)}\n```"
        ).callout(kind="success" if status < 400 else "danger")

    mo.vstack(
        [
            _top,
            mo.hstack(
                [
                    _answer("post", "**Predict first:** which fields will the answer have that we did not send? Then click **1) POST /products**."),
                    _answer("get", "Then click **2) GET /products/{id}** to read it back."),
                ],
                widths="equal",
                align="start",
                gap=1,
            ),
            mo.md(
                "**What to notice:** we sent four fields and got six back. The server chose the `product_id` and "
                "looked up `category_name`; neither came from us."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(
    box,
    ch8_api,
    ch8_stop,
    diagram,
    in_plain,
    mo,
    pydantic,
    run_gates,
    sale_slip,
    static_table,
):
    _top = mo.vstack(
        [
            mo.md("### Try it: Seven Order Slips, Two Checks"),
            in_plain(
                "A rep's order reaches the API as a slip of JSON. We send seven slips, one good and six broken, "
                "through two checks. **Gate 1** is our model `SaleCreate`, run here on the laptop. **Gate 2** is "
                "the running API, which can also look things up in EdgeWorks' data."
            ),
            run_gates,
        ],
        gap=0.6,
    )
    mo.stop(
        not run_gates.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** which slips does the laptop catch, and which only the server? "
                    "Then click **Send seven slips through both gates**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )
    from sw03_demo_api import SaleCreate as _SaleCreate  # gate 1: the server's own model, no network

    _ok = sale_slip
    _slips = {
        "a good order": _ok,
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
        _status, _answer = ch8_api(_top, "POST", "/sales", _slip)
        if not (isinstance(_answer, dict) and ("detail" in _answer or "sale_id" in _answer)):
            ch8_stop(_top, f"`POST /sales` answered `{_status}`: `{_answer}`. Is that the sales API?")
        if _status == 201:
            _good = _answer
            ch8_api(_top, "DELETE", f"/sales/{_good['sale_id']}")  # leave the file as we found it
            _gate2, _short2 = f"201 created — {len(_good)} fields back, total_price {_good['total_price']}", "&#10003; 201 created"
        else:
            _detail = _answer["detail"]
            _why = _detail if isinstance(_detail, str) else _detail[0]["msg"]
            _gate2 = f"{_status} — {_why}"
            _short2 = f"&#10007; {_status} " + (_why if isinstance(_detail, str) else _detail[0]["loc"][-1])
        _rows.append({"the slip": _name, "gate 1: your laptop": _gate1, "gate 2: the server": _gate2})
        _cells.append((_name, _gate1 == "passes", _short1, _status, _short2))
    if _good is None:
        ch8_stop(_top, "Even the good order was refused. Restart the API to reseed its data.")

    # One row per slip, one box per gate: teal got through, red was turned away.
    _svg = [
        '<text x="430" y="16" text-anchor="middle" font-weight="700">gate 1: your laptop</text>'
        '<text x="805" y="16" text-anchor="middle" font-weight="700">gate 2: the server</text>'
    ]
    for _i, (_name, _pass1, _short1, _status, _short2) in enumerate(_cells):
        _y = 32 + _i * 44
        _svg.append(
            f'<text x="250" y="{_y + 18}" text-anchor="end" dominant-baseline="central">{_name}</text>'
            + box(270, _y, _short1, w=320, h=36, cls="dg-box dg-ok" if _pass1 else "dg-box dg-hot")
            + box(610, _y, _short2, w=386, h=36, cls="dg-box dg-ok" if _status == 201 else "dg-box dg-hot")
        )
    _matrix = diagram(
        "".join(_svg),
        width=1000,
        height=32 + 44 * len(_cells),
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

    _unit = _good["total_price"] / _good["units_sold"]
    _tiles = mo.md(
        f"""
    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">422</div><div class="tile-title">{_count(422)}: the wrong shape</div>
        <p>Same message at both gates: both run the same model. A typo never reaches Mia's revenue.</p></div>
      <div class="tile"><div class="tile-key">400</div><div class="tile-title">{_count(400)}: a fact</div>
        <p>The id is well formed. Only the server can look in EdgeWorks' product list and find no product 9999.</p></div>
      <div class="tile"><div class="tile-key">201</div><div class="tile-title">{_count(201)}: booked</div>
        <p>{len(_ok)} fields sent, {len(_good)} back. The server priced it: {_good["units_sold"]} &times;
        CHF {_unit:,.2f} = CHF {_good["total_price"]:,.2f}.</p></div>
    </div>
        """
    )
    _why = mo.md(
        f"""
    A price the client may send is a price the client can invent: 10 sensors for CHF 0.01 instead of
    CHF {_good["total_price"]:,.2f}. `SaleCreate` has no `total_price` field, and `Input` refuses fields it
    does not know, so the slip that brought its own `total_price` was refused at both gates.
        """
    )
    mo.vstack(
        [
            _top,
            mo.ui.tabs({"Chart": _matrix, "Table": _table}),
            _tiles,
            mo.accordion({"Why a rep may not send total_price": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, ch8_api, ch8_stop, chart_or_table, diagram, in_plain, mo, run_twice, sale_slip):
    _top = mo.vstack(
        [
            mo.md("### Try it: A Rep Presses Save Twice"),
            in_plain(
                "A rep's laptop times out and the rep presses Save again. A request is **idempotent** (safe to "
                "repeat) when sending it twice leaves the sales file just as sending it once did. We send each "
                "verb twice in a row, against one test order: 10 Edge Sensor X1 for Germany."
            ),
            run_twice,
        ],
        gap=0.6,
    )
    mo.stop(
        not run_twice.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** which verb changes the sales file again on the second press? "
                    "Then click **Press every verb twice**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    _post1, _first = ch8_api(_top, "POST", "/sales", sale_slip)
    if _post1 != 201:
        ch8_stop(_top, f"`POST /sales` answered `{_post1}`: `{_first}`")
    _post2, _second = ch8_api(_top, "POST", "/sales", sale_slip)
    _one = f"/sales/{_first['sale_id']}"
    _put1, _ = ch8_api(_top, "PUT", _one, {"units_sold": 25})
    _put2, _ = ch8_api(_top, "PUT", _one, {"units_sold": 25})
    _get1, _got = ch8_api(_top, "GET", _one)
    _get2, _ = ch8_api(_top, "GET", _one)
    _del1, _ = ch8_api(_top, "DELETE", _one)
    _del2, _ = ch8_api(_top, "DELETE", _one)
    ch8_api(_top, "DELETE", f"/sales/{_second['sale_id']}")  # tidy up the duplicate

    _rows = [
        {
            "verb": "GET",
            "first press": _get1,
            "second press": _get2,
            "what happened to the sales file": "nothing: GET only reads",
            "safe to repeat?": "yes",
        },
        {
            "verb": "POST",
            "first press": _post1,
            "second press": _post2,
            "what happened to the sales file": f"the order booked twice: #{_first['sale_id']} and #{_second['sale_id']}",
            "safe to repeat?": "NO",
        },
        {
            "verb": "PUT",
            "first press": _put1,
            "second press": _put2,
            "what happened to the sales file": f"units_sold is {_got['units_sold']} either way",
            "safe to repeat?": "yes",
        },
        {
            "verb": "DELETE",
            "first press": _del1,
            "second press": _del2,
            "what happened to the sales file": "the order is gone, both times",
            "safe to repeat?": "yes",
        },
    ]
    # One row per verb: the two status codes, then what the file looks like after both presses.
    _svg = [
        '<text x="235" y="20" text-anchor="middle" font-weight="700">first press</text>'
        '<text x="405" y="20" text-anchor="middle" font-weight="700">second press</text>'
        '<text x="748" y="20" text-anchor="middle" font-weight="700">what happened to the sales file</text>'
    ]
    for _i, _row in enumerate(_rows):
        _y, _safe = 40 + _i * 58, _row["safe to repeat?"] == "yes"
        _svg.append(
            f'<text x="0" y="{_y + 20}" font-weight="700">{_row["verb"]}</text>'
            f'<text class="dg-muted" x="0" y="{_y + 42}">{"safe to repeat" if _safe else "NOT safe to repeat"}</text>'
            + box(160, _y, str(_row["first press"]), w=150, h=48)
            + box(330, _y, str(_row["second press"]), w=150, h=48, cls="dg-box" if _safe else "dg-box dg-hot")
            + box(500, _y, _row["what happened to the sales file"], w=496, h=48, cls="dg-box dg-ok" if _safe else "dg-box dg-hot")
        )
    _matrix = diagram(
        "".join(_svg),
        width=1000,
        height=40 + 58 * len(_rows),
        label="Each verb sent twice. "
        + "; ".join(
            f"{_r['verb']}: {_r['first press']} then {_r['second press']}, {_r['what happened to the sales file']}"
            for _r in _rows
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
            _top,
            chart_or_table(_matrix, _rows, label="Each verb, sent twice"),
            mo.md(
                f"**GET, PUT and DELETE are safe to repeat:** the sales file ends up the same. **POST is not:** "
                f"the second press booked the order again, and Mia's revenue would count "
                f"CHF {_first['total_price']:,.2f} twice. The second DELETE answers `{_del2}` yet changes nothing: "
                "safe to repeat is about the effect, not the status code."
            ).callout(kind="info"),
            mo.accordion({"Idempotence is a promise, not a law": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(
    Path,
    box,
    ch8_api,
    ch8_stop,
    chart_or_table,
    diagram,
    duckdb,
    in_plain,
    mo,
    run_follow,
    sale_slip,
):
    _top = mo.vstack(
        [
            mo.md("### Try it: Follow One Order Into the Sales File"),
            in_plain(
                "The API is not a database. It checks an order, prices it and appends it as one row to "
                "`data/sales.parquet`, the data tier. We count the file's rows, POST one order, count again, and "
                "set the stored row beside the API's answer."
            ),
            run_follow,
        ],
        gap=0.6,
    )
    mo.stop(
        not run_follow.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** does the file store the product's name, or only its id? "
                    "Then click **Follow the order into the file**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )
    _sales_file = Path(mo.notebook_dir()) / "data" / "sales.parquet"
    if not _sales_file.exists():
        ch8_stop(_top, "Needs a running API started from this folder (it creates `data/sales.parquet`).")
    _con = duckdb.connect()
    _count = f"SELECT count(*) FROM '{_sales_file.as_posix()}'"
    _before = _con.sql(_count).fetchone()[0]
    _status, _created = ch8_api(_top, "POST", "/sales", sale_slip)
    if _status != 201:
        ch8_stop(_top, f"`POST /sales` answered `{_status}`: `{_created}`")
    try:
        _after = _con.sql(_count).fetchone()[0]
        _stored = _con.execute(
            f"SELECT * FROM '{_sales_file.as_posix()}' WHERE sale_id = ?", [_created["sale_id"]]
        ).df()
    finally:
        ch8_api(_top, "DELETE", f"/sales/{_created['sale_id']}")  # leave the file as we found it
    if _stored.empty:
        ch8_stop(
            _top,
            f"Order {_created['sale_id']} never reached `{_sales_file}`: the API at the base URL writes "
            "to another `data/` folder. Start it from this notebook's folder.",
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
    **What to notice:** the **file** keeps `product_id {_created["product_id"]}` and
    `country_id {_created["country_id"]}`: ids, every fact written once. The **answer** spells out
    "{_created["product_name"]}", "{_created["country_name"]}" and "{_created["region_name"]}": the logic tier
    did the joining, so Mia's dashboard does not have to.
        """
    )
    _more = mo.md(
        """
    The logic tier did not invent a database. It wrote to `data/sales.parquet`, a working copy of
    the file you compressed in chapter 4 and queried in chapter 5 (the API copies `data/seed/` into
    `data/` on every start). Even the date changes shape: the file keeps a timestamp, the API sends a
    plain date.

    **One honest callback.** We just read that file behind the API's back. The API takes a lock
    around every write, but like the booking pen in chapter 1, a lock only protects those who ask
    for it. Pandas rewrites the whole Parquet file on every change, so a read at the wrong instant
    could catch it half-written. That is chapter 1's isolation problem, and the reason a real system
    puts a database at the bottom of the data tier rather than a file.
        """
    )
    mo.vstack(
        [
            _top,
            chart_or_table(_trip, _rows, label="Same order, two tiers, two shapes"),
            _caption,
            mo.accordion({"Where the file came from, and one honest callback": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(ch8_api, ch8_stop, chart_or_table, in_plain, mo, run_two_analysts):
    _top = mo.vstack(
        [
            mo.md("### Try it: Two Analysts Change One Price"),
            in_plain(
                "Anna and Ben, two analysts, open Edge Sensor X1 at the same price. Anna saves a **10% raise**, "
                "then Ben saves a **CHF 20 surcharge** on the price he saw. Each save is one `PUT`, and the API "
                "locks the file during each one. Every sale booked afterwards is priced from what is left."
            ),
            run_two_analysts,
        ],
        gap=0.6,
    )
    mo.stop(
        not run_two_analysts.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** what does an Edge Sensor X1 cost afterwards? Write it down, then click "
                    "**Run the two-analyst test**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    def _price(method, body=None):
        """GET or PUT product 1 and return its price. Anything but 200 OK stops the cell."""
        status, answer = ch8_api(_top, method, "/products/1", body)
        if status != 200:
            ch8_stop(_top, f"`{method} /products/1` answered `{status}`: `{answer}`")
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
        ch8_api(_top, "PUT", "/products/1", {"price": _start})  # put the price back, like the other labs tidy up
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
          <div class="lu-header">Price on the server (CHF)</div>

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
            _top,
            mo.hstack(
                [
                    mo.stat(f"CHF {_correct:,.2f}", label="should be", bordered=True),
                    mo.stat(f"CHF {_final:,.2f}", label="is", bordered=True),
                    mo.stat(f"CHF {_correct - _final:,.2f}", label="lost on every sensor sold, and nobody was told", bordered=True),
                ],
                widths="equal",
            ),
            chart_or_table(_grid, _steps, label=f"Six requests, strictly in order (then the price goes back to {_start:.2f})"),
            mo.md(
                "**Chapter 1's lost update, over HTTP:** Anna's raise is gone, and both saves answered `200 OK`. "
                "The requests ran one after another, so it fails on every click: a design bug, not a timing fluke."
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
        <summary><strong>Q1:</strong> Gate 1 already checked the slip on the laptop. Why check it again at the server?</summary>
        <p><strong>Answer:</strong> A partner's script can skip this notebook and post straight to the API with
        <code>curl</code>. Checking on the laptop is a courtesy to the rep, instant feedback with no round trip,
        never a substitute for the server's check.</p>
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
    mo.vstack(
        [
            mo.md(
                """
    ### Chapter 8 Conclusion

    - Partners read `/docs`: FastAPI writes it from the models that check every request, so it cannot
      drift. A hand-written docstring can.
    - The shape is checked anywhere (422), facts only at the server (400). Only the server computes `total_price`.
    - GET, PUT and DELETE are safe to press twice; a second POST books the order twice.
    - A lock per request cannot stop a lost update split over two requests: send the change, or `If-Match`.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Bridge to Next Chapter

    The sales API is ready. Next: the dashboard Mia actually opens, and what to build it with.
    A correct API is worth little if nobody can use what it serves:

    $$
    \\text{user value} = \\text{backend correctness} \\times \\text{frontend usability}
    $$
                """
            ).callout(kind="neutral"),
        ],
        gap=1,
    )
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 9. Frontend Framework Comparison"),
            chapter_intro(
                "presentation",
                "What should we build the dashboard with?",
                "The sales API from chapter 8 serves the data. Now the part Mia actually opens: what a frontend "
                "must do, what it must not, and which tool fits our team.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo):
    def _tier(x, tier, name, note, file, rule, why):
        """One tier of Mia's stack: its colour, what it holds, and how it states the units rule."""
        return (
            f'<g class="tier-{tier}"><rect class="dg-tier" x="{x}" y="110" width="280" height="220" rx="16"/></g>'
            f'<text x="{x + 20}" y="144" font-size="20" font-weight="700">{name}</text>'
            f'<text class="dg-muted" x="{x + 20}" y="170">{note}</text>'
            + box(x + 20, 188, file, w=240, h=44)
            + f'<rect class="dg-box" x="{x + 20}" y="250" width="240" height="62" rx="12"/>'
            f'<text x="{x + 140}" y="276" text-anchor="middle" font-family="monospace" font-size="15">{rule}</text>'
            f'<text class="dg-muted" x="{x + 140}" y="300" text-anchor="middle">{why}</text>'
        )

    _stack = diagram(
        _tier(2, "presentation", "Mia's dashboard", "ch. 9-10: what Mia sees", "sw03_demo_streamlit.py",
              "min_value=1", "repeated for convenience")
        + _tier(360, "logic", "the sales API", "ch. 6-8: the rules", "sw03_demo_api.py", "ge=1, le=100_000", "the rule")
        + _tier(718, "data", "the sales files", "ch. 1-5: the facts", "data/*.parquet", "sales, products, ...",
                "five tables, ids only")
        # a request goes right, the answer comes back left
        + '<path class="dg-edge" d="M284 206 H 354"/><path class="dg-edge" d="M358 250 H 288"/>'
        + '<path class="dg-edge" d="M642 206 H 712"/><path class="dg-edge" d="M716 250 H 646"/>'
        + '<text class="dg-muted" x="321" y="196" text-anchor="middle">request</text>'
        + '<text class="dg-muted" x="321" y="274" text-anchor="middle">answer</text>'
        + '<text class="dg-muted" x="679" y="196" text-anchor="middle">query</text>'
        + '<text class="dg-muted" x="679" y="274" text-anchor="middle">rows</text>'
        # the side door: a partner's script calls the API without passing the dashboard
        + box(340, 10, "a partner's script · curl", w=320, h=48, cls="dg-box dg-hot")
        + '<path class="dg-edge dg-hot" d="M500 58 V 104"/>'
        + '<text class="dg-hot" x="512" y="88">no dashboard in between</text>',
        width=1000,
        height=340,
        label="Three tiers: Mia's dashboard (Streamlit, chapters 9 and 10) sends requests to the sales API "
        "(chapters 6 to 8), which queries the sales files (Parquet, chapters 1 to 5). The units rule sits in the "
        "API; the dashboard's form repeats only its lower bound. A partner's script or curl calls the API directly.",
    )
    _more = mo.md(
        """
    - **The payoff for splitting the tiers.** Move the sales files from Parquet to DuckDB and Mia
      notices nothing. Rebuild the whole dashboard, Streamlit for React, and the API does not change one line.
    - **What a frontend does.** It sends a request to a path, like `GET /sales?region=Europe`, and
      arranges whatever comes back so Mia can decide something.
    - **It still computes.** The dashboard sorts, formats, adds up and draws every chart. So do not
      read this as "the frontend is dumb". Read it as **the frontend owns no rules**.
    - **The same rule, twice, on purpose.** The Streamlit form sets `min_value=1` for units sold; the API
      states `Units = Annotated[int, Field(ge=1, le=100_000)]`. The form does not even repeat the upper
      limit: only the API knows it.
        """
    )
    mo.vstack(
        [
            mo.md("### The Dashboard Shows, the API Decides"),
            in_plain(
                "A **frontend** is the part people see and click. Mia's dashboard sends requests to the sales API "
                "and draws the answers. It owns no rules: a partner's script calls the API directly and never sees "
                "the dashboard, so every rule has to live in the API."
            ),
            _stack,
            mo.md(
                "**What to notice:** the dashboard's *Units sold* box starts at 1 (`min_value=1`), a convenience "
                "for Mia. The rule itself, 1 to 100,000 units, lives in the API, where the partner's script meets it too."
            ),
            mo.accordion({"Why split the tiers, and what a frontend still computes": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, in_plain, mo):
    # Ordered by the fit assistant's iteration-speed weight, fastest first.
    _frameworks = [
        ("Streamlit", "Python", "our data team, in Python", "fastest: the whole dashboard is one Python script",
         "little: Streamlit lays out the page", "Every click reruns the script; big apps get hard to steer"),
        ("Marimo", "Python", "our data team, in Python", "fast: a notebook becomes the app (this deck is one)",
         "some: cells, tabs, slides", "Notebook-first, not for a big public website"),
        ("Dash", "Python", "our data team, in Python", "medium: a callback wires each widget to its charts",
         "more: Plotly charts, many components", "The callbacks tangle as the dashboard grows"),
        ("Flask", "Python + JavaScript", "our team plus some HTML and JavaScript", "slow: we build every page and widget",
         "full: every pixel is ours", "More setup, no ready-made widgets"),
        ("React", "JavaScript", "a web developer, in JavaScript", "slowest to start: a second language and its tools",
         "full: any layout Mia asks for", "Needs a JS/TS stack, a build step and someone to maintain it"),
    ]
    _tiles = "".join(
        f'<div class="tile"><div class="tile-key">{_name}</div><div class="tile-title">{_lang}</div>'
        f"<p><strong>Who builds it:</strong> {_who}</p><p><strong>First version:</strong> {_speed}</p>"
        f'<p><strong>Layout control:</strong> {_control}</p><p class="tile-bad">{_bad}</p></div>'
        for _name, _lang, _who, _speed, _control, _bad in _frameworks
    )
    _tradeoff = diagram(
        '<text x="0" y="26" font-weight="700">faster first version</text>'
        '<path class="dg-edge" d="M400 20 H 190"/>'
        '<text class="dg-muted" x="500" y="26" text-anchor="middle">the usual trade-off</text>'
        '<path class="dg-edge" d="M600 20 H 810"/>'
        '<text x="1000" y="26" text-anchor="end" font-weight="700">more layout control</text>',
        width=1000,
        height=40,
        label="The usual trade-off: the further left, the faster the first version; the further right, the more layout control.",
    )
    mo.vstack(
        [
            mo.md("### Five Ways to Build Mia's Dashboard"),
            in_plain(
                "All five tools can draw Mia's dashboard. They differ in **who on our team can build it**, **how "
                "soon Mia sees a first version**, and **how much say we have over the layout**. Faster usually "
                "means less control."
            ),
            _tradeoff,
            mo.Html(f'<div class="tiles tier-presentation" style="grid-template-columns: repeat(5, 1fr)">{_tiles}</div>'),
            mo.md(
                "**What to notice:** the three Python tools need nobody new on the team; Flask and React need "
                "JavaScript, the language browsers run, and buy full control with it.\n\n"
                '<p class="vis-caption">A rough guide, not a measurement. Showcases: '
                '<a href="https://marimo.io/gallery">Marimo gallery</a> · '
                '<a href="https://dash.gallery/Portal/">Dash gallery</a> · '
                '<a href="https://react.dev/community">React community</a> · '
                '<a href="https://flask.palletsprojects.com/en/stable/patterns/">Flask patterns</a></p>'
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    # The fit assistant's three questions, about EdgeWorks, not about the tools. Shown by the slide below.
    fw_speed = mo.ui.slider(1, 5, value=5, label="Mia needs changes fast", show_value=True, debounce=True)
    fw_control = mo.ui.slider(1, 5, value=3, label="Mia needs a custom layout", show_value=True, debounce=True)
    fw_js = mo.ui.slider(1, 5, value=2, label="Our team knows JavaScript", show_value=True, debounce=True)
    return fw_control, fw_js, fw_speed


@app.cell
def _(
    TIER,
    alt,
    chart_or_table,
    fw_control,
    fw_js,
    fw_speed,
    in_plain,
    mo,
    pd,
    tier_chart,
):
    # Teaching heuristic, not a recommendation engine. Every weight row sums to 3.0,
    # so no framework wins just by carrying more weight than the others.
    _weights = {
        # framework:   (fast changes, custom layout, JavaScript), python_native
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
        {"framework": name, "score": score, "weights (speed / layout / JS)": " / ".join(map(str, _weights[name][0]))}
        for name, score in _ranked
    ]
    _df = pd.DataFrame(_rows)
    _df["best"] = _df["framework"].isin(_top)
    _bars = alt.Chart(_df).encode(
        y=alt.Y("framework:N", sort=None, title=None),
        x=alt.X("score:Q", title="fit score (higher = better fit)", scale=alt.Scale(domain=[0, 15])),
        tooltip=["framework:N", "score:Q", "weights (speed / layout / JS):N"],
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
    _more = mo.md(
        """
    **JavaScript** is the programming language browsers run. Marimo, Streamlit and Dash let our team
    stay in Python; React is written in JavaScript, and a Flask app needs some as soon as a page has to
    react. So a low score on that slider is not a weakness, it just points at different tools.

    Each framework scores the three answers with its own weights, and every weight row adds up to the
    same total (3.0), so no framework wins just by carrying more weight. For the three Python-native
    tools the JavaScript answer counts as $6 - j$: they get *more* attractive when the team knows *less*
    JavaScript. For Flask and React it counts as $j$. Heuristic only: check it against the real team.
        """
    )
    mo.vstack(
        [
            mo.md("### Try it: Which Tool Fits Our Team?"),
            in_plain(
                "Answer three questions about EdgeWorks, from 1 (not at all) to 5 (very much), not about the tools. "
                "Each tool weighs the answers differently: Streamlit cares most about speed, Flask about layout, and "
                "the three Python tools score higher the less JavaScript the team knows."
            ),
            mo.hstack([fw_speed, fw_control, fw_js], widths="equal", gap=2),
            chart_or_table(tier_chart(_chart, "presentation"), _rows, label="Fit score (higher = better fit)"),
            mo.md(
                "**What to notice:** at the start (changes fast, little JavaScript) Streamlit wins, which is why "
                "Mia's dashboard is `sw03_demo_streamlit.py`. Set speed to 2 and layout and JavaScript to 5: React "
                "takes over.\n\n"
                "**In one line:** $\\text{score} = w_s \\cdot \\text{speed} + w_c \\cdot \\text{layout} + w_j \\cdot "
                "\\text{JS}$, and each tool's three weights add up to 3."
            ),
            mo.accordion({"How the score works": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion — Frontends</h3>
      <details>
        <summary><strong>Q1:</strong> The dashboard's form already refuses 0 units. Why does the API check again?</summary>
        <p><strong>Answer:</strong> A partner's script calls the API directly, with <code>curl</code> or its own
        code, and never sees the form. A rule that lives only in the dashboard is not a rule. The form repeats it
        for convenience: instant feedback for Mia, no round trip.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> The fit assistant says Streamlit. Is that the decision?</summary>
        <p><strong>Answer:</strong> No, it is a teaching heuristic with hand-picked weights. Check it against
        real constraints: how much layout and state control the dashboard needs, who will maintain it, and
        what the team already knows.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md(
                """
    ### Chapter 9 Conclusion

    - A frontend sends requests and arranges the answers. It owns no rules, so the API enforces
      every rule again.
    - Choose by who will build it, how soon Mia needs it and how much layout control she needs:
      a faster first version usually costs control. For our Python team, Streamlit.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Bridge to Next Chapter

    The dashboard can draw any chart. The last question is which chart tells the truth: Mia wants
    one for the board, and a chart can show a pattern that is not there.

    $$
    \\text{what you plot} = \\text{signal} + \\text{noise}
    $$
                """
            ).callout(kind="neutral"),
        ],
        gap=1,
    )
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 10. Honest Charts (Signal vs Noise)"),
            chapter_intro(
                "presentation",
                "Does spending more make customers happier? Mia wants a chart for the board.",
                "A chart can show a pattern that is not there. First we learn to read how sure a trend line is, "
                "then we see three ways the same sales can tell three different stories.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(in_plain, mo, shop_sales, statistics):
    def ch10_fit(xs, ys):
        """The least-squares line through (xs, ys): slope beta, intercept alpha, the slope's standard error, R²."""
        beta, alpha = statistics.linear_regression(xs, ys)
        r2 = statistics.correlation(xs, ys) ** 2
        # Standard error of the slope: how far beta would wander if we drew other sales.
        se = ((1 - r2) / (len(xs) - 2)) ** 0.5 * statistics.stdev(ys) / statistics.stdev(xs)
        return beta, alpha, se, r2

    # Every real sale: CHF spent (in CHF 10,000s) against the customer's rating.
    _beta, _alpha, _se, _r2 = ch10_fit(list(shop_sales["total_price"] / 1e4), list(shop_sales["customer_rating"]))
    _clear = abs(_beta) > 2 * _se
    _more = mo.md(
        f"""
    - The line is $\\text{{rating}} = \\alpha + \\beta \\times \\text{{CHF spent}}$. Here
      $\\alpha = {_alpha:.2f}$, the rating the line gives a sale of CHF 0, and $\\beta = {_beta:+.3f}$, the
      change in rating per CHF 10,000.
    - The **standard error** (SE) of $\\beta$ is how much it would wobble if we had drawn other sales.
      $\\beta \\pm 2\\,\\text{{SE}}$ is the range we are about 95% sure of.
    - $R^2$ is the share of the spread in ratings the line explains: 0 is none, 1 is every dot on the line.
        """
    )
    mo.vstack(
        [
            mo.md("### Two Questions Every Trend Line Answers"),
            in_plain(
                "Put one dot per sale, CHF spent across and the customer's rating up, and draw the straight line "
                "that fits best. That line answers two different questions. **Is there a trend?** Does the rating "
                "really rise with spending, or could the slope be luck? **Does it predict one sale?** Do single "
                "sales sit close to the line?"
            ),
            mo.md(
                f"""
    <div class="tiles tier-presentation">
      <div class="tile"><div class="tile-key">{_beta:+.3f} &plusmn; {2 * _se:.3f}</div>
        <div class="tile-title">Trend: is there a slope? (&beta; &plusmn; 2 SE)</div>
        <p>Per CHF 10,000 spent, the rating rises {_beta:.3f} points, give or take {2 * _se:.3f}.
        {"The range stays clear of 0: the trend is real, if small." if _clear else "The range includes 0: no trend we can tell from luck."}</p></div>
      <div class="tile"><div class="tile-key">R&sup2; = {_r2:.2f}</div>
        <div class="tile-title">Fit: how close are the dots?</div>
        <p>Spending accounts for {_r2:.0%} of the differences in rating between sales. The other
        {1 - _r2:.0%} is everything else.</p></div>
    </div>
                """
            ),
            mo.Html(f'<p class="vis-caption">All {len(shop_sales):,} EdgeWorks sales, one dot each.</p>'),
            mo.md(
                "**What to notice:** a trend can be real and still predict single sales badly. They are two "
                "questions: read both numbers, never one."
            ),
            mo.accordion({"What α, β, SE and R² mean": _more}),
        ],
        gap=0.6,
    )
    return (ch10_fit,)


@app.cell
def _(mo):
    # The signal-or-noise lab's controls, shown by the slide below.
    ch10_effect = mo.ui.slider(
        -0.06, 0.06, step=0.01, value=0.05, label="True effect: rating points per CHF 10,000", show_value=True, debounce=True
    )
    ch10_sales = mo.ui.slider(
        steps=[50, 100, 200, 500, 1000, 2000, 3360], value=500, label="Sales we look at", show_value=True, debounce=True
    )
    ch10_draw = mo.ui.button(value=0, on_click=lambda n: n + 1, label="Draw other sales")
    return ch10_draw, ch10_effect, ch10_sales


@app.cell
def _(
    TIER,
    alt,
    ch10_draw,
    ch10_effect,
    ch10_fit,
    ch10_sales,
    chart_or_table,
    in_plain,
    mo,
    pd,
    random,
    shop_sales,
    statistics,
    tier_chart,
):
    _effect = round(ch10_effect.value, 2)
    _rng = random.Random(ch10_draw.value)
    _picked = _rng.sample(range(len(shop_sales)), ch10_sales.value)
    _xs = [shop_sales["total_price"].iat[_i] / 1e4 for _i in _picked]  # CHF 10,000s
    # Real ratings, drawn apart from the spend so spending says nothing, plus the effect set above.
    _base = _rng.sample(list(shop_sales["customer_rating"]), ch10_sales.value)
    _xbar = statistics.fmean(_xs)
    _ys = [_r + _effect * (_x - _xbar) for _r, _x in zip(_base, _xs, strict=True)]
    _beta, _alpha, _se, _r2 = ch10_fit(_xs, _ys)
    _clear = abs(_beta) > 2 * _se  # the ± range below excludes 0

    _trend = (
        "The range stays clear of 0: these sales rule out *spending changes nothing*."
        if _clear
        else "The range includes 0: these sales cannot tell this effect from no effect at all."
    )
    _fit = (
        "single sales sit close to the line"
        if _r2 >= 0.5
        else "a trend with plenty of scatter around it"
        if _r2 >= 0.15
        else "single sales sit far from the line"
    )
    _verdict = mo.md(
        f"**Trend:** $\\beta = {_beta:+.3f} \\pm {2 * _se:.3f}$ rating points per CHF 10,000 (you set {_effect:+.2f}). "
        f"{_trend}  \n"
        f"**Fit:** $R^2 = {_r2:.2f}$: spending explains {_r2:.0%} of the differences in rating between these "
        f"sales; {_fit}."
    ).callout(kind="success" if _clear else "warn")

    # The fan: every line whose slope lies in beta ± 2 SE, pivoting on the centre of the data.
    _ybar = statistics.fmean(_ys)
    _grid = [min(_xs) + (max(_xs) - min(_xs)) * _i / 40 for _i in range(41)]
    _ends = [((_beta - 2 * _se) * (_g - _xbar), (_beta + 2 * _se) * (_g - _xbar)) for _g in _grid]
    _fan = pd.DataFrame(
        {
            "x": [_g * 1e4 for _g in _grid],
            "low": [_ybar + min(_e) for _e in _ends],
            "high": [_ybar + max(_e) for _e in _ends],
            "flat": _ybar,
        }
    )
    _x = alt.X("x:Q", title="CHF spent on the sale", axis=alt.Axis(format="~s", tickCount=8))
    _y = alt.Y("y:Q", title="rating (simulated)", scale=alt.Scale(zero=False))
    _points = (
        alt.Chart(pd.DataFrame({"x": [_v * 1e4 for _v in _xs], "y": _ys}))
        .mark_circle(size=30, opacity=0.35, color=TIER["muted"])
        .encode(x=_x, y=_y)
    )
    _band = alt.Chart(_fan).mark_area(opacity=0.25, color=TIER["presentation"]).encode(x=_x, y=alt.Y("low:Q", title="rating (simulated)"), y2="high:Q")
    _flat = alt.Chart(_fan).mark_line(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"]).encode(x=_x, y=alt.Y("flat:Q", title="rating (simulated)"))
    _line = _points.transform_regression("x", "y").mark_line(color=TIER["presentation"], strokeWidth=4)
    _chart = (_band + _points + _flat + _line).properties(width="container", height=270)
    _summary = [
        {"quantity": "effect you set (rating per CHF 10,000)", "value": _effect},
        {"quantity": "fitted slope β", "value": round(_beta, 3)},
        {"quantity": "margin of error (2 SE)", "value": round(2 * _se, 3)},
        {"quantity": "intercept α", "value": round(_alpha, 3)},
        {"quantity": "R²", "value": round(_r2, 3)},
        {"quantity": "sales (n)", "value": len(_xs)},
    ]
    _more = mo.md(
        """
    - **Effect 0:** the equation still prints a slope, and the ± range includes 0, which tells you not to
      believe it. About 1 draw in 20 still clears the bar at effect 0: that is what 95% means.
    - **Effect 0.05**, about the size of the real slope on the previous slide: $R^2$ calls the line
      nearly useless, yet with 500 sales the slope is clearly real.
    - **More sales** shrink the ±, but they do not push $R^2$ up. $R^2$ measures how predictable single
      sales are, not whether a trend exists.
    - The ratings are simulated so that we know the truth: each sale keeps its real price, gets a real
      rating drawn from another sale, and then the effect you set is added.
        """
    )
    mo.vstack(
        [
            mo.md("### Try it: If Spending Really Moved Ratings, Would We See It?"),
            in_plain(
                "Here **you** set the truth. We take real EdgeWorks sales, give each one a real rating drawn from "
                "another sale, so spending says nothing, then add the effect you choose. The fitted line has to "
                "find that effect again among the real spread of ratings."
            ),
            mo.hstack([ch10_effect, ch10_sales, ch10_draw], widths=[3, 3, 1], align="center", gap=2),
            _verdict,
            chart_or_table(tier_chart(_chart, "presentation"), _summary, label="Regression summary"),
            mo.md(
                "**What to notice:** the orange fan holds every slope inside β ± 2 SE. Set the effect to 0: the "
                "dashed flat line fits inside the fan. Set 0.01 with 500 sales, then 3,360: the fan narrows until "
                "the effect shows, while R² stays near 0."
            ),
            mo.accordion({"What each experiment shows": _more}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    # The three-ways lab's control, shown by the slide below.
    honest_view = mo.ui.radio(
        options=[
            "A - average the sales into fewer dots",
            "B - split by category",
            "C - drop one category",
        ],
        value="A - average the sales into fewer dots",
        label="Ask the same question a different way",
        inline=True,
    )
    return (honest_view,)


@app.cell
def _(
    SEED_DIR,
    TIER,
    alt,
    chart_or_table,
    duckdb,
    honest_view,
    in_plain,
    mia_asks,
    mo,
    tier_chart,
):
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
        _trick = (
            "**The trick:** average many sales into one dot. Fewer dots means less disagreement between them, "
            "so the line looks tight."
        )
        _views = [
            ("one dot per sale", "sales", ()),
            ("per product per month", _averaged("product, month"), ()),
            ("per category per month", _averaged("category, month"), ()),
            ("per category", _averaged("category"), ()),
        ]
    elif honest_view.value.startswith("B"):
        _trick = (
            "**The trick:** one line through all sales, or one line per category. The all-sales line mostly "
            "measures the gap between the categories."
        )
        _cats = [_c for (_c,) in _con.execute("SELECT DISTINCT category FROM sales ORDER BY 1").fetchall()]
        _views = [("all sales pooled", "sales", ())] + [(f"only {_c}", "sales WHERE category = ?", (_c,)) for _c in _cats]
    else:
        _trick = "**The trick:** leave one category out, and the slope can change sign."
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
            width="container",
            height=220,
            title=alt.TitleParams(
                row["what we plotted"],
                subtitle=f"n {row['dots (n)']:,} · R² {row['R²']:.2f} · slope {slope:+.2f}",
                fontSize=15,
                subtitleFontSize=14,
            ),
        )

    _panels = mo.hstack(
        [
            tier_chart(_panel(_i, _row, _view[1], _view[2]), "presentation")
            for _i, (_row, _view) in enumerate(zip(_rows, _views, strict=True))
        ],
        widths="equal",
        gap=1,
    )

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
            mo.md("### Try it: Three Ways to Change the Answer Without Changing the Data"),
            mia_asks("Does spending more make customers happier? I need one chart for the board."),
            in_plain(
                f"Every view below uses the same {_rows[0]['dots (n)']:,} real sales and the same question: rating "
                "against CHF spent. Only the way we look changes. Each panel prints its number of dots (n), its R² "
                "and its slope."
            ),
            honest_view,
            mo.md(_trick),
            chart_or_table(_panels, _rows, label=f"Same {_rows[0]['dots (n)']:,} sales, same question"),
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
def _(ch10_fit, mo, shop_sales):
    _beta, _alpha, _se, _r2 = ch10_fit(list(shop_sales["total_price"] / 1e4), list(shop_sales["customer_rating"]))
    mo.vstack(
        [
            mo.md(
                f"""
    ### Chapter 10 Conclusion

    - Read a slope with its ± range, and $R^2$ with its $n$.
    - $R^2$ says how close single sales sit to the line, not whether a trend exists.
    - Averaging, splitting or dropping a group can reverse a finding without changing one row: say which you did.
    - For Mia's board: one dot per sale, the slope with its ±, and $n$. The rating rises
      {_beta:.3f} ± {2 * _se:.3f} per CHF 10,000 ($R^2$ {_r2:.2f}), and most of that is Services being both
      dear and well rated.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Next: the Wrap-up

    Mia asked ten questions today. One slide answers all ten, and one more puts them back on the map.
                """
            ).callout(kind="neutral"),
        ],
        gap=1,
    )
    return


@app.cell
def _(ch10_fit, mo, shop_sales):
    _beta, _alpha, _se, _r2 = ch10_fit(list(shop_sales["total_price"] / 1e4), list(shop_sales["customer_rating"]))
    _hardware = shop_sales[shop_sales["category"] == "Hardware"]
    _hw_beta = ch10_fit(list(_hardware["total_price"] / 1e4), list(_hardware["customer_rating"]))[0]
    _answers = [
        ("data", "Locks", "Both reps read the same count and each saved it + 1: 9 orders booked, 8 counted. A lock or "
         "one transaction makes read-and-save one step."),
        ("data", "Formats", "Parquet: it carries the types, so store code 007 stays text. CSV keeps characters only, and "
         "the reader guessed a number."),
        ("data", "Layout", "Because the file stores sales row by row. Stored by column, as Parquet does, the total reads "
         "only <code>total_price</code>."),
        ("data", "Compression", "Yes: lossless compression gives back every cent. It feeds on repetition, and sales "
         "columns repeat a lot."),
        ("data", "DuckDB", "Yes: DuckDB runs SQL straight on the Parquet files and reads only the columns and rows the "
         "query needs."),
        ("logic", "REST", "Over HTTP: a verb and a path (<code>GET /sales</code>), and a status code that says who "
         "must act."),
        ("logic", "Pydantic", "A model at the door (<code>SaleCreate</code>): rating 9 and 0 units come back as one 422 "
         "that lists both."),
        ("logic", "FastAPI", "They open <code>/docs</code>: FastAPI writes it from the same models that check every "
         "request."),
        ("presentation", "Frontends", "Streamlit: our Python team ships it fast, and the API keeps every rule."),
        ("presentation", "Honest charts", f"Barely: {_beta:+.3f} rating per CHF 10,000 (R² {_r2:.2f}), and inside "
         f"Hardware it {'falls' if _hw_beta < 0 else 'rises'}. Show the board each sale, the ± and n."),
    ]
    _items = "".join(
        f'<li class="tier-{_tier}"><strong>{_topic}</strong>: {_text}</li>' for _tier, _topic, _text in _answers
    )
    mo.md(
        f"""
    <div class="section-card">
      <h3>Wrap-up: Mia's Ten Questions, Answered</h3>
      <ol class="mia-list" style="font-size: 1.2rem; gap: 12px">{_items}</ol>
      <p class="vis-caption">Blue: the sales files (data tier). Pink: the sales API (logic tier). Orange: Mia's
      dashboard (presentation tier).</p>
    </div>
        """
    )
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
