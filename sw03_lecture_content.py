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
                "Two reps booked an order at the same moment. Why is today's order count too low?",
                "The very bottom of the data tier: before any format or layout, every save has to land. We lose an "
                "order on purpose, then keep it: first with a lock, then with a database.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(in_plain, mo, shop_sales):
    # The story's day: EdgeWorks' busiest day of January 2026, its last two orders booked at the same moment.
    _per_day = shop_sales[shop_sales["sale_date"].dt.to_period("M") == "2026-01"].groupby("sale_date").size()
    _day, ch1_day_orders = _per_day.idxmax(), int(_per_day.max())
    _before = ch1_day_orders - 2
    mo.vstack(
        [
            mo.md("### How an order goes missing from the count"),
            in_plain(
                "Mia's dashboard shows **orders booked today**, a number kept in one file. Every booking updates "
                "it in three steps: **read** the number, **add** one, **save** it back. If two reps both read "
                "before either one saves, both save the same number, and one order drops out of the count. "
                "This is called a **lost update**."
            ),
            mo.md(
                f"""
    <div class="section-card flow-card">
      <div class="lost-update-wrap">
        <div class="lost-update-grid">
          <div class="lu-header">Step</div>
          <div class="lu-header">Rep A books order {_before + 1}</div>
          <div class="lu-header">Rep B books order {_before + 2}</div>
          <div class="lu-header">Orders today (the file)</div>

          <div class="lu-step">1</div>
          <div class="lu-event lu-read">reads {_before}</div>
          <div class="lu-event lu-read">reads {_before}</div>
          <div class="lu-state">{_before}</div>

          <div class="lu-step">2</div>
          <div class="lu-event lu-write">saves {_before} + 1 = {_before + 1}</div>
          <div class="lu-event">adds 1 to the {_before} it read</div>
          <div class="lu-state">{_before + 1}</div>

          <div class="lu-step">3</div>
          <div class="lu-event lu-idle">done</div>
          <div class="lu-event lu-stale">saves {_before} + 1 = {_before + 1}</div>
          <div class="lu-state lu-problem">{_before + 1} (A's order overwritten)</div>
        </div>
      </div>
      <div class="flow-note"><strong>{_day.day} {_day:%B %Y}, the busiest day that month: {ch1_day_orders} orders
      booked, {ch1_day_orders - 1} counted.</strong> Both orders are in the order book; only the count lost one.</div>
    </div>
                """
            ),
            mo.md(
                "**What to notice:** nobody saw an error. Each rep did the right thing; the timing did the damage. "
                "B's save is **stale**: it is based on a number that changed after B read it."
            ),
            mo.md(
                f"**In one line:** lost orders = orders booked − orders counted, here {ch1_day_orders} − "
                f"{ch1_day_orders - 1} = 1."
            ),
        ],
        gap=0.8,
    )
    return (ch1_day_orders,)


@app.cell
def _(mo):
    ch1_sim_orders = mo.ui.slider(1, 6, value=2, label="Orders each rep books", show_value=True, debounce=True)
    ch1_sim_timing = mo.ui.slider(1, 999, value=7, label="Timing (try another)", show_value=True, debounce=True)
    return ch1_sim_orders, ch1_sim_timing


@app.cell
def _(
    TIER,
    alt,
    ch1_day_orders,
    ch1_sim_orders,
    ch1_sim_timing,
    chart_or_table,
    mo,
    pd,
    random,
    tier_chart,
):
    _start = ch1_day_orders - 2  # where the story above left the count
    _rng = random.Random(ch1_sim_timing.value)
    _ops = {_rep: ["read", "save"] * ch1_sim_orders.value for _rep in "AB"}
    _read, _count, _log = {}, _start, []
    while _ops["A"] or _ops["B"]:
        _rep = _rng.choice([_r for _r in "AB" if _ops[_r]])
        _action = _ops[_rep].pop(0)
        _before = _count
        if _action == "read":
            _read[_rep] = _count
        else:
            _count = _read[_rep] + 1
        _log.append(
            {
                "step": len(_log) + 1,
                "rep": f"rep {_rep}",
                "action": _action,
                "count before": _before,
                "number the rep read": _read[_rep],
                "count after": _count,
                "note": "stale save" if _action == "save" and _read[_rep] != _before else "",
            }
        )

    _booked = _start + 2 * ch1_sim_orders.value
    _df = pd.DataFrame(_log)
    _df["kind"] = [_note or _action for _action, _note in zip(_df["action"], _df["note"], strict=True)]
    # A read shows the number it got, a save the number it left; short labels once the steps get narrow.
    _short = len(_df) > 12
    _df["label"] = [
        f"{_a[0].upper()}{_v}" if _short else f"{_a} {_v}"
        for _a, _v in zip(_df["action"], _df["count after"], strict=True)
    ]
    _df["orders booked"] = _start + (_df["action"] == "save").cumsum()
    _df["orders counted"] = _df["count after"]
    _x = alt.X("step:O", title="step", axis=alt.Axis(labelAngle=0))
    _lane = alt.Chart(_df).encode(x=_x, y=alt.Y("rep:N", title=None, axis=alt.Axis(minExtent=60)))
    _lanes = (
        _lane.mark_rect(cornerRadius=8).encode(
            color=alt.Color(
                "kind:N",
                title=None,
                scale=alt.Scale(domain=["read", "save", "stale save"], range=["#cfe0fb", TIER["data"], TIER["hot"]]),
            )
        )
        # fixed text colours: the fills above are the same in both themes
        + _lane.mark_text().encode(
            text="label:N", color=alt.condition("datum.kind == 'read'", alt.value("#0b1220"), alt.value("white"))
        )
    ).properties(width="container", height=110)
    _series = ["orders counted", "orders booked"]
    _counter = (
        alt.Chart(_df)
        .transform_fold(_series, as_=["series", "value"])
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=_x,
            y=alt.Y("value:Q", title="orders today", scale=alt.Scale(zero=False), axis=alt.Axis(minExtent=60)),
            color=alt.Color("series:N", title=None, scale=alt.Scale(domain=_series, range=[TIER["data"], TIER["muted"]])),
            strokeDash=alt.StrokeDash("series:N", title=None, scale=alt.Scale(domain=_series, range=[[1, 0], [6, 4]])),
        )
        .properties(width="container", height=170)
    )
    _stale = int((_df["note"] == "stale save").sum())

    mo.vstack(
        [
            mo.md("### Try it: rep A and rep B, step by step"),
            mo.md(
                f"Both reps start from the count of {_start} and book their orders. Every booking is two steps, "
                "**read** the count, then **save** it plus one. The timing slider shuffles who moves when, as on "
                "a real day: neither rep sees the other's screen."
            ),
            mo.hstack([ch1_sim_orders, ch1_sim_timing], widths="equal", gap=2),
            mo.hstack(
                [
                    mo.stat(_booked, label="orders booked", bordered=True),
                    mo.stat(_count, label="orders counted", bordered=True),
                    mo.stat(_booked - _count, label="lost from the count", bordered=True),
                ],
                widths="equal",
            ),
            chart_or_table(
                mo.vstack([tier_chart(_lanes, "data"), tier_chart(_counter, "data")]),
                _log,
                label="Every step, in order",
            ),
            mo.md(
                f"**What to notice:** {_stale} red stale save{'s' if _stale != 1 else ''}. A save turns red when the "
                "other rep saved between its read and its save, and it erases every order saved in that gap. "
                "Try other timings: the count is only right when no save is stale."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo):
    # Three reps who ask for the pen, one script that never does.
    _people = "".join(
        box(0, _y, _label, w=330, cls=_cls)
        for _y, _label, _cls in [
            (20, "rep 1 · holds the pen, books", "dg-tier"),
            (92, "rep 2 · waits for the pen", "dg-box"),
            (164, "rep 3 · waits for the pen", "dg-box"),
            (240, "import script · never asks", "dg-box dg-hot"),
        ]
    )
    _lock_map = diagram(
        _people
        + box(440, 64, "one pen per file", w=250, h=104, cls="dg-tier")
        + '<text class="dg-muted" x="565" y="194" text-anchor="middle">the OS hands it out: flock</text>'
        + box(820, 92, "orders_today.txt", w=200, h=48)
        + '<path class="dg-edge dg-ok" d="M330 42 C 390 42, 380 92, 434 92"/>'
        + '<path class="dg-edge" d="M330 114 H 434"/>'
        + '<path class="dg-edge" d="M330 186 C 390 186, 380 140, 434 140"/>'
        + '<path class="dg-edge dg-ok dg-flow" d="M690 116 H 814"/>'
        + '<path class="dg-edge dg-hot" d="M330 262 H 920 V 146"/>'
        + '<text class="dg-hot" x="625" y="250" text-anchor="middle">no flock call: saves straight away</text>',
        width=1020,
        height=290,
        label="Three reps queue for one pen (the OS file lock); only the rep holding it saves to orders_today.txt. "
        "An import script never asks for the pen and saves to the file directly.",
        tier="data",
    )
    _more = mo.md(
        """
    - The OS takes the pen back from a program that crashes, so a crash in the middle of a booking does
      **not** block the file forever.
    - There is a second kind of lock that many may hold at once, for reading but not saving (`LOCK_SH`).
      The lab below asks for the exclusive one, `LOCK_EX`.
    - The pen lies on *one* desk. Two computers sharing a network drive each have their own desk, which is
      why file locks are unreliable on a network filesystem.
    - **Where it breaks:** the rule is only as good as the people. A database does not rely on an
      agreement: every write goes through its lock, whether the program asked or not.
        """
    )
    mo.vstack(
        [
            mo.md("### A file lock is one booking pen at the sales desk"),
            in_plain(
                "A **file lock** lets one program at a time work on a file. Picture one pen at the sales desk: "
                "only the rep holding it may update the count, and the others wait for it. The operating system "
                "(OS) hands out the pen when a program calls `flock`, and only to programs that ask."
            ),
            _lock_map,
            mo.md(
                "**What to notice:** the import script at the bottom. A file lock is an agreement, not a door: "
                "a program that never asks for the pen saves anyway."
            ),
            mo.accordion({"Where the picture holds, and where it breaks": _more}),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(in_plain, mo):
    mo.vstack(
        [
            mo.md("### What a database promises: ACID"),
            in_plain(
                "A database groups changes into a **transaction**: a few steps it carries out as one unit, then "
                "**commits** them (keeps them all) or **rolls them back** (undoes them all). ACID names four "
                "promises a database makes about every transaction. A plain file makes none of them."
            ),
            mo.md(
                """
    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">A</div><div class="tile-title">Atomicity: all or nothing</div>
        <p>Moving a sale from Europe to Africa changes both region totals, or neither.</p>
        <p class="tile-bad">File: a crash in between drops the sale from total revenue.</p></div>
      <div class="tile"><div class="tile-key">C</div><div class="tile-title">Consistency: rules always hold</div>
        <p>A rule such as "units sold is at least 1" is checked on every save.</p>
        <p class="tile-bad">File: nothing checks; a sale with 0 units is saved.</p></div>
      <div class="tile"><div class="tile-key">I</div><div class="tile-title">Isolation: one after the other</div>
        <p>Two reps booking at once both get counted, as if one booked after the other.</p>
        <p class="tile-bad">File: one save overwrites the other; the count is too low.</p></div>
      <div class="tile"><div class="tile-key">D</div><div class="tile-title">Durability: saved stays saved</div>
        <p>A booking the rep saw confirmed survives a power cut a second later.</p>
        <p class="tile-bad">File: only after flush and fsync, which force the bytes onto the disk.</p></div>
    </div>
                """
            ),
            mo.md(
                "**What to notice:** the next lab tests **I**, reps booking at once. The one after it tests **A**, "
                "a crash halfway through a change."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    # Checkboxes, not a multiselect: the room sees every way of counting and whether it is on.
    ch1_strategy_labels = {
        "no_lock": "file, no lock",
        "thread_lock": "file + lock in one program",
        "file_lock": "file + OS lock (the pen)",
        "sqlite_naive": "database: read, +1, save",
        "sqlite": "database: one UPDATE",
    }
    ch1_strategies = mo.ui.dictionary(
        {_key: mo.ui.checkbox(value=_key != "thread_lock", label=_label) for _key, _label in ch1_strategy_labels.items()}
    )
    ch1_reps = mo.ui.slider(2, 8, value=4, label="Sales reps booking at once", show_value=True, debounce=True)
    # Capped so the slowest setting (8 x 120 x 2 ms, paid in a queue by flock) stays near 3 s in all.
    ch1_orders_per_rep = mo.ui.slider(10, 120, step=5, value=35, label="Orders each rep books", show_value=True, debounce=True)
    ch1_pause = mo.ui.slider(0, 2, value=1, step=1, label="Pause between reading and saving (ms)", show_value=True, debounce=True)
    ch1_run_race = mo.ui.run_button(label="Run the bookings", kind="success")
    return (
        ch1_orders_per_rep,
        ch1_pause,
        ch1_reps,
        ch1_run_race,
        ch1_strategies,
        ch1_strategy_labels,
    )


@app.cell
def _(
    Path,
    TIER,
    alt,
    ch1_orders_per_rep,
    ch1_pause,
    ch1_reps,
    ch1_run_race,
    ch1_strategies,
    ch1_strategy_labels,
    chart_or_table,
    mo,
    pd,
    shop_sales,
    sqlite3,
    tempfile,
    threading,
    tier_chart,
    time,
):
    _notes = mo.md(
        """
    - **file, no lock**: every rep reads and saves the count file whenever they like.
    - **file + lock in one program**: a Python `threading.Lock`, a pen only the reps inside this one program
      can see. A second program would not wait for it.
    - **file + OS lock (the pen)**: `flock`, held from the read to the save.
    - **database: read, +1, save**: SQLite, but the rep reads the count, adds one in Python and saves the
      result: the same gap as the file.
    - **database: one UPDATE**: `UPDATE counter SET value = value + 1` in a transaction: the database reads
      and saves in one step.

    The **pause** is the time between reading the count and saving it. It widens the gap the race lives in,
    and a locked strategy pays it one rep at a time.
        """
    )
    _target = ch1_reps.value * ch1_orders_per_rep.value
    _january = int((shop_sales["sale_date"].dt.to_period("M") == "2026-01").sum())
    _top = mo.vstack(
        [
            mo.md("### Try it: reps booking at once, five ways to keep the count"),
            mo.md(
                "Every rep books their orders as fast as they can, all at the same time, and each booking adds one "
                f"to the same count. The start setting replays January 2026: 4 reps share its {_january} orders, "
                "35 each. Tick the ways of keeping the count to compare."
            ),
            mo.hstack([ch1_reps, ch1_orders_per_rep, ch1_pause], widths="equal", gap=2),
            mo.hstack(
                [ch1_strategies.hstack(justify="start", gap=1.5, wrap=True), ch1_run_race],
                justify="space-between",
                align="center",
            ),
            mo.accordion({"What each way of keeping the count does": _notes}),
        ],
        gap=0.6,
    )
    mo.stop(
        not ch1_run_race.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    f"**Predict first:** {ch1_reps.value} reps × {ch1_orders_per_rep.value} orders = {_target:,} "
                    "bookings. Which ways of keeping the count reach that number? Then click **Run the bookings**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    from concurrent.futures import ThreadPoolExecutor as _Pool
    from contextlib import nullcontext as _nullcontext

    try:
        import fcntl as _fcntl
    except ImportError:  # Windows has no flock
        _fcntl = None

    _reps, _orders, _pause_s = ch1_reps.value, ch1_orders_per_rep.value, ch1_pause.value / 1000

    def _race(rep):
        """Run `rep` in every thread at once; return the seconds until the last one finished."""
        start = time.perf_counter()
        with _Pool(_reps) as pool:
            for future in [pool.submit(rep) for _ in range(_reps)]:
                future.result()  # a rep that crashed raises here instead of passing as a lost booking
        return time.perf_counter() - start

    def _file_counter(path, mode):
        # Fixed width: nobody ever reads an empty or half-written number, so the only race
        # left is the read-then-save gap this demo is about.
        path.write_text(f"{0:010d}")
        guard = threading.Lock() if mode == "thread_lock" else _nullcontext()

        def rep():
            for _ in range(_orders):
                with guard, path.open("r+") as f:
                    if mode == "file_lock" and _fcntl:
                        _fcntl.flock(f, _fcntl.LOCK_EX)  # released when the file closes
                    current = int(f.read())
                    if _pause_s:
                        time.sleep(_pause_s)
                    f.seek(0)
                    f.write(f"{current + 1:010d}")

        return _race(rep), int(path.read_text())

    def _sqlite_counter(path, one_statement):
        con = sqlite3.connect(path)
        con.executescript(
            "PRAGMA journal_mode=WAL; CREATE TABLE counter (value INTEGER NOT NULL); INSERT INTO counter VALUES (0);"
        )
        con.close()

        def rep():
            conn = sqlite3.connect(path, timeout=30, isolation_level=None)
            conn.execute("PRAGMA synchronous=OFF")  # this demo is about isolation, not durability
            for _ in range(_orders):
                if one_statement:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute("UPDATE counter SET value = value + 1")
                    conn.execute("COMMIT")
                else:
                    (current,) = conn.execute("SELECT value FROM counter").fetchone()
                    if _pause_s:
                        time.sleep(_pause_s)
                    conn.execute("UPDATE counter SET value = ?", (current + 1,))
            conn.close()

        seconds = _race(rep)
        con = sqlite3.connect(path)
        (value,) = con.execute("SELECT value FROM counter").fetchone()
        con.close()
        return seconds, value

    _labels = dict(ch1_strategy_labels)
    if not _fcntl:
        _labels["file_lock"] = "file, no OS lock on Windows"
    _rows = []
    # No mo.status.spinner here: as a slide, a cell whose output blanks while it runs drops into marimo's edit preview.
    with tempfile.TemporaryDirectory() as _tmp:
        for _key, _label in _labels.items():
            if not ch1_strategies.value[_key]:
                continue
            if _key.startswith("sqlite"):
                _seconds, _counted = _sqlite_counter(Path(_tmp) / f"{_key}.db", one_statement=_key == "sqlite")
            else:
                _seconds, _counted = _file_counter(Path(_tmp) / f"{_key}.txt", _key)
            _rows.append(
                {
                    "way of keeping the count": _label,
                    "orders booked": _target,
                    "orders counted": _counted,
                    "lost from the count": _target - _counted,
                    "time taken (ms)": round(_seconds * 1000, 1),
                }
            )
    mo.stop(not _rows, mo.vstack([_top, mo.md("Tick at least one way of keeping the count.").callout(kind="warn")]))

    _df = pd.DataFrame(_rows)
    _df["verdict"] = [f"{_lost:,} lost" if _lost else "all counted" for _lost in _df["lost from the count"]]
    _y = alt.Y("way of keeping the count:N", sort=None, title=None)
    # room to the right of the longest bar for its "all counted" label
    _x = alt.X("orders counted:Q", title="orders counted", scale=alt.Scale(domain=[0, _target * 1.2], nice=False))
    _reached = alt.Chart(_df).encode(y=_y, x=_x)
    _counts = (
        _reached.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.condition("datum['lost from the count'] > 0", alt.value(TIER["hot"]), alt.value(TIER["data"]))
        )
        + _reached.mark_text(align="left", dx=6).encode(text="verdict:N")
        + alt.Chart(pd.DataFrame({"target": [_target]}))
        .mark_rule(strokeDash=[6, 4], strokeWidth=2, color=TIER["muted"])
        .encode(x="target:Q")
    ).properties(width="container", height=42 * len(_df), title=f"Orders counted (dashed line: {_target:,} booked)")
    _durations = (
        alt.Chart(_df)
        .encode(y=alt.Y("way of keeping the count:N", sort=None, title=None, axis=None), x=alt.X("time taken (ms):Q", title=None))
        .mark_bar(cornerRadiusEnd=4, color=TIER["muted"])
        .properties(width="container", height=42 * len(_df), title="Time taken (ms)")
    )
    _lost = {_r["way of keeping the count"]: _r["lost from the count"] for _r in _rows}
    _worst = max(_lost, key=_lost.get)

    mo.vstack(
        [
            _top,
            chart_or_table(
                mo.hstack([tier_chart(_counts, "data"), tier_chart(_durations, "data")], widths=[3, 1], gap=1),
                _rows,
                label="Bookings, counted five ways",
            ),
            mo.md(
                f"**What to notice:** *{_worst}* lost {_lost[_worst]:,} of {_target:,} orders, without a single error. "
                "Compare the two database bars: same database, but only the one-statement UPDATE counts every "
                "order. A transaction protects the steps you put inside it, and nothing else."
            ),
            mo.accordion(
                {
                    "Why the unlocked bars stop near one rep's total": mo.md(
                        """
    With a pause, the unlocked reps fall into step: all read the same count, all pause, all save the same
    +1. So they end near *one* rep's total, as if the others never booked. Set the pause to 0 and the file
    race turns messy: its count changes from run to run.

    The OS lock is correct but slow: reps queue, so every millisecond of pause is paid one rep at a time.
    The one-statement UPDATE is quick too: there is no gap for the pause to widen, and the lock is held for
    microseconds.
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
    ch1_crash = mo.ui.switch(value=True, label="Crash between the two saves")
    return (ch1_crash,)


@app.cell
def _(Path, ch1_crash, chart_or_table, diagram, json, mia_asks, mo, shop_sales, sqlite3, tempfile):
    # The move: the biggest German sale, booked under Germany (Europe) but meant for Kenya (Africa).
    _sale = shop_sales.loc[shop_sales.loc[shop_sales["country"] == "Germany", "total_price"].idxmax()]
    # Money in whole cents: an integer never picks up float rounding, so "the total held" is exact.
    _move = int(round(float(_sale["total_price"]) * 100))
    _initial = {_r: int(round(_v * 100)) for _r, _v in shop_sales.groupby("region")["total_price"].sum().items()}
    _expected = sum(_initial.values())
    _timeline = []

    def _add_timeline(system, step, totals, note):
        _timeline.append(
            {
                "system": system,
                "step": step,
                "Europe (CHF)": totals["Europe"] / 100,
                "Africa (CHF)": totals["Africa"] / 100,
                "total revenue (CHF)": sum(totals.values()) / 100,
                "note": note,
            }
        )

    with tempfile.TemporaryDirectory() as _tmp:
        # File: the region totals in one JSON file; the two saves are separate and nothing ties them together.
        _file_path = Path(_tmp) / "region_totals.json"
        _totals = dict(_initial)
        _file_path.write_text(json.dumps(_totals))
        _add_timeline("file (JSON)", "start", _totals, "region totals before the move")
        _totals["Europe"] -= _move
        _file_path.write_text(json.dumps(_totals))
        _add_timeline("file (JSON)", "take off Europe", _totals, "first save")
        if ch1_crash.value:
            _add_timeline("file (JSON)", "crash", _totals, "crash before the second save")
        else:
            _totals["Africa"] += _move
            _file_path.write_text(json.dumps(_totals))
            _add_timeline("file (JSON)", "add to Africa", _totals, "second save")
        _file_total = sum(json.loads(_file_path.read_text()).values())

        # SQLite: both saves inside one transaction.
        _con = sqlite3.connect(Path(_tmp) / "region_totals.db", isolation_level=None)
        _con.execute("CREATE TABLE region_totals (region TEXT PRIMARY KEY, cents INTEGER)")
        _con.executemany("INSERT INTO region_totals VALUES (?, ?)", _initial.items())

        def _db_totals():
            return dict(_con.execute("SELECT region, cents FROM region_totals").fetchall())

        _add_timeline("SQLite", "start", _db_totals(), "region totals before the move")
        _con.execute("BEGIN")
        _con.execute("UPDATE region_totals SET cents = cents - ? WHERE region = 'Europe'", (_move,))
        _add_timeline("SQLite", "take off Europe", _db_totals(), "inside the transaction, not committed")
        try:
            if ch1_crash.value:
                raise RuntimeError("simulated crash between the two saves")
            _con.execute("UPDATE region_totals SET cents = cents + ? WHERE region = 'Africa'", (_move,))
            _con.execute("COMMIT")
            _add_timeline("SQLite", "commit", _db_totals(), "both saves kept")
        except RuntimeError:
            _con.execute("ROLLBACK")
            _add_timeline("SQLite", "roll back", _db_totals(), "first save undone")
        _db_total = sum(_db_totals().values())
        _con.close()

    # One lane per system, one box per step: the two region totals after it, and total revenue at the end.
    _style = {"crash": "dg-box dg-hot", "add to Africa": "dg-box dg-ok", "commit": "dg-box dg-ok", "roll back": "dg-box dg-ok"}

    def _lane(y, system, label, total):
        steps = [_row for _row in _timeline if _row["system"] == system]
        parts = [f'<text x="0" y="{y + 50}" font-weight="700">{label}</text>']
        for _i, _row in enumerate(steps):
            x = 110 + _i * 270
            parts.append(
                f'<rect class="{_style.get(_row["step"], "dg-box")}" x="{x}" y="{y}" width="230" height="96" rx="12"/>'
                f'<text x="{x + 115}" y="{y + 28}" text-anchor="middle" font-weight="700">{_row["step"]}</text>'
                f'<text class="dg-muted" x="{x + 115}" y="{y + 56}" text-anchor="middle">Europe {_row["Europe (CHF)"]:,.0f}</text>'
                f'<text class="dg-muted" x="{x + 115}" y="{y + 80}" text-anchor="middle">Africa {_row["Africa (CHF)"]:,.0f}</text>'
            )
            if _i:
                parts.append(f'<path class="dg-edge" d="M{x - 36} {y + 48} H {x - 6}"/>')
        _ok = total == _expected
        parts.append(
            f'<text class="{"dg-ok" if _ok else "dg-hot"}" x="930" y="{y + 44}" font-size="22">'
            f"{'&#10003;' if _ok else '&#10007;'} {total / 100:,.0f}</text>"
        )
        if not _ok:
            parts.append(f'<text class="dg-hot" x="930" y="{y + 72}">{(_expected - total) / 100:,.2f} missing</text>')
        return "".join(parts)

    _picture = diagram(
        '<text x="930" y="18" font-weight="700">total revenue (CHF)</text>'
        + _lane(36, "file (JSON)", "file", _file_total)
        + '<rect x="370" y="176" width="520" height="120" rx="16" fill="none" stroke="currentColor"'
        ' stroke-dasharray="8 6" opacity="0.45"/>'
        + '<text class="dg-muted" x="630" y="322" text-anchor="middle">one transaction: BEGIN ... COMMIT or ROLLBACK</text>'
        + _lane(188, "SQLite", "SQLite", _db_total),
        width=1160,
        height=334,
        label=f"Moving CHF {_move / 100:,.2f} from Europe to Africa: the file ends with total revenue CHF {_file_total / 100:,.2f}, "
        f"SQLite with CHF {_db_total / 100:,.2f}; both should be CHF {_expected / 100:,.2f}.",
    )

    _file_ok = _file_total == _expected
    _file_callout = mo.md(
        "**File:** the two saves are separate. "
        + (
            "Both landed, because nothing crashed."
            if _file_ok
            else f"The crash came between them: CHF {_move / 100:,.2f} left Europe and never reached Africa."
        )
    ).callout(kind="success" if _file_ok else "danger")
    _db_callout = mo.md(
        "**SQLite:** both saves sit in one transaction. "
        + ("The crash rolled the first one back, so total revenue holds." if ch1_crash.value else "They committed together.")
    ).callout(kind="success" if _db_total == _expected else "danger")

    mo.vstack(
        [
            mo.md("### Try it: move a sale between regions, and crash halfway"),
            mia_asks(
                f"We moved one sale to the right region, and total revenue dropped by CHF {_move / 100:,.2f}. "
                "Where did the money go?"
            ),
            mo.md(
                f"Sale #{_sale['sale_id']} ({_sale['product']}, CHF {_sale['total_price']:,.2f}) was booked under "
                "Germany, but say it belongs to Kenya. Moving it takes two saves to the region totals (in CHF) that "
                "Mia's dashboard reads: **take it off Europe**, then **add it to Africa**. Moving a sale must never "
                "change total revenue."
            ),
            ch1_crash,
            chart_or_table(_picture, _timeline, label="Every step, in order"),
            mo.hstack([_file_callout, _db_callout], widths="equal"),
            mo.md("**What to notice:** the total revenue column. With the crash on, only the transaction keeps it at "
                  f"CHF {_expected / 100:,.2f}."),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: Atomicity & Concurrency</h3>
      <details>
        <summary><strong>Q1:</strong> With only files (no database), how could moving a sale between regions be made all-or-nothing?</summary>
        <p><strong>Answer:</strong> Write the new totals to a temporary file, then rename it over the old one: a rename is
        atomic, so a reader sees the old totals or the new ones, never half a move. Or write a small log entry first
        (a write-ahead log, WAL), and replay or roll it back on restart.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> What must always stay true here, and how would we notice it breaking?</summary>
        <p><strong>Answer:</strong> Orders counted equals orders booked, and moving a sale never changes total revenue.
        Check both after crashes and retries: counting the order book every night and comparing it with the counter
        catches a lost update.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Should a system stop on an error, or allow a short mismatch?</summary>
        <p><strong>Answer:</strong> Invoices and payments fail fast. Mia's dashboard may show a count a minute behind and
        repair it later (eventual consistency). Weigh the cost of wrong data against the cost of downtime.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(SALES_SEED, format_bytes, mo, shop_sales):
    _raw = ["sale_id", "sale_date", "product_id", "country_id", "units_sold", "total_price", "customer_rating"]
    _csv_bytes = len(shop_sales[_raw].to_csv(index=False).encode())
    mo.vstack(
        [
            mo.md(
                """
    ### Chapter 1 Conclusion

    - Two reps who both read before either saves lose an order: no error, just a count too low.
    - A lock (the booking pen) or a database transaction closes the gap between reading and saving.
    - A database is not magic: read, +1 in Python, save loses orders in SQLite too. Make the read and the
      save one statement, or one transaction.
    - A transaction makes a two-step change all or nothing: the crashed move rolled back, and total revenue held.
    - Check what must stay true (orders counted = orders booked; a move leaves total revenue alone) to catch
      these bugs early.
                """
            ).callout(kind="success"),
            mo.md(
                f"""
    ### Bridge to Next Chapter

    The counted sales now have to be saved to files and sent to partners. A partner waits for every byte,
    then for reading it: EdgeWorks' {len(shop_sales):,} sales take {format_bytes(_csv_bytes)} as CSV and
    {format_bytes(SALES_SEED.stat().st_size)} as the Parquet file in `data/seed/`.
                """
                + """
    $$
    \\text{wait} \\approx \\frac{\\text{bytes}}{\\text{throughput}} + \\text{parse time}
    $$

    Better formats cut the wait by shrinking the bytes or speeding up the reading.
                """
            ).callout(kind="neutral"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 2. Serialization & Deserialization Benchmarks"),
            chapter_intro(
                "data",
                "We send sales files to partners. Which format, and why did the CSV turn store code 007 into 7?",
                "Chapter 1 made every save land. Now: what the bytes of a sales file look like, and what each format "
                "costs, keeps and loses on its way to a partner.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(diagram, in_plain, json, mo, shop_sales):
    _sale = shop_sales.iloc[0]
    _record = {
        "sale_id": int(_sale["sale_id"]),
        "sale_date": f"{_sale['sale_date']:%Y-%m-%d}",
        "product": str(_sale["product"]),
        "units_sold": int(_sale["units_sold"]),
        "total_price": float(_sale["total_price"]),
    }
    _bytes = json.dumps(_record).encode()
    _value_bytes = sum(len(json.dumps(_v)) for _v in _record.values())
    # The bytes in the middle are the real start of this sale's JSON.
    _hex = _bytes[:24].hex(" ").upper()

    def _object(x, title):
        lines = "".join(
            f'<text x="{x + 140}" y="{98 + _i * 25}" text-anchor="middle">{_k} <tspan font-weight="700">{_v}</tspan></text>'
            for _i, (_k, _v) in enumerate(_record.items())
        )
        return (
            f'<rect class="dg-tier" x="{x}" y="30" width="280" height="200" rx="12"/>'
            f'<text x="{x + 140}" y="62" text-anchor="middle" font-weight="700">{title}</text>{lines}'
        )

    def _arrow(x, verb, word):
        return (
            f'<path class="dg-edge dg-flow" d="M{x} 130 H {x + 122}"/>'
            f'<text x="{x + 60}" y="116" text-anchor="middle" font-weight="700">{verb}</text>'
            f'<text class="dg-muted" x="{x + 60}" y="156" text-anchor="middle">{word}</text>'
        )

    _pipeline = diagram(
        _object(0, "a sale in Python")
        + _arrow(290, "serialize", "write")
        + '<rect class="dg-box" x="422" y="30" width="276" height="200" rx="12"/>'
        + '<text x="560" y="62" text-anchor="middle" font-weight="700">bytes</text>'
        + "".join(
            f'<text x="560" y="{110 + _i * 30}" text-anchor="middle" font-family="monospace">{_hex[_i * 24 : _i * 24 + 23]}</text>'
            for _i in range(3)
        )
        + '<text class="dg-muted" x="560" y="208" text-anchor="middle">... and so on</text>'
        + _arrow(708, "deserialize", "read")
        + _object(840, "the sale again")
        + '<text class="dg-muted" x="560" y="262" text-anchor="middle">'
        "on disk or on the wire: files for partners, API answers, queues, caches</text>",
        width=1120,
        height=276,
        label="EdgeWorks' first sale is serialized into bytes for a file or the network, and deserialized back into "
        "the same sale in Python.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Serialization: from a sale to bytes, and back"),
            in_plain(
                "**Serialization** turns an object in memory, here one EdgeWorks sale, into bytes that can be saved "
                "to a file or sent to a partner. **Deserialization** turns the bytes back into an object. The "
                "**format** (JSON, CSV, Parquet, ...) decides what those bytes look like."
            ),
            _pipeline,
            mo.md(
                f"**What to notice:** as JSON this sale takes {len(_bytes)} bytes, and only {_value_bytes} of them are "
                "the values. The rest is field names and punctuation, written again for each of the "
                f"{len(shop_sales):,} sales."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(box, diagram, fastavro, html, in_plain, io, mo, shop_sales):
    _first, _second = shop_sales.iloc[0], shop_sales.iloc[1]
    _typo = f"about {round(_second['total_price'], -3):,.0f}"  # what a hurried rep types instead of the price
    # The printed form refuses an answer that does not fit its box: the real error from the Avro writer.
    try:
        fastavro.writer(io.BytesIO(), {"type": "record", "name": "Sale", "fields": [{"name": "total_price", "type": "double"}]}, [{"total_price": _typo}])
        _refusal = "accepted"
    except (TypeError, ValueError) as _exc:
        _refusal = f"{type(_exc).__name__}: {str(_exc).split(': ')[0]}"

    def _date(sale):
        return f"{sale['sale_date']:%Y-%m-%d}"

    def _sheet(y, sale, price):
        return (
            f'<rect class="dg-box" x="0" y="{y}" width="470" height="70" rx="8"/>'
            f'<text x="18" y="{y + 28}" font-family="monospace">{{"sale_id": {sale["sale_id"]}, "sale_date": "{_date(sale)}",</text>'
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
        '<text x="0" y="22" font-weight="700">JSON: answers on blank paper</text>'
        + _sheet(40, _first, f"{_first['total_price']}")
        + _sheet(124, _second, f'<tspan class="dg-hot">"{_typo}"</tspan>')
        + '<text class="dg-muted" x="0" y="222">every sheet writes the field names out again</text>'
        + f'<text class="dg-hot" x="0" y="248">and nothing stops "{_typo}" in the price box</text>'
        + '<text x="540" y="22" font-weight="700">Avro: a printed order form</text>'
        + _form_row(40, [_label for _label, _ in _form_cells], "dg-tier")
        + _form_row(92, [f"{_first['sale_id']}", _date(_first), f"{_first['total_price']}"], "dg-box")
        + _form_row(140, [f"{_second['sale_id']}", _date(_second), f'<tspan class="dg-hot" text-decoration="line-through">{_typo}</tspan>'], "dg-box")
        + '<text class="dg-muted" x="540" y="222">names printed once; each row holds only answers</text>'
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
        label=f"Left: JSON sheets repeat every field name, and one has '{_typo}' in the price box. Right: an Avro form "
        f"prints the names once, each row holds only the answers, and the writer refuses '{_typo}'. "
        "The same form returns in chapters 5, 7 and 8.",
        tier="data",
    )
    _breaks = mo.md(
        """
    - A paper form travels with its answers: true for Avro, which stores the form in the file, and false
      for JSON and CSV. There the form exists only in the head of whoever reads the file, which is why a
      partner and EdgeWorks can disagree about what the same file means. That is the reason chapter 7 exists.
    - **Schema evolution** is what happens when EdgeWorks adds a box to the form: do last year's sales,
      written on the old form, still get read? A slide later in this chapter tests exactly that.
        """
    )
    mo.vstack(
        [
            mo.md("### The schema is the blank order form"),
            in_plain(
                "A **schema** is the blank form, not the answers: which fields a sale has, in what order, and what "
                "kind of value goes in each box. JSON and CSV send only filled-in sheets. Avro sends the form inside "
                "the file, and its writer refuses an answer that does not fit the box."
            ),
            _forms,
            mo.md(
                f"**What to notice:** the price of sale #{_second['sale_id']}. A rep typed \"{_typo}\". JSON keeps "
                "it without a word; Avro refuses it before it ever reaches a partner."
            ),
            mo.accordion({"Where the picture breaks, and what schema evolution means": _breaks}),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(in_plain, mo):
    _criteria = mo.md(
        """
    - **Speed**: how long writing and reading take
    - **Size**: how many bytes hit the disk and the network
    - **Interoperability**: which languages and tools can read it (Excel, R, a partner's script)
    - **Type fidelity**: do dates and store codes come back as dates and store codes?
    - **Schema evolution**: do old files survive a new field?
    - **Safety**: can loading a file run someone else's code?
        """
    )
    mo.vstack(
        [
            mo.md("### Five kinds of format, and where EdgeWorks uses each"),
            in_plain(
                "Text formats (JSON, CSV) can be read by any tool and by people. Binary formats are smaller and "
                "faster, but need a library to read. Choose by who reads the file and what they do with it."
            ),
            mo.md(
                """
    <div class="tiles tier-data" style="grid-template-columns: repeat(5, 1fr)">
      <div class="tile"><div class="tile-key">JSON</div><div class="tile-title">Text, row by row</div>
        <p>The sales API answers the dashboard in JSON; a partner opens CSV in Excel.</p></div>
      <div class="tile"><div class="tile-key">Avro</div><div class="tile-title">Rows + a schema</div>
        <p>The order event stream: each booking sent as it happens.</p></div>
      <div class="tile"><div class="tile-key">Arrow</div><div class="tile-title">Columns in memory</div>
        <p>Arrow / Feather: hands the sales table from DuckDB to pandas without converting it.</p></div>
      <div class="tile"><div class="tile-key">Parquet</div><div class="tile-title">Columns on disk</div>
        <p>EdgeWorks' sales files: <code>data/*.parquet</code>.</p></div>
      <div class="tile"><div class="tile-key">Pickle</div><div class="tile-title">Python objects</div>
        <p>Python only.</p><p class="tile-bad">Loading it can run code: never from a partner.</p></div>
    </div>
                """
            ),
            mo.md(
                "**What to notice:** compare them on speed, size, interoperability, type fidelity, schema evolution "
                "and safety. The labs in this chapter measure four of the six on EdgeWorks' sales."
            ),
            mo.accordion({"What each criterion asks": _criteria}),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo, shop_sales):
    _files = shop_sales["country"].nunique()
    _kenya = int((shop_sales["country"] == "Kenya").sum())

    def _doc(x, y, w, h):
        """A sheet of paper with a folded corner: one sales file."""
        f = min(w, h) * 0.3
        return (
            f'<path class="dg-box" d="M{x} {y} H {x + w - f} L {x + w} {y + f} V {y + h} H {x} Z"/>'
            f'<path d="M{x + w - f} {y} V {y + f} H {x + w}" fill="none" stroke="currentColor" opacity="0.5"/>'
        )

    # Sales booked through the day; the nightly export sends them all at 22:00.
    _hours = [8, 10, 12, 14, 16, 18, 20]

    def _at(hour):
        return 60 + (hour - 8) * 60

    _picture = diagram(
        '<text x="0" y="24" font-weight="700">Latency: how long one partner waits</text>'
        + _doc(10, 50, 70, 84)
        + f'<text x="45" y="156" text-anchor="middle" class="dg-muted">Kenya: {_kenya} sales</text>'
        + '<path class="dg-edge" d="M92 92 H 300"/>'
        + '<text x="196" y="80" text-anchor="middle" font-weight="700">write · send · read</text>'
        + box(308, 68, "partner in Kenya", w=180, h=48)
        + '<text x="560" y="24" font-weight="700">Throughput: how much one run gets through</text>'
        + '<rect class="dg-tier" x="570" y="48" width="300" height="88" rx="10"/>'
        + '<text x="720" y="84" text-anchor="middle" font-weight="700">nightly export</text>'
        + f'<text x="720" y="112" text-anchor="middle">{_files} files · {len(shop_sales):,} sales</text>'
        + '<path class="dg-edge" d="M876 92 H 930"/>'
        + '<text x="990" y="86" text-anchor="middle" font-weight="700">sales</text>'
        + '<text x="990" y="108" text-anchor="middle" font-weight="700">per second</text>'
        # the trade: the export waits for the last sale of the day, so the first one waits longest
        + '<text x="0" y="214" font-weight="700">They trade:</text>'
        + f'<path d="M{_at(8)} 262 H {_at(22) - 60}" stroke="currentColor" opacity="0.35" stroke-width="2"/>'
        + "".join(
            _doc(_at(_h) - 12, 238, 24, 28)
            + f'<text class="dg-muted" x="{_at(_h)}" y="290" text-anchor="middle">{_h:02d}:00</text>'
            for _h in _hours
        )
        + f'<rect class="dg-tier" x="{_at(22) - 60}" y="232" width="120" height="40" rx="10"/>'
        + f'<text x="{_at(22)}" y="257" text-anchor="middle">export 22:00</text>'
        + f'<path class="dg-edge dg-hot" d="M{_at(8)} 310 H {_at(22) - 64}"/>'
        + f'<text class="dg-hot" x="{(_at(8) + _at(22)) / 2:.0f}" y="336" text-anchor="middle">'
        "a sale booked at 08:00 reaches its partner 14 hours later</text>",
        width=1060,
        height=350,
        label=f"Latency: one partner, in Kenya, waits for its file of {_kenya} sales to be written, sent and read. "
        f"Throughput: the nightly export writes {_files} files with {len(shop_sales):,} sales and is measured in sales "
        "per second. Sales booked from 08:00 all wait for the 22:00 export, so batching raises throughput and makes "
        "the first sale wait 14 hours.",
        tier="data",
    )
    _more = mo.md(
        """
    - A container ship has terrible latency and huge throughput; a bicycle courier is the opposite.
    - In the benchmark, one round trip is a file written and read back, and throughput counts sales,
      not bytes.
    - *Sometimes you get both*, by making the file smaller. That is what chapter 4 is for.
        """
    )
    mo.vstack(
        [
            mo.md("### Latency vs throughput: two meanings of \"fast\""),
            in_plain(
                "**Latency** is how long one thing takes: a partner asks for its file, how long until it has it? "
                "**Throughput** is how much gets through per second: how many sales the nightly export writes. "
                "Collecting work into one big run raises throughput, and makes each single sale wait longer."
            ),
            _picture,
            mo.md(
                "**What to notice:** the 08:00 sale. The export sends everything in one efficient run at 22:00, so "
                "that sale is 14 hours late. When someone asks for \"fast\", ask which one they mean."
            ),
            mo.md(
                "**In one line:** latency = write time + read time of one file; throughput = sales written per second."
            ),
            mo.accordion({"Container ships, and how to get both": _more}),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo, shop_sales):
    ch2_rows = mo.ui.slider(
        140, len(shop_sales), step=140, value=len(shop_sales), label="Sales in the file", show_value=True, debounce=True
    )
    ch2_run_bench = mo.ui.run_button(label="Run the format benchmark", kind="success")
    return ch2_rows, ch2_run_bench


@app.cell
def _(
    Path,
    TIER,
    alt,
    best_seconds,
    ch2_rows,
    ch2_run_bench,
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
    shop_sales,
    static_table,
    tempfile,
    tier_chart,
):
    _top = mo.vstack(
        [
            mo.md("### Try it: six formats, the same EdgeWorks sales"),
            mo.md(
                "Each format writes EdgeWorks' first sales to a file and reads them back, the best of 3 tries. The "
                f"slider sets how many: one month is 140, the whole history {len(shop_sales):,}."
            ),
            mo.hstack([ch2_rows, ch2_run_bench], justify="start", align="center", gap=3),
        ],
        gap=0.6,
    )
    mo.stop(
        not ch2_run_bench.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** is the smallest file also the fastest? Then click **Run the format benchmark**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    _cols = ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"]
    _records = [
        _r | {"sale_date": _r["sale_date"].date()} for _r in shop_sales.head(ch2_rows.value)[_cols].to_dict("records")
    ]
    _avro_schema = {
        "type": "record",
        "name": "Sale",
        "fields": [
            {"name": "sale_id", "type": "long"},
            {"name": "sale_date", "type": {"type": "int", "logicalType": "date"}},
            {"name": "product", "type": "string"},
            {"name": "country", "type": "string"},
            {"name": "units_sold", "type": "long"},
            {"name": "total_price", "type": "double"},
            {"name": "customer_rating", "type": "long"},
        ],
    }

    def _csv_write(path):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_cols)
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
            lambda p: p.write_text(json.dumps(_records, default=str), encoding="utf-8"),  # dates as text
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
                    "sales/s written": round(len(_records) / _write_ms * 1000),
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
            "sales/s written:Q",
            axis=None,
            scale=alt.Scale(domain=[0, _df["sales/s written"].max() * 1.3]),
        ),
        tooltip=_tooltip,
    )
    _throughput = (
        _speed.mark_bar(cornerRadiusEnd=4).encode(color=_color)
        + _speed.mark_text(align="left", dx=6).encode(text=alt.Text("sales/s written:Q", format=".2s"))
    ).properties(width="container", height=300, title="Throughput: sales written per second")

    _by = {_r["format"]: _r for _r in _rows}

    def _name(row):
        return row["format"].removesuffix(" (unsafe)")

    _smallest = min(_rows, key=lambda _r: _r["size (KB)"])
    _quickest = min(_rows, key=lambda _r: _r["latency (ms)"])
    mo.vstack(
        [
            _top,
            chart_or_table(
                mo.hstack([tier_chart(_scatter, "data"), tier_chart(_throughput, "data")], widths=[3, 2], gap=2),
                _rows,
                label=f"{len(_records):,} sales, best of 3",
            ),
            mo.md(
                f"**What to notice:** the smallest file is {_name(_smallest)} ({_smallest['size (KB)']:,} KB, "
                f"against {_by['JSON']['size (KB)']:,} KB for JSON); the quickest round trip is "
                f"{_name(_quickest)} ({_quickest['latency (ms)']:,} ms)."
                + (" Quick, and the one format a partner could never safely open." if _quickest["format"].startswith("Pickle") else "")
                + " Do latency and throughput rank the formats the same way? "
                + f"Try {140 if len(_records) > 140 else len(shop_sales):,} sales too: does the ranking hold?"
            ),
            mo.accordion(
                {
                    "The sales being saved, and why the reads are not quite like for like": mo.vstack(
                        [
                            static_table(_records[:3], label="The first three sales, as every format receives them"),
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
def _(Path, box, diagram, in_plain, mo, pd, shop_sales, tempfile):
    # Each partner store has a three-digit code. For this demo, the code is the country's number:
    # South Africa's partner store is 007, the classic case of a code that looks like a number and is not.
    _src = shop_sales[["sale_id", "sale_date", "total_price"]].copy()
    _src["store_code"] = [f"{_n:03d}" for _n in shop_sales["country_id"]]
    _sa_sale = int(shop_sales.loc[shop_sales["country"] == "South Africa", "sale_id"].iloc[0])

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
        height=264,
        label="The same four columns written to CSV and to Parquet and read back. Parquet returns every type it was given; "
        "CSV returns sale_date as text and store_code as a whole number.",
    )

    def _span(_df):
        try:
            return str(_df["sale_date"].max() - _df["sale_date"].min())
        except TypeError as _exc:
            return f"TypeError: {_exc}"

    def _ask(name, df, kind):
        _code = df.loc[df["sale_id"] == _sa_sale, "store_code"].tolist()[0]
        return mo.md(
            f"""
    **Ask the {name} copy**

    - How long did sales run? `{_span(df)}`
    - South Africa's store code: `{_code!r}`
            """
        ).callout(kind=kind)

    _why = mo.md(
        """
    Open the CSV in a text editor and the date is right there: `2024-03-07`. The bytes did not lose the
    date. They lost **the note saying it was a date**, and that note is what the analysis was standing
    on. Parquet stores the date as a plain number and keeps the note in its schema, which is why it came
    back as a date.
        """
    )
    mo.vstack(
        [
            mo.md("### Why the CSV turned store code 007 into 7"),
            in_plain(
                "CSV is plain text with no note of what type each column is, so the reader guesses. "
                "`2024-03-07` stays text, and `007` looks like a number, so it becomes `7`. Parquet stores the "
                f"type next to the data. Here all {len(_src):,} sales, with each partner store's code (for this demo, "
                "the country number: South Africa is 007), go into both files and come back out."
            ),
            _types,
            mo.hstack([_ask("Parquet", _from_pq, "success"), _ask("CSV", _from_csv, "danger")], widths="equal", gap=1),
            mo.md(
                "**What to notice:** the date failure shouted (a `TypeError`); the store code failed silently. "
                "**That one ends up in a partner's report.**"
            ),
            mo.accordion({"What the CSV actually lost": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(csv, diagram, fastavro, html, in_plain, io, mo, shop_sales):
    # Next March, EdgeWorks starts recording each sale's channel: online or partner. Two years of old files sit
    # on disk, and one old program nobody redeployed is still running. What happens?
    _v1 = {
        "type": "record",
        "name": "Sale",
        "fields": [{"name": "sale_id", "type": "long"}, {"name": "total_price", "type": "double"}],
    }
    _v2 = {
        "type": "record",
        "name": "Sale",
        "fields": [
            {"name": "sale_id", "type": "long"},
            {"name": "total_price", "type": "double"},
            {"name": "channel", "type": "string", "default": "unknown"},
        ],
    }

    def _avro_bytes(_schema, _rows):
        _buf = io.BytesIO()
        fastavro.writer(_buf, _schema, _rows)
        return _buf.getvalue()

    _first, _last = shop_sales.iloc[0], shop_sales.iloc[-1]
    _old_file = _avro_bytes(_v1, [{"sale_id": int(_first["sale_id"]), "total_price": float(_first["total_price"])}])
    _new_file = _avro_bytes(
        _v2, [{"sale_id": int(_last["sale_id"]), "total_price": float(_last["total_price"]), "channel": "online"}]
    )

    _old_by_new = list(fastavro.reader(io.BytesIO(_old_file), reader_schema=_v2))
    _new_by_old = list(fastavro.reader(io.BytesIO(_new_file), reader_schema=_v1))

    _csv_row = next(csv.DictReader(io.StringIO(f"sale_id,total_price\n{_first['sale_id']},{_first['total_price']}\n")))
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
    mo.vstack(
        [
            mo.md("### Schema evolution: EdgeWorks adds a channel box to the form"),
            in_plain(
                "**Schema evolution** means changing the form while old files and old programs live on. EdgeWorks "
                "starts recording each sale's `channel`: `online` or `partner`. Old sales have no such box, so the "
                "new form gives it a **default**, `unknown`, for any sale written without it."
            ),
            _lanes_svg,
            mo.md(
                "**What to notice:** the bottom row. CSV ships without the form, so the agreement lives only in "
                "someone's memory, and every reader has to be changed by hand."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    ch2_use_case = mo.ui.dropdown(
        options=["Sales files for partners", "Dashboard cache", "Sales history for analysis", "Order event stream"],
        value="Sales files for partners",
        label="EdgeWorks job",
    )
    ch2_priority = mo.ui.dropdown(
        options=["Interoperability", "Speed", "Small size", "Safety"],
        value="Interoperability",
        label="What matters most",
    )
    return ch2_priority, ch2_use_case


@app.cell
def _(ch2_priority, ch2_use_case, mo):
    # one row per job, one entry per priority in the order of the priority dropdown
    _recommendations = {
        "Sales files for partners": ["CSV for spreadsheets, Parquet for data teams", "Parquet", "Parquet, compressed with zstd (chapter 4)", "CSV or Parquet; never Pickle"],
        "Dashboard cache": ["Parquet / Arrow", "Arrow (Feather), or Pickle we wrote ourselves", "Parquet", "Arrow or Parquet; no Pickle from outside"],
        "Sales history for analysis": ["Parquet", "Parquet or Arrow", "Parquet + zstd / snappy", "Parquet with schema checks"],
        "Order event stream": ["Avro / JSON", "Avro", "Avro with compression", "Avro + a schema registry: one shared copy of every form"],
    }
    _priorities = list(ch2_priority.options)
    _pick = (ch2_use_case.value, _priorities.index(ch2_priority.value))

    def _cell(text, chosen):
        """A grey grid cell; the chosen job, priority and recommendation stand out as tiles."""
        return f'<div class="tile"><strong>{text}</strong></div>' if chosen else f'<div class="focus-item">{text}</div>'

    _grid = [_cell("", False)] + [_cell(f"<strong>{_p}</strong>", _p == ch2_priority.value) for _p in _priorities]
    for _use, _row in _recommendations.items():
        _grid.append(_cell(f"<strong>{_use}</strong>", _use == _pick[0]))
        _grid += [_cell(_r, (_use, _i) == _pick) for _i, _r in enumerate(_row)]
    mo.vstack(
        [
            mo.md("### Try it: which format for which EdgeWorks job?"),
            mo.md(
                "Pick a job and what matters most for it. **Interoperability** means how many tools can read the "
                "file: Excel, R, a partner's script. A **cache** is a saved copy the dashboard reloads instead of "
                "asking again."
            ),
            mo.hstack([ch2_use_case, ch2_priority], justify="start", gap=2),
            mo.md(
                f"""
    <div class="section-card tier-data">
      <div style="display: grid; grid-template-columns: 230px repeat(4, 1fr); gap: 6px; font-size: 15px; line-height: 1.3">
        {"".join(_grid)}
      </div>
    </div>
                """
            ),
            mo.md(
                f"**Starting point: {_recommendations[_pick[0]][_pick[1]]}.** A default to benchmark on EdgeWorks' own "
                "files, not a rule."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: Serialization Choices</h3>
      <details>
        <summary><strong>Q1:</strong> A partner in Japan asks for "the sales as a file". CSV, JSON or Parquet?</summary>
        <p><strong>Answer:</strong> Ask what they open it with. Excel: CSV, with the column types written down
        (store codes are text). A data team: Parquet, which carries the types itself. A web app: JSON.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> A partner sends us their sales as a Pickle file. Do we load it?</summary>
        <p><strong>Answer:</strong> No. Loading Pickle can run any code the sender put in it. Ask for Parquet or
        CSV, and validate whatever comes in.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Before switching the nightly export to a new format, where do we measure size and speed?</summary>
        <p><strong>Answer:</strong> On the real export in a test setup (staging), then on a canary: one partner gets
        the new format first, while the others keep the old one.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(mo, shop_sales):
    _fields = 7  # sale_id, sale_date, product_id, country_id, units_sold, total_price, customer_rating
    mo.vstack(
        [
            mo.md(
                """
    ### Chapter 2 Conclusion

    - Formats trade speed, size, interoperability and safety: benchmark on EdgeWorks' own sales.
    - CSV keeps the values and drops the types (dates come back as text, store code `007` as `7`);
      Parquet and Avro carry the schema with the data.
    - Avro's reader defaults let old files and new code agree when the form changes.
    - Never load Pickle from a partner, or from anyone you do not trust.
                """
            ).callout(kind="success"),
            mo.md(
                f"""
    ### Bridge to Next Chapter

    Next: **lay the bytes out** on disk, by row or by column. Mia's "total revenue" needs one field of
    the {_fields} in each sale. A file laid out row by row still passes through all {_fields} fields of every
    sale: {_fields * len(shop_sales):,} values read to use {len(shop_sales):,}.
                """
                + """
    $$
    \\text{read work} \\propto \\text{rows read} \\times \\text{columns touched}
    $$
                """
            ).callout(kind="neutral"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## 3. Column-Based vs Row-Based Storage"),
            chapter_intro(
                "data",
                '"Total revenue" reads one column. Why does it read the whole file?',
                "The same sales can sit on disk sale by sale or field by field, and that choice decides how much "
                "of the file a question has to read.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    ch3_query = mo.ui.radio(
        options=["Total revenue", "Show me sale 3,082", "Revenue in January 2026"],
        value="Total revenue",
        label="Mia asks:",
        inline=True,
    )
    return (ch3_query,)


@app.cell
def _(ch3_query, diagram, in_plain, mo, shop_sales):
    _fields = ["id", "date", "product", "country", "units", "price", "rating"]
    _sales = list(range(3079, 3085))  # the last two sales of December 2025, then the first four of January 2026
    _first_jan, _lookup = 3081, 3082
    _q = ch3_query.value

    def _needed(sale, field):
        """Does Mia's question use this field of this sale?"""
        if _q == "Total revenue":
            return field == "price"
        if _q == "Revenue in January 2026":  # every date, to find January; the price of January's sales
            return field == "date" or (field == "price" and sale >= _first_jan)
        return sale == _lookup

    def _row_reads(sale, field):
        """A slip is picked up whole: every field of a sale the question touches is read."""
        return any(_needed(sale, _f) for _f in _fields)

    def _col_reads(sale, field):
        """A total reads a page top to bottom; a lookup jumps to one line of every page."""
        if _q.startswith("Show me"):
            return sale == _lookup
        return any(_needed(_s, field) for _s in _sales)

    _cls = {"used": "dg-tier", "wasted": "dg-hot", "idle": "dg-box"}

    def _cell(x, y, reads, sale, field):
        state = "used" if _needed(sale, field) else "wasted" if reads(sale, field) else "idle"
        opacity = ' opacity="0.45"' if state == "idle" else ""
        return f'<rect class="{_cls[state]}" x="{x}" y="{y}" width="52" height="26" rx="4"{opacity}/>'

    _parts = [
        '<text x="0" y="20" font-weight="700">Row layout: one slip per sale</text>',
        '<text x="600" y="20" font-weight="700">Column layout: one page per field</text>',
    ]
    for _j, _f in enumerate(_fields):
        _parts.append(f'<text class="dg-muted" x="{134 + _j * 56}" y="54" text-anchor="middle">{_f}</text>')
        _parts.append(f'<text class="dg-muted" x="{670 + _j * 59}" y="54" text-anchor="middle">{_f}</text>')
        _taken = any(_col_reads(_s, _f) for _s in _sales)
        _parts.append(
            f'<rect class="{"dg-tier" if _taken else "dg-box"}" x="{642 + _j * 59}" y="62" width="56" '
            f'height="{len(_sales) * 38 + 4}" rx="6" fill-opacity="0.35"/>'
        )
    for _i, _sale in enumerate(_sales):
        _y = 66 + _i * 38
        _picked = _row_reads(_sale, "id")
        _parts.append(f'<rect class="{"dg-tier" if _picked else "dg-box"}" x="104" y="{_y}" width="400" height="34" rx="6" fill-opacity="0.35"/>')
        _parts.append(f'<text class="dg-muted" x="96" y="{_y + 22}" text-anchor="end">{_sale}</text>')
        _parts.append(f'<text class="dg-muted" x="632" y="{_y + 22}" text-anchor="end">{_sale}</text>')
        _parts += [_cell(108 + _j * 56, _y + 4, _row_reads, _sale, _f) for _j, _f in enumerate(_fields)]
        _parts += [_cell(644 + _j * 59, _y + 4, _col_reads, _sale, _f) for _j, _f in enumerate(_fields)]
    # where January starts, across both layouts
    _jan_y = 66 + _sales.index(_first_jan) * 38 - 2
    _parts.append(f'<path d="M0 {_jan_y} H 1060" style="stroke: var(--ink-muted); stroke-width: 1.5; stroke-dasharray: 6 6"/>')
    _parts.append('<text class="dg-muted" x="0" y="88">Dec</text>')
    _parts.append(f'<text class="dg-muted" x="0" y="{_jan_y + 24}">Jan</text>')

    _used = sum(_needed(_s, _f) for _s in _sales for _f in _fields)
    _row_read = sum(_row_reads(_s, _f) for _s in _sales for _f in _fields)
    _col_read = sum(_col_reads(_s, _f) for _s in _sales for _f in _fields)
    _slips = sum(_row_reads(_s, "id") for _s in _sales)
    _pages = sum(any(_col_reads(_s, _f) for _s in _sales) for _f in _fields)
    _tally_y = 66 + len(_sales) * 38 + 32

    def _tally(x, grabbed, read):
        hot = ' class="dg-hot"' if read > _used else ""
        return f'<text x="{x}" y="{_tally_y}">{grabbed} · reads <tspan font-weight="700"{hot}>{read} fields</tspan> to use {_used}</text>'

    _parts.append(_tally(0, f"picks up {_slips} slip{'s' if _slips > 1 else ''}", _row_read))
    _parts.append(_tally(600, f"opens {_pages} page{'s' if _pages > 1 else ''}", _col_read))
    _parts += [
        f'<rect class="{_cls[_state]}" x="{_x}" y="{_tally_y + 22}" width="22" height="16" rx="3"/>'
        f'<text class="dg-muted" x="{_x + 30}" y="{_tally_y + 35}">{_label}</text>'
        for _x, _state, _label in [(0, "used", "needed"), (130, "wasted", "read, not needed"), (330, "idle", "left alone")]
    ]
    _picture = diagram(
        "".join(_parts),
        width=1060,
        height=_tally_y + 44,
        label=f"{_q}: on six sales, the row layout picks up {_slips} slips and reads {_row_read} fields; the column "
        f"layout opens {_pages} pages and reads {_col_read} fields; the question needs {_used}.",
        tier="data",
    )

    # The same counts on the whole file, and Mia's answer.
    _n = len(shop_sales)
    _jan = shop_sales[shop_sales["sale_date"].dt.strftime("%Y-%m") == "2026-01"]
    _one = shop_sales[shop_sales["sale_id"] == _lookup].iloc[0]
    if _q == "Total revenue":
        _notice = (
            f"**What to notice:** on all {_n:,} sales the row layout reads **{_n * 7:,}** fields, the column layout "
            f"**{_n:,}**: just the prices. Mia's answer: CHF {shop_sales['total_price'].sum():,.2f}."
        )
    elif _q == "Revenue in January 2026":
        _notice = (
            f"**What to notice:** on all {_n:,} sales the row layout reads **{_n * 7:,}** fields, the column layout "
            f"**{_n * 2:,}** (every date, every price) to use {_n + len(_jan):,}. Mia's answer: "
            f"CHF {_jan['total_price'].sum():,.2f} from {len(_jan)} sales."
        )
    else:
        _notice = (
            "**What to notice:** one sale is the row layout's home game. All 7 fields lie on one slip, while the column layout "
            f"opens 7 pages for one line each. Sale {_lookup:,}: {_one['sale_date'].day} {_one['sale_date']:%B %Y}, {_one['product']}, "
            f"{_one['country']}, {_one['units_sold']} units, CHF {_one['total_price']:,.2f}."
        )

    _story = mo.md(
        """
    **The shoebox.** Every sale is one till receipt: number, date, product, country, units, price and
    rating printed together on one slip. To total January you pick up every slip, read the date and
    the price, and put the other five fields down unread. That is a **row store**, and it is exactly
    right for *show me sale 3,082*: one slip, one grab. Row stores suit OLTP (Online Transaction
    Processing): booking, looking up and correcting single records, like the sales reps' order system.

    **The ledger.** The same sales copied into a ledger, one field per page. A total now means taking
    down one or two pages and leaving the rest on the shelf. That is a **column store**: right for
    totals over many sales and for compression, wrong for *show me sale 3,082*, which is now one line
    on seven different pages.

    *Two things the picture does not show.* The ledger pages are written in shorthand, so they are not
    all the same size: chapter 4. And a real ledger is cut into sections with an index at the back:
    two slides from here.
        """
    )
    mo.vstack(
        [
            mo.md("### Two Ways to Lay Out the Same Sales"),
            in_plain(
                "A file is one long line of bytes, so the sales have to go in some order. A **row layout** writes "
                "one whole sale after another, like a box of till receipts (CSV, Avro, most databases). A **column "
                "layout** writes one field after another, all 3,360 dates, then all 3,360 prices, like a ledger "
                "with one page per field (Parquet)."
            ),
            ch3_query,
            _picture,
            mo.md(_notice),
            mo.md("**In short:** a total over $N$ sales reads $N \\times 7$ fields in a row layout, $N \\times$ the fields it needs in a column layout."),
            mo.accordion({"The shoebox and the ledger, told in full": _story}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    n_rows = mo.ui.slider(250, 1000, step=250, value=1000, label="Sales in memory (thousands)", show_value=True, debounce=True)
    run_storage = mo.ui.run_button(label="Run storage benchmark", kind="success")
    return n_rows, run_storage


@app.cell
def _(TIER, alt, best_seconds, chart_or_table, mo, n_rows, np, pd, run_storage, shop_sales, tier_chart):
    _top = mo.vstack(
        [
            mo.md("### Try it: Total Revenue From a Row Layout and a Column Layout"),
            mo.md(
                "Our 3,360 real sales, repeated until there are up to a million (so the times are long enough to "
                "measure), kept twice in memory: sale by sale and field by field. Each run adds up one field, the "
                "price, while every sale carries 2, 4, 7 (our sales file) or 10 fields (list price, category and "
                "region joined in)."
            ),
            mo.hstack([n_rows, run_storage], justify="start", align="center", gap=2),
        ],
        gap=0.6,
    )
    mo.stop(
        not run_storage.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** as every sale carries more fields, which layout gets slower at adding up the "
                    "prices? Then click **Run storage benchmark**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    # The price first, then the rest of the sale row, then three fields joined in from products and countries.
    _fields = ["total_price", "sale_id", "sale_date", "product_id", "country_id", "units_sold", "customer_rating", "list_price", "category_id", "region_id"]
    _real = shop_sales[_fields].assign(sale_date=shop_sales["sale_date"].astype("int64")).to_numpy(dtype=float)
    _n = n_rows.value * 1000
    _all = np.tile(_real, (-(-_n // len(_real)), 1))[:_n]  # the real sales, repeated to n rows
    _operations = {
        "Total revenue (sum of prices)": lambda t: t[:, 0].sum(),
        "Big deals (count of sales over CHF 50,000)": lambda t: np.count_nonzero(t[:, 0] > 50_000),
    }
    _results = []
    for _cols in (2, 4, 7, 10):
        _row_store = np.ascontiguousarray(_all[:, :_cols])  # C order: each sale's fields side by side
        _col_store = np.asfortranarray(_row_store)  # F order: each field's values side by side
        for _operation, _fn in _operations.items():
            # best of 5: each operation takes milliseconds, so a stray hiccup would dominate
            _row_ms = best_seconds(_fn, _row_store, repeat=5) * 1000
            _col_ms = best_seconds(_fn, _col_store, repeat=5) * 1000
            _results.append(
                {
                    "question": _operation,
                    "fields per sale": _cols,
                    "row layout (ms)": round(_row_ms, 3),
                    "column layout (ms)": round(_col_ms, 3),
                    "column is faster by": f"{_row_ms / _col_ms:.1f}x",
                }
            )

    _df = pd.DataFrame(_results)
    _long = _df.melt(
        id_vars=["question", "fields per sale"], value_vars=["row layout (ms)", "column layout (ms)"], var_name="layout", value_name="ms"
    )
    _long["layout"] = _long["layout"].str.removesuffix(" (ms)")
    _x = alt.X("fields per sale:O", title="fields per sale", axis=alt.Axis(labelAngle=0))
    _charts = []
    for _operation in _operations:
        _lines = (
            alt.Chart(_long[_long["question"] == _operation])
            .mark_line(point=alt.OverlayMarkDef(size=90), strokeWidth=3)
            .encode(
                x=_x,
                y=alt.Y("ms:Q", title="ms"),
                color=alt.Color(
                    "layout:N", title=None, scale=alt.Scale(domain=["row layout", "column layout"], range=[TIER["hot"], TIER["data"]])
                ),
                tooltip=["layout:N", "fields per sale:O", "ms:Q"],
            )
        )
        # over each row-layout point: how many times faster the column layout was
        _speedup = (
            alt.Chart(_df[_df["question"] == _operation])
            .mark_text(align="right", dx=-8, dy=-12)
            .encode(x=_x, y="row layout (ms):Q", text="column is faster by:N")
        )
        _charts.append((_lines + _speedup).properties(width="container", height=260, title=_operation))

    _seven = _df[(_df["fields per sale"] == 7) & (_df["question"] == next(iter(_operations)))].iloc[0]
    _why = mo.md(
        """
    No file is written, so this is not CSV against Parquet, only the access pattern each one uses.
    Both questions read one field. In the row layout the prices sit a whole sale apart, and the CPU
    fetches memory in 64-byte cache lines, so it hauls in the neighbouring fields and throws them
    away. In the column layout the prices lie side by side and every byte fetched is used. Parquet
    goes further and never reads the unused columns from disk.
        """
    )
    mo.vstack(
        [
            _top,
            chart_or_table(mo.hstack([tier_chart(_c, "data") for _c in _charts], widths="equal", gap=2), _results, label="Row vs column layout, the same sales"),
            mo.md(
                f"**What to notice:** at 7 fields, our real sale, the column layout adds up the prices "
                f"**{_seven['column is faster by']}** faster ({_seven['column layout (ms)']:.2f} against "
                f"{_seven['row layout (ms)']:.2f} ms). Labels: how many times faster the column layout was."
            ),
            mo.md(
                "**In short:** to use 1 of $C$ fields, the row layout reads all $C$ and the column layout 1. The gap "
                "grows with $C$, though not exactly by $C$."
            ),
            mo.accordion({"Why: cache lines, and what Parquet adds": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SALES_SEED, box, diagram, in_plain, label_w, mo, pd):
    # The real sales in date order, cut into row groups of 420, as the lab on the next slide writes them.
    _dates = pd.read_parquet(SALES_SEED, columns=["sale_date"])["sale_date"].sort_values().reset_index(drop=True)
    _groups = [(_dates[_i : _i + 420].min(), _dates[_i : _i + 420].max()) for _i in range(0, len(_dates), 420)]
    _from, _to = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-31")
    # The footer can only rule a row group out: its dates end before January, or start after it.
    _open = [_hi >= _from and _lo <= _to for _lo, _hi in _groups]
    _wanted = [1, 5]  # the date and price chunks of the seven
    _query = "SUM(total_price) WHERE sale_date BETWEEN '2026-01-01' AND '2026-01-31'"

    def _rect(x, y, w, h, lit):
        """A row group or a column chunk: tier-coloured when the query reads it, faded when it stays shut."""
        return f'<rect class="{"dg-tier" if lit else "dg-box"}" x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="3" opacity="{1 if lit else 0.45}"/>'

    _parts = [box(0, 0, _query, cls="dg-tier")]
    _parts.append('<text class="dg-muted" x="0" y="90">row groups of 420 sales, 7 column chunks each</text>')
    for _g, _lit in enumerate(_open):
        _x = _g * 78
        _parts.append(f'<text x="{_x + 34}" y="122" text-anchor="middle" font-weight="700">{_g}</text>')
        _parts.append(_rect(_x, 132, 68, 170, _lit))
        _parts += [_rect(_x + 5 + _p * 8.5, 140, 7, 154, _lit and _p in _wanted) for _p in range(7)]
    # the footer: one line per row group, its smallest and largest date
    _parts.append('<rect class="dg-box" x="680" y="76" width="380" height="250" rx="10"/>')
    _parts.append('<text x="700" y="104" font-weight="700">footer: min and max sale_date</text>')
    for _g, (_lo, _hi) in enumerate(_groups):
        _y = 132 + _g * 24
        _parts.append(f'<text x="700" y="{_y}" font-family="monospace" font-size="15">{_g}  {_lo:%Y-%m-%d} .. {_hi:%Y-%m-%d}</text>')
        _parts.append(
            f'<text class="{"dg-ok" if _open[_g] else "dg-muted"}" x="1044" y="{_y}" text-anchor="end">{"open" if _open[_g] else "skip"}</text>'
        )
    _first_open = _open.index(True)
    _end = label_w(_query)
    _parts.append(f'<path class="dg-edge" d="M{_end:.0f} 22 H 870 V 70"/>')
    _parts.append(f'<text class="dg-muted" x="{(_end + 870) / 2:.0f}" y="14" text-anchor="middle">read the footer first</text>')
    _parts.append(f'<path class="dg-edge dg-ok" d="M676 {126 + _first_open * 24} H {_first_open * 78 + 74}"/>')
    _binder = diagram(
        "".join(_parts),
        width=1060,
        height=330,
        label=f"The sales in {len(_groups)} row groups of 420, seven column chunks each. The footer lists each row "
        "group's first and last date; only row groups whose dates can reach January 2026 are opened, and only "
        "their date and price chunks are read.",
        tier="data",
    )
    _fences = mo.md(
        """
    - The footer can prove a row group is **hopeless**, never that it is **useful**. A row group dated
      <code style="white-space: nowrap">2024-03-01 .. 2026-02-27</code> must be opened, and may hold no
      January sale at all. Min and max are a rejection test, not a search.
    - Row groups 0 to 6 are skipped not *probably* but **provably**: their latest date is before
      1 January 2026, so no sale inside them can be in January.
    - The order the sales were written in is not cosmetic. Write them in random order and every row
      group spans the whole two years, every min-max is useless, and all eight are opened. The
      mechanism did not fail; it was given nothing to work with. The next lab measures exactly that.
        """
    )
    _closed = _open.count(False)
    mo.vstack(
        [
            mo.md("### Inside a Parquet File: Row Groups, Column Chunks, a Footer"),
            in_plain(
                "Parquet cuts the ledger into sections. A **row group** is a block of sales (here 420, about three "
                "months). Inside it, each field's values sit together in a **column chunk**. At the end of the file, "
                "the **footer** keeps each chunk's smallest and largest value, its **min-max statistics**. A reader "
                "looks at the footer first and skips every row group that cannot hold a match."
            ),
            _binder,
            mo.md(
                f"**What to notice:** for Mia's January revenue the footer rules out {_closed} of {len(_groups)} row "
                f"groups without opening them, and in the one left only the date and price chunks are read: "
                f"**2 of {len(_groups) * 7} chunks**."
            ),
            mo.accordion({"What the footer can and cannot prove": _fences}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, TIER, alt, chart_or_table, diagram, duckdb, format_bytes, mia_asks, mo, pd, tempfile, tier_chart):
    _df = pd.read_parquet(SALES_SEED)
    _from, _to = "2026-01-01", "2026-02-01"
    _wanted = ["sale_date", "total_price"]
    _steps = ["every column", "date and price only", "date and price, footer skips"]

    with tempfile.TemporaryDirectory() as _td:
        _ordered = Path(_td) / "date_ordered.parquet"
        _shuffled = Path(_td) / "shuffled.parquet"
        _df.sort_values("sale_date").to_parquet(_ordered, index=False, row_group_size=420)
        _df.sample(frac=1, random_state=7).to_parquet(_shuffled, index=False, row_group_size=420)

        _con = duckdb.connect()
        _rows, _cards = [], {}
        _ordered_size, _shuffled_size = _ordered.stat().st_size, _shuffled.stat().st_size
        for _label, _path in (("sorted by date", _ordered), ("shuffled", _shuffled)):
            _md = _con.execute(
                "SELECT row_group_id, path_in_schema, total_compressed_size, stats_min, stats_max "
                f"FROM parquet_metadata('{_path.as_posix()}')"
            ).df()
            _two_cols = _md[_md["path_in_schema"].isin(_wanted)]
            # The footer: a row group survives unless its dates end before January or start after it.
            _dates = _md[_md["path_in_schema"] == "sale_date"].sort_values("row_group_id")
            _maybe = (_dates["stats_max"] >= _from) & (_dates["stats_min"] < _to)
            _live = _dates[_maybe]["row_group_id"]
            _cards[_label] = list(zip(_dates["stats_min"].str[:7], _dates["stats_max"].str[:7], _maybe))
            _answer = _con.execute(
                f"SELECT round(sum(total_price), 2) FROM '{_path.as_posix()}' WHERE sale_date >= '{_from}' AND sale_date < '{_to}'"
            ).fetchone()[0]
            _rows.append(
                {
                    "file": _label,
                    _steps[0]: int(_md["total_compressed_size"].sum()),
                    _steps[1]: int(_two_cols["total_compressed_size"].sum()),
                    _steps[2]: int(_two_cols[_two_cols["row_group_id"].isin(_live)]["total_compressed_size"].sum()),
                    "row groups opened": f"{len(_live)} of {_md['row_group_id'].nunique()}",
                    "January revenue (CHF)": _answer,
                }
            )
        _con.close()

    # One strip per file: every row group with its date range, opened (tier) or skipped (grey).
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
        label=f"File sorted by date: each row group spans three months and {_rows[0]['row groups opened']} are opened. "
        f"Shuffled file: every row group spans the whole two years and {_rows[1]['row groups opened']} are opened.",
        tier="data",
    )

    _bars = pd.DataFrame([{"file": _r["file"], "read": _s, "bytes": _r[_s]} for _r in _rows for _s in _steps])
    _bars["label"] = [format_bytes(_b) for _b in _bars["bytes"]]
    # red where the footer bought nothing: the last step still reads everything the one before it read
    _bars["nothing skipped"] = [_s == _steps[2] and _r[_steps[2]] == _r[_steps[1]] for _r in _rows for _s in _steps]
    _x = alt.X("bytes:Q", title=None, axis=None, scale=alt.Scale(domain=[0, _bars["bytes"].max() * 1.3]))
    _charts = []
    for _i, _file in enumerate(_cards):
        _base = alt.Chart(_bars[_bars["file"] == _file]).encode(
            y=alt.Y("read:N", sort=None, title=None, axis=alt.Axis(labelLimit=280) if _i == 0 else None),
            x=_x,
            tooltip=["file:N", "read:N", "bytes:Q"],
        )
        _charts.append(
            (
                _base.mark_bar(cornerRadiusEnd=4).encode(
                    color=alt.condition("datum['nothing skipped']", alt.value(TIER["hot"]), alt.value(TIER["data"]))
                )
                + _base.mark_text(align="left", dx=6).encode(text="label:N")
            ).properties(width="container", height=150, title=f"{_file}: bytes the query must read")
        )
    _sorted, _mixed = _rows
    _notes = mo.md(
        f"""
    - These are bytes the reader is *allowed to skip*, worked out from each file's own footer, not
      bytes measured leaving the disk.
    - The shuffled file is also {_shuffled_size / _ordered_size - 1:.0%} larger ({_shuffled_size:,} against
      {_ordered_size:,} bytes) from the very same sales: a preview of chapter 4, where order is itself a
      form of compression.
        """
    )
    mo.vstack(
        [
            mo.md("### Try it: Does the Order We Write Sales In Matter?"),
            mia_asks("What did we sell in January 2026?"),
            mo.md(
                "Our 3,360 sales written to Parquet twice, 420 to a row group: once sorted by date, once shuffled "
                "into random order. Each file's footer decides which row groups the January query may skip."
            ),
            _strip_svg,
            chart_or_table(mo.hstack([tier_chart(_c, "data") for _c in _charts], widths="equal", gap=2), _rows, label="Bytes the January query must read"),
            mo.md(
                f"**What to notice:** sorted by date, reading only two columns took the query from "
                f"**{format_bytes(_sorted[_steps[0]])}** to **{format_bytes(_sorted[_steps[1]])}**, and the footer took it to "
                f"**{format_bytes(_sorted[_steps[2]])}**. Shuffled, the footer skips **nothing** ({_mixed['row groups opened']} "
                f"opened). Both files answer CHF {_sorted['January revenue (CHF)']:,.2f}."
            ),
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
        <summary><strong>Q1:</strong> The sales reps book and correct single orders all day. Row or column layout?</summary>
        <p><strong>Answer:</strong> Row layout: each booking reads or writes one whole sale. That is OLTP (Online
        Transaction Processing), and it is what row databases are built for. Mia's dashboard reads column files.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> Mia's chart shows revenue per region. Which column chunks does it read?</summary>
        <p><strong>Answer:</strong> Two of seven: <code>total_price</code> and <code>country_id</code> (the country
        gives the region). Reading only the columns a query names is called projection pushdown.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> Why does the order we write sales in matter for Parquet?</summary>
        <p><strong>Answer:</strong> The footer can only skip a row group whose min-max range misses the filter.
        Sorted by date, each row group spans three months; shuffled, every one spans all two years.</p>
      </details>
    </div>
    """)
    return


@app.cell
def _(SALES_SEED, mo, pq):
    _meta = pq.ParquetFile(SALES_SEED).metadata
    _price = sum(
        _meta.row_group(_g).column(_c).total_compressed_size
        for _g in range(_meta.num_row_groups)
        for _c in range(_meta.num_columns)
        if _meta.row_group(_g).column(_c).path_in_schema == "total_price"
    )
    _file = SALES_SEED.stat().st_size
    mo.vstack(
        [
            mo.md(
                f"""
    ### Chapter 3 Conclusion

    - **Mia's answer:** "total revenue" reads the whole file when the file is a row layout (CSV, Avro): the
      prices sit between the other six fields of every sale. In our Parquet file it reads only the price
      column: {_price:,} of the file's {_file:,} bytes.
    - Row layouts suit booking and looking up single sales; column layouts suit totals over many sales.
    - Parquet's footer keeps min-max per row group: sorted by date, January 2026 opens 1 of 8 row groups;
      shuffled, all 8.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Bridge to Next Chapter

    A column puts similar values side by side: the same 3 categories, 7 products and 8 countries over and
    over. Repetition is what compression feeds on. Next: how small can the sales history get, without
    losing a cent?
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
            mo.md("## 4. Compression & Encoding (Parquet, Gzip)"),
            chapter_intro(
                "data",
                "The sales history fills the disk. Can we shrink it without losing a cent?",
                "Lossless compression shrinks a file and gives back every byte. This chapter measures how much it "
                "saves on our sales, and what unpacking costs.",
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(SALES_SEED, diagram, gzip, in_plain, mo, pd):
    _csv = pd.read_parquet(SALES_SEED).to_csv(index=False).encode()
    _gz = gzip.compress(_csv, 6)
    # A sketch of the timing model, not a measurement: segment lengths only show which step grows.
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
        '<text x="0" y="20" font-weight="700">Sent to the analyst in Berlin, over the network: moving bytes dominates</text>'
        + _bar(36, "plain CSV", [("read", 520), ("compute", 120)])
        + _bar(82, "gzipped CSV", [("read", 190), ("unpack", 110), ("compute", 120)], _faster)
        + '<text x="0" y="160" font-weight="700">Read by the dashboard, file already in memory: unpacking dominates</text>'
        + _bar(176, "plain CSV", [("read", 40), ("compute", 120)])
        + _bar(222, "gzipped CSV", [("read", 16), ("unpack", 110), ("compute", 120)], _slower),
        width=1000,
        height=270,
        label="A sketch: sent over the network, the gzipped file saves more read time than unpacking adds, so the total "
        "shrinks. Already in memory, there is little read time to save, and unpacking makes it slower.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### What Compression Trades: Fewer Bytes, More Unpacking"),
            in_plain(
                "Compression writes the same sales in fewer bytes by spotting repetition. The catch: every reader "
                "has to unpack the file before using it. So it pays when moving bytes is slow, as on the way to "
                "our analyst in Berlin, and costs time when the bytes are already in memory."
            ),
            _sketch,
            mo.md(
                f"**What to notice:** our sales as CSV are {len(_csv):,} bytes, gzipped {len(_gz):,} "
                f"({len(_gz) / len(_csv):.0%}). Unpacking costs the same in both pictures; only the read shrinks, so "
                "only a slow read makes it worth it. *A sketch, not a measurement: bar lengths show which step grows.*"
            ),
            mo.md(
                "**In short:** total time ≈ read + unpack + compute. The compression ratio "
                f"$r$ = compressed size / original size, here {len(_gz) / len(_csv):.2f}; it saves $1 - r$."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch4_sales_per_month = mo.ui.radio(
        options={"140 (today)": 140, "1,400": 1_400, "14,000": 14_000, "140,000": 140_000, "1.4 million": 1_400_000},
        value="140 (today)",
        label="Sales per month:",
        inline=True,
    )
    ch4_years_kept = mo.ui.slider(1, 10, value=2, label="Years of sales kept (today: 2)", show_value=True, debounce=True)
    budget_scans_day = mo.ui.slider(1, 80, value=20, label="Dashboard reads of the whole history per day", show_value=True, debounce=True)
    return budget_scans_day, ch4_sales_per_month, ch4_years_kept


@app.cell
def _(SALES_SEED, TIER, alt, budget_scans_day, ch4_sales_per_month, ch4_years_kept, format_bytes, gzip, mo, pd, tier_chart):
    _sales = pd.read_parquet(SALES_SEED)
    _csv = _sales.to_csv(index=False).encode()
    _per_sale = len(_csv) / len(_sales)  # bytes of CSV per sale, measured on today's file
    _r = len(gzip.compress(_csv, 6)) / len(_csv)  # the compression ratio gzip reaches on it
    _history = ch4_sales_per_month.value * 12 * ch4_years_kept.value * _per_sale
    _reads = budget_scans_day.value
    _day = pd.DataFrame({"stored": ["plain CSV", "gzipped CSV"], "bytes read per day": [_history * _reads, _history * _r * _reads]})
    _day["label"] = [format_bytes(_b) for _b in _day["bytes read per day"]]
    _base = alt.Chart(_day).encode(
        y=alt.Y("stored:N", sort=None, title=None),
        x=alt.X("bytes read per day:Q", title=None, axis=None, scale=alt.Scale(domain=[0, _day["bytes read per day"].max() * 1.2])),
        tooltip=["stored:N", "bytes read per day:Q"],
    )
    _bars = (
        _base.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("stored:N", legend=None, scale=alt.Scale(domain=["plain CSV", "gzipped CSV"], range=[TIER["muted"], TIER["data"]]))
        )
        + _base.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=110, title="Bytes the dashboard reads per day")
    mo.vstack(
        [
            mo.md("### Try it: How Big Does the Sales History Get?"),
            mo.md(
                f"Today the history is {len(_sales):,} sales, {format_bytes(len(_csv))} as CSV. Pick how fast EdgeWorks "
                f"grows and how long it keeps its sales. Assumed: every new sale takes as many bytes as today's "
                f"({_per_sale:.0f} as CSV), gzip keeps today's ratio ({_r:.2f}), and every dashboard read scans the "
                "whole history."
            ),
            ch4_sales_per_month,
            mo.hstack([ch4_years_kept, budget_scans_day], widths="equal", gap=2),
            mo.hstack(
                [
                    mo.stat(format_bytes(_history), label="History as plain CSV", bordered=True),
                    mo.stat(format_bytes(_history * _r), label=f"Gzipped (r = {_r:.2f})", bordered=True),
                    mo.stat(format_bytes(_history * (1 - _r) * _reads), label="Less to read per day", bordered=True),
                ],
                widths="equal",
            ),
            tier_chart(_bars, "data"),
            mo.md(
                f"**What to notice:** gzip keeps every sale and saves {1 - _r:.0%} of the disk and of every read: here "
                f"**{format_bytes(_history * (1 - _r))}** on disk and **{format_bytes(_history * (1 - _r) * _reads)}** of "
                "reading a day."
            ),
            mo.md("**In short:** on disk = sales × bytes per sale × $r$; read per day = on disk × reads per day."),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch4_k_range = (4, 90, 2)  # first, last, step: the slider below and the curve the lab draws
    image_demo_rank = mo.ui.slider(*ch4_k_range, value=26, label="Patterns kept (k)", show_value=True, debounce=True)
    image_demo_width = mo.ui.slider(200, 360, value=280, step=20, label="Picture width (px)", show_value=True, debounce=True)
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
def _(TIER, alt, box, ch4_cat, ch4_cat_curve, ch4_cat_svd, chart_or_table, diagram, gzip, image_demo_rank, image_demo_width, in_plain, label_w, mo, np, pd, tier_chart):
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
    _x = alt.X("k:Q", title="patterns kept (k)")
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

    _flow, _at = "", 0
    for _i, _step in enumerate(["picture: 3 grids of numbers (R, G, B)", f"keep the strongest k = {_k} patterns", "rebuilt picture"]):
        _flow += box(_at, 8, _step, cls="dg-tier" if _i == 1 else "dg-box")
        _at += label_w(_step)
        if _i < 2:  # an arrow to the next box
            _flow += f'<path class="dg-edge" d="M{_at + 6:.0f} 30 H {_at + 50:.0f}"/>'
            _at += 56
    _pipeline = diagram(
        _flow,
        width=940,
        height=60,
        label=f"The picture as three grids of colour values, of which only the strongest {_k} patterns are kept, then rebuilt.",
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
            image_demo_rank,
            chart_or_table(_charts, _rows, label=f"Same {ch4_cat.nbytes:,}-byte picture, two kinds of compression"),
            mo.md(
                f"**What to notice:** at k = {_k} the {'PCA' if _pca_wins else 'gzip'} file is smaller"
                + (
                    ", but only gzip gives back the exact picture."
                    if _pca_wins
                    else ": a smooth drawing repeats itself, and lossless compression removes repetition."
                )
                + " Fewer patterns, fewer bytes, more error."
            ),
        ],
        gap=0.6,
    )
    mo.vstack(
        [
            mo.md("### Try it: Shrink a Picture by Keeping Its Strongest Patterns"),
            in_plain(
                "The one example today that is not about sales, because lossy compression is easiest to see. A "
                "picture is a grid of numbers. **PCA** keeps only its k strongest patterns and throws the rest away: "
                "fewer patterns, fewer bytes, a blurrier cat, and no way back to the original."
            ),
            mo.hstack([image_demo_rank, image_demo_width], widths="equal", gap=2),
            _pipeline,
            mo.hstack(
                [
                    mo.image(ch4_cat, width=420, caption="Original"),
                    mo.image(_rebuilt, width=420, caption=f"Rebuilt from k = {_k} patterns"),
                ],
                justify="center",
                gap=3,
            ),
            mo.md(
                "Rebuilt from the top `k` singular vectors per colour channel: rank-k SVD, the maths behind "
                "[PCA](https://en.wikipedia.org/wiki/Principal_component_analysis). *PCA itself is covered in "
                "Machine Learning 2; here it only illustrates compression.*"
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
def _(SALES_SEED, TIER, alt, chart_or_table, in_plain, io, mo, pd, tier_chart):
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
    _exact, _exact_gz, *_, _hundred = _rows

    _df = pd.DataFrame(_rows)
    _df["verdict"] = [f"total off by CHF {_off:+,.2f}" if _off else "exact total" for _off in _df["off by"]]
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
    {1 - _hundred['bytes'] / _exact_gz['bytes']:.0%} off the gzipped file, a bigger win than gzip itself managed on
    the exact prices ({1 - _exact_gz['bytes'] / _exact['bytes']:.0%}). Every lossy file loads cleanly, the column is
    still a decimal, and every tool downstream is perfectly happy. Nobody minds a cat whose pixels are a few
    shades off; every accountant minds a total that is off by hundreds of francs, and by then the exact
    prices are gone.
        """
    )
    mo.vstack(
        [
            mo.md("### Rounded Prices: Smaller File, Wrong Revenue"),
            in_plain(
                "Rounding is the cat trick for numbers: fewer different digits, so compression finds more "
                "repetition and the file shrinks. Here are EdgeWorks' 3,360 real prices, stored exactly and rounded."
            ),
            chart_or_table(tier_chart(_chart, "data"), _rows, label=f"Same {len(_src):,} prices, stored five ways"),
            mo.md(
                f"**What to notice:** the true revenue is CHF {_truth:,.2f}. Rounded to 100 francs, the file is "
                f"{1 - _hundred['bytes'] / _exact_gz['bytes']:.0%} smaller than the exact gzipped one, and the total is "
                f"off by CHF {_hundred['off by']:+,.2f}."
            ),
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
    compress_rows = mo.ui.slider(steps=[500, 1_000, 2_000, 3_360], value=3_360, label="Sales in the file", show_value=True, debounce=True)
    ch4_columns = mo.ui.radio(
        options=["the whole sale (7 fields)", "prices only", "category only"],
        value="the whole sale (7 fields)",
        label="What we store:",
        inline=True,
    )
    return ch4_columns, compress_rows


@app.cell
def _(TIER, alt, ch4_columns, chart_or_table, compress_rows, csv, gzip, io, json, mo, pa, pd, pq, shop_sales, tier_chart):
    _fields = {
        "the whole sale (7 fields)": ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"],
        "prices only": ["total_price"],
        "category only": ["category"],
    }[ch4_columns.value]
    _sales = shop_sales.head(compress_rows.value)[_fields]
    if "sale_date" in _fields:  # a date as a partner's file writes it
        _sales = _sales.assign(sale_date=_sales["sale_date"].dt.strftime("%Y-%m-%d"))
    _records = _sales.to_dict("records")
    _csv = io.StringIO()
    _writer = csv.DictWriter(_csv, fieldnames=_fields)
    _writer.writeheader()
    _writer.writerows(_records)

    # Sizes measured in memory: the bytes a file would hold, without writing one.
    _texts = {"JSON": json.dumps(_records).encode(), "CSV": _csv.getvalue().encode()}
    _sizes = {_name: len(_blob) for _name, _blob in _texts.items()}
    # Level 1 is fastest, 9 squeezes hardest (Python's default), 6 is the gzip tool's default.
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
    ).properties(width="container", height=26 * len(_df), title=f"The first {len(_sales):,} sales, twelve ways")

    _distinct = _sales[_fields[0]].nunique()  # used for the one-column choices
    _reason = {
        "the whole sale (7 fields)": "Parquet keeps each field apart, so the fields with few values (product, country, "
        "rating) are encoded on their own, while gzip sees all seven mixed together.",
        "prices only": f"{_distinct:,} different prices in {len(_sales):,} sales: little repetition. Parquet stores each "
        "as an 8-byte number; gzipped text pays only for the digits written.",
        "category only": f"{_distinct} different values, over and over: every compressed format shrinks it to a sliver "
        "of the CSV. What is left is mostly fixed overhead, such as Parquet's footer.",
    }[ch4_columns.value]
    _why = mo.md(
        """
    - **Prices only:** nearly every price is different. Parquet stores each one as an 8-byte number,
      while gzipped text pays only for the six to nine digits written, so text plus gzip comes out smallest.
    - **Category only:** three values over and over. Every compressed format turns tens of kilobytes into
      a few hundred bytes; the gaps left are fixed costs, such as Parquet's footer.
    - **The whole sale:** Parquet stores each field apart, so product, country and rating, each with a
      handful of values, are encoded on their own; gzip sees all seven fields interleaved. From about
      1,000 sales up that puts Parquet ahead; with 500 its fixed footer still costs too much.
        """
    )
    mo.vstack(
        [
            mo.md("### Try it: Which Format Is Smallest for Our Sales?"),
            mo.md(
                "**Predict first:** JSON, CSV, gzip or Parquet? Does the answer change when we store only the prices, "
                "or only the category?"
            ),
            mo.hstack([ch4_columns, compress_rows], justify="start", align="center", gap=3),
            chart_or_table(tier_chart(_chart, "data"), _rows, label="Sizes (baseline: JSON)"),
            mo.md(
                f"**What to notice:** smallest here is **{_best}**, at {_smallest / _sizes['JSON']:.1%} of the JSON and "
                f"{_smallest / _sizes['CSV']:.0%} of the CSV. {_reason}"
            ),
            mo.accordion({"Why the winner changes with the columns": _why}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    run_ctime = mo.ui.run_button(label="Run compression timing", kind="success")
    return (run_ctime,)


@app.cell
def _(SALES_SEED, TIER, alt, best_seconds, chart_or_table, format_bytes, gzip, io, mia_asks, mo, pd, run_ctime, tier_chart):
    _raw = pd.read_parquet(SALES_SEED).to_csv(index=False).encode("utf-8")
    _top = mo.vstack(
        [
            mo.md("### Try it: Is the Gzipped Sales File Faster to Query?"),
            mia_asks("If the gzipped file is a third of the size, is my total revenue three times faster?"),
            mo.md(
                f"The sales as CSV ({format_bytes(len(_raw))}), already in memory: unpack it if gzipped, parse it, add up "
                "the prices. Four files: plain, and gzip at level 1 (fastest), 6 (the gzip tool's default) and 9 "
                "(smallest, Python's default). Best of 5 bursts."
            ),
            run_ctime,
        ],
        gap=0.6,
    )
    mo.stop(
        not run_ctime.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Predict first:** the gzipped file is far smaller. Is the total on it faster or slower? "
                    "Then click **Run compression timing**."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

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
            f"**No, not here.** The gzipped file is {_l6['bytes'] / len(_raw):.0%} of the size and still takes "
            "*longer* to answer the same question."
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
    ).properties(width="container", height=200, title="Time to answer total revenue (vs plain CSV)")
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
    read, while unpacking them costs CPU on every query. Send the same file to the analyst in Berlin and
    the trade flips, which is why compression is normal for transfer and a judgement call on a local disk.
    Levels 6 and 9 land {abs(_l6['bytes'] - _l9['bytes']):,} bytes apart, and level 9 spent
    {_l9['compress (ms)'] / _l6['compress (ms)']:.1f}x the CPU to find them.
        """
    )
    mo.vstack(
        [
            _top,
            chart_or_table(mo.hstack([tier_chart(_answer_chart, "data"), tier_chart(_write_chart, "data")], widths=[3, 2], gap=2), _rows, label="Same question, four files"),
            mo.md(
                f"**What to notice:** {_verdict} Unpacking costs about the same at every level: **the level is a "
                "decision about writing, not reading.**"
            ).callout(kind="warn"),
            mo.accordion({"Why: CPU for I/O, and the price of level 9": _note}),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, in_plain, math, mo, shop_sales):
    _first = shop_sales["product"].head(8).tolist()  # the first eight real sales
    _codes = {_v: _i for _i, _v in enumerate(dict.fromkeys(_first))}
    _bits = max(1, math.ceil(math.log2(len(_codes))))
    _parts = [
        '<text x="0" y="20" font-weight="700">product, as written</text>',
        '<text x="300" y="20" font-weight="700">code</text>',
        '<text x="460" y="20" font-weight="700">dictionary, written once</text>',
    ]
    for _i, _name in enumerate(_first):
        _y = 34 + _i * 36
        _parts.append(box(0, _y, _name, w=200, h=30))
        _parts.append(f'<text class="dg-muted" x="212" y="{_y + 20}">{len(_name)} bytes</text>')
        _parts.append(box(300, _y, str(_codes[_name]), w=44, h=30, cls="dg-tier"))
    for _name, _c in _codes.items():
        _parts.append(box(460, 34 + _c * 36, f"{_c} = {_name}", w=250, h=30, cls="dg-tier"))
    _parts.append(
        f'<text class="dg-muted" x="460" y="{34 + len(_codes) * 36 + 30}">{sum(map(len, _first))} bytes of names become</text>'
        f'<text class="dg-muted" x="460" y="{34 + len(_codes) * 36 + 54}">{sum(map(len, _codes))} bytes of dictionary + 8 codes of {_bits} bits</text>'
    )
    _drawing = diagram(
        "".join(_parts),
        width=760,
        height=34 + len(_first) * 36,
        label=f"The product names of the first eight sales become a dictionary of {len(_codes)} names and the codes "
        + ", ".join(str(_codes[_n]) for _n in _first)
        + ".",
        tier="data",
    )
    # The same on the whole product column.
    _names = shop_sales["product"]
    _raw = sum(len(_v.encode()) for _v in _names)
    _dictionary = sum(len(_v.encode()) for _v in _names.unique())
    _code_bits = math.ceil(math.log2(_names.nunique()))
    _total = _dictionary + len(_names) * _code_bits / 8
    mo.vstack(
        [
            mo.md("### Dictionary Encoding: Each Product Name Written Once"),
            in_plain(
                "A column with few different values is stored as a short list of those values, the **dictionary**, "
                "plus one small number per sale, its **code**, that points into the list. Parquet does this by default."
            ),
            _drawing,
            mo.md(
                f"**What to notice:** on all {len(_names):,} sales, {_names.nunique()} products with "
                f"{_names.value_counts().iloc[0]:,} sales each, {_raw:,} bytes of names become {_dictionary} bytes of "
                f"dictionary plus {len(_names):,} codes of {_code_bits} bits: {_total:,.0f} bytes, "
                f"**{_total / _raw:.1%}** of the names written in full."
            ),
            mo.md("**In short:** size ≈ dictionary + sales × ⌈log₂(different values)⌉ bits."),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo, shop_sales):
    ch4_dict_column = mo.ui.radio(
        options={f"{_c} ({shop_sales[_c].nunique():,} different)": _c for _c in ("country", "product", "sale_date", "total_price")},
        value=f"country ({shop_sales['country'].nunique():,} different)",
        label="Column:",
        inline=True,
    )
    return (ch4_dict_column,)


@app.cell
def _(TIER, alt, ch4_dict_column, chart_or_table, format_bytes, math, mo, pd, shop_sales, tier_chart):
    _column = shop_sales[ch4_dict_column.value]
    # Each value as the CSV writes it, in bytes.
    _text = _column.dt.strftime("%Y-%m-%d") if ch4_dict_column.value == "sale_date" else _column.astype(str)
    _rows_n, _unique = len(_text), _text.nunique()
    _code_bits = max(1, math.ceil(math.log2(_unique)))
    _raw_bytes = sum(len(_v.encode()) for _v in _text)
    _dictionary_bytes = sum(len(_v.encode()) for _v in _text.unique())
    _index_bytes = _rows_n * _code_bits / 8
    _ratio = (_dictionary_bytes + _index_bytes) / _raw_bytes

    _rows = [
        {"metric": "Values in full (no dictionary)", "formula": "sum of value lengths", "value": _raw_bytes},
        {"metric": "Dictionary", "formula": "sum of the different values' lengths", "value": _dictionary_bytes},
        {"metric": "Code size per sale (bits)", "formula": "ceil(log2(different values))", "value": _code_bits},
        {"metric": "Codes", "formula": "sales x code bits / 8", "value": round(_index_bytes, 2)},
        {"metric": "Encoded / in full", "formula": "(dictionary + codes) / in full", "value": round(_ratio, 4)},
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
            "label": [format_bytes(_raw_bytes), f"{format_bytes(_dictionary_bytes + _index_bytes)}, {_ratio:.0%} of in full"],
        }
    )
    _y = alt.Y("stored:N", sort=None, title=None)
    _x = alt.X("bytes:Q", title="bytes", stack="zero", scale=alt.Scale(domain=[0, _totals["bytes"].max() * 1.45]))
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
    _verdict = (
        "Nearly every value is different, so the dictionary is the whole column again, and the codes come on top: "
        "**bigger than writing the values in full.**"
        if _ratio > 1
        else f"Few different values, short codes: **{1 - _ratio:.0%} saved.**"
    )
    mo.vstack(
        [
            mo.md("### Try it: Which of Our Columns Does a Dictionary Help?"),
            mo.md(
                "The same count on four real columns of our 3,360 sales, each value in bytes as the CSV writes it. "
                "A column with 8 different values needs 3-bit codes; one with 3,358 needs 12."
            ),
            ch4_dict_column,
            chart_or_table(tier_chart(_chart, "data"), _rows, label=f"Dictionary encoding of {ch4_dict_column.value}"),
            mo.md(
                f"**What to notice:** {ch4_dict_column.value} has {_unique:,} different values in {_rows_n:,} sales, so each "
                f"code needs **{_code_bits} bits**. {_verdict}"
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
        <summary><strong>Q1:</strong> Every night we send the sales history to the analyst in Berlin. Compress it?</summary>
        <p><strong>Answer:</strong> Yes: over a network, moving bytes dominates, and gzip sends a third of them.
        Time it on the real link.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> May we store prices rounded to the franc to save space?</summary>
        <p><strong>Answer:</strong> Never: the total revenue drifts and the exact prices are gone. Rounding is for
        measurements, to the instrument's own precision, noted in the schema. Prices, ids, dates: never.</p>
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
def _(SALES_SEED, gzip, io, mo, pd):
    _sales = pd.read_parquet(SALES_SEED)
    _csv = _sales.to_csv(index=False).encode()
    _gz = gzip.compress(_csv, 6)
    _back = pd.read_csv(io.BytesIO(gzip.decompress(_gz)))["total_price"].sum()
    mo.vstack(
        [
            mo.md(
                f"""
    ### Chapter 4 Conclusion

    - **Mia's answer:** yes. gzip shrinks the sales CSV to {len(_gz) / len(_csv):.0%} ({len(_gz):,} of
      {len(_csv):,} bytes), and the total after unpacking is still CHF {_back:,.2f}, to the cent.
    - Lossless gives back every byte; lossy (rounding, PCA) only an approximation: never for prices, ids or dates.
    - Compression feeds on repetition: the category column shrinks to a sliver, the prices only about halve.
    - Smaller is not automatically faster: in memory, unpacking costs CPU and saves no I/O; on the way to
      Berlin, it pays.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Bridge to Next Chapter

    Smaller files help; the reader must also skip work:
    $\\text{query time} \\approx \\text{I/O time} + \\text{compute time}$.
    Next, DuckDB answers Mia's revenue per region straight from these files, reading only the columns and
    row groups the query needs.
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
def _(api_base_url, fastapi_check, mo):
    # Display only, so editing the shared URL re-renders these widgets instead of rebuilding them.
    mo.vstack(
        [
            mo.md(
                "### Live API Workflow: Is It Running?\n\n"
                "Start the API (`uvicorn sw03_demo_api:app`), then press the buttons in order."
            ),
            mo.hstack([api_base_url, fastapi_check], widths=[5, 1], align="end"),
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
def _(fastapi_get, fastapi_item_id, fastapi_payload, fastapi_post, mo):
    mo.vstack(
        [
            mo.md(
                "### Live API Workflow: Create, Then Read\n\n"
                "Press **2)** twice: the name is taken, so the second answer is `400`."
            ),
            fastapi_payload,
            mo.hstack([fastapi_post, fastapi_item_id, fastapi_get], justify="start", align="end", gap=2),
        ],
        gap=0.8,
    ).callout(kind="neutral")
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
            mo.md("### Signal or Noise: Set the Truth, Then Read the Fit"),
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
            width="container",
            height=230,
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
            chart_or_table(
                _panels, _rows, label=f"Same {_rows[0]['dots (n)']:,} sales, same question"
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
