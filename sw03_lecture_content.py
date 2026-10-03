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
    import tempfile
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
        tempfile,
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
        Case study: <strong>EdgeWorks</strong>, a vendor of sensors, software and services in eight
        countries, requires a reliable sales dashboard. The lecture follows its sales data from a file,
        through an API, to a dashboard.
      </div>
      <div class="hero-pills">
        <span class="pill">Part 1 · File formats and serialization</span>
        <span class="pill">Part 2 · Storage: layout, compression, queries</span>
        <span class="pill">Part 3 · APIs</span>
        <span class="pill">Part 4 · Presentation frameworks</span>
      </div>
    </div>
    """)
    return


@app.cell
def _(guiding_question, in_plain, mo, shop_sales, static_table):
    _months = shop_sales["sale_date"].dt.to_period("M").nunique()
    _sample = shop_sales.sort_values("sale_id").head(4)[
        ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"]
    ]
    mo.vstack(
        [
            mo.md("## Case Study: EdgeWorks"),
            guiding_question("How does revenue per region get from the sales file onto a dashboard?"),
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
                label="Each sale is one row (sample from data/seed/sales.parquet)",
            ),
            in_plain(
                "All examples in this lecture use this data set. Each part answers one step of the guiding question: "
                "how the data is stored (Parts 1 and 2), how it is served (Part 3) and how it is presented (Part 4)."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Learning Objectives</h3>
      <p class="vis-caption">After this lecture, you can</p>
      <ol class="question-list">
        <li class="tier-data">compare CSV, JSON, Avro, Parquet, Arrow and Pickle by readability, size, speed, types, schema support and safety;</li>
        <li class="tier-data">explain why a columnar layout, partitioning and compression make analytical queries fast, and query Parquet files with SQL;</li>
        <li class="tier-data">explain what a database transaction adds compared with a plain file;</li>
        <li class="tier-logic">describe an HTTP request and its response, and retrieve data from an API with Python;</li>
        <li class="tier-logic">build a small API with FastAPI that validates its input with Pydantic;</li>
        <li class="tier-presentation">compare Streamlit, marimo and Dash, choose a framework for a given dashboard, and a chart type for a given question.</li>
      </ol>
    </div>
    """)
    return


@app.cell
def _(box, diagram, label_w, mo):
    def _tier(y, tier, name, role, chapters):
        """One tier band: name and role on the left, then one chip per topic, numbered by part."""
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
        '<text x="1000" y="22" text-anchor="middle" font-weight="700">response</text>'
        + _tier(40, "presentation", "Presentation tier", "the sales dashboard", [("4", "frameworks"), ("4", "analysis choices")])
        + _tier(172, "logic", "Logic tier", "the sales API", [("3", "HTTP"), ("3", "consume"), ("3", "FastAPI"), ("3", "validation")])
        + _tier(304, "data", "Data tier", "the sales files", [("1", "formats"), ("2", "layout"), ("2", "compression"), ("2", "queries"), ("2", "transactions")])
        # one hop per neighbour: down for the request, up for the response
        + '<path class="dg-edge" d="M920 88 V 166"/><path class="dg-edge" d="M920 220 V 298"/>'
        + '<path class="dg-edge" d="M1000 352 V 274"/><path class="dg-edge" d="M1000 220 V 142"/>'
        + '<circle class="dg-dot" r="9"><animateMotion dur="5s" repeatCount="indefinite" path="M920 88 V 352 H 1000 V 88 Z"/></circle>',
        width=1060,
        height=420,
        label="Three tiers, stacked: presentation (Part 4) on logic (Part 3) on data (Parts 1 and 2). "
        "A request travels down one tier at a time and the response comes back up the same way.",
    )
    mo.md(f"""
    <div class="section-card">
      <h3>Overview: A Three-Tier Architecture</h3>
      {tier_map}
      <p class="vis-caption">The <strong>data tier</strong> stores the sales files
      (<code>data/*.parquet</code>), the <strong>logic tier</strong> is the sales API
      (<code>sw03_demo_api.py</code>), and the <strong>presentation tier</strong> is the dashboard
      (<code>sw03_demo_streamlit.py</code>). Each tier communicates only with its neighbour, so any one
      of them can be replaced without changing the others. The numbers on the chips are the parts of this
      lecture.</p>
    </div>
    """)
    return (tier_map,)


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Structure of Each Part</h3>
      <div class="tiles">
        <div class="tile"><div class="tile-key">?</div><div class="tile-title">Guiding question</div>
          <p>Each part starts from one question of the EdgeWorks case.</p></div>
        <div class="tile"><div class="tile-key">=</div><div class="tile-title">Key idea</div>
          <p>The central concept in one or two sentences.</p></div>
        <div class="tile"><div class="tile-key">&#9654;</div><div class="tile-title">Experiment</div>
          <p>A live analysis of the sales data; longer benchmarks run on demand.</p></div>
        <div class="tile"><div class="tile-key">&#8230;</div><div class="tile-title">Discussion and summary</div>
          <p>Questions with expandable answers, then the key points of the part.</p></div>
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
    from pyarrow import feather

    # Charts as SVG, not canvas: the slides are zoomed to fit the screen, and a canvas bitmap zoomed up blurs.
    # Assigned, so the cell shows nothing (an output would become a slide of its own).
    _ = alt.renderers.set_embed_options(renderer="svg")

    return (
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
def _(html, mo, requests, timeit):
    def format_bytes(num_bytes):
        """Human-friendly byte counts."""
        value = float(num_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if value < 1024:
                return f"{value:,.0f} B" if unit == "B" else f"{value:,.2f} {unit}"
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
    # the --red of sw03_deck.css for what broke (the dg-hot of the diagrams), and its --amber for decompression
    TIER = {
        "data": "#2f7fe0",
        "logic": "#c9479f",
        "presentation": "#dd6325",
        "muted": "#626b78" if _dark else "#9aa4b2",
        "hot": "#ff9b8f" if _dark else "#b42318",
        "amber": "#f5b43c" if _dark else "#d97706",
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

    def guiding_question(question: str):
        """The question from the EdgeWorks case that a part or an experiment answers (markdown)."""
        return mo.Html(
            f'<div class="guiding-q"><span class="guiding-q-label">Guiding question</span>{mo.md(question).text}</div>'
        )

    def in_plain(text: str):
        """The key idea in one or two sentences (markdown), shown before any formula."""
        return mo.Html(f'<div class="in-plain"><span class="in-plain-label">Key idea</span>{mo.md(text).text}</div>')

    def chapter_intro(tier: str, question: str, context: str, topics: tuple[str, ...] = ()):
        """A part's opening card: the tier badge, the guiding question in large type, one line of context, the topics."""
        pills = "".join(f'<span class="pill">{html.escape(_t)}</span>' for _t in topics)
        return mo.Html(
            f'<div class="key-q tier-{tier}"><span class="tier-badge">{tier} tier</span>'
            f'<span class="guiding-q-label key-q-who">Guiding question</span>'
            f'<p class="key-q-text">{question}</p>{mo.md(context).text}'
            + (f'<div class="hero-pills">{pills}</div>' if pills else "")
            + "</div>"
        )

    def card_box(x, y, title, sub, cls="dg-box", w=235, h=72):
        """SVG for a two-line box at (x, y): a bold title over a muted line."""
        return (
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 29}" text-anchor="middle" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="{x + w / 2:.0f}" y="{y + 53}" text-anchor="middle">{sub}</text>'
        )

    return (
        TIER,
        best_seconds,
        call_api,
        card_box,
        chapter_intro,
        chart_or_table,
        format_bytes,
        format_ms,
        guiding_question,
        in_plain,
        static_table,
        tier_chart,
    )


@app.cell
def _(chapter_intro, mo):
    mo.vstack(
        [
            mo.md("## Part 1 · File Formats and Serialization"),
            chapter_intro(
                "data",
                "In which format should the sales data be stored and exchanged?",
                "How a table becomes bytes, what each format preserves and loses, and how to choose between formats.",
                topics=(
                    "Serialization",
                    "Text and binary formats",
                    "Encodings and CSV dialects",
                    "Dates and time zones",
                    "Schemas and schema evolution",
                    "Arrow and Pickle",
                    "Latency and throughput",
                    "Format benchmark",
                ),
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
        + _object(840, "the same sale")
        + '<text class="dg-muted" x="560" y="262" text-anchor="middle">'
        "on disk or over the network: partner files, API responses, queues, caches</text>",
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
                "**Serialization** converts an in-memory object, here one EdgeWorks sale, into a sequence of bytes "
                "that can be stored in a file or sent to a partner. **Deserialization** reconstructs the object from "
                "the bytes. The **format** (JSON, CSV, Parquet, ...) determines the byte representation."
            ),
            _pipeline,
            mo.md(
                f"**Observation:** as JSON, this sale occupies {len(_bytes)} bytes, of which only {_value_bytes} "
                "encode values. The remainder consists of field names and punctuation, repeated for each of the "
                f"{len(shop_sales):,} sales."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(in_plain, mo):
    mo.vstack(
        [
            mo.md("### Five format families and their use at EdgeWorks"),
            in_plain(
                "Text formats (JSON, CSV) are readable by any tool and by humans. Binary formats are smaller and "
                "faster but require a library to read. The choice depends on who reads the file and for what purpose."
            ),
            mo.md(
                """
    <div class="tiles tier-data" style="grid-template-columns: repeat(5, 1fr)">
      <div class="tile"><div class="tile-key">JSON</div><div class="tile-title">Text, row by row</div>
        <p>The sales API responds to the dashboard in JSON; partners open CSV in Excel.</p></div>
      <div class="tile"><div class="tile-key">Avro</div><div class="tile-title">Rows + a schema</div>
        <p>The order event stream: each order is sent when it occurs.</p></div>
      <div class="tile"><div class="tile-key">Arrow</div><div class="tile-title">Columns in memory</div>
        <p>Arrow / Feather: passes the sales table from DuckDB to pandas without conversion.</p></div>
      <div class="tile"><div class="tile-key">Parquet</div><div class="tile-title">Columns on disk</div>
        <p>EdgeWorks' sales files: <code>data/*.parquet</code>.</p></div>
      <div class="tile"><div class="tile-key">Pickle</div><div class="tile-title">Python objects</div>
        <p>Python only.</p><p class="tile-bad">Loading it can execute code: never from a partner.</p></div>
    </div>
                """
            ),
            mo.md(
                "**Comparison criteria:** speed, size, interoperability (which tools can read a file), type fidelity, "
                "schema evolution and safety. The following slides examine each of them on the EdgeWorks sales data."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(fastavro, html, in_plain, io, json, mo, pa, pickle, pq, shop_sales):
    _first = shop_sales.head(3)
    _three = _first[["sale_id", "sale_date", "product", "units_sold", "total_price"]].assign(
        sale_date=_first["sale_date"].dt.strftime("%Y-%m-%d")
    )
    _records = _three.to_dict("records")
    _table = pa.Table.from_pylist(_records)

    def _avro():
        _schema = {
            "type": "record",
            "name": "Sale",
            "fields": [
                {"name": "sale_id", "type": "long"},
                {"name": "sale_date", "type": "string"},
                {"name": "product", "type": "string"},
                {"name": "units_sold", "type": "long"},
                {"name": "total_price", "type": "double"},
            ],
        }
        _buf = io.BytesIO()
        fastavro.writer(_buf, _schema, _records)
        return _buf.getvalue()

    def _parquet():
        _buf = io.BytesIO()
        pq.write_table(_table, _buf)
        return _buf.getvalue()

    def _arrow():
        # the Arrow IPC file format, which is what a Feather file is
        _sink = pa.BufferOutputStream()
        with pa.ipc.new_file(_sink, _table.schema) as _writer:
            _writer.write_table(_table)
        return _sink.getvalue().to_pybytes()

    _files = [
        ("CSV", "text", _three.to_csv(index=False).encode(), "one line per sale; the header names the columns"),
        ("JSON", "text", json.dumps(_records).encode(), "every record repeats the field names"),
        ("Avro", "binary", _avro(), "starts with Obj, followed by its schema as JSON"),
        ("Parquet", "binary", _parquet(), "starts and ends with PAR1"),
        ("Arrow / Feather", "binary", _arrow(), "starts and ends with ARROW1"),
        ("Pickle", "binary", pickle.dumps(_records, protocol=pickle.HIGHEST_PROTOCOL), "Python's own format, for Python only"),
    ]

    def _as_text(data):
        """Printable characters as they are, a line break as ↵, every other byte as a dot."""
        return html.escape("".join(chr(_b) if 32 <= _b < 127 else "↵" if _b == 10 else "·" for _b in data))

    def _excerpt(data):
        return _as_text(data) if len(data) <= 110 else _as_text(data[:90]) + " … " + _as_text(data[-14:])

    _tiles = "".join(
        f'<div class="tile"><div class="tile-key">{_name}</div><div class="tile-title">{_kind} · {len(_data):,} bytes</div>'
        '<pre style="margin: 6px 0; white-space: pre-wrap; word-break: break-all; font-size: 13px; line-height: 1.35">'
        f"{_excerpt(_data)}</pre><p>{_note}</p></div>"
        for _name, _kind, _data, _note in _files
    )
    _sizes = {_name: len(_data) for _name, _, _data, _ in _files}
    mo.vstack(
        [
            mo.md("### What a file contains: the same three sales in six formats"),
            in_plain(
                "A **text format** stores characters that any editor can display. A **binary format** stores numbers "
                "and structures as raw bytes that only a library can interpret; it usually begins with a fixed "
                "signature, the *magic number*, that identifies the format."
            ),
            mo.Html(f'<div class="tiles tier-data" style="grid-template-columns: repeat(3, 1fr)">{_tiles}</div>'),
            mo.md(
                f"**Observation:** CSV and JSON can be read as plain text; in the binary files only fragments such as "
                f"field names are legible. For three sales, Parquet ({_sizes['Parquet']:,} bytes) is larger than CSV "
                f"({_sizes['CSV']:,} bytes) because its metadata dominates; with thousands of rows the ranking reverses."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo):
    _word = "Zürich"
    _parts = [
        '<text x="0" y="34" font-weight="700">character</text>',
        '<text x="0" y="114" font-weight="700">UTF-8 bytes</text>',
    ]
    _x = 150
    for _char in _word:
        _code = _char.encode("utf-8")
        _w = 58 * len(_code) + 10 * (len(_code) - 1)
        _cls = "dg-tier" if len(_code) > 1 else "dg-box"
        _parts.append(box(_x, 6, _char, w=_w, cls=_cls))
        _parts.append(f'<path class="dg-edge" d="M{_x + _w / 2:.0f} 54 V 82"/>')
        _parts.append(box(_x, 88, " ".join(f"{_b:02X}" for _b in _code), w=_w, cls=_cls))
        _x += _w + 12
    _bytes = diagram(
        "".join(_parts),
        width=int(_x),
        height=138,
        label="Zürich as six characters and their UTF-8 bytes: Z is 5A, ü is C3 BC, r 72, i 69, c 63, h 68. "
        "The ü takes two bytes.",
        tier="data",
    )
    _misread = _word.encode("utf-8").decode("latin-1")
    try:
        _word.encode("latin-1").decode("utf-8")
        _error = "no error"
    except UnicodeDecodeError as _exc:
        _error = f"UnicodeDecodeError: {_exc.reason}"
    mo.vstack(
        [
            mo.md("### Text encodings: characters are stored as bytes"),
            in_plain(
                "A file stores bytes, not characters. An **encoding** maps each character to bytes: **UTF-8**, today's "
                "standard, uses one byte for each ASCII character and two to four bytes for others, such as ü. "
                "Writer and reader must use the same encoding."
            ),
            _bytes,
            mo.hstack(
                [
                    mo.md(f"**Written as UTF-8, read as UTF-8**\n\n`{_word}`").callout(kind="success"),
                    mo.md(f"**Written as UTF-8, read as Latin-1**\n\n`{_misread}`").callout(kind="danger"),
                    mo.md(f"**Written as Latin-1, read as UTF-8**\n\n`{_error}`").callout(kind="danger"),
                ],
                widths="equal",
                gap=1,
            ),
            mo.md(
                f"**Observation:** '{_word}' has {len(_word)} characters but {len(_word.encode('utf-8'))} bytes in UTF-8. "
                f"Read with the wrong encoding, the same bytes appear as '{_misread}', a frequent error with CSV files "
                "exported in a regional code page such as Windows-1252. Text files should therefore be read and written "
                'with an explicit encoding, for example `pd.read_csv(path, encoding="utf-8")`.'
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p1_csv_reader = mo.ui.radio(
        options={
            "pd.read_csv(f)": {},
            'pd.read_csv(f, sep=";")': {"sep": ";"},
            'pd.read_csv(f, sep=";", decimal=",")': {"sep": ";", "decimal": ","},
        },
        value="pd.read_csv(f)",
        label="Reader settings:",
    )
    return (p1_csv_reader,)


@app.cell
def _(in_plain, io, mo, p1_csv_reader, pd, shop_sales, static_table):
    _source = shop_sales.head(4)[["sale_id", "sale_date", "units_sold", "total_price"]]
    # The same rows as Excel writes them with German regional settings: semicolons, decimal commas, day-first dates.
    _exported = _source.to_csv(index=False, sep=";", decimal=",", date_format="%d.%m.%Y")
    _read = pd.read_csv(io.StringIO(_exported), **p1_csv_reader.value)
    _shown = _read if isinstance(_read.index, pd.RangeIndex) else _read.reset_index()
    _last = _read[_read.columns[-1]].sum()
    if len(_read.columns) == 1:
        _verdict = mo.md(
            "**One column.** The comma inside `4034,91` was taken as the separator; the rest of each line became an "
            f"unnamed index, and the 'sum' of the remaining column is {_last:,}: a meaningless number, without an error."
        ).callout(kind="danger")
    elif isinstance(_last, str):
        _verdict = mo.md(
            "**Four columns, but `total_price` is text.** Its `.sum()` therefore concatenates the strings: "
            f"`{_last[:32]}…`"
        ).callout(kind="danger")
    else:
        _verdict = mo.md(
            f"**Correct:** four columns, `total_price` is a number, and the total is CHF {_last:,.2f}, as in the "
            "source. `sale_date` is still text; `parse_dates=['sale_date'], dayfirst=True` converts it."
        ).callout(kind="success")
    mo.vstack(
        [
            mo.md("### CSV is not one format: separators, decimal marks, dates"),
            in_plain(
                "CSV has no single standard. Separator, decimal mark, quoting, date format and encoding depend on the "
                "program and its regional settings, and the reader must be told which ones a file uses."
            ),
            mo.hstack(
                [
                    mo.vstack([mo.md("**The file**, exported with German regional settings"), mo.md(f"```text\n{_exported}```")]),
                    mo.vstack([p1_csv_reader, static_table(_shown, label="What pandas reads")]),
                ],
                widths=[2, 3],
                gap=2,
            ),
            _verdict,
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p1_day_boundary = mo.ui.radio(
        options={"local time of the store": "local", "UTC": "UTC", "Zurich (head office)": "Europe/Zurich"},
        value="local time of the store",
        label="Count each sale on its date in:",
        inline=True,
    )
    return (p1_day_boundary,)


@app.cell
def _(in_plain, mo, p1_day_boundary, pd, shop_sales, static_table):
    # Six sales around midnight at the end of January, each recorded in its store's local time. The amounts are
    # EdgeWorks sales of these countries; the clock times are illustrative, since the sales files store dates only.
    _stores = [
        ("United States", "New York", "America/New_York", "2026-01-31 22:30"),
        ("Canada", "Toronto", "America/Toronto", "2026-01-31 18:05"),
        ("United Kingdom", "London", "Europe/London", "2026-01-31 23:40"),
        ("Germany", "Berlin", "Europe/Berlin", "2026-02-01 00:15"),
        ("Japan", "Tokyo", "Asia/Tokyo", "2026-02-01 06:30"),
        ("India", "Mumbai", "Asia/Kolkata", "2026-02-01 03:10"),
    ]
    _sales = [
        (_city, pd.Timestamp(_local).tz_localize(_zone), float(shop_sales.loc[shop_sales["country"] == _country, "total_price"].iloc[-1]))
        for _country, _city, _zone, _local in _stores
    ]

    def _month(moment, boundary):
        """The month a sale counts towards when its date is taken in `boundary` (a time zone, or "local")."""
        return (moment if boundary == "local" else moment.tz_convert(boundary)).strftime("%B")

    def _january(boundary):
        return sum(_amount for _, _moment, _amount in _sales if _month(_moment, boundary) == "January")

    _boundary = p1_day_boundary.value
    _rows = [
        {
            "store": _city,
            "recorded (local time)": _moment.strftime("%d %b %H:%M"),
            "UTC": _moment.tz_convert("UTC").strftime("%d %b %H:%M"),
            "Zurich": _moment.tz_convert("Europe/Zurich").strftime("%d %b %H:%M"),
            "counts towards": _month(_moment, _boundary),
            "amount (CHF)": round(_amount, 2),
        }
        for _city, _moment, _amount in _sales
    ]
    _in_january = sum(_r["counts towards"] == "January" for _r in _rows)
    _us_style = pd.to_datetime("01/03/2026", format="%m/%d/%Y")
    _european = pd.to_datetime("01/03/2026", format="%d/%m/%Y")
    mo.vstack(
        [
            mo.md("### Dates and time zones"),
            in_plain(
                "A date written as text needs its format: `01/03/2026` is 1 March in Europe and 3 January in the US. A "
                "point in time also needs its time zone. **ISO 8601** (`2026-03-01T22:30:00+01:00`) fixes the order of "
                "the parts, and storing times in **UTC** gives every system the same reference."
            ),
            mo.hstack(
                [
                    mo.md(f'`format="%m/%d/%Y"` reads `01/03/2026` as **{_us_style.day} {_us_style:%B %Y}**').callout(kind="neutral"),
                    mo.md(f'`format="%d/%m/%Y"` reads it as **{_european.day} {_european:%B %Y}**').callout(kind="neutral"),
                    mo.md("`2026-03-01`, in ISO 8601, has only one reading").callout(kind="success"),
                ],
                widths="equal",
                gap=1,
            ),
            p1_day_boundary,
            mo.hstack(
                [
                    static_table(_rows, label="Six sales around midnight on 31 January (illustrative clock times)"),
                    mo.stat(f"CHF {_january(_boundary):,.0f}", label="January revenue", caption=f"{_in_january} of 6 sales", bordered=True),
                ],
                widths=[4, 1],
                gap=2,
                align="center",
            ),
            mo.md(
                f"**Observation:** the same six sales give a January revenue of CHF {_january('local'):,.0f} counted in "
                f"local time, CHF {_january('UTC'):,.0f} in UTC and CHF {_january('Europe/Zurich'):,.0f} in Zurich time. A "
                "report is reproducible only if it states the time zone of its day boundary; storing UTC and converting "
                "for display avoids the ambiguity."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(box, diagram, fastavro, html, in_plain, io, mo, shop_sales):
    _first, _second = shop_sales.iloc[0], shop_sales.iloc[1]
    _typo = f"about {round(_second['total_price'], -3):,.0f}"  # a free-text entry instead of the price
    # Avro's writer rejects a value that does not match the schema: the actual error from the Avro writer.
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
        '<text x="0" y="22" font-weight="700">JSON: text records, no schema</text>'
        + _sheet(40, _first, f"{_first['total_price']}")
        + _sheet(124, _second, f'<tspan class="dg-hot">"{_typo}"</tspan>')
        + '<text class="dg-muted" x="0" y="222">every record repeats the field names</text>'
        + f'<text class="dg-hot" x="0" y="248">and nothing rejects "{_typo}" as a price</text>'
        + '<text x="540" y="22" font-weight="700">Avro: binary records with a schema</text>'
        + _form_row(40, [_label for _label, _ in _form_cells], "dg-tier")
        + _form_row(92, [f"{_first['sale_id']}", _date(_first), f"{_first['total_price']}"], "dg-box")
        + _form_row(140, [f"{_second['sale_id']}", _date(_second), f'<tspan class="dg-hot" text-decoration="line-through">{_typo}</tspan>'], "dg-box")
        + '<text class="dg-muted" x="540" y="222">field names stored once; rows hold only values</text>'
        + f'<text class="dg-hot" x="540" y="248" font-size="15">rejected: {html.escape(_refusal, quote=False)}</text>'
        + '<text x="0" y="306" font-weight="700">The schema recurs:</text>'
        + '<g class="tier-data"><rect class="dg-tier" x="190" y="282" width="250" height="40" rx="12"/>'
        '<text x="315" y="307" text-anchor="middle">Part 2 · DuckDB <tspan font-weight="700">infers</tspan> it</text></g>'
        + '<g class="tier-logic"><rect class="dg-tier" x="456" y="282" width="270" height="40" rx="12"/>'
        '<text x="591" y="307" text-anchor="middle">Part 3 · Pydantic <tspan font-weight="700">enforces</tspan> it</text>'
        '<rect class="dg-tier" x="742" y="282" width="270" height="40" rx="12"/>'
        '<text x="877" y="307" text-anchor="middle">Part 3 · FastAPI <tspan font-weight="700">publishes</tspan> it</text></g>',
        width=1040,
        height=330,
        label=f"Left: JSON records repeat every field name, and one has '{_typo}' as its price. Right: an Avro file "
        f"stores the field names once in its schema, each row holds only values, and the writer rejects '{_typo}'. "
        "The schema recurs in Parts 2 and 3.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### The schema: structure and types, separate from the values"),
            in_plain(
                "A **schema** describes the structure of the data, not the values: which fields a sale has, in which "
                "order, and which type each field takes. JSON and CSV transmit only the values. Avro stores the schema "
                "in the file, and its writer rejects any value that does not match the declared type."
            ),
            _forms,
            mo.md(
                f"**Observation:** the price of sale #{_second['sale_id']} was entered as \"{_typo}\". JSON stores it "
                "without complaint; Avro rejects it before it reaches a partner."
            ),

        ],
        gap=0.8,
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
    _xs = {"written": 190, "read from CSV": 470, "read from Parquet": 750}
    _parts = [f'<text x="{_x + 130}" y="22" text-anchor="middle" font-weight="700">{_name}</text>' for _name, _x in _xs.items()]
    for _i, _c in enumerate(_src.columns):
        _y = 40 + _i * 56
        _wrote = str(_src[_c].dtype)
        _parts.append(f'<text x="0" y="{_y + 27}" font-family="monospace" font-weight="700">{_c}</text>')
        _parts.append(box(_xs["written"], _y, _wrote, w=260))
        for _x, _back_df in ((_xs["read from CSV"], _from_csv), (_xs["read from Parquet"], _from_pq)):
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
    **Query on the {name} copy**

    - Time span of the sales: `{_span(df)}`
    - South Africa's store code: `{_code!r}`
            """
        ).callout(kind=kind)

    mo.vstack(
        [
            mo.md("### Type loss in CSV: store code 007 becomes 7"),
            in_plain(
                "CSV is plain text without type information, so the reader infers the types: `2024-03-07` remains "
                "text, and the store code `007` resembles a number, so it becomes `7`. Parquet stores the type with "
                f"the data. Here all {len(_src):,} sales, each with a three-digit store code, are written to both "
                "formats and read back."
            ),
            _types,
            mo.hstack([_ask("Parquet", _from_pq, "success"), _ask("CSV", _from_csv, "danger")], widths="equal", gap=1),
            mo.md(
                "**Observation:** the date error is explicit (a `TypeError`); the store code error is silent and "
                "would therefore propagate into a partner's report."
            ),

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
        ("last year's Avro file", "old schema", "this year's code", "new schema: + channel",
         _fields(_old_by_new[0]), "&#10003; the reader filled in the default", "dg-box dg-ok"),
        ("this year's Avro file", "new schema", "the old program", "old schema",
         _fields(_new_by_old[0]), "&#10003; the extra field is skipped", "dg-box dg-ok"),
        ("last year's CSV file", "no embedded schema", "this year's code", "expects channel",
         _csv_result, "&#10007; only remedy: change every reader", "dg-box dg-hot"),
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
            mo.md("### Schema evolution: adding a `channel` field"),
            in_plain(
                "**Schema evolution** means changing the schema while old files and old programs remain in use. "
                "EdgeWorks starts recording each sale's `channel`: `online` or `partner`. Old sales lack this field, "
                "so the new schema defines a **default**, `unknown`, for any sale written without it."
            ),
            _lanes_svg,
            mo.md(
                "**Observation:** CSV carries no schema, so the agreement on its structure exists only as implicit "
                "knowledge, and every reader must be changed manually."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(SALES_SEED, best_seconds, box, diagram, duckdb, in_plain, io, mo, pd, static_table):
    with duckdb.connect() as _con:
        _arrow = _con.sql(f"SELECT * FROM read_parquet('{SALES_SEED.as_posix()}')").to_arrow_table()
    _df = _arrow.to_pandas()
    _csv_text = _df.to_csv(index=False)
    _from_csv = pd.read_csv(io.StringIO(_csv_text))
    _arrow_ms = best_seconds(_arrow.to_pandas, repeat=5) * 1000
    _csv_ms = best_seconds(lambda: pd.read_csv(io.StringIO(_csv_text)), repeat=5) * 1000

    _hub = diagram(
        box(0, 0, "DuckDB", w=170)
        + box(0, 64, "pandas", w=170)
        + box(0, 128, "Polars, Spark, R", w=170)
        + box(270, 48, "Arrow table in memory", w=260, h=68, cls="dg-tier")
        + box(630, 10, "Feather file: Arrow as is", w=310)
        + box(630, 118, "Parquet file: encoded, compressed", w=310)
        + '<path class="dg-edge" d="M170 22 C 220 22, 220 70, 264 70"/>'
        + '<path class="dg-edge" d="M170 86 H 264"/>'
        + '<path class="dg-edge" d="M170 150 C 220 150, 220 100, 264 100"/>'
        + '<path class="dg-edge" d="M530 70 C 580 70, 580 32, 624 32"/>'
        + '<path class="dg-edge" d="M530 100 C 580 100, 580 140, 624 140"/>'
        + '<text class="dg-muted" x="400" y="140" text-anchor="middle">shared without conversion</text>',
        width=940,
        height=176,
        label="DuckDB, pandas and other tools share one Arrow table in memory without converting it. A Feather file "
        "stores this table as it is; a Parquet file stores it encoded and compressed.",
        tier="data",
    )
    _types = static_table(
        [
            {
                "column": _field.name,
                "Arrow type": str(_field.type),
                "pandas, via Arrow": str(_df[_field.name].dtype),
                "pandas, via CSV text": str(_from_csv[_field.name].dtype),
            }
            for _field in _arrow.schema
        ],
        label="Column types after each route",
    )
    mo.vstack(
        [
            mo.md("### Arrow: one table format for all tools in memory"),
            in_plain(
                "**Apache Arrow** defines a standard columnar layout for tables in memory. Tools that support it, such as "
                "DuckDB, pandas, Polars and Spark, exchange tables without converting them. **Feather** writes this "
                "layout unchanged to a file; **Parquet** encodes and compresses it for long-term storage."
            ),
            mo.hstack([_hub, _types], widths=[3, 2], gap=2, align="center"),
            mo.md(
                f"**Observation:** DuckDB returns its result as an Arrow table with typed columns. Converting it to pandas "
                f"takes {_arrow_ms:.1f} ms; parsing the same {len(_df):,} rows from CSV text takes {_csv_ms:.1f} ms, and "
                f"`sale_date` arrives as `{_from_csv['sale_date'].dtype}` instead of a date."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(html, in_plain, mo, pickle):
    import platform as _platform

    class _Payload:
        def __reduce__(self):
            return (_platform.platform, ())

    _data = pickle.dumps(_Payload())
    _loaded = pickle.loads(_data)  # this call runs platform.platform(): the file decides what is executed
    _as_text = html.escape("".join(chr(_b) if 32 <= _b < 127 else "·" for _b in _data))
    _code = """
class Payload:
    def __reduce__(self):               # tells pickle how to rebuild the object
        return (platform.platform, ())  # "call this function"

data = pickle.dumps(Payload())          # the sender saves this as sales.pkl
pickle.loads(data)                      # the receiver only loads the "data"
"""
    mo.vstack(
        [
            mo.md("### Pickle: loading a file can execute code"),
            in_plain(
                "**Pickle** stores arbitrary Python objects, including trained models. The file records how to rebuild "
                "each object, which can mean calling a function. Loading a pickle file therefore executes code chosen "
                "by whoever created the file."
            ),
            mo.hstack(
                [
                    mo.md(f"```python\n{_code.strip()}\n```"),
                    mo.vstack(
                        [
                            mo.md(f"**The file as text** ({len(_data)} bytes):"),
                            mo.Html(f'<pre style="margin: 0; white-space: pre-wrap; word-break: break-all">{_as_text}</pre>'),
                            mo.md(f"**Loading it returned:** `{_loaded}`").callout(kind="danger"),
                        ],
                        gap=0.4,
                    ),
                ],
                widths="equal",
                gap=2,
                align="start",
            ),
            mo.md(
                f"**Observation:** loading these {len(_data)} bytes called `platform.platform()` and returned this "
                "computer's operating system. A malicious file could call any other function instead, for example one "
                "that deletes or uploads files. Pickle files, including saved models, may only be loaded from trusted "
                "sources."
            ),
        ],
        gap=0.6,
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
        + '<text x="560" y="24" font-weight="700">Throughput: how much one run processes</text>'
        + '<rect class="dg-tier" x="570" y="48" width="300" height="88" rx="10"/>'
        + '<text x="720" y="84" text-anchor="middle" font-weight="700">nightly export</text>'
        + f'<text x="720" y="112" text-anchor="middle">{_files} files · {len(shop_sales):,} sales</text>'
        + '<path class="dg-edge" d="M876 92 H 930"/>'
        + '<text x="990" y="86" text-anchor="middle" font-weight="700">sales</text>'
        + '<text x="990" y="108" text-anchor="middle" font-weight="700">per second</text>'
        # the trade: the export waits for the last sale of the day, so the first one waits longest
        + '<text x="0" y="214" font-weight="700">Trade-off:</text>'
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
        "a sale recorded at 08:00 reaches its partner 14 hours later</text>",
        width=1060,
        height=350,
        label=f"Latency: one partner, in Kenya, waits for its file of {_kenya} sales to be written, sent and read. "
        f"Throughput: the nightly export writes {_files} files with {len(shop_sales):,} sales and is measured in sales "
        "per second. Sales recorded from 08:00 all wait for the 22:00 export, so batching raises throughput and makes "
        "the first sale wait 14 hours.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Latency vs throughput: two meanings of \"fast\""),
            in_plain(
                "**Latency** is the time one operation takes: from a partner's request for its file until the file "
                "is available. **Throughput** is the amount processed per unit of time: how many sales per second the "
                "nightly export writes. Batching raises throughput and increases the latency of each single sale."
            ),
            _picture,
            mo.md(
                "**Observation:** the export sends all sales in one efficient run at 22:00, so a sale recorded at "
                "08:00 arrives 14 hours later. Batch processing favours throughput; streaming each event as it occurs "
                "favours latency. A requirement for \"fast\" must state which of the two is meant."
            ),
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
    tempfile,
    tier_chart,
):
    _top = mo.vstack(
        [
            mo.md("### Six formats on the same EdgeWorks sales"),
            mo.md(
                "Each format writes the first EdgeWorks sales to a file and reads them back; the best of 3 runs is "
                f"reported. The slider sets the number of sales: one month is 140, the whole history {len(shop_sales):,}."
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
                    "**Question:** is the smallest file also the fastest?"
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
    ).properties(width="container", height=300, title="Size vs latency (lower left is better)")
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
                f"**Observation:** the smallest file is {_name(_smallest)} ({_smallest['size (KB)']:,} KB, "
                f"compared with {_by['JSON']['size (KB)']:,} KB for JSON); the fastest round trip is "
                f"{_name(_quickest)} ({_quickest['latency (ms)']:,} ms)."
                + (" It is also the one format a partner could not open safely." if _quickest["format"].startswith("Pickle") else "")
                + " Do latency and throughput rank the formats in the same order? "
                + f"Does the ranking hold for {140 if len(_records) > 140 else len(shop_sales):,} sales? "
                "Timings depend on the machine, so only the relative order is meaningful."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch2_use_case = mo.ui.dropdown(
        options=["Sales files for partners", "Dashboard cache", "Sales history for analysis", "Order event stream"],
        value="Sales files for partners",
        label="Use case",
    )
    ch2_priority = mo.ui.dropdown(
        options=["Interoperability", "Speed", "Small size", "Safety"],
        value="Interoperability",
        label="Primary criterion",
    )
    return ch2_priority, ch2_use_case


@app.cell
def _(ch2_priority, ch2_use_case, mo):
    # one row per job, one entry per priority in the order of the priority dropdown
    _recommendations = {
        "Sales files for partners": ["CSV for spreadsheets, Parquet for data teams", "Parquet", "Parquet, compressed with zstd (Part 2)", "CSV or Parquet; never Pickle"],
        "Dashboard cache": ["Parquet / Arrow", "Arrow (Feather), or self-produced Pickle", "Parquet", "Arrow or Parquet; no external Pickle"],
        "Sales history for analysis": ["Parquet", "Parquet or Arrow", "Parquet + zstd / snappy", "Parquet with schema checks"],
        "Order event stream": ["Avro / JSON", "Avro", "Avro with compression", "Avro + a schema registry: one shared copy of every schema"],
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
            mo.md("### Format selection by use case and criterion"),
            mo.md(
                "Each use case is combined with its primary criterion. **Interoperability** is the range of tools that "
                "can read the file: Excel, R, a partner's script. A **cache** is a stored copy the dashboard reloads "
                "instead of requesting the data again."
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
                f"**Starting point: {_recommendations[_pick[0]][_pick[1]]}.** A default to be validated by benchmarks "
                "on the EdgeWorks files, not a fixed rule."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: File Formats</h3>
      <details>
        <summary><strong>Q1:</strong> A partner asks for "the sales as a file". CSV, JSON or Parquet?</summary>
        <p><strong>Answer:</strong> It depends on the consuming tool. Excel: CSV in UTF-8, with documented column types
        (store codes are text). A data team: Parquet, which carries the types itself. A web application: JSON.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> A CSV file opened in Excel shows "ZÃ¼rich" instead of "Zürich". What happened?</summary>
        <p><strong>Answer:</strong> The file was written as UTF-8 and read as Windows-1252. It has to be imported with
        the correct encoding (in Excel: Data, From Text/CSV, UTF-8), or written for Excel with
        <code>encoding="utf-8-sig"</code>, which adds a marker that Excel recognises.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> A partner sends its sales as a Pickle file. Should it be loaded?</summary>
        <p><strong>Answer:</strong> No. Loading a Pickle file can execute arbitrary code embedded by the sender.
        Parquet or CSV should be requested instead, and all incoming data validated.</p>
      </details>
      <details>
        <summary><strong>Q4:</strong> Which format suits the order event stream, in which each order is sent as it occurs?</summary>
        <p><strong>Answer:</strong> Avro: compact rows with a schema, written one record at a time. New fields with
        defaults keep old and new consumers compatible; a schema registry stores one shared copy of every schema.</p>
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
    ### Part 1 Summary

    - Serialization converts objects into bytes; the format determines these bytes. Text formats (CSV, JSON)
      are readable, binary formats (Avro, Parquet, Arrow, Pickle) are compact and typed.
    - Text files require the matching encoding (UTF-8) and CSV dialect (separator, decimal mark); dates need
      an explicit format and a time zone (ISO 8601, stored in UTC).
    - CSV stores no types (`007` becomes `7`); Avro, Parquet and Arrow carry a schema, and Avro's defaults
      support schema evolution.
    - Arrow exchanges tables between tools in memory; Pickle executes code when it is loaded.
    - Latency and throughput are different goals; benchmarks on the actual data decide.
                """
            ).callout(kind="success"),
            mo.md(
                f"""
    ### Next: Part 2

    Total revenue needs one of the {_fields} fields of each sale. A row-oriented file nevertheless passes
    through all {_fields} fields of every sale: {_fields * len(shop_sales):,} values read to use {len(shop_sales):,}.
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
            mo.md("## Part 2 · Storage: Layout, Compression and Queries"),
            chapter_intro(
                "data",
                "Total revenue needs one column. Why does the query read the whole CSV file but only part of the Parquet file?",
                "How the bytes are arranged on disk, how they are compressed, how SQL reads them directly, and what a "
                "database adds to plain files.",
                topics=(
                    "Row vs column layout",
                    "Inside a Parquet file",
                    "Compression",
                    "SQL on files with DuckDB",
                    "Partitioned datasets",
                    "Schema on read and on write",
                    "Transactions and ACID",
                ),
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    ch3_query = mo.ui.radio(
        options=["Total revenue", "Look up sale 3,082", "Revenue in January 2026"],
        value="Total revenue",
        label="Query:",
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
        """Does the query use this field of this sale?"""
        if _q == "Total revenue":
            return field == "price"
        if _q == "Revenue in January 2026":  # every date, to find January; the price of January's sales
            return field == "date" or (field == "price" and sale >= _first_jan)
        return sale == _lookup

    def _row_reads(sale, field):
        """A row is read whole: every field of a sale the query touches is read."""
        return any(_needed(sale, _f) for _f in _fields)

    def _col_reads(sale, field):
        """An aggregate reads a column top to bottom; a lookup jumps to one value of every column."""
        if _q.startswith("Look up"):
            return sale == _lookup
        return any(_needed(_s, field) for _s in _sales)

    _cls = {"used": "dg-tier", "wasted": "dg-hot", "idle": "dg-box"}

    def _cell(x, y, reads, sale, field):
        state = "used" if _needed(sale, field) else "wasted" if reads(sale, field) else "idle"
        opacity = ' opacity="0.45"' if state == "idle" else ""
        return f'<rect class="{_cls[state]}" x="{x}" y="{y}" width="52" height="26" rx="4"{opacity}/>'

    _parts = [
        '<text x="0" y="20" font-weight="700">Row layout: one record after another</text>',
        '<text x="600" y="20" font-weight="700">Column layout: one field after another</text>',
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

    _parts.append(_tally(0, f"scans {_slips} record{'s' if _slips > 1 else ''}", _row_read))
    _parts.append(_tally(600, f"scans {_pages} column{'s' if _pages > 1 else ''}", _col_read))
    _parts += [
        f'<rect class="{_cls[_state]}" x="{_x}" y="{_tally_y + 22}" width="22" height="16" rx="3"/>'
        f'<text class="dg-muted" x="{_x + 30}" y="{_tally_y + 35}">{_label}</text>'
        for _x, _state, _label in [(0, "used", "needed"), (130, "wasted", "read, not needed"), (330, "idle", "not read")]
    ]
    _picture = diagram(
        "".join(_parts),
        width=1060,
        height=_tally_y + 44,
        label=f"{_q}: on six sales, the row layout scans {_slips} records and reads {_row_read} fields; the column "
        f"layout scans {_pages} columns and reads {_col_read} fields; the query needs {_used}.",
        tier="data",
    )

    # The same counts on the whole file, and the query result.
    _n = len(shop_sales)
    _jan = shop_sales[shop_sales["sale_date"].dt.strftime("%Y-%m") == "2026-01"]
    _one = shop_sales[shop_sales["sale_id"] == _lookup].iloc[0]
    if _q == "Total revenue":
        _notice = (
            f"**Observation:** on all {_n:,} sales the row layout reads **{_n * 7:,}** fields, the column layout "
            f"**{_n:,}**: only the prices. Result: CHF {shop_sales['total_price'].sum():,.2f}."
        )
    elif _q == "Revenue in January 2026":
        _notice = (
            f"**Observation:** on all {_n:,} sales the row layout reads **{_n * 7:,}** fields, the column layout "
            f"**{_n * 2:,}** (every date, every price) to use {_n + len(_jan):,}. Result: "
            f"CHF {_jan['total_price'].sum():,.2f} from {len(_jan)} sales."
        )
    else:
        _notice = (
            "**Observation:** a single-record lookup is the best case for the row layout. All 7 fields are stored together, "
            f"while the column layout accesses 7 columns for one value each. Sale {_lookup:,}: {_one['sale_date'].day} {_one['sale_date']:%B %Y}, {_one['product']}, "
            f"{_one['country']}, {_one['units_sold']} units, CHF {_one['total_price']:,.2f}."
        )

    mo.vstack(
        [
            mo.md("### Two Ways to Lay Out the Same Sales"),
            in_plain(
                "A file is a linear sequence of bytes, so the sales must be stored in some order. A **row layout** "
                "stores one complete sale after another (CSV, Avro, transactional databases) and suits single records "
                "(OLTP). A **column layout** stores one field after another, all 3,360 dates, then all 3,360 prices "
                "(Parquet), and suits aggregates over many records (OLAP)."
            ),
            ch3_query,
            _picture,
            mo.md(_notice),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p2_read_rows = mo.ui.slider(
        steps=[100_000, 300_000, 1_000_000], value=300_000, label="Sales in the file", show_value=True, debounce=True
    )
    p2_read_run = mo.ui.run_button(label="Run the read benchmark", kind="success")
    return p2_read_rows, p2_read_run


@app.cell
def _(
    Path,
    TIER,
    alt,
    best_seconds,
    chart_or_table,
    format_bytes,
    in_plain,
    mo,
    p2_read_rows,
    p2_read_run,
    pd,
    shop_sales,
    tempfile,
    tier_chart,
):
    _top = mo.vstack(
        [
            mo.md("### Reading one column: CSV vs Parquet"),
            in_plain(
                "In a row layout (CSV), the reader has to scan every line, even if only one column is needed. In a "
                "column layout (Parquet), it loads only the bytes of the requested column."
            ),
            mo.md(
                "The sales, repeated to the chosen size, written once as CSV and once as Parquet, then read with pandas: "
                'all columns, and only `total_price` (`usecols=["total_price"]` or `columns=["total_price"]`). Best of 3 runs.'
            ),
            mo.hstack([p2_read_rows, p2_read_run], justify="start", align="center", gap=2),
        ],
        gap=0.6,
    )
    mo.stop(
        not p2_read_run.value,
        mo.vstack(
            [_top, mo.md("**Question:** how much faster is reading only `total_price` from Parquet than from CSV?").callout(kind="neutral")],
            gap=0.6,
        ),
    )
    _cols = ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"]
    _n = p2_read_rows.value
    _sales = pd.concat([shop_sales[_cols]] * -(-_n // len(shop_sales)), ignore_index=True).head(_n)
    _rows = []
    with tempfile.TemporaryDirectory() as _td:
        _csv, _pq = Path(_td) / "sales.csv", Path(_td) / "sales.parquet"
        _sales.to_csv(_csv, index=False)
        _sales.to_parquet(_pq, index=False)
        for _format, _path, _all, _one in (
            ("CSV", _csv, lambda: pd.read_csv(_csv), lambda: pd.read_csv(_csv, usecols=["total_price"])),
            ("Parquet", _pq, lambda: pd.read_parquet(_pq), lambda: pd.read_parquet(_pq, columns=["total_price"])),
        ):
            for _what, _read in (("all 7 columns", _all), ("only total_price", _one)):
                _rows.append(
                    {
                        "format": _format,
                        "columns read": _what,
                        "ms": round(best_seconds(_read) * 1000, 1),
                        "file size": format_bytes(_path.stat().st_size),
                    }
                )
    _df = pd.DataFrame(_rows)
    _order = ["all 7 columns", "only total_price"]
    _bars = alt.Chart(_df).encode(
        y=alt.Y("format:N", sort=["CSV", "Parquet"], title=None),
        yOffset=alt.YOffset("columns read:N", sort=_order),
        x=alt.X("ms:Q", title="milliseconds", scale=alt.Scale(domain=[0, _df["ms"].max() * 1.25])),
        tooltip=list(_rows[0]),
    )
    _chart = (
        _bars.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("columns read:N", title=None, sort=_order, scale=alt.Scale(domain=_order, range=[TIER["muted"], TIER["data"]]))
        )
        + _bars.mark_text(align="left", dx=6).encode(text=alt.Text("ms:Q", format=",.1f"))
    ).properties(width="container", height=200, title=f"Read time for {_n:,} sales (ms)")
    _ms = {(_r["format"], _r["columns read"]): _r["ms"] for _r in _rows}
    _csv_one, _pq_one = _ms[("CSV", "only total_price")], _ms[("Parquet", "only total_price")]
    mo.vstack(
        [
            _top,
            chart_or_table(tier_chart(_chart, "data"), _rows, label="Read times, best of 3"),
            mo.md(
                f"**Observation:** reading only `total_price` from Parquet takes {_pq_one:,.1f} ms, "
                f"{_csv_one / max(_pq_one, 0.1):,.0f}× faster than from CSV. For CSV, `usecols` saves memory but "
                f"comparatively little time ({_ms[('CSV', 'all 7 columns')] / max(_csv_one, 0.1):.1f}× faster than "
                "reading everything): the parser still has to split every line."
            ),
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
    _closed = _open.count(False)
    mo.vstack(
        [
            mo.md("### Inside a Parquet File: Row Groups, Column Chunks, a Footer"),
            in_plain(
                "Parquet divides the rows into blocks. A **row group** is a block of sales (here 420, about three "
                "months). Within it, the values of each field are stored together in a **column chunk**. At the end "
                "of the file, the **footer** records the smallest and largest value of each chunk, its **min-max "
                "statistics**. A reader consults the footer first and skips every row group that cannot contain a match."
            ),
            _binder,
            mo.md(
                f"**Observation:** for the January revenue query, the footer excludes {_closed} of {len(_groups)} row "
                f"groups without reading them, and in the remaining one only the date and price chunks are read: "
                f"**2 of {len(_groups) * 7} chunks**. This works because the file is sorted by date, as the next "
                "experiment shows."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, diagram, duckdb, format_bytes, in_plain, mo, pd, tempfile):
    _df = pd.read_parquet(SALES_SEED)
    _from, _to = "2026-01-01", "2026-02-01"
    _query = f"SELECT sum(total_price) FROM 'sales.parquet' WHERE sale_date >= '{_from}' AND sale_date < '{_to}'"

    with tempfile.TemporaryDirectory() as _td:
        _files = {"sorted by date": Path(_td) / "sorted.parquet", "random order": Path(_td) / "shuffled.parquet"}
        _df.sort_values("sale_date").to_parquet(_files["sorted by date"], index=False, row_group_size=420)
        _df.sample(frac=1, random_state=7).to_parquet(_files["random order"], index=False, row_group_size=420)

        _con = duckdb.connect()
        _result = {}
        for _label, _path in _files.items():
            _md = _con.execute(
                "SELECT row_group_id, path_in_schema, total_compressed_size, stats_min, stats_max "
                f"FROM parquet_metadata('{_path.as_posix()}')"
            ).df()
            # The footer's min-max statistics: a row group is read unless its dates end before January or start after it.
            _dates = _md[_md["path_in_schema"] == "sale_date"].sort_values("row_group_id")
            _read = (_dates["stats_max"] >= _from) & (_dates["stats_min"] < _to)
            # what the query reads: the date and price chunks of those row groups
            _chunks = _md[
                _md["path_in_schema"].isin(["sale_date", "total_price"]) & _md["row_group_id"].isin(_dates["row_group_id"][_read])
            ]
            _result[_label] = {
                "groups": list(zip(_dates["stats_min"].str[:7], _dates["stats_max"].str[:7], _read)),
                "read": int(_read.sum()),
                "bytes": int(_chunks["total_compressed_size"].sum()),
                "revenue": _con.execute(_query.replace("'sales.parquet'", f"'{_path.as_posix()}'")).fetchone()[0],
            }
        _con.close()

    # One strip per file: each row group with the date range its footer records, read (tier) or skipped (grey).
    _parts = []
    for _r, (_label, _res) in enumerate(_result.items()):
        _y, _all = _r * 84, len(_res["groups"])
        _parts.append(f'<text x="0" y="{_y + 25}" font-weight="700">{_label}</text>')
        _parts.append(
            f'<text class="{"dg-hot" if _res["read"] == _all else "dg-ok"}" x="0" y="{_y + 51}">'
            f'reads {_res["read"]} of {_all} · {format_bytes(_res["bytes"])}</text>'
        )
        for _s, (_lo, _hi, _open) in enumerate(_res["groups"]):
            _x = 230 + _s * 111
            _parts.append(
                f'<rect class="{"dg-tier" if _open else "dg-box"}" x="{_x}" y="{_y}" width="104" height="62" rx="10"/>'
                f'<text x="{_x + 52}" y="{_y + 26}" text-anchor="middle">{_lo}</text>'
                f'<text class="dg-muted" x="{_x + 52}" y="{_y + 50}" text-anchor="middle">to {_hi}</text>'
            )
    _parts.append(
        '<text class="dg-muted" x="230" y="176">one box per row group of 420 sales, labelled with the date range in '
        "the footer; blue: read, grey: skipped</text>"
    )
    _sorted, _random = _result.values()
    _strip = diagram(
        "".join(_parts),
        width=1120,
        height=184,
        label=f"Sorted by date, each row group spans three months and the query reads {_sorted['read']} of "
        f"{len(_sorted['groups'])}. In random order, every row group spans all dates and the query reads "
        f"{_random['read']} of {len(_random['groups'])}.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Does the Write Order of the Sales Matter?"),
            in_plain(
                f"Min-max statistics only help when similar values are stored together. The same {len(_df):,} sales "
                "are written to Parquet twice, 420 per row group: sorted by date, and in random order. Both files "
                "answer the same query:"
            ),
            mo.md(f"```sql\n{_query}\n```"),
            _strip,
            mo.md(
                f"**Observation:** both files return CHF {_sorted['revenue']:,.2f}. Sorted, the footer excludes "
                f"{len(_sorted['groups']) - _sorted['read']} of {len(_sorted['groups'])} row groups, and the query "
                f"reads {format_bytes(_sorted['bytes'])}. In random order, every row group spans all dates, nothing "
                f"can be excluded, and the query reads {format_bytes(_random['bytes'])}, "
                f"{_random['bytes'] / _sorted['bytes']:.0f}× as much. Sorting by a column that queries filter on "
                "makes these queries cheaper."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SALES_SEED, diagram, format_bytes, gzip, in_plain, mo, pd):
    _csv = pd.read_parquet(SALES_SEED).to_csv(index=False).encode()
    _gz = gzip.compress(_csv, 6)
    # A sketch of the timing model, not a measurement: segment lengths only show which step grows.
    _amber = ' style="fill: color-mix(in srgb, var(--amber) 22%, transparent); stroke: var(--amber); stroke-width: 1.5"'
    _kinds = {"transfer": ' class="dg-tier"', "decompress": _amber, "compute": ' class="dg-box"'}

    def _bar(y, name, parts, verdict=""):
        x, out = 190, [f'<text x="0" y="{y + 25}">{name}</text>']
        for kind, w in parts:
            out.append(f'<rect{_kinds[kind]} x="{x}" y="{y}" width="{w}" height="38" rx="6"/>')
            out.append(f'<text x="{x + w / 2:.0f}" y="{y + 25}" text-anchor="middle">{kind}</text>')
            x += w + 3
        return "".join(out) + verdict.format(x=x + 12, y=y + 25)

    _faster = '<text class="dg-ok" x="{x}" y="{y}">&#10003; faster</text>'
    _slower = '<text class="dg-hot" x="{x}" y="{y}">&#10007; slower</text>'
    _sketch = diagram(
        '<text x="0" y="20" font-weight="700">Downloaded over a network: the transfer dominates</text>'
        + _bar(36, "plain CSV", [("transfer", 540), ("compute", 110)])
        + _bar(82, "gzipped CSV", [("transfer", 190), ("decompress", 120), ("compute", 110)], _faster)
        + '<text x="0" y="160" font-weight="700">Already in memory: there is no transfer to shorten</text>'
        + _bar(176, "plain CSV", [("compute", 110)])
        + _bar(222, "gzipped CSV", [("decompress", 120), ("compute", 110)], _slower),
        width=1000,
        height=270,
        label="A sketch: over a network, the gzipped file saves more transfer time than decompression adds, so the "
        "total time decreases. In memory, there is no transfer to save, and decompression makes it slower.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### The Compression Trade-off: Fewer Bytes, More Decompression"),
            in_plain(
                "Compression stores the same data in fewer bytes, and every reader must decompress it before using "
                "it. Compression pays off when moving the bytes takes longer than decompressing them, and costs time "
                "when the data is already in memory."
            ),
            _sketch,
            mo.md(
                "**Formally:** time ≈ transfer + decompress + compute. Compression shortens only the transfer, by "
                f"the ratio $r$ = compressed size / original size: for the sales as CSV, {format_bytes(len(_gz))} / "
                f"{format_bytes(len(_csv))} = {len(_gz) / len(_csv):.2f}. *The bar lengths are schematic; a later "
                "experiment measures both cases.*"
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SALES_SEED, diagram, format_bytes, in_plain, io, mo, pd):
    _src = pd.read_parquet(SALES_SEED, columns=["sale_id", "total_price"])
    _truth = round(float(_src["total_price"].sum()), 2)
    _variants = []
    for _label, _digits in (("exact", None), ("rounded to 1 CHF", 0), ("rounded to 100 CHF", -2)):
        _stored = _src if _digits is None else _src.assign(total_price=_src["total_price"].round(_digits))
        _blob = _stored.to_parquet(index=False, compression="gzip")  # no path: the file's bytes
        _back = pd.read_parquet(io.BytesIO(_blob))["total_price"]
        _variants.append(
            {
                "label": _label,
                "first": float(_back.iloc[0]),
                "bytes": len(_blob),
                "deviation": round(float(_back.sum()) - _truth, 2),
                "largest change": float((_back - _src["total_price"]).abs().max()),
            }
        )
    _exact, _franc, _hundred = _variants

    # One card per way of storing the prices: the first sale's price, the file size, what the total becomes.
    _cards = []
    for _i, _v in enumerate(_variants):
        _x, _cx = _i * 350, _i * 350 + 160
        _size = format_bytes(_v["bytes"]) + (f" ({_v['bytes'] / _exact['bytes'] - 1:+.0%})" if _i else "")
        _total = f"total off by CHF {_v['deviation']:+,.2f}" if _v["deviation"] else "total revenue exact"
        _cards.append(
            f'<rect class="dg-box {"dg-hot" if _i else "dg-ok"}" x="{_x}" y="0" width="320" height="150" rx="12"/>'
            f'<text x="{_cx}" y="32" text-anchor="middle" font-weight="700">{_v["label"]}</text>'
            f'<text x="{_cx}" y="64" text-anchor="middle">sale #1: CHF {_v["first"]:,.2f}</text>'
            f'<text class="dg-muted" x="{_cx}" y="94" text-anchor="middle">file: {_size}</text>'
            f'<text class="{"dg-hot" if _v["deviation"] else "dg-ok"}" x="{_cx}" y="126" text-anchor="middle">{_total}</text>'
        )
    _drawing = diagram(
        "".join(_cards),
        width=1020,
        height=150,
        label=f"The prices stored exactly: {format_bytes(_exact['bytes'])}, exact total. Rounded to 1 franc: "
        f"{format_bytes(_franc['bytes'])}, total off by CHF {_franc['deviation']:+,.2f}. Rounded to 100 francs: "
        f"{format_bytes(_hundred['bytes'])}, total off by CHF {_hundred['deviation']:+,.2f}.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Lossless and Lossy Compression"),
            mo.md(
                """
    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">=</div><div class="tile-title">Lossless</div>
        <p>Decompression restores every bit: gzip, zstd, PNG, Parquet's encodings. Required for prices, identifiers and dates.</p></div>
      <div class="tile"><div class="tile-key">&asymp;</div><div class="tile-title">Lossy</div>
        <p>Smaller, but the original cannot be restored: JPEG, MP3, video. Acceptable where small deviations go unnoticed.</p></div>
    </div>
                """
            ),
            in_plain(
                "Lossy methods usually round values first (quantisation) and then compress losslessly: fewer distinct "
                f"values give more repetition. Below, the {len(_src):,} EdgeWorks prices are stored as Parquet with "
                "gzip, once exactly and twice rounded."
            ),
            _drawing,
            mo.md(
                f"**Observation:** rounded to 100 francs, the file is {1 - _hundred['bytes'] / _exact['bytes']:.0%} "
                f"smaller, but each price changes by up to CHF {_hundred['largest change']:,.2f}, and the exact prices "
                "cannot be recovered. For prices, identifiers and dates, only lossless compression is acceptable."
            ),
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
            mo.md("### Dictionary Encoding: Each Product Name Stored Once"),
            in_plain(
                "A column with few distinct values is stored as a short list of these values, the **dictionary**, "
                "plus one small integer per sale, its **code**, which references an entry in the list. Parquet applies "
                "this encoding by default."
            ),
            _drawing,
            mo.md(
                f"**Observation:** on all {len(_names):,} sales, {_names.nunique()} products with "
                f"{_names.value_counts().iloc[0]:,} sales each, {_raw:,} bytes of names become {_dictionary} bytes of "
                f"dictionary plus {len(_names):,} codes of {_code_bits} bits: {_total:,.0f} bytes, "
                f"**{_total / _raw:.1%}** of the names stored in full."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch4_columns = mo.ui.radio(
        options=["the whole sale (7 fields)", "prices only", "category only"],
        value="the whole sale (7 fields)",
        label="Stored columns:",
        inline=True,
    )
    return (ch4_columns,)


@app.cell
def _(TIER, alt, ch4_columns, csv, format_bytes, gzip, io, json, mo, pa, pd, pq, shop_sales, tier_chart):
    _fields = {
        "the whole sale (7 fields)": ["sale_id", "sale_date", "product", "country", "units_sold", "total_price", "customer_rating"],
        "prices only": ["total_price"],
        "category only": ["category"],
    }[ch4_columns.value]
    _sales = shop_sales[_fields]
    if "sale_date" in _fields:  # a date as a partner's file writes it
        _sales = _sales.assign(sale_date=_sales["sale_date"].dt.strftime("%Y-%m-%d"))
    _records = _sales.to_dict("records")
    _csv = io.StringIO()
    _writer = csv.DictWriter(_csv, fieldnames=_fields)
    _writer.writeheader()
    _writer.writerows(_records)

    # Sizes measured in memory: the bytes a file would hold, without writing one. gzip at level 6, its usual default.
    _texts = {"JSON": json.dumps(_records).encode(), "CSV": _csv.getvalue().encode()}
    _sizes = {_name: len(_blob) for _name, _blob in _texts.items()}
    _sizes |= {f"{_name} + gzip": len(gzip.compress(_blob, 6)) for _name, _blob in _texts.items()}
    _table = pa.Table.from_pylist(_records)
    for _codec, _name in (("snappy", "Parquet (snappy, the default)"), ("zstd", "Parquet (zstd)")):
        _buf = io.BytesIO()
        pq.write_table(_table, _buf, compression=_codec)
        _sizes[_name] = len(_buf.getvalue())

    _best = min(_sizes, key=_sizes.get)
    _compressed = [_size for _name, _size in _sizes.items() if _name not in ("JSON", "CSV")]
    _df = pd.DataFrame({"format": list(_sizes), "bytes": list(_sizes.values())})
    _df["label"] = [format_bytes(_b) for _b in _df["bytes"]]
    _df["smallest"] = _df["format"] == _best
    _base = alt.Chart(_df).encode(
        y=alt.Y("format:N", sort=None, title=None, axis=alt.Axis(labelLimit=320)),
        x=alt.X("bytes:Q", title=None, axis=None, scale=alt.Scale(domain=[0, _df["bytes"].max() * 1.25])),
        tooltip=["format:N", "bytes:Q"],
    )
    _chart = (
        _base.mark_bar(cornerRadiusEnd=4).encode(color=alt.condition("datum.smallest", alt.value(TIER["data"]), alt.value(TIER["muted"])))
        + _base.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=40 * len(_df), title=f"{len(_sales):,} sales, {ch4_columns.value}")

    _distinct = _sales[_fields[0]].nunique()  # used for the one-column choices
    _reason = {
        "the whole sale (7 fields)": "Compression matters more than the format: every compressed variant needs "
        f"{format_bytes(min(_compressed))} to {format_bytes(max(_compressed))}, the JSON {format_bytes(_sizes['JSON'])}.",
        "prices only": f"{_distinct:,} distinct prices repeat little. Parquet stores each as an 8-byte number; the "
        "CSV holds only the digits written, which gzip compresses well.",
        "category only": f"{_distinct} distinct values, repeated {len(_sales):,} times: every compressed variant "
        "reduces the column to almost nothing; what remains is mostly fixed overhead, such as Parquet's footer.",
    }[ch4_columns.value]
    mo.vstack(
        [
            mo.md("### Which Format Is Smallest for the Sales Data?"),
            mo.md(
                "**Question:** JSON, CSV or Parquet, with or without compression? Does the answer depend on the "
                "stored columns?"
            ),
            ch4_columns,
            tier_chart(_chart, "data"),
            mo.md(
                f"**Observation:** the smallest variant is **{_best}**, {format_bytes(_sizes[_best])}, "
                f"{_sizes[_best] / _sizes['JSON']:.1%} of the JSON. {_reason}"
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    run_ctime = mo.ui.run_button(label="Run compression timing", kind="success")
    return (run_ctime,)


@app.cell
def _(SALES_SEED, TIER, alt, best_seconds, format_bytes, gzip, io, mo, pd, run_ctime, tier_chart):
    _raw = pd.read_parquet(SALES_SEED).to_csv(index=False).encode("utf-8")
    _gz = gzip.compress(_raw, 6)
    _mbit = 50  # a typical home connection, as on the slide "Aggregate where the data is"
    _top = mo.vstack(
        [
            mo.md("### Is the Gzipped Sales File Faster to Query?"),
            mo.md(
                f"Total revenue is computed from the sales as CSV ({format_bytes(len(_raw))}) or gzipped "
                f"({format_bytes(len(_gz))}), in two situations: the file is already in memory, or it is first "
                f"downloaded at {_mbit} Mbit/s. Decompressing and parsing are measured on this computer; the download "
                "time follows from the file size."
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
                    "**Question:** the gzipped file is about a third of the size. Is total revenue computed faster "
                    "or slower from it?"
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    def _ms(_fn, _calls=20):
        """Milliseconds per call, fastest of 5 bursts. A burst averages out sub-millisecond noise."""
        return best_seconds(_fn, repeat=5, number=_calls) * 1000

    # Decompressed, the gzipped file holds the same bytes, so both variants parse the same text.
    _parse = _ms(lambda: pd.read_csv(io.BytesIO(_raw))["total_price"].sum())
    _decompress = _ms(lambda: gzip.decompress(_gz))
    _steps = []
    for _where in ("in memory", f"at {_mbit} Mbit/s"):
        for _file, _size in (("plain CSV", len(_raw)), ("gzipped CSV", len(_gz))):
            _variant = f"{_file}, {_where}"
            if _where != "in memory":
                _steps.append({"variant": _variant, "step": "download", "ms": _size * 8 / (_mbit * 1e6) * 1000})
            if _file == "gzipped CSV":
                _steps.append({"variant": _variant, "step": "decompress", "ms": _decompress})
            _steps.append({"variant": _variant, "step": "parse + sum", "ms": _parse})
    _df = pd.DataFrame(_steps)
    _df["order"] = _df["step"].map({"download": 0, "decompress": 1, "parse + sum": 2})
    _totals = _df.groupby("variant", sort=False)["ms"].sum()
    _mem_plain, _mem_gz, _net_plain, _net_gz = _totals.tolist()
    _ends = pd.DataFrame(
        {
            "variant": _totals.index,
            "ms": _totals.values,
            "label": [
                f"{_mem_plain:.1f} ms",
                f"{_mem_gz:.1f} ms ({_mem_gz / _mem_plain - 1:+.0%})",
                f"{_net_plain:.1f} ms",
                f"{_net_gz:.1f} ms ({_net_gz / _net_plain - 1:+.0%})",
            ],
        }
    )
    _y = alt.Y("variant:N", sort=None, title=None, axis=alt.Axis(labelLimit=320))
    _bars = alt.Chart(_df).mark_bar().encode(
        y=_y,
        x=alt.X("ms:Q", stack="zero", title="ms", scale=alt.Scale(domain=[0, _totals.max() * 1.3])),
        color=alt.Color(
            "step:N",
            title=None,
            scale=alt.Scale(domain=["download", "decompress", "parse + sum"], range=[TIER["data"], TIER["amber"], TIER["muted"]]),
        ),
        order=alt.Order("order:Q"),
        tooltip=["variant:N", "step:N", alt.Tooltip("ms:Q", format=".2f")],
    )
    _chart = (_bars + alt.Chart(_ends).mark_text(align="left", dx=6).encode(y=_y, x="ms:Q", text="label:N")).properties(
        width="container", height=200, title="Time to compute total revenue"
    )
    mo.vstack(
        [
            _top,
            tier_chart(_chart, "data"),
            mo.md(
                f"**Observation:** in memory, the gzipped file is slower ({_mem_gz:.1f} vs {_mem_plain:.1f} ms): "
                f"decompressing takes {_decompress:.1f} ms, and there is no download to shorten. Downloaded first, it "
                f"is faster ({_net_gz:.1f} vs {_net_plain:.1f} ms): the download shrinks by more than decompressing "
                "costs. Compression pays off when moving the bytes is the slowest step."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SEED_DIR, alt, best_seconds, chart_or_table, duckdb, in_plain, mo, tier_chart):
    from textwrap import dedent as _dedent

    # Exactly what runs: DuckDB finds the three file names in data/seed/.
    _sql = _dedent(
        """
        SELECT r.name AS region, sum(s.total_price) AS revenue
        FROM 'sales.parquet' s                            -- the 3,360 sales
        JOIN 'countries.parquet' c USING (country_id)     -- each sale's country
        JOIN 'sales_regions.parquet' r USING (region_id)  -- each country's region
        GROUP BY region                                   -- one total per region
        ORDER BY revenue DESC
        """
    ).strip()
    with duckdb.connect() as _con:
        _con.execute(f"SET file_search_path = '{SEED_DIR}'")
        _answer = _con.execute(_sql).df()
        _ms = best_seconds(lambda: _con.execute(_sql).fetchall()) * 1000

    _answer["label"] = [f"CHF {_v / 1e6:,.1f} M" for _v in _answer["revenue"]]
    _bars = alt.Chart(_answer).encode(
        y=alt.Y("region:N", sort=None, title=None),
        x=alt.X("revenue:Q", axis=None, scale=alt.Scale(domain=[0, _answer["revenue"].max() * 1.3])),
    )
    _chart = (_bars.mark_bar(cornerRadiusEnd=4) + _bars.mark_text(align="left", dx=6).encode(text="label:N")).properties(
        width="container", height=230, title="Revenue per region, March 2024 to February 2026"
    )
    mo.vstack(
        [
            mo.md("### Revenue per region, computed directly from the files"),
            in_plain(
                "**DuckDB** is an embedded database that runs inside the Python process: after `import duckdb`, there "
                "is no server to install, start or administer. It reads Parquet and CSV files by file name and "
                "executes **SQL**, the standard query language of relational databases."
            ),
            mo.hstack(
                [
                    mo.md(f"`duckdb.sql(query)`, with this query:\n\n```sql\n{_sql}\n```"),
                    chart_or_table(
                        tier_chart(_chart, "data"),
                        [{"region": _r, "revenue (CHF)": f"{_v:,.2f}"} for _r, _v in zip(_answer["region"], _answer["revenue"], strict=True)],
                        label="Revenue per region",
                    ),
                ],
                widths=[1, 1],
                gap=2,
            ),
            mo.md(
                f"**Observation:** three files joined, four totals returned in {_ms:.1f} ms, without any prior loading "
                "or import. DuckDB is an *analytical* (OLAP) database: designed for aggregates over many rows, not for "
                "recording single sales one at a time (the transactional workload at the end of this part)."
            ).callout(kind="info"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    # The queries, each as (what it selects, its filter, its grouping, the observation).
    ch5_question = mo.ui.dropdown(
        options={
            "Total revenue, all time": (
                "sum(total_price)",
                None,
                None,
                "one column of seven, every row: a row layout would read all seven.",
            ),
            "Revenue in January 2026": (
                "sum(total_price)",
                "sale_date BETWEEN '2026-01-01' AND '2026-01-31'",
                None,
                "the date is checked on all 3,360 rows, the price fetched only for the 140 January sales. They are "
                "contiguous near the end, because the file is stored month by month.",
            ),
            "Revenue per country": (
                "country_id, sum(total_price)",
                None,
                "country_id",
                "no filter, so every row is included, but only two of the seven columns are read.",
            ),
            "Average rating of the Gateway Node Pro (product 2)": (
                "avg(customer_rating)",
                "product_id = 2",
                None,
                "its 480 sales are spread across the file: thin stripes, not one contiguous band. Still only two "
                "columns are read, and the rating only where the product matches.",
            ),
            "Every field of every sale": (
                "*",
                None,
                None,
                "nothing can be skipped: <code>SELECT *</code> reads every cell. Queries should name only the columns "
                "they need.",
            ),
        },
        value="Revenue in January 2026",
        label="Query",
    )
    return (ch5_question,)


@app.cell
def _(SALES_SEED, ch5_question, diagram, duckdb, in_plain, mo, np, pd):
    _select, _where, _group, _note = ch5_question.value
    _sql = (
        f"SELECT {_select}\nFROM 'sales.parquet'"
        + (f"\nWHERE {_where}" if _where else "")
        + (f"\nGROUP BY {_group}" if _group else "")
    )
    _sales = pd.read_parquet(SALES_SEED)  # in the file's own order: month by month
    _n, _columns = len(_sales), list(_sales.columns)
    with duckdb.connect() as _con:
        _answer = _con.execute(_sql.replace("'sales.parquet'", "read_parquet(?)"), [str(SALES_SEED)]).fetchall()
        _kept_ids = (
            [_r[0] for _r in _con.execute(f"SELECT sale_id FROM read_parquet(?) WHERE {_where}", [str(SALES_SEED)]).fetchall()]
            if _where
            else list(_sales["sale_id"])
        )
    _kept = np.flatnonzero(_sales["sale_id"].isin(_kept_ids))  # positions in the file of the rows that pass
    _runs = np.split(_kept, np.flatnonzero(np.diff(_kept) > 1) + 1) if len(_kept) else []

    # How each column is read: every row ("all"), only the rows that pass ("kept"), or not at all.
    _filter_cols = {_c for _c in _columns if _where and _c in _where}
    _used = set(_columns) if _select == "*" else {_c for _c in _columns if _c in _sql}
    _how = {_c: "all" if _c in _filter_cols or (_c in _used and not _where) else "kept" if _c in _used else "none" for _c in _columns}
    _read = sum(_n if _h == "all" else len(_kept) if _h == "kept" else 0 for _h in _how.values())

    _top, _tall, _step, _w = 40, 230, 132, 120
    _parts = [
        f'<text class="dg-muted" x="0" y="{_top + 14}">row 1</text>',
        f'<text class="dg-muted" x="0" y="{_top + 34}">Mar 2024</text>',
        f'<text class="dg-muted" x="0" y="{_top + _tall - 22}">row {_n:,}</text>',
        f'<text class="dg-muted" x="0" y="{_top + _tall - 2}">Feb 2026</text>',
    ]
    for _i, _c in enumerate(_columns):
        _x = 92 + _i * _step
        _parts.append(f'<text x="{_x + _w / 2}" y="24" text-anchor="middle" font-size="15">{_c}</text>')
        _parts.append(
            f'<rect x="{_x}" y="{_top}" width="{_w}" height="{_tall}" style="fill: color-mix(in srgb, var(--ink) 9%, transparent)"/>'
        )
        if _how[_c] == "all":
            _parts.append(f'<rect x="{_x}" y="{_top}" width="{_w}" height="{_tall}" style="fill: var(--tier)"/>')
        elif _how[_c] == "kept":
            # each run of neighbouring rows that pass, at least a sliver so a single row still shows
            _parts += [
                f'<rect x="{_x}" y="{_top + _tall * _r[0] / _n:.2f}" width="{_w}" height="{max(_tall * len(_r) / _n, 0.8):.2f}" style="fill: var(--tier)"/>'
                for _r in _runs
            ]
        _says = {"all": f"{_n:,} read", "kept": f"{len(_kept):,} read", "none": "skipped"}[_how[_c]]
        _parts.append(f'<text class="dg-muted" x="{_x + _w / 2}" y="{_top + _tall + 26}" text-anchor="middle">{_says}</text>')
    _picture = diagram(
        "".join(_parts),
        width=92 + 7 * _step,
        height=_top + _tall + 40,
        label=f"The sales file as seven column strips, row 1 at the top. Blue cells are read: {_read:,} of {_n * len(_columns):,}.",
        tier="data",
    )
    if len(_answer) > 1 or len(_answer[0]) > 1:
        _value = f"{len(_answer):,} rows"
    else:
        _value = f"CHF {_answer[0][0]:,.2f}" if _select.startswith("sum") else f"{_answer[0][0]:,.2f}"
    mo.vstack(
        [
            mo.md("### Which parts of the file does a query read?"),
            in_plain(
                "**Pushdown**: DuckDB moves parts of the query into the scan of the file and reads only what is "
                "needed. *Projection pushdown* reads only the columns the query references. *Predicate pushdown* "
                "evaluates the filter (the `WHERE` condition) during the scan: the filter column is checked on every "
                "row, the other columns are fetched only for qualifying rows."
            ),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            ch5_question,
                            mo.md(f"```sql\n{_sql}\n```"),
                            mo.hstack(
                                [
                                    mo.stat(f"{_read:,}", label="cells read", caption=f"of {_n * len(_columns):,} in the file", bordered=True),
                                    mo.stat(f"{_n * len(_columns) / _read:,.1f}x", label="reduction", bordered=True),
                                    mo.stat(_value, label="result", bordered=True),
                                ],
                                widths="equal",
                            ),
                        ],
                        gap=0.6,
                    ),
                    _picture,
                ],
                widths=[2, 3],
                gap=2,
            ),
            mo.md(f"**Observation:** {_note}").callout(kind="info"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    ch5_copies = mo.ui.slider(
        1, 30, value=1, label="Copies of the 3,360 sales (simulates a larger data volume)", show_value=True, debounce=True
    )
    ch5_run_sources = mo.ui.run_button(label="Run the query on all three sources", kind="success")
    return ch5_copies, ch5_run_sources


@app.cell
def _(
    Path,
    TIER,
    alt,
    best_seconds,
    ch5_copies,
    ch5_run_sources,
    chart_or_table,
    duckdb,
    format_bytes,
    format_ms,
    in_plain,
    mo,
    pd,
    shop_sales,
    tempfile,
    tier_chart,
):
    _top = mo.vstack(
        [
            mo.md("### One query, three storage formats"),
            in_plain(
                "The same sales are stored three ways: a **CSV** file (plain text), a **Parquet** file (typed columns) "
                "and a **DuckDB table** (loaded once into DuckDB's own file format). The revenue per "
                "region query runs on each and is timed. Only the `FROM` clause changes: `FROM 'sales.csv'`, "
                "`FROM 'sales.parquet'`, `FROM sales`."
            ),
            mo.hstack([ch5_copies, ch5_run_sources], justify="start", align="center", gap=2),
        ],
        gap=0.6,
    )
    mo.stop(
        not ch5_run_sources.value,
        mo.vstack(
            [
                _top,
                mo.md(
                    "**Question:** which source answers fastest, and which file is the smallest?"
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )

    # The sales with their names joined in, as a partner would get them: 8 columns, region among them.
    _flat = shop_sales[["sale_id", "sale_date", "product", "country", "region", "units_sold", "total_price", "customer_rating"]]
    _sales = pd.concat([_flat] * ch5_copies.value, ignore_index=True)
    _sql = "SELECT region, sum(total_price) AS revenue FROM {} GROUP BY region ORDER BY revenue DESC"
    with tempfile.TemporaryDirectory() as _td:
        _csv, _parquet, _db = (Path(_td) / _name for _name in ("sales.csv", "sales.parquet", "sales.duckdb"))
        _sales.to_csv(_csv, index=False)
        _sales.to_parquet(_parquet, index=False)
        with duckdb.connect(_db) as _con:

            def _best(sql, params=()):  # best of 3, so a cold first run does not decide the ranking
                return best_seconds(lambda: _con.execute(sql, params).fetchall())

            _load_csv = _best("CREATE OR REPLACE TABLE sales AS FROM read_csv(?)", [str(_csv)])
            _query_csv = _best(_sql.format("read_csv(?)"), [str(_csv)])
            _query_parquet = _best(_sql.format("read_parquet(?)"), [str(_parquet)])
            _query_table = _best(_sql.format("sales"))

        _csv_size, _parquet_size, _db_size = (_p.stat().st_size for _p in (_csv, _parquet, _db))

    _sources = [
        # name, file, size, per query, load into a table once
        ("CSV file", "sales.csv", _csv_size, _query_csv, _load_csv),
        ("Parquet file", "sales.parquet", _parquet_size, _query_parquet, None),
        ("DuckDB table", "sales.duckdb", _db_size, _query_table, None),
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
    ).properties(width="container", height=230, title="Time (best of 3 runs)")
    _sized = alt.Chart(
        pd.DataFrame({"source": _names, "bytes": [_s[2] for _s in _sources], "label": [format_bytes(_s[2]) for _s in _sources]})
    ).encode(
        y=alt.Y("source:N", sort=_names, title=None, axis=None),
        x=alt.X("bytes:Q", axis=None, scale=alt.Scale(domain=[0, max(_s[2] for _s in _sources) * 1.6])),
    )
    _size = (
        _sized.mark_bar(cornerRadiusEnd=4, color=TIER["muted"]) + _sized.mark_text(align="left", dx=6).encode(text="label:N")
    ).properties(width="container", height=230, title="File size")


    mo.vstack(
        [
            _top,
            chart_or_table(
                mo.hstack([tier_chart(_time, "data"), tier_chart(_size, "data")], widths=[2, 1], gap=2),
                _rows,
                label=f"Revenue per region on {len(_sales):,} sales, three sources (best of 3 runs)",
            ),
            mo.md(
                f"**Observation:** the CSV is {_query_csv / _query_parquet:,.0f}x slower than Parquet. It is text that is "
                "parsed into numbers on every query; Parquet and the table store typed columns. Loading the CSV into a "
                f"table once costs as much as {_load_csv / _query_csv:.1f} CSV queries."
            ).callout(kind="info"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p2_partition_filter = mo.ui.dropdown(
        options={
            "January 2026": "year = 2026 AND month = 1",
            "the whole of 2025": "year = 2025",
            "one product, all time": "product_id = 2",
        },
        value="January 2026",
        label="Filter",
    )
    return (p2_partition_filter,)


@app.cell
def _(Path, SALES_SEED, diagram, duckdb, format_bytes, in_plain, mo, p2_partition_filter, re, tempfile):
    _where = p2_partition_filter.value
    _sql = (
        "SELECT round(sum(total_price), 2) AS revenue, count(*) AS sales\n"
        "FROM read_parquet('sales/*/*/*.parquet', hive_partitioning = true)\n"
        f"WHERE {_where}"
    )
    with tempfile.TemporaryDirectory() as _td:
        _root = Path(_td) / "sales"
        with duckdb.connect() as _con:
            # one folder per year and month, as data lakes store large tables
            _con.execute(
                "COPY (SELECT *, year(sale_date) AS year, month(sale_date) AS month "
                f"FROM read_parquet('{SALES_SEED.as_posix()}')) "
                f"TO '{_root.as_posix()}' (FORMAT parquet, PARTITION_BY (year, month))"
            )
            _run = _sql.replace("'sales/", f"'{_root.as_posix()}/")
            _revenue, _count = _con.execute(_run).fetchone()
            _plan = "\n".join(_row[-1] for _row in _con.execute(f"EXPLAIN ANALYZE {_run}").fetchall())
            _keys = {
                (int(re.search(r"year=(\d+)", _f.as_posix())[1]), int(re.search(r"month=(\d+)", _f.as_posix())[1])): _f.stat().st_size
                for _f in _root.rglob("*.parquet")
            }
            # the folders the filter selects, decided on the folder names alone; a filter on other columns selects none
            try:
                _values = ", ".join(f"({_y}, {_m})" for _y, _m in _keys)
                _picked = set(_con.execute(f"SELECT year, month FROM (VALUES {_values}) AS t(year, month) WHERE {_where}").fetchall())
            except duckdb.Error:
                _picked = set(_keys)
    _files_read = int(re.search(r"Total Files Read:\s*(\d+)", _plan)[1])  # as DuckDB reports it
    _bytes_read = sum(_size for _key, _size in _keys.items() if _key in _picked)

    _parts = [
        f'<text class="dg-muted" x="{150 + _m * 76:.0f}" y="18" text-anchor="middle">{_name}</text>'
        for _m, _name in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ]
    for _r, _year in enumerate(sorted({_y for _y, _ in _keys})):
        _y0 = 30 + _r * 56
        _parts.append(f'<text x="0" y="{_y0 + 28}" font-family="monospace" font-size="16">year={_year}/</text>')
        for _m in range(1, 13):
            if (_year, _m) in _keys:
                _lit = (_year, _m) in _picked
                _parts.append(
                    f'<rect class="{"dg-tier" if _lit else "dg-box"}" x="{116 + (_m - 1) * 76}" y="{_y0}" width="68" height="44"'
                    f' rx="8" opacity="{1 if _lit else 0.45}"/>'
                    f'<text x="{150 + (_m - 1) * 76}" y="{_y0 + 28}" text-anchor="middle" font-size="15">month={_m}</text>'
                )
    _folders = diagram(
        "".join(_parts),
        width=1030,
        height=30 + 56 * len({_y for _y, _ in _keys}),
        label=f"The sales stored in {len(_keys)} folders, one per year and month. The filter {_where} reads "
        f"{_files_read} of them.",
        tier="data",
    )
    _pruned = _files_read < len(_keys)
    mo.vstack(
        [
            mo.md("### Partitioned datasets: one folder per month"),
            in_plain(
                "Large tables are stored as many files in folders named after a column's values, for example "
                "`sales/year=2026/month=1/`. A query that filters on these columns reads only the matching folders "
                "(**partition pruning**); inside each file, Parquet's min-max statistics still apply."
            ),
            mo.hstack([p2_partition_filter, mo.md(f"```sql\n{_sql}\n```")], widths=[1, 3], gap=2, align="center"),
            _folders,
            mo.hstack(
                [
                    mo.stat(f"{_files_read} of {len(_keys)}", label="files read", bordered=True),
                    mo.stat(format_bytes(_bytes_read if _pruned else sum(_keys.values())), label="bytes in the files read",
                            caption=f"of {format_bytes(sum(_keys.values()))}", bordered=True),
                    mo.stat(f"CHF {_revenue:,.0f}", label="revenue", caption=f"{_count:,} sales", bordered=True),
                ],
                widths="equal",
            ),
            mo.md(
                f"**Observation:** the filter on the partition columns reads {_files_read} of {len(_keys)} files; DuckDB "
                "skips the other folders without opening them."
                if _pruned
                else "**Observation:** `product_id` is not a partition column, so every folder has to be opened. "
                "Partitioning pays off for the columns that most queries filter on, typically a date."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, card_box, diagram, duckdb, html, in_plain, mo, pd, random, re, tempfile):
    _src = pd.read_parquet(SALES_SEED).head(400)
    _export = _src[["sale_id", "sale_date", "product_id", "units_sold", "total_price"]].astype({"total_price": str})
    _bad_rows = random.Random(5).sample(range(len(_export)), 20)
    _export.loc[_bad_rows, "total_price"] = ["", "1 234,50", "EUR 900", "n/a"] * 5

    with tempfile.TemporaryDirectory() as _td:
        _csv = str(Path(_td) / "sales_export.csv")
        _export.to_csv(_csv, index=False)
        _con = duckdb.connect()

        # Lane 1: let DuckDB infer the types, then convert the prices to numbers wherever possible.
        _inferred = dict(_row[:2] for _row in _con.execute("DESCRIBE FROM read_csv(?)", [_csv]).fetchall())["total_price"]
        _rows, _parsed, _revenue = _con.execute(
            "SELECT count(*), count(TRY_CAST(total_price AS DOUBLE)), "
            "round(sum(TRY_CAST(total_price AS DOUBLE)), 2) FROM read_csv(?)",
            [_csv],
        ).fetchone()

        # Lane 2: declare the schema first, with its rules, then try to load into it.
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
            _refused = ("loaded", "no error")
        except duckdb.Error as _exc:
            _lines = str(_exc).splitlines()
            _told = f"{_lines[0]}. {_lines[2]}"
            _line = re.search(r"Line: (\d+)", _told)
            _value = re.search(r'string "([^"]*)"', _told)
            _refused = (
                "load rejected",
                f'line {_line[1]}: "{_value[1]}"' if _line and _value else type(_exc).__name__,
            )
        _loaded = _con.execute("SELECT count(*) FROM sales_clean").fetchone()[0]
        _con.close()

    _true = _src["total_price"].sum()
    _low = 1 - _revenue / _true
    _lanes = diagram(
        '<rect class="dg-box" x="0" y="72" width="190" height="156" rx="12"/>'
        '<text x="95" y="122" text-anchor="middle" font-weight="700">sales_export.csv</text>'
        f'<text class="dg-muted" x="95" y="152" text-anchor="middle">{_rows:,} rows</text>'
        f'<text class="dg-hot" x="95" y="180" text-anchor="middle">{len(_bad_rows)} invalid prices</text>'
        '<path class="dg-edge" d="M190 120 C 215 120, 215 76, 234 76"/>'
        '<path class="dg-edge" d="M190 180 C 215 180, 215 226, 234 226"/>'
        '<text x="240" y="24" font-weight="700">schema-on-read: <tspan class="dg-muted" font-weight="400">the types are inferred while reading</tspan></text>'
        + card_box(240, 40, "infer the types", f"price read as text ({html.escape(_inferred)})", w=250)
        + card_box(520, 40, "convert to numbers", f"{_rows - _parsed} prices become NULL", w=250)
        + card_box(800, 40, f"revenue {_revenue:,.0f}", f"{_low:.1%} too low, no warning", cls="dg-box dg-hot", w=250)
        + '<text x="240" y="174" font-weight="700">schema-on-write: <tspan class="dg-muted" font-weight="400">the types are declared before loading</tspan></text>'
        + card_box(240, 190, "declare the types", "price: a number &gt; 0, required", w=250)
        + card_box(520, 190, _refused[0], html.escape(_refused[1]), cls="dg-box dg-ok", w=250)
        + card_box(800, 190, f"{_loaded:,} rows loaded", "the error is reported", cls="dg-box dg-ok", w=250)
        + '<path class="dg-edge" d="M490 76 H 514"/><path class="dg-edge" d="M770 76 H 794"/>'
        + '<path class="dg-edge" d="M490 226 H 514"/><path class="dg-edge" d="M770 226 H 794"/>',
        width=1050,
        height=270,
        label=f"One faulty CSV, two approaches. Schema-on-read reads the prices as {_inferred}, converts {_parsed} of "
        f"{_rows} and reports a revenue {_low:.1%} too low without a warning. Schema-on-write rejects the load and "
        "names the faulty line.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Schema-on-read or schema-on-write: when are invalid prices detected?"),
            in_plain(
                "A **schema** fixes the name and type of every column; a CSV file carries none. **Schema-on-read** "
                "infers the types when the data is read. **Schema-on-write** declares them first and rejects rows "
                "that do not conform. The two differ in when an invalid value is noticed."
            ),
            mo.md(
                f"The file: {_rows:,} sales, {len(_bad_rows)} of them with invalid prices as they occur in practice "
                "(`n/a`, empty, `1 234,50`, `EUR 900`)."
            ),
            _lanes,
            mo.md(
                "**Observation:** schema-on-read returns a plausible but wrong total, without a warning: the "
                f"{_rows - _parsed} invalid prices became `NULL`, which `SUM` ignores. Schema-on-write returns no "
                "total, but an error that names the faulty line. Schema-on-read suits exploration; schema-on-write "
                "suits data on which decisions are based."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(Path, SALES_SEED, card_box, diagram, duckdb, html, in_plain, mo, pd, tempfile):
    _all = pd.read_parquet(SALES_SEED)
    with tempfile.TemporaryDirectory() as _td:
        _dir = Path(_td).as_posix()
        _files = {}
        for _year, _part in _all.groupby(_all["sale_date"].dt.year):
            _files[_year] = f"{_dir}/sales_{_year}.parquet"
            # customer_rating joined the schema in 2025, so the 2024 file never had it
            (_part.drop(columns="customer_rating") if _year < 2025 else _part).to_parquet(_files[_year], index=False)
        _sizes = _all.groupby(_all["sale_date"].dt.year).size()
        _con = duckdb.connect()

        def _read(sql):
            """What one reading of the folder gives back: (dg class, outcome)."""
            try:
                _df = _con.execute(sql, [f"{_dir}/sales_*.parquet"]).df()
            except duckdb.Error as _exc:
                return "dg-box dg-hot", f"rejected: {type(_exc).__name__}"
            if "customer_rating" not in _df:
                return "dg-box dg-hot", f"{len(_df):,} rows, customer_rating missing"
            return "dg-box dg-ok", f"{len(_df):,} rows, {_df['customer_rating'].count():,} with a rating"

        _readings = [
            (
                "read_parquet('sales_*.parquet')",
                "default: the first file defines the columns",
                _read("FROM read_parquet(?)"),
                "2024 comes first: the new column is dropped",
            ),
            (
                "read_parquet('sales_*.parquet', union_by_name = true)",
                "the columns of all files, matched by name",
                _read("FROM read_parquet(?, union_by_name = true)"),
                "the 2024 sales get NULL as their rating",
            ),
        ]
        _con.close()

    _files_row = "".join(
        card_box(
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
        f'<path class="dg-edge" d="M500 {_y + 36} H 534"/>'
        + card_box(540, _y, html.escape(_outcome), _why, cls=_cls, w=470)
        for _y, (_how, _hint, (_cls, _outcome), _why) in zip((120, 210), _readings, strict=True)
    )
    _picture = diagram(
        _files_row + _reading_rows,
        width=1010,
        height=290,
        label="Three yearly files, only the newer two with customer_rating. Read with the defaults, the column is "
        "silently dropped; read with union_by_name, every row is kept and the 2024 sales get NULL.",
        tier="data",
    )
    mo.vstack(
        [
            mo.md("### Schema drift across files: a column added in 2025"),
            in_plain(
                "EdgeWorks keeps one sales file per year. Suppose `customer_rating` was added to the schema in 2025: "
                "the 2024 file lacks the column, the 2025 and 2026 files have it. (For this demonstration, the column "
                "is removed from the 2024 sales.)"
            ),
            _picture,
            mo.md(
                "**Observation:** the default reading takes its columns from the first file and drops "
                "`customer_rating` without an error. `union_by_name = true` combines the columns of all files and "
                "fills the gaps with `NULL`. When the files in a folder can differ in their columns, this must be "
                "specified when reading."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo, shop_sales):
    # The example day: EdgeWorks' busiest day of January 2026, its last two orders recorded at the same moment.
    _per_day = shop_sales[shop_sales["sale_date"].dt.to_period("M") == "2026-01"].groupby("sale_date").size()
    _day, ch1_day_orders = _per_day.idxmax(), int(_per_day.max())
    _before = ch1_day_orders - 2
    mo.vstack(
        [
            mo.md("### The lost update: two concurrent read-modify-write cycles"),
            in_plain(
                "The dashboard shows the **number of orders recorded today**, a counter stored in one file. Each new "
                "order updates it in three steps: **read** the value, **add** one, **write** it back. If two clients "
                "both read before either writes, both write the same value, and one order is missing from the count. "
                "This anomaly is called a **lost update**."
            ),
            mo.md(
                f"""
    <div class="section-card flow-card">
      <div class="lost-update-wrap">
        <div class="lost-update-grid">
          <div class="lu-header">Step</div>
          <div class="lu-header">Client A records order {_before + 1}</div>
          <div class="lu-header">Client B records order {_before + 2}</div>
          <div class="lu-header">Orders today (the file)</div>

          <div class="lu-step">1</div>
          <div class="lu-event lu-read">reads {_before}</div>
          <div class="lu-event lu-read">reads {_before}</div>
          <div class="lu-state">{_before}</div>

          <div class="lu-step">2</div>
          <div class="lu-event lu-write">writes {_before} + 1 = {_before + 1}</div>
          <div class="lu-event">adds 1 to the {_before} it read</div>
          <div class="lu-state">{_before + 1}</div>

          <div class="lu-step">3</div>
          <div class="lu-event lu-idle">done</div>
          <div class="lu-event lu-stale">writes {_before} + 1 = {_before + 1}</div>
          <div class="lu-state lu-problem">{_before + 1} (A's order overwritten)</div>
        </div>
      </div>
      <div class="flow-note"><strong>{_day.day} {_day:%B %Y}, the busiest day of that month: {ch1_day_orders} orders
      recorded, {ch1_day_orders - 1} counted.</strong> Both orders are stored; only the counter is wrong.</div>
    </div>
                """
            ),
            mo.md(
                "**Observation:** no error is raised. Each client behaves correctly in isolation; the anomaly results "
                "from the interleaving. B's write is **stale**: it is based on a value that changed after B read it."
            ),
        ],
        gap=0.8,
    )
    return (ch1_day_orders,)


@app.cell
def _(mo):
    ch1_sim_orders = mo.ui.slider(1, 6, value=2, label="Orders per client", show_value=True, debounce=True)
    ch1_sim_timing = mo.ui.slider(1, 999, value=7, label="Interleaving (random seed)", show_value=True, debounce=True)
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
    _start = ch1_day_orders - 2  # where the example above left the count
    _rng = random.Random(ch1_sim_timing.value)
    _ops = {_rep: ["read", "write"] * ch1_sim_orders.value for _rep in "AB"}
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
                "client": f"client {_rep}",
                "action": _action,
                "count before": _before,
                "value read by the client": _read[_rep],
                "count after": _count,
                "note": "stale write" if _action == "write" and _read[_rep] != _before else "",
            }
        )

    _booked = _start + 2 * ch1_sim_orders.value
    _df = pd.DataFrame(_log)
    _df["kind"] = [_note or _action for _action, _note in zip(_df["action"], _df["note"], strict=True)]
    # A read shows the number it got, a write the number it left; short labels once the steps get narrow.
    _short = len(_df) > 12
    _df["label"] = [
        f"{_a[0].upper()}{_v}" if _short else f"{_a} {_v}"
        for _a, _v in zip(_df["action"], _df["count after"], strict=True)
    ]
    _df["orders recorded"] = _start + (_df["action"] == "write").cumsum()
    _df["orders counted"] = _df["count after"]
    _x = alt.X("step:O", title="step", axis=alt.Axis(labelAngle=0))
    _lane = alt.Chart(_df).encode(x=_x, y=alt.Y("client:N", title=None, axis=alt.Axis(minExtent=60)))
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
    _series = ["orders counted", "orders recorded"]
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
    _stale = int((_df["note"] == "stale write").sum())

    mo.vstack(
        [
            mo.md("### Two concurrent clients, step by step"),
            mo.md(
                f"Both clients start from a count of {_start} and record their orders. Each order takes two steps: "
                "**read** the count, then **write** it plus one. The random seed determines how the steps of the two "
                "clients interleave; neither client observes the other."
            ),
            mo.hstack([ch1_sim_orders, ch1_sim_timing], widths="equal", gap=2),
            mo.hstack(
                [
                    mo.stat(_booked, label="orders recorded", bordered=True),
                    mo.stat(_count, label="orders counted", bordered=True),
                    mo.stat(_booked - _count, label="lost updates", bordered=True),
                ],
                widths="equal",
            ),
            chart_or_table(
                mo.vstack([tier_chart(_lanes, "data"), tier_chart(_counter, "data")]),
                _log,
                label="Every step, in order",
            ),
            mo.md(
                f"**Observation:** {_stale} stale write{'s' if _stale != 1 else ''} (red). A write is stale when the "
                "other client wrote between its read and its write; it overwrites every order written in that interval. "
                "The count is correct only for interleavings without a stale write."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo):
    mo.vstack(
        [
            mo.md("### What a database promises: ACID"),
            in_plain(
                "A database groups changes into a **transaction**: a sequence of operations executed as one unit and "
                "then either **committed** (all changes kept) or **rolled back** (all changes undone). ACID denotes "
                "four guarantees a database provides for every transaction. A plain file provides none of them."
            ),
            mo.md(
                """
    <div class="tiles tier-data">
      <div class="tile"><div class="tile-key">A</div><div class="tile-title">Atomicity: all or nothing</div>
        <p>Moving a sale from Europe to Africa changes both region totals, or neither.</p>
        <p class="tile-bad">File: a crash between the two writes removes the sale from total revenue.</p></div>
      <div class="tile"><div class="tile-key">C</div><div class="tile-title">Consistency: constraints always hold</div>
        <p>A constraint such as "units sold is at least 1" is checked on every write.</p>
        <p class="tile-bad">File: no checks; a sale with 0 units is stored.</p></div>
      <div class="tile"><div class="tile-key">I</div><div class="tile-title">Isolation: as if executed serially</div>
        <p>Two concurrent orders are both counted, as if one had been recorded after the other.</p>
        <p class="tile-bad">File: one write overwrites the other; the count is too low.</p></div>
      <div class="tile"><div class="tile-key">D</div><div class="tile-title">Durability: committed changes persist</div>
        <p>A confirmed order survives a power failure one second later.</p>
        <p class="tile-bad">File: only after flush and fsync, which force the bytes onto the disk.</p></div>
    </div>
                """
            ),
            mo.md(
                "**Outlook:** the simulation before this slide violated **I**, with files instead of a database. The "
                "next experiment tests **A**: a crash in the middle of a change."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(Path, diagram, json, mo, shop_sales, sqlite3, tempfile):
    # The correction: the biggest German sale, booked under Germany (Europe) but meant for Kenya (Africa).
    _sale = shop_sales.loc[shop_sales.loc[shop_sales["country"] == "Germany", "total_price"].idxmax()]
    # Money in whole cents: an integer never picks up float rounding, so "the total held" is exact.
    _move = int(round(float(_sale["total_price"]) * 100))
    _initial = {_r: int(round(_v * 100)) for _r, _v in shop_sales.groupby("region")["total_price"].sum().items()}
    _expected = sum(_initial.values())
    _steps = {"file": [], "SQLite": []}  # (step, region totals in cents after it)

    with tempfile.TemporaryDirectory() as _tmp:
        # File: the region totals in one JSON file; the two saves are separate and nothing ties them together.
        _file_path = Path(_tmp) / "region_totals.json"
        _totals = dict(_initial)
        _file_path.write_text(json.dumps(_totals))
        _steps["file"].append(("start", dict(_totals)))
        _totals["Europe"] -= _move
        _file_path.write_text(json.dumps(_totals))
        _steps["file"].append(("subtract from Europe", dict(_totals)))
        # the crash: the program ends before the second write; what remains is what the file holds
        _steps["file"].append(("after the crash", json.loads(_file_path.read_text())))

        # SQLite: both writes inside one transaction.
        _db = Path(_tmp) / "region_totals.db"
        _con = sqlite3.connect(_db, isolation_level=None)
        _con.execute("CREATE TABLE region_totals (region TEXT PRIMARY KEY, cents INTEGER)")
        _con.executemany("INSERT INTO region_totals VALUES (?, ?)", _initial.items())
        _query = "SELECT region, cents FROM region_totals"
        _steps["SQLite"].append(("start", dict(_con.execute(_query).fetchall())))
        _con.execute("BEGIN")
        _con.execute("UPDATE region_totals SET cents = cents - ? WHERE region = 'Europe'", (_move,))
        _steps["SQLite"].append(("subtract from Europe", dict(_con.execute(_query).fetchall())))
        _con.close()  # the crash: the connection ends before COMMIT, so SQLite discards the transaction
        _con = sqlite3.connect(_db)  # the database, opened again after the crash
        _steps["SQLite"].append(("after the crash", dict(_con.execute(_query).fetchall())))
        _con.close()

    def _lane(y, system, label):
        """One lane: a box per step with the two region totals after it, then total revenue at the end."""
        parts = [f'<text x="0" y="{y + 54}" font-weight="700">{label}</text>']
        total = sum(_steps[system][-1][1].values())
        for _i, (_step, _t) in enumerate(_steps[system]):
            x = 150 + _i * 270
            cls = "dg-box" if _i < 2 else "dg-box dg-ok" if total == _expected else "dg-box dg-hot"
            parts.append(
                f'<rect class="{cls}" x="{x}" y="{y}" width="230" height="96" rx="12"/>'
                f'<text x="{x + 115}" y="{y + 28}" text-anchor="middle" font-weight="700">{_step}</text>'
                f'<text class="dg-muted" x="{x + 115}" y="{y + 56}" text-anchor="middle">Europe {_t["Europe"] / 100:,.0f}</text>'
                f'<text class="dg-muted" x="{x + 115}" y="{y + 80}" text-anchor="middle">Africa {_t["Africa"] / 100:,.0f}</text>'
            )
            if _i:
                parts.append(f'<path class="dg-edge" d="M{x - 36} {y + 48} H {x - 6}"/>')
        ok = total == _expected
        parts.append(
            f'<text class="{"dg-ok" if ok else "dg-hot"}" x="960" y="{y + 44}" font-size="22">'
            f"{'&#10003;' if ok else '&#10007;'} {total / 100:,.0f}</text>"
            f'<text class="{"dg-ok" if ok else "dg-hot"}" x="960" y="{y + 72}">'
            + ("unchanged" if ok else f"{(_expected - total) / 100:,.2f} missing")
            + "</text>"
        )
        return "".join(parts)

    _picture = diagram(
        '<text x="960" y="18" font-weight="700">total revenue (CHF)</text>'
        + _lane(36, "file", "file (JSON)")
        + '<rect x="404" y="176" width="262" height="120" rx="16" fill="none" stroke="currentColor"'
        ' stroke-dasharray="8 6" opacity="0.45"/>'
        + '<text class="dg-muted" x="535" y="322" text-anchor="middle">transaction: BEGIN, no COMMIT</text>'
        + _lane(188, "SQLite", "SQLite"),
        width=1150,
        height=334,
        label=f"Moving CHF {_move / 100:,.2f} from Europe to Africa, with a crash between the two writes: the file ends "
        f"with total revenue CHF {sum(_steps['file'][-1][1].values()) / 100:,.2f}, SQLite with CHF "
        f"{sum(_steps['SQLite'][-1][1].values()) / 100:,.2f}; both should be CHF {_expected / 100:,.2f}.",
    )
    _lost = _expected - sum(_steps["file"][-1][1].values())
    mo.vstack(
        [
            mo.md("### Atomicity: a crash between two writes"),
            mo.md(
                f"Sale #{_sale['sale_id']} (CHF {_sale['total_price']:,.2f}) was recorded under Germany but belongs "
                "to Kenya. The correction takes two writes to the region totals that the dashboard reads: **subtract "
                "it from Europe**, then **add it to Africa**. Without a crash, a file and a database give the same "
                "result. Here, the program crashes between the two writes."
            ),
            _picture,
            mo.md(
                f"**Observation:** the file keeps the first write: CHF {_lost / 100:,.2f} of revenue have disappeared. "
                "In SQLite, both writes belong to one transaction, which was never committed; when the database is "
                "opened again, the first write is undone and the totals are as before. **Atomicity:** a transaction "
                "takes effect completely or not at all."
            ).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: Storage</h3>
      <details>
        <summary><strong>Q1:</strong> The order-entry system creates and corrects single orders throughout the day. Row or column layout?</summary>
        <p><strong>Answer:</strong> Row layout: each operation reads or writes one complete sale. This is OLTP (online
        transaction processing). The dashboard, in contrast, aggregates many sales (OLAP) and reads columnar files.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> May prices be stored rounded to the franc to save space?</summary>
        <p><strong>Answer:</strong> No: total revenue deviates, and the exact prices are lost. Rounding is acceptable
        for measurements, to the precision of the instrument and documented in the schema; not for prices, identifiers
        or dates.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> When is loading the sales into a DuckDB table better than reading the files each time?</summary>
        <p><strong>Answer:</strong> When the same queries or joins run repeatedly: the file is parsed once at load time
        instead of on every query (materialisation: storing structured intermediate data for reuse).</p>
      </details>
      <details>
        <summary><strong>Q4:</strong> Without a database, how could the reassignment of a sale between regions be made atomic?</summary>
        <p><strong>Answer:</strong> Write the new totals to a temporary file, then rename it over the old one: a rename is
        atomic, so a reader sees either the old or the new totals, never an intermediate state. Alternatively, write a
        log entry first (a write-ahead log), and replay or undo it on restart.</p>
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
    ### Part 2 Summary

    - Row layouts suit single records (OLTP), column layouts suit aggregates (OLAP). Parquet reads only the
      requested columns and skips row groups using their min-max statistics; partitioned folders let a query
      skip whole files.
    - Compression trades CPU time for fewer bytes and pays off for slow transfers. Lossless compression keeps
      every value; rounding loses information. Columns with few distinct values compress best.
    - DuckDB runs SQL directly on Parquet and CSV files. Schema-on-write rejects invalid data when it is loaded;
      schema-on-read fails silently.
    - Concurrent read-modify-write cycles on a file lose updates; database transactions make changes atomic
      and isolated.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Next: Part 3

    So far, everything ran locally. Next, the dashboard and the partners' scripts request the sales over the
    network: a **request** is sent, a **response** is returned, and the latency is the sum of network time and
    server time.
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
            mo.md("## Part 3 · APIs: Requesting and Serving Data"),
            chapter_intro(
                "logic",
                "How do the dashboard and the partners' scripts obtain the sales data?",
                "The structure of HTTP requests and responses, retrieving data with Python, and building an API with "
                "FastAPI and Pydantic.",
                topics=(
                    "Requests and responses",
                    "URLs",
                    "Verbs and status codes",
                    "From JSON to a DataFrame",
                    "A public API",
                    "APIs as data sources",
                    "FastAPI",
                    "Validation with Pydantic",
                    "Live: the sales API",
                ),
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, html, in_plain, mo, shop_sales):
    _sale = shop_sales.iloc[0]  # sale 1, as GET /sales/1 sends it back
    _json = [
        f'{{"sale_id": {_sale["sale_id"]}, "sale_date": "{_sale["sale_date"]:%Y-%m-%d}",',
        f' "product_name": "{_sale["product"]}",',
        f' "country_name": "{_sale["country"]}",',
        f' "units_sold": {_sale["units_sold"]}, "total_price": {_sale["total_price"]}, ...}}',
    ]
    _labels = [
        # (x, y, text): the names of the parts, above the request and below the response
        (245, 62, "verb: the operation"),
        (378, 62, "path: the resource"),
        (308, 158, "endpoint = verb + path"),
        (262, 344, "status code: the outcome"),
        (596, 344, "the sale, serialized as JSON"),
    ]
    _message = diagram(
        '<rect class="dg-box" x="0" y="40" width="170" height="276" rx="12"/>'
        '<text x="85" y="172" text-anchor="middle" font-weight="700">dashboard</text>'
        '<text class="dg-muted" x="85" y="198" text-anchor="middle">the client</text>'
        '<rect class="dg-tier" x="930" y="40" width="170" height="276" rx="12"/>'
        '<text x="1015" y="172" text-anchor="middle" font-weight="700">sales API</text>'
        '<text class="dg-muted" x="1015" y="198" text-anchor="middle">sw03_demo_api</text>'
        '<path class="dg-edge" d="M170 100 H 924"/><path class="dg-edge" d="M930 248 H 176"/>'
        # an opaque strip under each message, so the arrow does not show through its see-through boxes
        '<rect x="196" y="74" width="460" height="52" style="fill: var(--surface)"/>'
        '<rect x="196" y="176" width="672" height="144" style="fill: var(--surface)"/>'
        + box(200, 78, "GET", w=90, cls="dg-tier")
        + box(310, 78, "/sales/1", w=136, cls="dg-tier")
        + '<text class="dg-muted" x="466" y="105">no body: a GET only reads</text>'
        + '<path d="M202 128 V 136 H 444 V 128" fill="none" stroke="currentColor" opacity="0.45"/>'
        + box(200, 226, "200 OK", w=124, cls="dg-box dg-ok")
        + '<rect class="dg-box" x="336" y="180" width="520" height="136" rx="12"/>'
        + "".join(
            f'<text x="352" y="{208 + 28 * _i}" style="font-family: var(--monospace-font, monospace); font-size: 15px; white-space: pre">'
            f"{html.escape(_line)}</text>"
            for _i, _line in enumerate(_json)
        )
        + "".join(f'<text class="dg-muted" x="{_x}" y="{_y}" text-anchor="middle">{_t}</text>' for _x, _y, _t in _labels),
        width=1100,
        height=356,
        label="The dashboard sends the request GET /sales/1 to the sales API: the verb GET and the path /sales/1, "
        f"no body. The API returns 200 OK and sale 1 as JSON: {_sale['product']}, {_sale['country']}, "
        f"{_sale['units_sold']} units, CHF {_sale['total_price']:,.2f}.",
        tier="logic",
    )
    mo.vstack(
        [
            mo.md("### The dashboard requests sale 1 from the sales API"),
            in_plain(
                "An **API** (application programming interface) is the interface through which a program offers its "
                "functionality to other programs. The dashboard never opens the sales files: it sends a **request** "
                "to the sales API over **HTTP**, the application protocol of the web, and receives a **response**."
            ),
            _message,
            mo.md(
                "**Observation:** the dashboard knows only the address `/sales/1`. Where and in which format the sale "
                "is stored is encapsulated by the API: the files could be replaced by a database without any change to "
                "the dashboard."
            ).callout(kind="info"),
            mo.md(
                "**Terms:** a *resource* is an entity the server manages (a sale); its *path* is its address "
                "(`/sales/1`); an *endpoint* combines a verb with a path (`GET /sales/1`); a *payload* is the data sent "
                "with a request. HTTPS is HTTP with encryption."
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(box, diagram, html, in_plain, json, label_w, mo, shop_sales):
    _parts = [
        ("http://", "protocol"),
        ("127.0.0.1", "host: this computer"),
        (":8000", "port"),
        ("/sales", "path: the resource"),
        ("?region=Europe&min_rating=4", "query parameters: filters"),
    ]
    _svg, _x = [], 0.0
    for _i, (_text, _label) in enumerate(_parts):
        _w = label_w(_text)
        _svg.append(box(_x, 0, html.escape(_text), w=_w, cls="dg-tier" if _i >= 3 else "dg-box"))
        _svg.append(f'<text class="dg-muted" x="{_x + _w / 2:.0f}" y="{72 + 24 * (_i % 2)}" text-anchor="middle">{_label}</text>')
        _x += _w + 6
    _url = diagram(
        "".join(_svg),
        width=int(_x),
        height=106,
        label="The URL http://127.0.0.1:8000/sales?region=Europe&min_rating=4 split into protocol, host, port, path "
        "and query parameters.",
        tier="logic",
    )
    # The first sale the API would return for this request: Europe, rating 4 or more, newest first.
    _hit = (
        shop_sales[(shop_sales["region"] == "Europe") & (shop_sales["customer_rating"] >= 4)]
        .sort_values(["sale_date", "sale_id"], ascending=False)
        .iloc[0]
    )
    _record = {
        "sale_id": int(_hit["sale_id"]),
        "sale_date": f"{_hit['sale_date']:%Y-%m-%d}",
        "product_name": _hit["product"],
        "region_name": _hit["region"],
        "total_price": float(_hit["total_price"]),
    }
    _request = "GET /sales?region=Europe&min_rating=4 HTTP/1.1\nHost: 127.0.0.1:8000\nAccept: application/json"
    _fields = ",\n   ".join(f"{json.dumps(_k)}: {json.dumps(_v)}" for _k, _v in _record.items())
    _response = f"HTTP/1.1 200 OK\ncontent-type: application/json\n\n[\n  {{{_fields},\n   ...}},\n  ...\n]"
    mo.vstack(
        [
            mo.md("### Anatomy of a URL, a request and a response"),
            in_plain(
                "A **URL** addresses a resource on a server: protocol, host, port, path and optional query parameters. "
                "A **request** combines a verb with a URL, headers and, for POST and PUT, a body. The **response** "
                "returns a status code, headers and a body, usually JSON."
            ),
            _url,
            mo.hstack(
                [
                    mo.vstack([mo.md("**The request**, as sent over the network"), mo.md(f"```http\n{_request}\n```")]),
                    mo.vstack([mo.md("**The response**"), mo.md(f"```http\n{_response}\n```")]),
                ],
                widths="equal",
                gap=2,
            ),
            mo.md(
                "**Observation:** the filters travel as query parameters in the URL, and the server applies them before "
                "it answers. A header such as `Accept: application/json` states which format the client expects."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo):
    mo.vstack(
        [
            mo.md("### Four verbs: the operations available to clients"),
            in_plain(
                "The **verb** (formally, the HTTP request *method*) specifies the operation on the resource the path "
                "identifies. HTTP defines four common ones, and the API supports all four on `/sales`. A verb is "
                "**idempotent** if sending the same request twice leaves the data in the same state as sending it "
                "once. **REST** is the convention behind this design: resources addressed by paths, changed with "
                "these standard verbs."
            ),
            mo.md(
                """
    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">GET</div><div class="tile-title">fetch: <code>GET /sales/1</code></div>
        <p>The dashboard shows sale 1.</p>
        <p>Sent twice: the same sale, no change.</p></div>
      <div class="tile"><div class="tile-key">POST</div><div class="tile-title">create: <code>POST /sales</code></div>
        <p>A client creates a new order; the API assigns the next id, 3,361.</p>
        <p class="tile-bad">Sent twice: two orders created.</p></div>
      <div class="tile"><div class="tile-key">PUT</div><div class="tile-title">change: <code>PUT /sales/1</code></div>
        <p>A correction: the customer's rating was 5, not 3. This API accepts only the changed fields
        (the HTTP standard calls that PATCH).</p>
        <p>Sent twice: still 5.</p></div>
      <div class="tile"><div class="tile-key">DELETE</div><div class="tile-title">remove: <code>DELETE /sales/1</code></div>
        <p>The order was cancelled.</p>
        <p>Sent twice: deleted either way.</p></div>
    </div>
                """
            ),
            mo.md(
                "**Observation:** only POST is not safe to resend. A client whose POST timed out cannot tell whether "
                "the order was created; resending it may create the order twice. Deleting a sale twice returns 204, "
                "then 404, and is still idempotent: the end state is the same."
            ).callout(kind="info"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(in_plain, mo, static_table):
    _codes = [
        ("200 OK", "success; the resource is in the response", "GET /sales/1"),
        ("201 Created", "created; the new sale is in the response", "POST /sales with a valid sale"),
        ("204 No Content", "success; no response body", "DELETE /sales/1"),
        ("400 Bad Request", "well-formed, but violates a business rule", "a sale of product 99, which does not exist"),
        ("404 Not Found", "no resource at this path", "GET /sales/999999"),
        ("422 Unprocessable Content", "the payload violates a declared rule", "a sale with rating 9"),
        ("500 Internal Server Error", "failure on the server side, not caused by the client", "a bug in the API"),
    ]
    mo.vstack(
        [
            mo.md("### Status codes: the outcome of a request"),
            in_plain(
                "Every response begins with a three-digit **status code**, which the client evaluates first. The first "
                "digit indicates which side has to act."
            ),
            mo.md(
                """
    <div class="tiles tier-logic">
      <div class="tile"><div class="tile-key">2xx</div><div class="tile-title">Success</div>
        <p>The request succeeded; no action is required.</p></div>
      <div class="tile"><div class="tile-key">4xx</div><div class="tile-title">Client error</div>
        <p>The client must change the request: resending it unchanged yields the same response.</p></div>
      <div class="tile"><div class="tile-key">5xx</div><div class="tile-title">Server error</div>
        <p>A retry may succeed, but automatic retries are safe only for idempotent verbs.</p></div>
    </div>
                """
            ),
            static_table(
                [{"status code": _c, "meaning": _t, "sent by the sales API for": _w} for _c, _t, _w in _codes],
                label="Status codes used by the sales API",
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    # One box for chapters 6 and 8: chapter 8 shows this same element again, and both copies stay in sync.
    api_base_url = mo.ui.text(value="http://127.0.0.1:8000", label="API base URL", full_width=True)
    _sale = {"sale_date": "2026-09-01", "product_id": 1, "country_id": 3, "units_sold": 2, "customer_rating": 4}
    ch6_preset = mo.ui.dropdown(
        options={
            "Show sale 1": ("GET", "/sales/1", None),
            "Create a valid sale": ("POST", "/sales", _sale),
            "Show a sale that does not exist": ("GET", "/sales/999999", None),
            "Create a sale of product 99, which does not exist": ("POST", "/sales", _sale | {"product_id": 99}),
            "Create a sale with rating 9": ("POST", "/sales", _sale | {"customer_rating": 9}),
            "Create a sale that includes its own total_price": ("POST", "/sales", _sale | {"total_price": 1.0}),
            "Create a country whose name is three spaces": ("POST", "/countries", {"name": "   ", "region_id": 1}),
            "Update sale 1: set the rating to 5": ("PUT", "/sales/1", {"customer_rating": 5}),
            "Delete sale 1 (a cancelled order)": ("DELETE", "/sales/1", None),
        },
        value="Show sale 1",
        label="Request",
    )
    return api_base_url, ch6_preset


@app.cell
def _(ch6_preset, json, mo):
    _method, _path, _body = ch6_preset.value
    ch6_method = mo.ui.dropdown(["GET", "POST", "PUT", "DELETE"], value=_method, label="Verb")
    ch6_path = mo.ui.text(value=_path, label="Path")
    ch6_body = mo.ui.text_area(
        value=json.dumps(_body) if _body else "", rows=3, label="JSON body (sent with POST and PUT)", full_width=True
    )
    ch6_send = mo.ui.run_button(label="Send request", kind="success")
    return ch6_body, ch6_method, ch6_path, ch6_send


@app.cell
def _(
    api_base_url,
    call_api,
    ch6_body,
    ch6_method,
    ch6_path,
    ch6_preset,
    ch6_send,
    html,
    json,
    mo,
    requests,
):
    from http.client import responses as _phrases

    _controls = mo.vstack(
        [
            ch6_preset,
            api_base_url,
            mo.hstack([ch6_method, ch6_path], justify="start", gap=2),
            ch6_body,
            ch6_send,
        ],
        gap=0.6,
    )

    def _show(result):
        """The whole lab slide: heading, the controls on the left, `result` on the right."""
        return mo.vstack(
            [
                mo.md("### Requests to the sales API"),
                mo.md(
                    "Each preset defines a request, which can be edited before it is sent. Sending POST, PUT and DELETE "
                    "twice each shows which of them leave the data in the state of the first request. Prerequisite: "
                    "the API runs in a terminal (`uvicorn sw03_demo_api:app`, without `--reload`); every restart "
                    "resets `data/` from `data/seed/`."
                ),
                mo.hstack([_controls, result], widths=[2, 3], gap=2, align="start"),
            ],
            gap=0.6,
        )

    mo.stop(
        not ch6_send.value,
        _show(mo.md("**Question:** which status code will the API return?").callout(kind="neutral")),
    )

    _url = api_base_url.value.rstrip("/") + "/" + ch6_path.value.lstrip("/")
    try:
        _body = json.loads(ch6_body.value) if ch6_method.value in {"POST", "PUT"} else None
    except json.JSONDecodeError as _exc:
        mo.stop(True, _show(mo.md(f"The body is not valid JSON: {_exc}").callout(kind="danger")))
    try:
        _status, _answer = call_api(ch6_method.value, _url, _body)
    except requests.RequestException:
        mo.stop(
            True,
            _show(mo.md(f"No response from `{_url}`. The API must be running: `uvicorn sw03_demo_api:app`").callout(kind="danger")),
        )

    # JSON as a code block, not mo.json: its tree view squeezes a name of three spaces to one
    if isinstance(_answer, list):  # GET /sales is thousands of rows: show a taste, not a wall
        _shown = mo.md(f"*{len(_answer):,} items, the first 3 shown*\n\n```json\n{json.dumps(_answer[:3], indent=2)}\n```")
    elif isinstance(_answer, dict):
        _shown = mo.md(f"```json\n{json.dumps(_answer, indent=2)}\n```")
    elif _answer:
        _shown = mo.plain_text(str(_answer))  # not JSON, e.g. a 500 "Internal Server Error"
    else:
        _shown = mo.md("*No body: 204 means success without a response body.*")
    _kind, _colour, _meaning = {
        2: ("success", "var(--teal)", "success"),
        4: ("warn", "var(--amber)", "client error: resending it unchanged yields the same response"),
    }.get(_status // 100, ("danger", "var(--red)", "server error: a retry may succeed"))
    _badge = mo.Html(
        '<div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px">'
        f'<span style="color: {_colour}; font-size: 3rem; font-weight: 700; line-height: 1">{_status}</span>'
        f'<span style="font-size: 1.4rem; font-weight: 700">{_phrases.get(_status, "(no standard name)")}</span>'
        f'<span style="color: var(--ink-soft); font-size: 1.1rem">{_meaning}</span></div>'
        f"<p><code>{html.escape(ch6_method.value)} {html.escape(_url)}</code></p>"
    )
    _show(mo.vstack([_badge, _shown], gap=0.5).callout(kind=_kind))
    return


@app.cell
def _(mo):
    p3_consume_run = mo.ui.run_button(label="Send the request", kind="success")
    return (p3_consume_run,)


@app.cell
def _(alt, api_base_url, in_plain, mo, p3_consume_run, pd, requests, static_table, tier_chart):
    # Run from this text, so the slide shows exactly the code that runs.
    _code = (
        'response = requests.get(f"{base_url}/sales", params={"start_date": "2026-01-01"}, timeout=5)\n'
        "response.raise_for_status()                # stops on 4xx and 5xx\n"
        "sales = pd.DataFrame(response.json())      # a list of JSON objects becomes a table\n"
        'revenue = sales.groupby("region_name")["total_price"].sum()'
    )
    _top = mo.vstack(
        [
            mo.md("### Retrieving data from an API with Python"),
            in_plain(
                "In data collection, an API is often the source of the data. The `requests` library sends the request; "
                "the JSON response converts directly into a pandas DataFrame."
            ),
            mo.md(f"```python\n{_code}\n```"),
            p3_consume_run,
        ],
        gap=0.6,
    )
    mo.stop(
        not p3_consume_run.value,
        mo.vstack(
            [_top, mo.md("**Question:** how many rows and columns will the DataFrame have?").callout(kind="neutral")],
            gap=0.6,
        ),
    )
    _names = {"requests": requests, "pd": pd, "base_url": api_base_url.value.rstrip("/")}
    try:
        exec(_code, _names)
    except requests.RequestException as _exc:
        mo.stop(
            True,
            mo.vstack(
                [
                    _top,
                    mo.md(
                        f"No usable response from the API (`{type(_exc).__name__}`). The API must be running: "
                        "`uvicorn sw03_demo_api:app`"
                    ).callout(kind="danger"),
                ],
                gap=0.6,
            ),
        )
    _response, _sales = _names["response"], _names["sales"]
    _revenue = _names["revenue"].reset_index().rename(columns={"region_name": "region", "total_price": "revenue (CHF)"})
    _chart = (
        alt.Chart(_revenue)
        .mark_bar(cornerRadiusEnd=4)
        .encode(x=alt.X("revenue (CHF):Q", title=None), y=alt.Y("region:N", sort="-x", title=None))
        .properties(width="container", height=170, title="revenue: total_price per region since 1 January 2026")
    )
    mo.vstack(
        [
            _top,
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md(f"`{_response.status_code} {_response.reason}` · `GET {_response.url}`").callout(kind="success"),
                            static_table(
                                _sales[["sale_id", "sale_date", "product_name", "region_name", "total_price"]].head(4),
                                label=f"sales: {len(_sales):,} rows × {_sales.shape[1]} columns (first 4 rows, 5 columns)",
                            ),
                        ],
                        gap=0.4,
                    ),
                    tier_chart(_chart, "logic"),
                ],
                widths="equal",
                gap=2,
            ),
            mo.md(
                f"**Observation:** the response contains {len(_sales):,} sales as JSON objects with {_sales.shape[1]} fields "
                "each, and `pd.DataFrame` turns them into a table in one step. The server evaluated the query parameter "
                "`start_date`, so only the requested rows were transferred."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p3_weather_run = mo.ui.run_button(label="Request the forecast", kind="success")
    return (p3_weather_run,)


@app.cell
def _(alt, in_plain, json, mo, p3_weather_run, pd, requests, tier_chart):
    # Run from this text, so the slide shows exactly the code that runs.
    _code = (
        'params = {"latitude": 47.05, "longitude": 8.31, "hourly": "temperature_2m",\n'
        '          "timezone": "Europe/Zurich", "forecast_days": 2}\n'
        'response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=5)\n'
        "response.raise_for_status()\n"
        'weather = pd.DataFrame(response.json()["hourly"])    # one row per hour'
    )
    # A response recorded on 2 October 2026, shown when the lecture room has no network.
    _recorded = {
        "latitude": 47.04,
        "longitude": 8.32,
        "timezone": "Europe/Zurich",
        "hourly_units": {"time": "iso8601", "temperature_2m": "°C"},
        "hourly": {
            "time": [f"2026-10-{2 + _h // 24:02d}T{_h % 24:02d}:00" for _h in range(48)],
            "temperature_2m": [
                16.6, 15.8, 15.2, 15.2, 15.3, 14.9, 14.9, 14.9, 14.7, 14.8, 15.3, 15.9, 17.0, 17.8, 18.5, 19.5,
                19.7, 19.1, 18.8, 17.9, 16.7, 16.8, 16.9, 15.8, 15.0, 14.8, 14.1, 13.4, 13.7, 13.1, 13.1, 12.8,
                12.6, 13.9, 15.1, 16.7, 18.6, 20.0, 21.1, 21.8, 22.1, 22.0, 21.6, 20.6, 19.4, 18.4, 17.7, 16.9,
            ],
        },
    }
    _top = mo.vstack(
        [
            mo.md("### A public API: the weather forecast for Lucerne"),
            in_plain(
                "**Open-Meteo** returns weather forecasts as JSON, without an API key; location, variables and time "
                "zone are query parameters."
            ),
            mo.md(f"```python\n{_code}\n```"),
            p3_weather_run,
        ],
        gap=0.6,
    )
    mo.stop(
        not p3_weather_run.value,
        mo.vstack([_top, mo.md("**Question:** what structure will the JSON response have?").callout(kind="neutral")], gap=0.6),
    )
    _names = {"requests": requests, "pd": pd}
    try:
        exec(_code, _names)
        _data = _names["response"].json()
        _status, _kind = f"`{_names['response'].status_code} {_names['response'].reason}` · live response", "success"
    except (requests.RequestException, KeyError, ValueError) as _exc:
        _data = _recorded
        _names["weather"] = pd.DataFrame(_data["hourly"])
        _status = f"No usable response (`{type(_exc).__name__}`): showing a response recorded on 2 October 2026."
        _kind = "warn"
    _weather = _names["weather"].assign(time=lambda d: pd.to_datetime(d["time"]))
    # The response, abridged to lines that fit beside the chart: the top-level keys, the first value of each list.
    _meta = [f"{json.dumps(_k)}: {json.dumps(_data[_k], ensure_ascii=False)}" for _k in ("latitude", "longitude", "timezone") if _k in _data]
    _hourly = [f"{json.dumps(_k)}: [{json.dumps(_v[0])}, …]" for _k, _v in _data["hourly"].items()]
    _preview = "{" + ",\n ".join(_meta) + ',\n "hourly": {' + ",\n            ".join(_hourly) + "}}"
    _chart = (
        alt.Chart(_weather)
        .mark_line(strokeWidth=3)
        .encode(x=alt.X("time:T", title=None), y=alt.Y("temperature_2m:Q", title="°C", scale=alt.Scale(zero=False)))
        .properties(width="container", height=180, title="Temperature in Lucerne, next 48 hours")
    )
    mo.vstack(
        [
            _top,
            mo.hstack(
                [
                    mo.md(f"{_status}\n\n```json\n{_preview}\n```").callout(kind=_kind),
                    tier_chart(_chart, "logic"),
                ],
                widths=[2, 3],
                gap=2,
            ),
            mo.md(
                f"**Observation:** metadata at the top level, the {len(_weather)} hourly values as parallel lists under "
                "`hourly`; `pd.DataFrame(...[\"hourly\"])` turns these lists into columns. With `timezone`, the times "
                "are local ISO 8601 times (Part 1)."
            ),
            mo.md(
                '<p class="vis-caption">Weather data by <a href="https://open-meteo.com">Open-Meteo.com</a>, '
                'licensed under CC BY 4.0: the attribution is part of the terms of use.</p>'
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo):
    mo.vstack(
        [
            mo.md("### APIs as data sources in practice"),
            in_plain(
                "Public and commercial APIs add rules around every request. A client that collects data has to handle "
                "them explicitly."
            ),
            mo.md(
                """
    <div class="tiles tier-logic" style="grid-template-columns: repeat(3, 1fr)">
      <div class="tile"><div class="tile-key">KEY</div><div class="tile-title">Authentication</div>
        <p>Most APIs require a key or a token, sent in a header. Keys belong in environment variables, not in notebooks.</p></div>
      <div class="tile"><div class="tile-key">429</div><div class="tile-title">Rate limits</div>
        <p>Servers limit the requests per minute; above the limit they answer 429 Too Many Requests.</p></div>
      <div class="tile"><div class="tile-key">1/n</div><div class="tile-title">Pagination</div>
        <p>Large results arrive in pages (<code>?page=2</code>, <code>?offset=100</code>); the client requests pages until none are left.</p></div>
      <div class="tile"><div class="tile-key">&#8635;</div><div class="tile-title">Timeouts and retries</div>
        <p>Always set a timeout. Retry after 429 and 5xx with increasing pauses; never retry a POST blindly.</p></div>
      <div class="tile"><div class="tile-key">{ }</div><div class="tile-title">Nested JSON</div>
        <p>Responses are often nested; <code>pd.json_normalize</code> flattens nested objects into columns.</p></div>
      <div class="tile"><div class="tile-key">&sect;</div><div class="tile-title">Terms of use</div>
        <p>Licences and usage limits apply to collected data, as to any other data source.</p></div>
    </div>
                """
            ),
            mo.md(
                '<p class="vis-caption">Public examples: <a href="https://opendata.swiss">opendata.swiss</a> · '
                '<a href="https://open-meteo.com">Open-Meteo</a> (weather) · '
                '<a href="https://www.wikidata.org/wiki/Wikidata:Data_access">Wikidata</a> · '
                '<a href="https://docs.github.com/en/rest">GitHub REST API</a></p>'
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(SEED_DIR, duckdb):
    import inspect as _inspect

    from fastapi import FastAPI, HTTPException

    # The minimal API of Part 3, run from this text: the slide shows this code, only the data folder is made absolute.
    p3_api_code = _inspect.cleandoc(
        '''
        duckdb.execute("SET file_search_path = 'data/seed'")  # where the Parquet files are
        SQL = """
            SELECT r.name AS region, round(sum(s.total_price), 2) AS revenue
            FROM 'sales.parquet' s
            JOIN 'countries.parquet' c USING (country_id)
            JOIN 'sales_regions.parquet' r USING (region_id)
            GROUP BY region ORDER BY revenue DESC
        """

        app = FastAPI(title="Revenue API")


        @app.get("/revenue")
        def revenue_per_region() -> list[dict]:
            """Total revenue per region."""
            return [{"region": r, "revenue": v} for r, v in duckdb.sql(SQL).fetchall()]


        @app.get("/revenue/{region}")
        def revenue_of_region(region: str) -> dict:
            """Total revenue of one region, or 404."""
            for row in revenue_per_region():
                if row["region"] == region:
                    return row
            raise HTTPException(status_code=404, detail=f"no region named {region}")
        '''
    )
    _names = {"FastAPI": FastAPI, "HTTPException": HTTPException, "duckdb": duckdb}
    exec(p3_api_code.replace("'data/seed'", f"'{SEED_DIR.as_posix()}'"), _names)
    p3_api = _names["app"]
    return p3_api, p3_api_code


@app.cell
def _(in_plain, json, mo, p3_api, p3_api_code):
    from fastapi.testclient import TestClient as _TestClient

    _client = _TestClient(p3_api)  # real HTTP requests to the app, inside this process, without a server
    _calls = []
    for _path in ("/revenue", "/revenue/Europe", "/revenue/Mars"):
        _answer = _client.get(_path)
        _body = _answer.json()
        _text = "[\n" + ",\n".join(f" {json.dumps(_item)}" for _item in _body) + "\n]" if isinstance(_body, list) else json.dumps(_body)
        _calls.append(
            mo.md(f"`GET {_path}` → **{_answer.status_code}**\n\n```json\n{_text}\n```").callout(
                kind="success" if _answer.status_code == 200 else "warn"
            )
        )
    _paths = " and ".join(f"`{_p}`" for _p in p3_api.openapi()["paths"])
    mo.vstack(
        [
            mo.md("### Building an API with FastAPI"),
            in_plain(
                "**FastAPI** turns Python functions into API endpoints. The decorator `@app.get(\"/revenue\")` assigns a "
                "function to a verb and a path; FastAPI converts the return value to JSON and generates the "
                "documentation from the code."
            ),
            mo.hstack(
                [mo.md(f"```python\n{p3_api_code}\n```"), mo.vstack(_calls, gap=0.4)],
                widths=[3, 2],
                gap=2,
                align="start",
            ),
            mo.md(
                f"**Observation:** two endpoints in about 20 lines. FastAPI returned JSON, answered an unknown region with "
                f"404, and generated the OpenAPI description of {_paths}, the basis of `/docs`, without additional code. "
                "Exercise 7 builds a similar app."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(pydantic):
    from datetime import date as _date
    from inspect import cleandoc as _cleandoc

    # Two models for a new sale, run from this text: the lab slide shows exactly the code that runs.
    ch7_code = _cleandoc(
        """
        class SaleIn(BaseModel):                       # types, and two rules
            product_id: int
            country_id: int
            units_sold: int = Field(ge=1)              # at least 1
            customer_rating: int = Field(ge=1, le=5)   # 1 to 5
            sale_date: date

        class StrictSaleIn(SaleIn):                    # plus the missing rules
            model_config = ConfigDict(strict=True)     # "42" is not 42
            product_id: int = Field(ge=1)
            units_sold: int = Field(ge=1, le=100_000)
            sale_date: date = Field(ge=date(2000, 1, 1))
        """
    )
    _names = {"BaseModel": pydantic.BaseModel, "ConfigDict": pydantic.ConfigDict, "Field": pydantic.Field, "date": _date}
    exec(ch7_code, _names)
    ch7_models = {"SaleIn": _names["SaleIn"], "StrictSaleIn": _names["StrictSaleIn"]}
    return ch7_code, ch7_models


@app.cell
def _(ch7_models, diagram, html, in_plain, json, mo, pydantic):
    _sent = {"product_id": 1, "country_id": 3, "units_sold": 0, "customer_rating": 9, "sale_date": "2026-01-15"}
    try:
        ch7_models["SaleIn"].model_validate_json(json.dumps(_sent))
        _errors = []
    except pydantic.ValidationError as _exc:
        _errors = [f"{_e['loc'][0]}: {_e['msg']}" for _e in _exc.errors()]

    def _card(x, y, title, sub, cls, w=280, h=130):
        return (
            f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
            f'<text x="{x + w / 2}" y="{y + h / 2 - 6}" text-anchor="middle" font-weight="700">{title}</text>'
            f'<text class="dg-muted" x="{x + w / 2}" y="{y + h / 2 + 20}" text-anchor="middle">{sub}</text>'
        )

    _door = diagram(
        '<path d="M680 0 V 200" fill="none" stroke="currentColor" stroke-dasharray="6 6" opacity="0.45"/>'
        '<text class="dg-muted" x="668" y="20" text-anchor="end">untrusted</text>'
        '<text class="dg-muted" x="692" y="20">trusted</text>'
        + _card(0, 50, "the submitted sale", f"{_sent['units_sold']} units · rating {_sent['customer_rating']}", "dg-box dg-hot", w=250)
        + _card(330, 50, "SaleIn, a Pydantic model", "validation: types and rules", "dg-tier")
        + _card(720, 50, "a validated sale", "the endpoint code relies on it", "dg-box dg-ok")
        + f'<rect class="dg-box dg-hot" x="190" y="232" width="560" height="{50 + 26 * len(_errors)}" rx="12"/>'
        + f'<text x="470" y="264" text-anchor="middle" font-weight="700">422: rejected, {len(_errors)} errors in one response</text>'
        + "".join(
            f'<text class="dg-muted" x="470" y="{294 + 26 * _i}" text-anchor="middle">{html.escape(_line)}</text>'
            for _i, _line in enumerate(_errors)
        )
        + '<path class="dg-edge" d="M250 115 H 324"/><path class="dg-edge dg-ok" d="M610 115 H 714"/>'
        + '<path class="dg-edge dg-hot" d="M470 180 V 226"/>',
        width=1000,
        height=300 + 26 * len(_errors),
        label=f"The submitted sale, {_sent['units_sold']} units and rating {_sent['customer_rating']}, is validated by the "
        f"SaleIn model. A sale that passes becomes a validated Python object on the trusted side; this one is rejected "
        f"with a 422 that lists every violated rule: {'; '.join(_errors)}.",
        tier="logic",
    )
    mo.vstack(
        [
            mo.md("### Pydantic: validating every sale at the API boundary"),
            in_plain(
                "**Pydantic** is a Python library that validates data against a **model**: a class that declares each "
                "field of a sale, its type and its constraints. Valid input becomes a typed Python object the "
                "application can rely on; invalid input is rejected with a list of all violations."
            ),
            _door,
            mo.md(
                "**Observation:** both violations are reported in one response, and the endpoint code never ran: this "
                "list is what the API returns with status 422. A **type hint** (`units_sold: int`) is only an "
                "annotation in plain Python; Pydantic enforces it."
            ).callout(kind="info"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    _sale = {"product_id": 1, "country_id": 3, "units_sold": 2, "customer_rating": 4, "sale_date": "2026-01-15"}
    ch7_preset = mo.ui.dropdown(
        options={
            "A valid sale → should pass": _sale,
            "A sale without a date → should fail": {_k: _v for _k, _v in _sale.items() if _k != "sale_date"},
            "0 units, rating 9 → should fail": _sale | {"units_sold": 0, "customer_rating": 9},
            'Wrong types: units "many", date "yesterday" → should fail': _sale | {"units_sold": "many", "sale_date": "yesterday"},
            # Every field is the declared type and inside its declared range. Every field is also implausible.
            "Implausible values with valid types → ?": {
                "product_id": -7,
                "country_id": 999,
                "units_sold": 5_000_000,
                "customer_rating": 1,
                "sale_date": "1900-01-01",
            },
            # Two numbers arrive as text, and nothing is rejected either.
            'Numbers sent as strings: "42" units → ?': _sale | {"units_sold": "42", "customer_rating": "4"},
        },
        value="A valid sale → should pass",
        label="Submitted sale",
    )
    return (ch7_preset,)


@app.cell
def _(ch7_preset, json, mo):
    ch7_json = mo.ui.text_area(value=json.dumps(ch7_preset.value, indent=2), rows=7, label="as JSON (editable)", full_width=True)
    return (ch7_json,)


@app.cell
def _(ch7_code, ch7_json, ch7_models, ch7_preset, html, json, mo, pydantic):
    try:
        _sent = json.loads(ch7_json.value)
    except json.JSONDecodeError:
        _sent = None  # Pydantic reports it too, as one error on the whole input

    def _code(value):
        # as JSON writes it; no-break spaces, so a run of spaces does not collapse to one
        return f"<code>{html.escape(json.dumps(value)).replace(' ', '&nbsp;')}</code>"

    def _row(colour, field, sent, verdict):
        return (
            f'<div style="margin-top: 8px; padding: 8px 12px; border-left: 4px solid {colour}; border-radius: 8px;'
            f' background: color-mix(in srgb, {colour} 12%, transparent)"><strong>{field}</strong> {sent} {verdict}</div>'
        )

    def _column(title, model):
        """One model's verdict: a tile with one row per field, ok in teal and broken in red; and the raw output."""
        try:
            sale = model.model_validate_json(ch7_json.value)  # parse + validate in one step
            errors, raw, kept = {}, sale.model_dump_json(), sale.model_dump(mode="json")
        except pydantic.ValidationError as exc:
            # one line per error, and without "ctx" (its msg already says it), so both answers fit on the slide
            issues = [{_k: _v for _k, _v in _i.items() if _k != "ctx"} for _i in json.loads(exc.json(include_url=False))]
            sale, kept, errors, raw = None, {}, {}, "[\n" + ",\n".join(f"  {json.dumps(_i)}" for _i in issues) + "\n]"
            for _e in exc.errors():
                errors.setdefault(".".join(map(str, _e["loc"])) or "JSON", []).append(_e["msg"])
        fields = [*model.model_fields, *(_f for _f in errors if _f not in model.model_fields)] if isinstance(_sent, dict) else list(errors)
        rows = []
        for field in fields:
            sent = _code(_sent[field]) if isinstance(_sent, dict) and field in _sent else "<em>(missing)</em>"
            if field in errors:
                rows.append(_row("var(--red)", field, sent, "&#10007; " + html.escape("; ".join(errors[field]))))
            elif sale is None:
                rows.append(_row("var(--teal)", field, sent, "&#10003;"))
            else:
                changed = isinstance(_sent, dict) and kept[field] != _sent.get(field)
                rows.append(_row("var(--teal)", field, sent, "&#10003;" + (f" became {_code(kept[field])}" if changed else "")))
        ok = sale is not None
        verdict = "accepted" if ok else f"rejected, {sum(map(len, errors.values()))} error(s)"
        tile = (
            f'<div class="tile" style="--tier: var({"--teal" if ok else "--red"})">'
            f'<div class="tile-key">{"&#10003;" if ok else "&#10007;"}</div>'
            f'<div class="tile-title">{title}: {verdict}</div>{"".join(rows)}</div>'
        )
        return tile, mo.md(f"**{title}**\n\n```json\n{raw}\n```")

    _verdicts = [_column(_name, _model) for _name, _model in ch7_models.items()]
    mo.vstack(
        [
            mo.md("### Which sales pass validation?"),
            mo.md(
                "Two models validate the same sale: `SaleIn` declares the types and two ranges; `StrictSaleIn` adds "
                "the missing rules and rejects strings where a number is expected. **The last two presets are the "
                "instructive cases:** validation checks structure, not truth, and `SaleIn` converts `\"42\"` to 42 "
                "unless strict mode forbids it."
            ),
            mo.hstack(
                [mo.md(f"```python\n{ch7_code}\n```"), mo.vstack([ch7_preset, ch7_json], gap=0.4)],
                widths=[1, 1],
                gap=2,
                align="start",
            ),
            mo.ui.tabs(
                {
                    "Per field": mo.Html(f'<div class="grid-2" style="font-size: 16px">{"".join(_t for _t, _r in _verdicts)}</div>'),
                    # stacked: side by side, a long error line would push a twin off screen
                    "Raw output": mo.vstack([_r for _t, _r in _verdicts]),
                }
            ),
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
            ch8_stop(top, f"Could not reach `{base}`. The API must be running: `uvicorn sw03_demo_api:app`.")
        if answer and isinstance(answer, str):  # HTML or plain text, e.g. the Streamlit dashboard's port
            ch8_stop(top, f"`{base}{path}` returned `{status}`, but not JSON. The base URL may not point to the sales API.")
        return status, answer

    return ch8_api, ch8_phrases, ch8_stop


@app.cell
def _(SEED_DIR, mo, pd):
    # Every chapter 8 control. Shown by the slides below, so this cell has no output (no slide of its own).
    fastapi_check = mo.ui.run_button(label="Check API status", kind="success")
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
    return (
        ch8_answers,
        ch8_set_answers,
        fastapi_check,
        fastapi_get,
        fastapi_item_id,
        fastapi_payload,
        fastapi_post,
    )


@app.cell
def _(api_base_url, box, ch8_api, ch8_stop, diagram, fastapi_check, in_plain, mo):
    _base = api_base_url.value.rstrip("/")
    _top = mo.vstack(
        [
            mo.md("### Live: Is the API Running?"),
            in_plain(
                "The API runs as a separate process; the **base URL** is its address. The notebook requests "
                "`/openapi.json`, the machine-readable specification. A response confirms that the API is running, "
                "and it lists every path the API serves and every verb each path accepts."
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
                    "Prerequisite: the API runs in a terminal (`uvicorn sw03_demo_api:app`)."
                ).callout(kind="neutral"),
            ],
            gap=0.6,
        ),
    )
    _status, _schema = ch8_api(_top, "GET", "/openapi.json")
    if _status != 200:
        ch8_stop(_top, f"`{_base}/openapi.json` returned `{_status}`. The base URL may not point to the sales API.")
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
        label="The paths this part uses and the verbs each accepts, read from /openapi.json: "
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
                    mo.stat(len(_schema["paths"]), label="paths in the specification", bordered=True),
                    mo.md(f"Documentation for partners: **[{_base}/docs]({_base}/docs)**"),
                ],
                widths=[2, 1, 2],
                align="center",
            ),
            _matrix,
            mo.md(
                "**Observation:** this table was not written by hand. The API derived it from its own code, and "
                "partners see the same paths and verbs at `/docs`."
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
            mo.md("### Live: Creating a New Product"),
            in_plain(
                "**POST** sends the new product; the API validates it, assigns the next free id and returns "
                "**201 Created**. **GET** with that id reads it back. A second POST fails because the name is now "
                "taken: **400 Bad Request**, a property of the stored data that no type hint can express."
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
                    _answer("post", "**Question:** which fields will the response contain that were not sent?"),
                    _answer("get", "`GET /products/{id}` reads the created product back."),
                ],
                widths="equal",
                align="start",
                gap=1,
            ),
            mo.md(
                "**Observation:** four fields were sent and six returned. The server assigned the `product_id` and "
                "looked up `category_name`; neither was part of the request."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: APIs</h3>
      <details>
        <summary><strong>Q1:</strong> A client's <code>POST /sales</code> timed out. When is it safe to resend it?</summary>
        <p><strong>Answer:</strong> Only if the server can recognise the repetition: the client sends a unique key
        (an idempotency key, or a client-generated id), and the server refuses to create a second record with that key.
        This API assigns <code>sale_id</code> itself, so a retried POST creates a second sale.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> Where should a sale be validated: in the dashboard, in the API, or both?</summary>
        <p><strong>Answer:</strong> In both. The dashboard provides immediate feedback; the API must enforce the rules
        (server-side validation), because any client can bypass the dashboard and call the API directly.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> A public API answers <code>429 Too Many Requests</code>. What should the client do?</summary>
        <p><strong>Answer:</strong> Pause and retry with increasing waiting times, respect a <code>Retry-After</code>
        header if the server sends one, and reduce the request rate, for example by requesting larger pages.</p>
      </details>
      <details>
        <summary><strong>Q4:</strong> How can the API evolve without breaking the partners' scripts?</summary>
        <p><strong>Answer:</strong> Add only optional fields, version endpoints when necessary, and deprecate gradually
        with clear timelines (backward compatibility).</p>
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
    ### Part 3 Summary

    - An HTTP request consists of a verb, a URL (path and query parameters), headers and an optional body; the
      response returns a status code and usually JSON.
    - 2xx means success, 4xx a client error, 5xx a server error. GET, PUT and DELETE are idempotent, POST is not.
    - `requests` retrieves data from the sales API and from public APIs alike, and the JSON converts directly
      into a DataFrame; authentication, rate limits, pagination and terms of use have to be handled.
    - FastAPI maps Python functions to endpoints and generates the documentation (`/docs`) from the code.
    - Pydantic validates every request against a model before the endpoint code runs; it checks structure,
      not truth.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Next: Part 4

    The sales API is complete. Next: the dashboard as the user-facing component, and the choice of its
    framework. A correct API has limited value if its results cannot be used effectively:

    $$
    \\text{user value} = \\text{backend correctness} \\times \\text{frontend usability}
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
            mo.md("## Part 4 · Presentation Frameworks"),
            chapter_intro(
                "presentation",
                "With which framework should the dashboard be built, and how is the data presented faithfully?",
                "The role of a frontend, Streamlit, marimo, Dash and React compared, and how the chart type and the "
                "analysis choices shape what a chart shows.",
                topics=(
                    "Role of the frontend",
                    "Aggregate where the data is",
                    "Framework landscape",
                    "One dashboard, three frameworks",
                    "Live: marimo and Streamlit",
                    "Choosing a framework",
                    "Choosing a chart type",
                    "Analysis choices",
                ),
            ),
        ],
        gap=1,
    )
    return


@app.cell
def _(box, diagram, in_plain, mo):
    def _tier(x, tier, name, note, file, rule, why):
        """One tier of the stack: its colour, what it holds, and how it states the units rule."""
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
        _tier(2, "presentation", "the dashboard", "Part 4: what users see", "sw03_demo_streamlit.py",
              "min_value=1", "repeated for convenience")
        + _tier(360, "logic", "the sales API", "Part 3: the rules", "sw03_demo_api.py", "ge=1, le=100_000", "the rule")
        + _tier(718, "data", "the sales files", "Parts 1-2: the data", "data/*.parquet", "sales, products, ...",
                "five tables, ids only")
        # a request goes right, the response comes back left
        + '<path class="dg-edge" d="M284 206 H 354"/><path class="dg-edge" d="M358 250 H 288"/>'
        + '<path class="dg-edge" d="M642 206 H 712"/><path class="dg-edge" d="M716 250 H 646"/>'
        + '<text class="dg-muted" x="321" y="196" text-anchor="middle">request</text>'
        + '<text class="dg-muted" x="321" y="274" text-anchor="middle">response</text>'
        + '<text class="dg-muted" x="679" y="196" text-anchor="middle">query</text>'
        + '<text class="dg-muted" x="679" y="274" text-anchor="middle">rows</text>'
        # the side door: a partner's script calls the API without passing the dashboard
        + box(340, 10, "a partner's script · curl", w=320, h=48, cls="dg-box dg-hot")
        + '<path class="dg-edge dg-hot" d="M500 58 V 104"/>'
        + '<text class="dg-hot" x="512" y="88">no dashboard in between</text>',
        width=1000,
        height=340,
        label="Three tiers: the dashboard (Streamlit, Part 4) sends requests to the sales API "
        "(Part 3), which queries the sales files (Parquet, Parts 1 and 2). The units rule sits in the "
        "API; the dashboard's form repeats only its lower bound. A partner's script or curl calls the API directly.",
    )
    mo.vstack(
        [
            mo.md("### The Dashboard Presents, the API Enforces"),
            in_plain(
                "A **frontend** is the user-facing component of a system. The dashboard sends requests to the sales "
                "API and visualises the responses. It owns no business rules: a partner's script calls the API "
                "directly and never passes the dashboard, so every rule must be enforced in the API."
            ),
            _stack,
            mo.md(
                "**Observation:** the dashboard's *Units sold* field starts at 1 (`min_value=1`), a convenience for "
                "users. The rule itself, 1 to 100,000 units, is enforced in the API, where it also applies to the "
                "partner's script. The frontend still sorts, aggregates and draws, but it owns no business rules."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p4_volume = mo.ui.slider(
        steps=[3_360, 33_600, 336_000, 3_360_000], value=3_360, label="Sales in the system", show_value=True, debounce=True
    )
    return (p4_volume,)


@app.cell
def _(best_seconds, format_bytes, in_plain, json, mo, p4_volume, shop_sales):
    # The records GET /sales returns (13 fields, as in sw03_demo_api.py) and the 4 rows of GET /revenue.
    _fields = {
        "sale_id": "sale_id", "sale_date": "sale_date", "units_sold": "units_sold", "total_price": "total_price",
        "customer_rating": "customer_rating", "product_id": "product_id", "product": "product_name",
        "category_id": "category_id", "category": "category_name", "country_id": "country_id",
        "country": "country_name", "region_id": "region_id", "region": "region_name",
    }
    _records = (
        shop_sales.assign(sale_date=shop_sales["sale_date"].dt.strftime("%Y-%m-%d"))[list(_fields)]
        .rename(columns=_fields)
        .to_dict("records")
    )
    _rows_json = json.dumps(_records)
    _revenue_json = json.dumps(
        shop_sales.groupby("region", as_index=False)["total_price"].sum().round(2)
        .rename(columns={"total_price": "revenue"}).to_dict("records")
    )
    _scale = p4_volume.value / len(_records)  # more sales: proportionally more rows, the same 4 aggregates
    _rows_bytes, _revenue_bytes = len(_rows_json) * _scale, len(_revenue_json)
    _parse_ms = best_seconds(json.loads, _rows_json) * 1000 * _scale

    def _transfer(num_bytes, mbit=50):
        """Seconds to send num_bytes over a 50 Mbit/s connection."""
        return num_bytes * 8 / (mbit * 1e6)

    _a = """
# A: every row to the dashboard, aggregated there
sales = pd.DataFrame(requests.get(f"{API}/sales").json())
chart = sales.groupby("region_name")["total_price"].sum()
"""
    _b = """
# B: the API aggregates, the dashboard displays
chart = pd.DataFrame(requests.get(f"{API}/revenue").json())
"""
    mo.vstack(
        [
            mo.md("### Aggregate where the data is"),
            in_plain(
                "A dashboard shows totals, not single sales. If the API returns every row, all rows travel over the "
                "network and the browser aggregates them; if the API aggregates first, only the result travels."
            ),
            p4_volume,
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.md(f"```python\n{_a.strip()}\n```"),
                            mo.hstack(
                                [
                                    mo.stat(format_bytes(_rows_bytes), label="JSON sent", caption=f"{p4_volume.value:,} rows", bordered=True),
                                    mo.stat(f"{_transfer(_rows_bytes):,.2f} s", label="transfer at 50 Mbit/s", caption=f"+ {_parse_ms:,.0f} ms to parse", bordered=True),
                                ],
                                widths="equal",
                            ),
                        ],
                        gap=0.4,
                    ),
                    mo.vstack(
                        [
                            mo.md(f"```python\n{_b.strip()}\n```"),
                            mo.hstack(
                                [
                                    mo.stat(format_bytes(_revenue_bytes), label="JSON sent", caption="4 rows", bordered=True),
                                    mo.stat(f"{_transfer(_revenue_bytes) * 1000:,.3f} ms", label="transfer at 50 Mbit/s", bordered=True),
                                ],
                                widths="equal",
                            ),
                        ],
                        gap=0.4,
                    ),
                ],
                widths="equal",
                gap=2,
            ),
            mo.md(
                f"**Observation:** both variants draw the same chart. Variant A sends {format_bytes(_rows_bytes)} and grows "
                f"with every sale; variant B sends {format_bytes(_revenue_bytes)}, {_rows_bytes / _revenue_bytes:,.0f} times "
                "less, whatever the number of sales. Aggregations belong where the data is, in the database or the API; "
                "the frontend requests what it displays."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(diagram, in_plain, mo):
    # Ordered from the fastest first version to the most layout control.
    _frameworks = [
        ("Streamlit", "Python", "fastest start: the whole dashboard is one script", "every interaction reruns the script"),
        ("marimo", "Python", "reactive notebook that also runs as an app (this deck is one)", "notebook-oriented, not for large public websites"),
        ("Dash", "Python", "Plotly charts linked by callbacks", "callbacks become complex as the app grows"),
        ("Flask", "Python + HTML/JS", "full control over pages and forms", "every page and widget is built by hand"),
        ("React", "JavaScript", "any interface, for many users", "requires web developers and a build toolchain"),
    ]
    _tiles = "".join(
        f'<div class="tile"><div class="tile-key">{_name}</div><div class="tile-title">{_lang}</div>'
        f'<p>{_strength}</p><p class="tile-bad">{_limit}</p></div>'
        for _name, _lang, _strength, _limit in _frameworks
    )
    _tradeoff = diagram(
        '<text x="0" y="26" font-weight="700">faster first version</text>'
        '<path class="dg-edge" d="M400 20 H 190"/>'
        '<text class="dg-muted" x="500" y="26" text-anchor="middle">typical trade-off</text>'
        '<path class="dg-edge" d="M600 20 H 810"/>'
        '<text x="1000" y="26" text-anchor="end" font-weight="700">more layout control</text>',
        width=1000,
        height=40,
        label="The typical trade-off: the further left, the faster the first version; the further right, the more layout control.",
    )
    mo.vstack(
        [
            mo.md("### Five Frameworks for the Dashboard"),
            in_plain(
                "All five frameworks can implement the dashboard. They differ in **the skills required to build it**, "
                "**the time to a first version**, and **the degree of layout control**. Faster development usually "
                "means less control."
            ),
            _tradeoff,
            mo.Html(f'<div class="tiles tier-presentation" style="grid-template-columns: repeat(5, 1fr)">{_tiles}</div>'),
            mo.md(
                "**Observation:** the three Python frameworks require no additional skills in the team; Flask and React "
                "require JavaScript, the language browsers execute, and offer full control in return.\n\n"
                '<p class="vis-caption">An approximate guide, not a measurement. Showcases: '
                '<a href="https://marimo.io/gallery">marimo gallery</a> · '
                '<a href="https://dash.gallery/Portal/">Dash gallery</a> · '
                '<a href="https://react.dev/community">React community</a> · '
                '<a href="https://flask.palletsprojects.com/en/stable/patterns/">Flask patterns</a></p>'
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo):
    _streamlit = """
import pandas as pd, requests, streamlit as st

API = "http://127.0.0.1:8000"
sales = pd.DataFrame(requests.get(f"{API}/sales", timeout=5).json())
region = st.selectbox("Region", sorted(sales["region_name"].unique()))

picked = sales[sales["region_name"] == region]
st.bar_chart(picked.groupby("product_name")["total_price"].sum())
"""
    _marimo = """
# cell 1
import altair as alt, marimo as mo, pandas as pd, requests

API = "http://127.0.0.1:8000"
sales = pd.DataFrame(requests.get(f"{API}/sales", timeout=5).json())
region = mo.ui.dropdown(sorted(sales["region_name"].unique()), value="Europe", label="Region")
region

# cell 2: reruns automatically when region changes
picked = sales[sales["region_name"] == region.value]
alt.Chart(picked).mark_bar().encode(x="sum(total_price)", y="product_name")
"""
    _dash = """
import pandas as pd, plotly.express as px, requests
from dash import Dash, Input, Output, dcc, html

API = "http://127.0.0.1:8000"
sales = pd.DataFrame(requests.get(f"{API}/sales", timeout=5).json())
app = Dash()
app.layout = html.Div([dcc.Dropdown(sorted(sales["region_name"].unique()), "Europe", id="region"),
                       dcc.Graph(id="chart")])

@app.callback(Output("chart", "figure"), Input("region", "value"))
def update(region):  # Dash calls this function whenever the dropdown changes
    picked = sales[sales["region_name"] == region]
    return px.histogram(picked, x="product_name", y="total_price")

app.run()
"""
    mo.vstack(
        [
            mo.md("### One dashboard, three frameworks"),
            in_plain(
                "Streamlit, marimo and Dash build the same small dashboard in about ten lines of Python: a region "
                "selector and the revenue per product. They differ in **how they react to user input**."
            ),
            mo.md(
                """
    <div class="tiles tier-presentation" style="grid-template-columns: repeat(3, 1fr)">
      <div class="tile"><div class="tile-key">Streamlit</div><div class="tile-title">Script</div>
        <p>Every interaction reruns the whole script from the top; <code>st.cache_data</code> avoids repeating expensive steps.</p></div>
      <div class="tile"><div class="tile-key">marimo</div><div class="tile-title">Reactive cells</div>
        <p>A change reruns only the cells that depend on it; the same file runs as a notebook, an app or slides.</p></div>
      <div class="tile"><div class="tile-key">Dash</div><div class="tile-title">Callbacks</div>
        <p>Each function declares its inputs and outputs; Dash calls it when one of its inputs changes.</p></div>
    </div>
                """
            ),
            mo.ui.tabs(
                {
                    "Streamlit": mo.md(f"```python\n{_streamlit.strip()}\n```"),
                    "marimo": mo.md(f"```python\n{_marimo.strip()}\n```"),
                    "Dash": mo.md(f"```python\n{_dash.strip()}\n```"),
                }
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo, shop_sales):
    p4_region = mo.ui.dropdown(sorted(shop_sales["region"].unique()), value="Europe", label="Region")
    p4_measures = {"revenue (CHF)": "total_price", "units sold": "units_sold"}
    p4_measure = mo.ui.radio(options=list(p4_measures), value="revenue (CHF)", label="Measure", inline=True)
    return p4_measure, p4_measures, p4_region


@app.cell
def _(alt, in_plain, mo, p4_measure, p4_measures, p4_region, shop_sales, tier_chart):
    _column = p4_measures[p4_measure.value]
    _picked = shop_sales[shop_sales["region"] == p4_region.value]
    _by_product = _picked.groupby("product", as_index=False)[_column].sum()
    _chart = (
        alt.Chart(_by_product)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X(f"{_column}:Q", title=p4_measure.value),
            y=alt.Y("product:N", sort="-x", title=None),
            tooltip=["product:N", f"{_column}:Q"],
        )
        .properties(width="container", height=230)
    )
    _total = _picked[_column].sum()
    mo.vstack(
        [
            mo.md("### This slide is a marimo app"),
            in_plain(
                "The controls below are marimo UI elements. Changing one reruns only the cells that read it, and the "
                "chart updates; the code of this slide is about a dozen lines, like the marimo tab on the previous slide."
            ),
            mo.hstack([p4_region, p4_measure], justify="start", gap=3),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.stat(f"{len(_picked):,}", label=f"sales in {p4_region.value}", bordered=True),
                            mo.stat(
                                f"CHF {_total:,.0f}" if _column == "total_price" else f"{_total:,}",
                                label=p4_measure.value,
                                bordered=True,
                            ),
                        ],
                        gap=0.6,
                    ),
                    tier_chart(_chart, "presentation"),
                ],
                widths=[1, 3],
                gap=2,
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo):
    _excerpt = '''
# sw03_demo_streamlit.py (abridged)
@st.cache_data(ttl="15s", show_spinner="Loading sales…")
def fetch_sales(url: str, params: dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(api("GET", url, params=params))  # GET /sales with the chosen filters
    ...
'''
    mo.vstack(
        [
            mo.md("### Live: the EdgeWorks dashboard in Streamlit"),
            in_plain(
                "The demo dashboard `sw03_demo_streamlit.py` is a Streamlit app that obtains all of its data from the "
                "sales API. It runs while the API is running: `streamlit run sw03_demo_streamlit.py`, then "
                "`http://localhost:8501`."
            ),
            mo.md(
                """
    <div class="tiles tier-presentation" style="grid-template-columns: repeat(3, 1fr)">
      <div class="tile"><div class="tile-key">GET</div><div class="tile-title">Reads</div>
        <p>The <em>Dashboard</em> tab requests <code>GET /sales</code> with the selected filters and draws time series,
        a heatmap and a rating chart.</p></div>
      <div class="tile"><div class="tile-key">POST</div><div class="tile-title">Writes</div>
        <p>The <em>Records</em> tab creates and edits records with <code>POST</code> and <code>PUT</code>; the API
        validates every change and rejects invalid input with 422.</p></div>
      <div class="tile"><div class="tile-key">15 s</div><div class="tile-title">Caches</div>
        <p>Responses are cached for 15 seconds (<code>st.cache_data</code>), so a rerun of the script does not repeat
        every request.</p></div>
    </div>
                """
            ),
            mo.md(f"```python\n{_excerpt.strip()}\n```"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(in_plain, mo, static_table):
    _rows = [
        ("Internal dashboard on a DataFrame or an API, built by data scientists", "Streamlit", "one Python script; widgets and charts in a few lines"),
        ("Analysis that should also run as an app or as slides", "marimo", "reactive notebook; the same file runs as an app"),
        ("Larger app with many linked charts and precise control of updates", "Dash", "explicit callbacks, Plotly charts"),
        ("Server-rendered pages and forms, small web services", "Flask", "minimal web framework with HTML templates"),
        ("Public product with a custom design and many users", "React, with an API", "full control of the interface; requires web developers"),
    ]
    mo.vstack(
        [
            mo.md("### Which framework for which purpose?"),
            in_plain(
                "No framework is best in general. The choice depends on who builds and maintains the app, how much the "
                "layout must be customised, and who uses it."
            ),
            static_table(
                [{"situation": _s, "suitable choice": _f, "reason": _r} for _s, _f, _r in _rows],
                label="A guide, not a rule",
                wrapped_columns=["situation", "reason"],
                column_widths={"situation": 620, "suitable choice": 220, "reason": 620},
            ),
            mo.md(
                "**Observation:** for EdgeWorks, a data team without web developers that builds a dashboard for internal "
                "users, Streamlit or marimo is the natural choice. Because the API enforces the rules, this decision can "
                "be revised later without touching the data and logic tiers."
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    p4_question = mo.ui.radio(
        options=[
            "Comparison: revenue per region",
            "Trend: revenue per month",
            "Relationship: units and sale value",
            "Share: categories within each region",
        ],
        value="Comparison: revenue per region",
        label="Question:",
        inline=True,
    )
    return (p4_question,)


@app.cell
def _(TIER, alt, in_plain, mo, p4_question, shop_sales, tier_chart):
    _q = p4_question.value
    _muted = TIER["muted"]
    if _q.startswith("Comparison"):
        _df = shop_sales.groupby("region", as_index=False)["total_price"].sum()
        _good = alt.Chart(_df).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("total_price:Q", title="revenue (CHF)"), y=alt.Y("region:N", sort="-x", title=None)
        )
        _poor = alt.Chart(_df).mark_line(point=alt.OverlayMarkDef(color=_muted, size=80), strokeWidth=3, color=_muted).encode(
            x=alt.X("region:N", sort=None, title=None), y=alt.Y("total_price:Q", title="revenue (CHF)", scale=alt.Scale(zero=False))
        )
        _why = (
            "bars from zero, sorted by value: the ranking is visible at once.",
            "a line suggests a development between unrelated regions, and the axis without zero exaggerates the differences.",
        )
    elif _q.startswith("Trend"):
        _df = (
            shop_sales.assign(month=shop_sales["sale_date"].dt.to_period("M").dt.to_timestamp())
            .groupby("month", as_index=False)["total_price"].sum()
        )
        _df["label"] = _df["month"].dt.strftime("%b %Y")
        _good = alt.Chart(_df).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("month:T", title=None), y=alt.Y("total_price:Q", title="revenue (CHF)")
        )
        _poor = alt.Chart(_df).mark_bar(color=_muted).encode(
            x=alt.X("label:N", sort="-y", title="months, sorted by revenue", axis=alt.Axis(labels=False, ticks=False)),
            y=alt.Y("total_price:Q", title="revenue (CHF)"),
        )
        _why = (
            "a line along the time axis shows the development from month to month.",
            "bars sorted by value destroy the time order: the trend can no longer be seen.",
        )
    elif _q.startswith("Relationship"):
        _df = shop_sales.sample(600, random_state=3)[["units_sold", "total_price"]].reset_index(drop=True)
        _good = alt.Chart(_df).mark_circle(size=45, opacity=0.5).encode(
            x=alt.X("units_sold:Q", title="units sold"), y=alt.Y("total_price:Q", title="sale value (CHF)")
        )
        _poor = alt.Chart(_df.reset_index()).mark_line(strokeWidth=1, color=_muted).encode(
            x=alt.X("index:Q", title="row in the file"), y=alt.Y("total_price:Q", title="sale value (CHF)")
        )
        _why = (
            "a scatter plot places each sale by both measures, and the relationship becomes visible.",
            "a line in row order connects unrelated sales, and the second measure is missing entirely.",
        )
    else:
        _df = shop_sales.groupby(["region", "category"], as_index=False)["total_price"].sum()
        _good = alt.Chart(_df).mark_bar().encode(
            x=alt.X("total_price:Q", stack="normalize", title="share of revenue", axis=alt.Axis(format="%")),
            y=alt.Y("region:N", title=None),
            color=alt.Color("category:N", title=None),
        )
        _poor = alt.Chart(_df).mark_arc().encode(
            theta=alt.Theta("total_price:Q", stack=True),
            color=alt.Color("category:N", title=None),
            facet=alt.Facet("region:N", columns=4, title=None),
        )
        _why = (
            "bars normalised to 100% align the shares on one axis, so the regions can be compared directly.",
            "angles in separate pie charts are hard to compare from one region to the next.",
        )
    _good = _good.properties(width="container", height=250)
    _poor = _poor.properties(width=120, height=120) if _q.startswith("Share") else _poor.properties(width="container", height=250)
    mo.vstack(
        [
            mo.md("### Choosing a chart type"),
            in_plain(
                "The chart type follows from the question: a **comparison** of categories uses bars, a **trend** over "
                "time a line, a **relationship** between two measures a scatter plot, and a **share** of a whole "
                "stacked bars. A mismatched type hides the answer or suggests a false one."
            ),
            p4_question,
            mo.hstack(
                [
                    mo.vstack([mo.md(f"**Suitable:** {_why[0]}").callout(kind="success"), tier_chart(_good, "presentation")], gap=0.4),
                    mo.vstack([mo.md(f"**Misleading:** {_why[1]}").callout(kind="danger"), tier_chart(_poor, "presentation")], gap=0.4),
                ],
                widths="equal",
                gap=2,
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    # The analysis-choices lab's control, shown by the slide below.
    honest_view = mo.ui.radio(
        options=["A: average the sales", "B: one line per category", "C: leave out one category"],
        value="A: average the sales",
        label="Analysis choice:",
        inline=True,
    )
    return (honest_view,)


@app.cell
def _(SEED_DIR, TIER, alt, duckdb, honest_view, in_plain, mo, pd, tier_chart):
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
    _cats = [_c for (_c,) in _con.execute("SELECT DISTINCT category FROM sales ORDER BY 1").fetchall()]
    _palette = alt.Scale(domain=_cats, range=["#4c78a8", "#b279a2", "#54a24b", "#9d755d"][: len(_cats)])
    _averages = "(SELECT avg(x) AS x, avg(y) AS y FROM sales GROUP BY product, month)"
    _choice = honest_view.value[0]
    # Two panels per choice: (title, the points, one fitted line per value of this expression)
    _views = {
        "A": [("each sale", "sales", "'all'"), ("average per product and month", _averages, "'all'")],
        "B": [("all sales, one line", "sales", "'all'"), ("one line per category", "sales", "category")],
        "C": [("all sales", "sales", "'all'"), ("without Services", "sales WHERE category <> 'Services'", "'all'")],
    }[_choice]

    def _fit(source, group):
        """Least squares, computed by DuckDB: one line per group, as (group, slope, intercept, R², n, x min, x max)."""
        return _con.execute(
            f"SELECT {group} AS grp, regr_slope(y, x), regr_intercept(y, x), regr_r2(y, x), count(*), min(x), max(x) "
            f"FROM {source} GROUP BY grp ORDER BY grp"
        ).fetchall()

    def _panel(i, title, source, group):
        """One scatter plot with its fitted lines; a single line is red where it slopes down."""
        fits = _fit(source, group)
        per_category = group == "category"
        points = _con.execute(f"SELECT x, y{', category AS grp' if per_category else ''} FROM {source}").df()
        segments = pd.DataFrame(
            [{"grp": g, "x": _x, "y": b + a * _x, "down": a < 0} for g, a, b, _r2, _n, lo, hi in fits for _x in (lo, hi)]
        )
        if per_category:
            subtitle = "slope per CHF 10,000: " + " · ".join(f"{g} {a * 10_000:+.2f}" for g, a, *_ in fits)
        else:
            _g, a, _b, r2, n, *_ = fits[0]
            subtitle = f"n = {n:,} · R² = {r2:.2f} · slope {a * 10_000:+.2f} per CHF 10,000"
        x = alt.X("x:Q", title="sale amount (CHF)", axis=alt.Axis(format="~s", tickCount=5))
        y = alt.Y("y:Q", title="rating" if i == 0 else None, scale=alt.Scale(domain=[1, 5]))
        dense = len(points) > 1000
        dots = alt.Chart(points).mark_circle(size=22 if dense else 60, opacity=0.35 if dense else 0.7).encode(x=x, y=y)
        lines = alt.Chart(segments).mark_line(strokeWidth=4).encode(x=x, y=y, detail="grp:N")
        if per_category:
            color = alt.Color(
                "grp:N", scale=_palette, title=None, legend=alt.Legend(orient="bottom", symbolOpacity=1, symbolSize=160)
            )
            dots, lines = dots.encode(color=color), lines.encode(color=color)
        else:
            dots = dots.encode(color=alt.value(TIER["muted"]))
            lines = lines.encode(color=alt.condition("datum.down", alt.value(TIER["hot"]), alt.value(TIER["presentation"])))
        chart = (dots + lines).properties(
            width="container",
            height=240,
            title=alt.TitleParams(title, subtitle=subtitle, fontSize=16, subtitleFontSize=14),
        )
        return chart, fits

    _made = [_panel(_i, *_view) for _i, _view in enumerate(_views)]
    _panels = mo.hstack([tier_chart(_chart, "presentation") for _chart, _ in _made], widths="equal", gap=2)
    _all_line = _made[0][1][0]  # (group, slope, intercept, R², n, x min, x max)
    if _choice == "A":
        _avg_line = _made[1][1][0]
        _lesson = (
            f"**Averaging raised R² from {_all_line[3]:.2f} to {_avg_line[3]:.2f} without adding any information.** "
            "Each average hides the spread of the sales behind it, so the points lie closer to the line; between "
            "single sales, the relationship remains weak."
        )
    elif _choice == "B":
        # per category: negative, about zero (under 0.02 rating per CHF 10,000) or positive
        _slopes = {_g: _a * 10_000 for _g, _a, *_ in _made[1][1]}
        _kinds = {
            "negative": [_g for _g, _s in _slopes.items() if _s <= -0.02],
            "about zero": [_g for _g, _s in _slopes.items() if abs(_s) < 0.02],
            "positive": [_g for _g, _s in _slopes.items() if _s >= 0.02],
        }
        _per = [f"{_kind} within {' and '.join(_gs)}" for _kind, _gs in _kinds.items() if _gs]
        _priciest = _con.execute("SELECT category FROM sales GROUP BY 1 ORDER BY avg(x) DESC LIMIT 1").fetchone()[0]
        _best_rated = _con.execute("SELECT category FROM sales GROUP BY 1 ORDER BY avg(y) DESC LIMIT 1").fetchone()[0]
        _lesson = (
            f"**The pooled line contradicts the categories.** Across all sales, the slope is "
            f"{'positive' if _all_line[1] > 0 else 'negative'}; per category, it is "
            + (", ".join(_per[:-1]) + " and " + _per[-1] if len(_per) > 1 else _per[0])
            + "."
            + (
                f" The pooled line mainly reflects that {_priciest}, the most expensive category, is also rated "
                "highest (related to Simpson's paradox)."
                if _priciest == _best_rated
                else ""
            )
        )
    else:
        _without = _made[1][1][0]
        _lesson = (
            f"**Leaving out one category reverses the slope**, from {_all_line[1] * 10_000:+.2f} to "
            f"{_without[1] * 10_000:+.2f} per CHF 10,000, while R² barely changes ({_all_line[3]:.2f} → "
            f"{_without[3]:.2f}). R² does not reveal that a single group determines the direction."
        )

    mo.vstack(
        [
            mo.md("### Three Analysis Choices That Change the Result Without Changing the Data"),
            in_plain(
                f"The same {_all_line[4]:,} sales and the same question: do customers who spend more give higher "
                "ratings? Each choice below changes only the analysis. **R²** measures how closely the points follow "
                "the fitted line (0 to 1); the **slope** gives its direction."
            ),
            honest_view,
            _panels,
            mo.md(_lesson).callout(kind="warn"),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Discussion: Presentation</h3>
      <details>
        <summary><strong>Q1:</strong> The dashboard's form already rejects 0 units. Why does the API validate again?</summary>
        <p><strong>Answer:</strong> A partner's script calls the API directly, with <code>curl</code> or its own
        code, and never passes the form. A rule enforced only in the dashboard can be bypassed. The form repeats
        it for convenience: immediate feedback for the user, without a round trip.</p>
      </details>
      <details>
        <summary><strong>Q2:</strong> When is Streamlit not a good choice?</summary>
        <p><strong>Answer:</strong> When many users need a custom, highly interactive interface, or when parts of a
        page must update independently: every interaction reruns the whole script. Dash, with its callbacks, or a
        React frontend on top of the API then fits better.</p>
      </details>
      <details>
        <summary><strong>Q3:</strong> The dashboard becomes slow once EdgeWorks has three million sales. What should change?</summary>
        <p><strong>Answer:</strong> Aggregate in the API or the database and request only the figures the dashboard
        displays, cache repeated requests, and page through tables instead of loading every row.</p>
      </details>
      <details>
        <summary><strong>Q4:</strong> A slide shows a closely fitting line and a high R². What should be asked first?</summary>
        <p><strong>Answer:</strong> What one point represents, and how many points there are. Averaging the same sales
        into a few groups turns a weak per-sale relationship into a close fit, without any new information.</p>
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
    ### Part 4 Summary

    - A frontend presents data and collects input; the rules remain in the API, which every client must pass.
      Aggregations belong in the API or the database: the dashboard requests what it displays.
    - Streamlit reruns a script, marimo reruns dependent cells, Dash calls callbacks; Flask and React require
      web development skills.
    - The choice depends on who builds and maintains the app, the layout control required and the audience.
    - The chart type follows from the question: bars compare, lines show trends, scatter plots show
      relationships, stacked bars show shares.
    - Aggregating, stratifying or excluding a group can change a finding without changing the data: the unit of
      analysis and the number of points must be reported.
                """
            ).callout(kind="success"),
            mo.md(
                """
    ### Next: the Wrap-up

    One question, followed through all three tiers.
                """
            ).callout(kind="neutral"),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo):
    _tiers = [
        (
            "data",
            "SQL on Parquet (Part 2)",
            "sql",
            """
SELECT r.name AS region, sum(s.total_price) AS revenue
FROM 'sales.parquet' s
JOIN 'countries.parquet' c USING (country_id)
JOIN 'sales_regions.parquet' r USING (region_id)
GROUP BY region
""",
        ),
        (
            "logic",
            "an endpoint in FastAPI (Part 3)",
            "python",
            """
@app.get("/revenue")
def revenue_per_region() -> list[dict]:
    rows = duckdb.sql(SQL).fetchall()
    return [{"region": r, "revenue": v} for r, v in rows]
""",
        ),
        (
            "presentation",
            "a chart in Streamlit (Part 4)",
            "python",
            """
revenue = requests.get(f"{API}/revenue", timeout=5).json()
st.bar_chart(pd.DataFrame(revenue), x="region", y="revenue")
""",
        ),
    ]
    _columns = [
        mo.vstack(
            [
                mo.Html(
                    f'<div class="key-q tier-{_tier}" style="padding: 10px 16px">'
                    f'<span class="tier-badge">{_tier} tier</span> <strong>{_title}</strong></div>'
                ),
                mo.md(f"```{_lang}\n{_code.strip()}\n```"),
            ],
            gap=0.4,
        )
        for _tier, _title, _lang, _code in _tiers
    ]
    mo.vstack(
        [
            mo.md("### Wrap-up: One Question Through Three Tiers"),
            mo.md("*How does revenue per region get from the sales file onto a dashboard?*"),
            mo.hstack(_columns, widths="equal", gap=1.5),
            mo.md(
                '<p class="vis-caption">Each tier uses the formats and interfaces of this lecture: Parquet and SQL in the '
                "data tier, HTTP and JSON in the logic tier, a Python framework in the presentation tier. About a dozen "
                "lines per tier are enough for a working end-to-end prototype.</p>"
            ),
        ],
        gap=0.8,
    )
    return


@app.cell
def _(mo, tier_map):
    mo.vstack(
        [
            mo.md(
                f"""
    <div class="section-card">
      <h3>Wrap-up: The Three-Tier Architecture Revisited</h3>
      {tier_map}
      <p class="vis-caption">Each tier communicates only with its neighbour, so any one of them can be
      replaced without changing the others.</p>
      <div class="tiles">
        <div class="tile"><div class="tile-key">1</div><div class="tile-title">Correctness</div>
          <p>A property of the design, not of a tool; established first.</p></div>
        <div class="tile"><div class="tile-key">2</div><div class="tile-title">Performance</div>
          <p>Optimised once correctness is established.</p></div>
        <div class="tile"><div class="tile-key">3</div><div class="tile-title">Usability</div>
          <p>Results presented clearly and without distortion.</p></div>
      </div>
    </div>
                """
            ),
        ],
        gap=0.6,
    )
    return


@app.cell
def _(mo):
    mo.md("""
    <div class="section-card">
      <h3>Wrap-up: Key Takeaways</h3>
      <ol class="question-list" style="font-size: 1.15rem; gap: 10px">
        <li class="tier-data"><strong>Formats:</strong> CSV and JSON are readable text; Avro, Parquet and Arrow are
        binary and typed. Parquet suits analytics, Avro streams, Arrow in-memory exchange; Pickle only trusted data.
        Dates need an explicit format and time zone.</li>
        <li class="tier-data"><strong>Storage:</strong> a column layout reads only the needed columns and compresses
        well; partitioning lets a query skip whole files; compression trades CPU time for fewer bytes.</li>
        <li class="tier-data"><strong>Queries:</strong> DuckDB runs SQL directly on files; schema-on-write rejects
        invalid data early, schema-on-read fails silently.</li>
        <li class="tier-data"><strong>Transactions:</strong> concurrent read-modify-write cycles on files lose updates;
        transactions make changes atomic and isolated.</li>
        <li class="tier-logic"><strong>APIs:</strong> a request is a verb and a URL, the response a status code and JSON.
        <code>requests</code> retrieves data; FastAPI and Pydantic serve and validate it.</li>
        <li class="tier-presentation"><strong>Presentation:</strong> Streamlit, marimo and Dash differ in how they react
        to input; the dashboard requests aggregates, and the chart type follows the question. Analysis choices
        change what a chart shows.</li>
      </ol>
      <p class="vis-caption">Practice: exercises 1–2 (marimo) · 3–4 (CSV and Parquet) · 5–6 (compression) ·
      7–8 (building and calling an API), in <code>sw03_lecture_exercises.py</code>.</p>
    </div>
    """)
    return


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("## Further Reading and Documentation"),
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
