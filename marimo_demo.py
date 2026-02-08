import marimo

app = marimo.App()


@app.cell
def _():
    import asyncio
    import datetime as dt
    import importlib.util as iu
    import math
    import random
    import sqlite3
    import statistics
    import textwrap
    from collections import Counter

    import marimo as mo

    return (
        Counter,
        asyncio,
        dt,
        iu,
        math,
        mo,
        random,
        sqlite3,
        statistics,
        textwrap,
    )


@app.cell
def _(mo):
    css = mo.Html(
        """
        <style>
          :root {
            --ink: #f5f7fb;
            --ink-2: #ffffff;
            --surface: rgba(255, 255, 255, 0.86);
            --surface-strong: rgba(255, 255, 255, 0.95);
            --border: rgba(121, 144, 178, 0.25);
            --accent: #6c7cff;
            --accent-2: #ff8db1;
            --accent-3: #5ec8b5;
            --text: #1c2233;
            --muted: #4f5d75;
            --text-strong: #0f172a;
          }

          body {
            background: linear-gradient(180deg, #f7f8fc 0%, #f1f4fb 45%, #eef2f9 100%);
            color: var(--text);
            font-family: "IBM Plex Sans", "Space Grotesk", "Segoe UI", sans-serif;
            color-scheme: light;
          }

          main, .marimo-main, .mo-main {
            max-width: 1440px;
            margin: 0 auto;
            padding-bottom: 64px;
          }

          body, main, .marimo-main, .mo-main, .marimo-root {
            color: var(--text);
          }

          h2 {
            font-size: 1.4rem;
            letter-spacing: 0.02em;
            margin-top: 1.6rem;
            color: var(--text-strong);
          }

          h3 {
            font-size: 1.05rem;
            color: var(--muted);
          }

          pre, code {
            background: rgba(240, 244, 255, 0.9);
            border: 1px solid rgba(108, 124, 255, 0.2);
            border-radius: 10px;
            font-family: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, Menlo, monospace;
            color: var(--text-strong);
          }

          pre {
            padding: 12px 14px;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            overflow: hidden;
            color: var(--text-strong);
          }

          th, td {
            padding: 10px 12px;
            border-bottom: 1px solid rgba(121, 144, 178, 0.2);
            color: var(--text-strong);
          }

          thead th {
            text-align: left;
            font-weight: 700;
            color: var(--text-strong);
            background: rgba(108, 124, 255, 0.12);
          }

          tbody tr:nth-child(even) td {
            background: rgba(108, 124, 255, 0.04);
          }

          input, select, textarea, button {
            color: var(--text-strong);
          }

          .dataframe, .dataframe * {
            color: var(--text-strong) !important;
          }

          .hero {
            position: relative;
            border-radius: 20px;
            padding: 28px 28px 24px 28px;
            background: linear-gradient(120deg, #f3f1ff 0%, #eef4ff 55%, #f7f2ff 100%);
            border: 1px solid var(--border);
            box-shadow: 0 24px 60px rgba(108, 124, 255, 0.2);
            overflow: hidden;
          }

          .hero-glow {
            position: absolute;
            inset: -40% 10% 10% -30%;
            background: radial-gradient(circle at 25% 30%, rgba(108, 124, 255, 0.35), transparent 55%),
                        radial-gradient(circle at 80% 20%, rgba(255, 141, 177, 0.3), transparent 55%),
                        radial-gradient(circle at 35% 80%, rgba(94, 200, 181, 0.3), transparent 55%);
            filter: blur(45px);
            opacity: 0.9;
          }

          .hero-content {
            position: relative;
            z-index: 2;
            color: var(--text);
          }

          .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 6px 12px;
            border-radius: 999px;
            background: rgba(108, 124, 255, 0.15);
            border: 1px solid rgba(108, 124, 255, 0.35);
            color: var(--accent);
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            font-size: 12px;
          }

          .hero-title {
            font-size: 2.2rem;
            line-height: 1.1;
            margin: 12px 0 8px 0;
          }

          .hero-subtitle {
            color: var(--muted);
            font-size: 1rem;
            max-width: 720px;
          }

          .hero-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
          }

          .hero-pill {
            padding: 6px 12px;
            border-radius: 999px;
            border: 1px solid rgba(121, 144, 178, 0.2);
            background: rgba(255, 255, 255, 0.6);
            color: var(--text);
            font-size: 12px;
          }

          .section-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
          }

          .chip {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(255, 141, 177, 0.2);
            color: #b24f7f;
            font-size: 12px;
            border: 1px solid rgba(255, 141, 177, 0.4);
          }

          .muted {
            color: var(--muted);
            font-size: 0.9rem;
          }
        </style>
        """
    )
    css
    return (css,)


@app.cell
def _(mo):
    hero = mo.md(
        f"""
        <a id="overview"></a>
        <div class="hero">
          <div class="hero-glow"></div>
          <div class="hero-content">
            <div class="hero-badge">{mo.icon('lucide:database')} MARIMO FOR DATA TEAMS</div>
            <div class="hero-title">Data Ops Control Room</div>
            <div class="hero-subtitle">
              A purpose-built notebook for Data Scientists and Data Engineers: reactive inputs, data
              profiling, SQL exploration, charts, pipelines, and operational status in one live app.
            </div>
            <div class="hero-pills">
              <div class="hero-pill">Synthetic Data Gen</div>
              <div class="hero-pill">Quality Checks</div>
              <div class="hero-pill">SQL Playground</div>
              <div class="hero-pill">Charts + Metrics</div>
              <div class="hero-pill">Operational Status</div>
            </div>
          </div>
        </div>
        """
    )
    hero
    return (hero,)


@app.cell
def _(mo):
    seed = mo.ui.slider(1, 999, value=42, label="Seed", show_value=True)
    volume = mo.ui.slider(500, 5000, step=250, value=2000, label="Events", show_value=True)
    date_window = mo.ui.date_range(label="Date window")
    regions = mo.ui.multiselect(
        options=["us-east", "us-west", "eu-central", "ap-south"],
        value=["us-east", "us-west", "eu-central"],
        label="Regions",
    )
    stages = mo.ui.multiselect(
        options=["ingest", "transform", "load", "serve"],
        value=["ingest", "transform", "load"],
        label="Pipeline stages",
    )
    latency_threshold = mo.ui.slider(
        50, 1200, step=10, value=450, label="Latency threshold (ms)", show_value=True
    )
    show_outliers = mo.ui.switch(value=True, label="Highlight outliers")
    resample = mo.ui.button(label="Resample data", value=0, kind="success")

    form = (
        mo.md("""**Notebook context**\n\n{name}\n\n{team}\n\n{priority}""")
        .batch(
            name=mo.ui.text(label="Project"),
            team=mo.ui.text(label="Owning team"),
            priority=mo.ui.dropdown(
                options=["P0", "P1", "P2"], value="P1", label="Priority"
            ),
        )
        .form(bordered=False, show_clear_button=True)
    )

    control_panel = mo.vstack(
        [
            mo.md("## Controls").callout(kind="info"),
            mo.hstack([seed, volume], widths="equal"),
            date_window,
            mo.hstack([regions, stages], widths="equal"),
            mo.hstack([latency_threshold, show_outliers], widths="equal"),
            resample,
            form,
        ],
        gap=0.8,
    )

    return (
        control_panel,
        date_window,
        latency_threshold,
        regions,
        resample,
        seed,
        show_outliers,
        stages,
        volume,
    )


@app.cell
def _(Counter, dt, random, resample, seed, volume):
    rng = random.Random(seed.value + resample.value)
    total_events = volume.value

    _regions = ["us-east", "us-west", "eu-central", "ap-south"]
    _stages = ["ingest", "transform", "load", "serve"]
    _event_types = ["view", "click", "purchase", "error"]
    _systems = ["orders", "payments", "inventory", "support", "analytics"]

    now = dt.datetime.now()
    start = now - dt.timedelta(days=21)

    events = []
    for idx in range(total_events):
        ts = start + dt.timedelta(minutes=rng.randint(0, 21 * 24 * 60))
        region = rng.choice(_regions)
        stage = rng.choice(_stages)
        system = rng.choice(_systems)
        event_type = rng.choice(_event_types)
        latency = max(20, int(rng.gauss(280 + _stages.index(stage) * 90, 80)))
        bytes_out = max(120, int(rng.gauss(8000, 1800)))
        status = "error" if (event_type == "error" or rng.random() < 0.03) else "ok"

        if rng.random() < 0.02:
            region = None
        if rng.random() < 0.02:
            bytes_out = None

        events.append(
            {
                "event_id": f"evt_{idx:06d}",
                "timestamp": ts,
                "region": region,
                "stage": stage,
                "system": system,
                "event_type": event_type,
                "latency_ms": latency,
                "bytes_out": bytes_out,
                "status": status,
            }
        )

    if total_events > 50:
        for _ in range(3):
            events.append(rng.choice(events))

    stage_counts = Counter([_row["stage"] for _row in events])
    return events, now, stage_counts


@app.cell
def _(
    date_window,
    events,
    latency_threshold,
    regions,
    show_outliers,
    stages,
    statistics,
):
    _chosen_regions = set(regions.value or [])
    _chosen_stages = set(stages.value or [])

    _min_date = min(event["timestamp"] for event in events).date()
    _max_date = max(event["timestamp"] for event in events).date()

    _window = date_window.value
    if _window and _window[0] and _window[1]:
        start_date, end_date = _window
    else:
        start_date, end_date = _min_date, _max_date

    def _region_filter(_row):
        return _row["region"] in _chosen_regions if _chosen_regions else True

    def _stage_filter(_row):
        return _row["stage"] in _chosen_stages if _chosen_stages else True

    filtered_events = [
        _row
        for _row in events
        if start_date <= _row["timestamp"].date() <= end_date
        and _region_filter(_row)
        and _stage_filter(_row)
    ]

    _latencies = [_row["latency_ms"] for _row in filtered_events]
    _bytes = [_row["bytes_out"] for _row in filtered_events if _row["bytes_out"]]
    _errors = [_row for _row in filtered_events if _row["status"] == "error"]

    if _latencies:
        _sorted = sorted(_latencies)
        p95 = _sorted[int(0.95 * (len(_sorted) - 1))]
        avg_latency = round(sum(_latencies) / len(_latencies), 1)
    else:
        p95 = 0
        avg_latency = 0

    avg_bytes = round(sum(_bytes) / len(_bytes), 1) if _bytes else 0

    _day_span = max(1, (end_date - start_date).days + 1)
    throughput = round(len(filtered_events) / _day_span, 1)

    error_rate = round((len(_errors) / max(1, len(filtered_events))) * 100, 2)

    metrics = {
        "total": len(filtered_events),
        "p95": p95,
        "avg_latency": avg_latency,
        "avg_bytes": avg_bytes,
        "throughput": throughput,
        "error_rate": error_rate,
    }

    if show_outliers.value:
        outliers = [
            _row
            for _row in filtered_events
            if _row["latency_ms"] >= latency_threshold.value
        ]
    else:
        outliers = []

    return filtered_events, metrics, outliers, start_date, end_date


@app.cell
def _(metrics, mo, outliers, start_date, end_date):
    stats_panel = mo.hstack(
        [
            mo.stat(metrics["total"], label="Events", caption="Filtered window"),
            mo.stat(metrics["p95"], label="P95 latency", caption="Milliseconds"),
            mo.stat(metrics["throughput"], label="Throughput/day"),
            mo.stat(
                f"{metrics['error_rate']}%",
                label="Error rate",
                caption="Event failures",
                direction="decrease",
            ),
        ],
        widths="equal",
        gap=0.8,
    )

    window_note = mo.md(
        f"Window: **{start_date.isoformat()} → {end_date.isoformat()}**"
    )

    outlier_note = (
        mo.md(f"{len(outliers)} latency outliers detected.").callout(kind="warn")
        if outliers
        else mo.md("No latency outliers detected.").callout(kind="success")
    )

    telemetry_panel = mo.vstack(
        [mo.md("## Live telemetry"), stats_panel, window_note, outlier_note],
        gap=0.6,
    )

    return telemetry_panel


@app.cell
def _(latency_threshold, metrics, mo):
    alerts = []
    if metrics["p95"] > latency_threshold.value:
        alerts.append(
            {
                "severity": "warn",
                "rule": "Latency SLO",
                "message": "P95 latency above threshold",
            }
        )
    if metrics["error_rate"] > 1.5:
        alerts.append(
            {
                "severity": "warn",
                "rule": "Error budget",
                "message": "Error rate above 1.5%",
            }
        )
    if metrics["total"] < 200:
        alerts.append(
            {
                "severity": "info",
                "rule": "Volume",
                "message": "Low event volume in window",
            }
        )

    if not alerts:
        alerts = [
            {
                "severity": "ok",
                "rule": "All checks",
                "message": "SLOs are within target ranges",
            }
        ]

    alert_table = mo.ui.table(alerts, label="Alert rules")
    alert_panel = mo.vstack(
        [mo.md("## Alerts + SLOs"), mo.md("Active thresholds and triggers."), alert_table],
        gap=0.6,
    )
    return alert_panel


@app.cell
def _(filtered_events, mo):
    table_rows = [
        {
            **_row,
            "timestamp": _row["timestamp"].isoformat(timespec="seconds"),
        }
        for _row in filtered_events[:250]
    ]
    table_panel = mo.ui.table(table_rows, label="Event stream (sample)")
    return table_panel


@app.cell
def _(Counter, filtered_events, iu, mo):
    _stage_counts = Counter([_row["stage"] for _row in filtered_events])
    _region_counts = Counter(
        [
            _row["region"] if _row["region"] is not None else "unknown"
            for _row in filtered_events
        ]
    )
    _system_counts = Counter([_row["system"] for _row in filtered_events])
    _type_counts = Counter([_row["event_type"] for _row in filtered_events])

    _total = len(filtered_events)
    _safe_total = max(1, _total)

    def _top(counter):
        return counter.most_common(1)[0][0] if counter else "n/a"

    def _share(counter):
        if not counter or _total == 0:
            return 0
        return round(counter.most_common(1)[0][1] / _safe_total, 2)

    summary_rows = [
        {
            "dimension": "stage",
            "unique": len(_stage_counts),
            "top": _top(_stage_counts),
            "share": _share(_stage_counts),
        },
        {
            "dimension": "region",
            "unique": len(_region_counts),
            "top": _top(_region_counts),
            "share": _share(_region_counts),
        },
        {
            "dimension": "system",
            "unique": len(_system_counts),
            "top": _top(_system_counts),
            "share": _share(_system_counts),
        },
        {
            "dimension": "event_type",
            "unique": len(_type_counts),
            "top": _top(_type_counts),
            "share": _share(_type_counts),
        },
    ]

    summary_table = mo.ui.table(summary_rows, label="Distribution summary")

    if iu.find_spec("altair") is None or iu.find_spec("pandas") is None:
        profile_chart = mo.md(
            "Install `pandas` + `altair` for distribution charts."
        ).callout(kind="info")
    else:
        import altair as _alt
        import pandas as _pd

        _rows = []
        for _dimension, counter in (
            ("stage", _stage_counts),
            ("region", _region_counts),
            ("system", _system_counts),
        ):
            for key, count in counter.items():
                _rows.append({"dimension": _dimension, "key": key, "count": count})

        _df = _pd.DataFrame(_rows)
        _chart = (
            _alt.Chart(_df)
            .mark_bar()
            .encode(
                x="count:Q",
                y=_alt.Y("key:N", sort="-x"),
                color="dimension:N",
                tooltip=["dimension", "key", "count"],
            )
            .properties(height=260)
        )
        profile_chart = mo.ui.altair_chart(_chart)

    profiling_panel = mo.vstack(
        [
            mo.md("## Profiling"),
            mo.md("High-level distribution checks across key dimensions."),
            summary_table,
            profile_chart,
        ],
        gap=0.6,
    )
    return profiling_panel


@app.cell
def _(Counter, filtered_events, mo):
    _missing_region = sum(1 for _row in filtered_events if _row["region"] is None)
    _missing_bytes = sum(1 for _row in filtered_events if _row["bytes_out"] is None)
    _dup_counts = Counter([_row["event_id"] for _row in filtered_events])
    _dups = sum(1 for count in _dup_counts.values() if count > 1)

    quality_rows = [
        {
            "check": "Missing region",
            "value": _missing_region,
            "status": "warn" if _missing_region else "ok",
        },
        {
            "check": "Missing bytes_out",
            "value": _missing_bytes,
            "status": "warn" if _missing_bytes else "ok",
        },
        {
            "check": "Duplicate event_id",
            "value": _dups,
            "status": "warn" if _dups else "ok",
        },
    ]

    quality_table = mo.ui.table(quality_rows, label="Quality checks")
    quality_panel = mo.vstack(
        [
            mo.md("## Data quality"),
            mo.md("Automated checks for completeness and deduping."),
            quality_table,
        ],
        gap=0.6,
    )
    return quality_panel


@app.cell
def _(mo):
    schema = {
        "event_id": "string",
        "timestamp": "datetime",
        "region": "string | null",
        "stage": "string",
        "system": "string",
        "event_type": "string",
        "latency_ms": "int",
        "bytes_out": "int | null",
        "status": "ok | error",
    }

    schema_panel = mo.vstack(
        [
            mo.md("## Schema + contract"),
            mo.md("A lightweight data contract for downstream consumers."),
            mo.tree(schema, label="Schema"),
        ],
        gap=0.6,
    )
    return schema_panel


@app.cell
def _(filtered_events, iu, mo):
    if iu.find_spec("pandas") is None:
        df = None
        dataframe_panel = mo.md(
            "Install `pandas` to enable the dataframe explorer."
        ).callout(kind="warn")
        explorer_panel = mo.md(
            "Data explorer requires `pandas`."
        ).callout(kind="neutral")
    else:
        import pandas as pd

        df = pd.DataFrame(filtered_events)
        dataframe_panel = mo.ui.dataframe(df, page_size=8)
        explorer_panel = mo.ui.data_explorer(
            df, x="timestamp", y="latency_ms", color="stage"
        )
    return df, dataframe_panel, explorer_panel


@app.cell
def _(df, iu, mo):
    if df is None or iu.find_spec("altair") is None:
        chart_panel = mo.md(
            "Install `altair` to unlock interactive charts."
        ).callout(kind="info")
    else:
        import altair as alt

        _chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x="timestamp:T",
                y="latency_ms:Q",
                color="stage:N",
                tooltip=["event_id", "system", "latency_ms", "region"],
            )
            .properties(height=280)
        )
        chart_panel = mo.ui.altair_chart(_chart)
    return chart_panel


@app.cell
def _(filtered_events, math, mo):
    _rows = []
    for _row in filtered_events[:20]:
        _bytes = _row["bytes_out"] or 0
        payload_kb = round(_bytes / 1024, 2)
        latency_score = round(math.log(_row["latency_ms"] + 1), 3)
        _throughput = round((payload_kb / max(1, _row["latency_ms"])) * 1000, 3)
        error_flag = 1 if _row["status"] == "error" else 0
        quality_flag = 1 if (_row["region"] is None or _row["bytes_out"] is None) else 0
        _rows.append(
            {
                "event_id": _row["event_id"],
                "latency_ms": _row["latency_ms"],
                "payload_kb": payload_kb,
                "latency_score": latency_score,
                "throughput": _throughput,
                "error_flag": error_flag,
                "quality_flag": quality_flag,
            }
        )

    formula = mo.md(
        """
```text
latency_score = log(latency_ms + 1)
throughput = (payload_kb / latency_ms) * 1000
quality_flag = missing(region) or missing(bytes_out)
```
"""
    )
    feature_table = mo.ui.table(_rows, label="Feature preview")
    feature_panel = mo.vstack(
        [
            mo.md("<a id='features'></a>"),
            mo.md("## Feature engineering"),
            mo.md("Derived signals used for anomaly detection and modeling."),
            formula,
            feature_table,
        ],
        gap=0.6,
    )
    return feature_panel


@app.cell
def _(mo):
    model_version = mo.ui.dropdown(
        options=["v1.2", "v1.3", "v2.0"], value="v1.3", label="Model version"
    )
    decision_threshold = mo.ui.slider(
        0.1, 0.9, value=0.55, step=0.01, label="Decision threshold", show_value=True
    )
    rescore = mo.ui.run_button(label="Rescore predictions", kind="success")
    model_controls = mo.vstack(
        [
            mo.md("### Model controls"),
            model_version,
            decision_threshold,
            rescore,
        ],
        gap=0.4,
    )
    return decision_threshold, model_controls, model_version, rescore


@app.cell
def _(
    decision_threshold,
    filtered_events,
    latency_threshold,
    model_controls,
    model_version,
    mo,
    random,
    rescore,
):
    _ = rescore.value
    _rng = random.Random(rescore.value + len(filtered_events))
    tp = fp = tn = fn = 0

    for _row in filtered_events:
        _label = 1 if (
            _row["status"] == "error" or _row["latency_ms"] >= latency_threshold.value
        ) else 0
        base = 0.18 + (_row["latency_ms"] / 1200) + (
            0.35 if _row["status"] == "error" else 0
        )
        score = min(0.99, max(0.01, base + _rng.uniform(-0.08, 0.08)))
        pred = 1 if score >= decision_threshold.value else 0

        if _label == 1 and pred == 1:
            tp += 1
        elif _label == 0 and pred == 1:
            fp += 1
        elif _label == 0 and pred == 0:
            tn += 1
        else:
            fn += 1

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = (2 * precision * recall) / max(1e-6, precision + recall)
    accuracy = (tp + tn) / max(1, tp + tn + fp + fn)

    model_stats_panel = mo.hstack(
        [
            mo.stat(f"{precision:.2f}", label="Precision"),
            mo.stat(f"{recall:.2f}", label="Recall"),
            mo.stat(f"{f1:.2f}", label="F1"),
            mo.stat(f"{accuracy:.2f}", label="Accuracy"),
        ],
        widths="equal",
        gap=0.6,
    )

    confusion_rows = [
        {"actual": "Positive", "pred_positive": tp, "pred_negative": fn},
        {"actual": "Negative", "pred_positive": fp, "pred_negative": tn},
    ]
    confusion_table = mo.ui.table(confusion_rows, label="Confusion matrix")

    model_panel = mo.vstack(
        [
            mo.md("## Model monitor"),
            mo.md(f"Current model: **{model_version.value}**"),
            model_controls,
            model_stats_panel,
            confusion_table,
        ],
        gap=0.6,
    )
    return model_panel


@app.cell
def _(mo):
    sql_query = mo.ui.text_area(
        value=(
            "SELECT stage, region, COUNT(*) AS events, "
            "ROUND(AVG(latency_ms), 1) AS avg_latency\n"
            "FROM events\n"
            "WHERE status = 'ok'\n"
            "GROUP BY stage, region\n"
            "ORDER BY avg_latency DESC;"
        ),
        label="SQL query",
        rows=6,
    )
    run_sql = mo.ui.run_button(label="Run SQL")
    return run_sql, sql_query


@app.cell
def _(filtered_events, mo, run_sql, sql_query, sqlite3):
    _ = run_sql.value

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE events (
            event_id TEXT,
            timestamp TEXT,
            region TEXT,
            stage TEXT,
            system TEXT,
            event_type TEXT,
            latency_ms INTEGER,
            bytes_out INTEGER,
            status TEXT
        )
        """
    )
    cur.executemany(
        """
        INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                _row["event_id"],
                _row["timestamp"].isoformat(timespec="seconds"),
                _row["region"],
                _row["stage"],
                _row["system"],
                _row["event_type"],
                _row["latency_ms"],
                _row["bytes_out"],
                _row["status"],
            )
            for _row in filtered_events
        ],
    )
    conn.commit()

    try:
        cur.execute(sql_query.value)
        columns = [col[0] for col in cur.description] if cur.description else []
        rows = cur.fetchmany(50)
        sql_rows = [dict(zip(columns, _row)) for _row in rows]
        sql_result = mo.ui.table(sql_rows, label="SQL results")
    except Exception as exc:  # noqa: BLE001
        sql_result = mo.md(f"SQL error: `{exc}`").callout(kind="danger")
    finally:
        conn.close()

    sql_panel = mo.vstack(
        [
            mo.md("<a id='sql'></a>"),
            mo.md("## SQL playground"),
            mo.md("Run ad-hoc queries on the in-memory events table."),
            mo.hstack([sql_query, run_sql], widths=[5, 1], gap=0.6),
            sql_result,
        ],
        gap=0.6,
    )
    return sql_panel


@app.cell
def _(mo):
    diagram = mo.mermaid(
        """
        flowchart LR
            A[Ingest] --> B[Validate]
            B --> C[Transform]
            C --> D[Store]
            D --> E[Serve]
            C --> F[Feature Store]
            F --> G[Model Training]
            G --> H[Model Registry]
        """
    )

    slides = mo.carousel(
        [
            mo.md("### Data Engineer\nOrchestrate reliable pipelines."),
            mo.md("### Data Scientist\nExplore, model, iterate quickly."),
            mo.md("### ML Engineer\nShip models with observability."),
        ]
    )

    accordion = mo.accordion(
        {
            "SLOs": mo.md("Latency P95 < 500 ms, error rate < 1%."),
            "Backfills": mo.md("Daily backfill for late-arriving events."),
            "Lineage": mo.md("Track from ingestion to feature store.")
        }
    )

    diagram_panel = mo.vstack(
        [
            mo.md("## Pipeline view"),
            diagram,
            slides,
            accordion,
        ],
        gap=0.8,
    )
    return diagram_panel


@app.cell
def _(mo):
    warehouse = mo.ui.dropdown(
        options=["snowflake", "bigquery", "redshift", "databricks"],
        value="snowflake",
        label="Warehouse",
    )
    schedule = mo.ui.dropdown(
        options=["hourly", "daily", "weekly"], value="hourly", label="Schedule"
    )
    batch_size = mo.ui.slider(1000, 20000, step=1000, value=8000, label="Batch size")
    parallelism = mo.ui.slider(1, 16, value=4, label="Parallelism", show_value=True)
    retry_policy = mo.ui.dropdown(
        options=["none", "linear", "exponential"], value="exponential", label="Retry policy"
    )
    enable_lineage = mo.ui.switch(value=True, label="Lineage tracking")

    config_controls = mo.vstack(
        [
            mo.md("### Config builder"),
            warehouse,
            schedule,
            mo.hstack([batch_size, parallelism], widths="equal"),
            mo.hstack([retry_policy, enable_lineage], widths="equal"),
        ],
        gap=0.4,
    )
    return (
        batch_size,
        config_controls,
        enable_lineage,
        parallelism,
        retry_policy,
        schedule,
        warehouse,
    )


@app.cell
def _(
    batch_size,
    config_controls,
    enable_lineage,
    mo,
    parallelism,
    retry_policy,
    schedule,
    warehouse,
):
    config = f"""pipeline:
  schedule: {schedule.value}
  batch_size: {batch_size.value}
  parallelism: {parallelism.value}
  retry_policy: {retry_policy.value}
  lineage: {str(enable_lineage.value).lower()}
warehouse: {warehouse.value}
"""
    config_panel = mo.vstack(
        [
            mo.md("<a id='config'></a>"),
            mo.md("## Pipeline config"),
            mo.md("Live config generated from the builder."),
            config_controls,
            mo.md(f"```yaml\n{config}\n```"),
        ],
        gap=0.6,
    )
    return config_panel


@app.cell
def _(filtered_events, mo, textwrap):
    export_rows = filtered_events[:500]
    header = "event_id,timestamp,region,stage,system,event_type,latency_ms,bytes_out,status"
    lines = [header]
    for _row in export_rows:
        lines.append(
            ",".join(
                [
                    _row["event_id"],
                    _row["timestamp"].isoformat(timespec="seconds"),
                    _row["region"] or "",
                    _row["stage"],
                    _row["system"],
                    _row["event_type"],
                    str(_row["latency_ms"]),
                    "" if _row["bytes_out"] is None else str(_row["bytes_out"]),
                    _row["status"],
                ]
            )
        )

    csv_payload = "\n".join(lines).encode("utf-8")
    download_panel = mo.download(
        data=csv_payload,
        filename="events_sample.csv",
        mimetype="text/csv",
        label="Download sample CSV",
    )
    return download_panel


@app.cell
def _(mo):
    file_upload = mo.ui.file(kind="area", label="Drop a CSV to inspect")
    return file_upload


@app.cell
def _(download_panel, file_upload, mo):
    if file_upload.value:
        _info = file_upload.value
        file_meta = mo.md(
            f"Uploaded: `{_info.name}` ({_info.size} bytes)"
        ).callout(kind="success")
    else:
        file_meta = mo.md("No file uploaded yet.").callout(kind="neutral")

    exports_panel = mo.vstack(
        [
            mo.md("## Ops + exports"),
            mo.md("Export a sample dataset or inspect an uploaded file."),
            download_panel,
            file_upload,
            file_meta,
        ],
        gap=0.6,
    )
    return exports_panel


@app.cell
def _(mo):
    status_run = mo.ui.run_button(label="Run pipeline sync")
    status_panel = mo.vstack(
        [
            mo.md("## Status monitor"),
            mo.md("Trigger a simulated sync to showcase async status."),
            status_run,
        ],
        gap=0.6,
    )
    return status_panel, status_run


@app.cell
async def _(asyncio, mo, status_run):
    _clicks = status_run.value
    if _clicks > 0:
        for _ in mo.status.progress_bar(
            range(14),
            title="Backfilling partitions",
            subtitle="Streaming late data",
            show_eta=True,
        ):
            await asyncio.sleep(0.08)
        with mo.status.spinner(title="Publishing", subtitle="Sealing outputs") as spinner:
            await asyncio.sleep(0.4)
            spinner.update("Complete")
            await asyncio.sleep(0.2)
    return


@app.cell
def _(
    alert_panel,
    chart_panel,
    config_panel,
    control_panel,
    dataframe_panel,
    diagram_panel,
    explorer_panel,
    exports_panel,
    feature_panel,
    model_panel,
    mo,
    profiling_panel,
    quality_panel,
    schema_panel,
    sql_panel,
    status_panel,
    table_panel,
    telemetry_panel,
):
    overview_section = mo.vstack(
        [
            telemetry_panel,
            alert_panel,
            control_panel,
        ],
        gap=1.0,
    )

    data_section = mo.vstack(
        [
            mo.md("<a id='data'></a>"),
            mo.md("## Event data"),
            table_panel,
            profiling_panel,
            mo.md("## Dataframe + explorer"),
            dataframe_panel,
            explorer_panel,
            mo.md("## Charts"),
            chart_panel,
        ],
        gap=1.0,
    )

    quality_section = mo.vstack(
        [
            mo.md("<a id='quality'></a>"),
            quality_panel,
            schema_panel,
        ],
        gap=1.0,
    )

    ml_section = mo.vstack(
        [
            mo.md("<a id='ml'></a>"),
            mo.md("## ML"),
            feature_panel,
            model_panel,
        ],
        gap=1.0,
    )

    pipeline_section = mo.vstack(
        [
            mo.md("<a id='pipelines'></a>"),
            diagram_panel,
            config_panel,
        ],
        gap=1.0,
    )

    ops_section = mo.vstack(
        [
            mo.md("<a id='ops'></a>"),
            status_panel,
            exports_panel,
        ],
        gap=1.0,
    )

    full_page = mo.vstack(
        [
            overview_section,
            data_section,
            quality_section,
            ml_section,
            sql_panel,
            pipeline_section,
            ops_section,
        ],
        gap=1.6,
    )
    full_page
    return (full_page,)


@app.cell
def _(mo):
    nav = mo.nav_menu(
        {
            "#overview": f"{mo.icon('lucide:layout-dashboard')} Overview",
            "#data": f"{mo.icon('lucide:table')} Data",
            "#quality": f"{mo.icon('lucide:shield-check')} Quality",
            "#ml": f"{mo.icon('lucide:brain')} ML",
            "#sql": f"{mo.icon('lucide:terminal')} SQL",
            "#pipelines": f"{mo.icon('lucide:git-branch')} Pipelines",
            "#config": f"{mo.icon('lucide:sliders')} Config",
            "#ops": f"{mo.icon('lucide:activity')} Ops",
            "Links": {
                "https://docs.marimo.io": "marimo docs",
                "https://marimo.io": "marimo.io",
            },
        },
        orientation="vertical",
    )

    sidebar = mo.sidebar(
        mo.vstack(
            [
                mo.md("## Navigation"),
                nav,
                mo.outline(label="On this page"),
                mo.md("Run this notebook as an app or in edit mode."),
            ],
            gap=0.8,
        ),
        footer=mo.md("Data Ops Control Room"),
        width="240px",
    )

    sidebar
    return nav, sidebar


if __name__ == "__main__":
    app.run()
