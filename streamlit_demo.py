"""Streamlit UI for the 3-tier Parquet + FastAPI demo.

Run with:
    streamlit run streamlit_demo.py
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import altair as alt
import pandas as pd
import requests

# Fallback compatibility for environments with protobuf/streamlit mismatch.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
import streamlit as st

st.set_page_config(
    page_title="Sales Flow Studio",
    page_icon="SF",
    layout="wide",
)

LIGHT_THEME: dict[str, str] = {
    "bg_base": "#ffffff",
    "bg_a": "rgba(168, 197, 255, 0.22)",
    "bg_b": "rgba(194, 241, 216, 0.2)",
    "bg_c": "rgba(253, 245, 191, 0.2)",
    "hero_a": "rgba(173, 200, 255, 0.52)",
    "hero_b": "rgba(205, 244, 223, 0.5)",
    "hero_c": "rgba(255, 248, 204, 0.5)",
    "surface": "rgba(255, 255, 255, 0.84)",
    "surface_strong": "rgba(255, 255, 255, 0.96)",
    "text": "#0f172a",
    "muted": "#334155",
    "border": "rgba(15, 23, 42, 0.14)",
    "accent": "#4f6de6",
    "accent_soft": "#dfe7ff",
    "accent_warm": "#7f99ff",
    "chart_text": "#0f172a",
    "chart_grid": "rgba(15, 23, 42, 0.24)",
    "chart_bg": "rgba(255, 255, 255, 0.98)",
    "heat_low": "#eef2ff",
    "heat_high": "#8ea2ff",
    "shadow": "0 10px 28px rgba(15, 23, 42, 0.1)",
    "input_bg": "rgba(255, 255, 255, 0.96)",
    "input_border": "rgba(15, 23, 42, 0.18)",
    "button_bg": "#e8eeff",
    "button_border": "#a8b8f6",
    "button_text": "#2443a8",
    "chip_bg": "#eaf1ff",
    "chip_text": "#1d2f64",
    "table_bg": "#ffffff",
    "table_header_bg": "#eef3ff",
    "table_header_text": "#0f172a",
    "table_text": "#111827",
    "table_border": "rgba(15, 23, 42, 0.12)",
    "chart_c1": "#4f6de6",
    "chart_c2": "#45b69c",
    "chart_c3": "#7f99ff",
    "chart_c4": "#9a86e8",
}

DARK_THEME: dict[str, str] = {
    "bg_base": "#0b0d12",
    "bg_a": "rgba(136, 154, 245, 0.16)",
    "bg_b": "rgba(119, 185, 165, 0.12)",
    "bg_c": "rgba(182, 173, 122, 0.09)",
    "hero_a": "rgba(77, 95, 166, 0.46)",
    "hero_b": "rgba(64, 114, 99, 0.36)",
    "hero_c": "rgba(108, 102, 72, 0.26)",
    "surface": "rgba(15, 18, 26, 0.86)",
    "surface_strong": "rgba(20, 24, 34, 0.95)",
    "text": "#f8fafc",
    "muted": "#cbd5e1",
    "border": "rgba(226, 232, 240, 0.16)",
    "accent": "#9fb2ff",
    "accent_soft": "#26345d",
    "accent_warm": "#7fa1ff",
    "chart_text": "#e2e8f0",
    "chart_grid": "rgba(148, 163, 184, 0.35)",
    "chart_bg": "rgba(17, 22, 34, 0.96)",
    "heat_low": "#1f2b4d",
    "heat_high": "#9db2ff",
    "shadow": "0 20px 45px rgba(0, 0, 0, 0.45)",
    "input_bg": "rgba(22, 27, 39, 0.96)",
    "input_border": "rgba(148, 163, 184, 0.34)",
    "button_bg": "#27345d",
    "button_border": "#4f66ad",
    "button_text": "#e8eeff",
    "chip_bg": "#28365e",
    "chip_text": "#dce6ff",
    "table_bg": "#151a27",
    "table_header_bg": "#1f283d",
    "table_header_text": "#e2e8f0",
    "table_text": "#e5e7eb",
    "table_border": "rgba(148, 163, 184, 0.2)",
    "chart_c1": "#84a0ff",
    "chart_c2": "#5fd0b3",
    "chart_c3": "#a4b7ff",
    "chart_c4": "#b19df0",
}


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://127.0.0.1:8000"


def inject_theme(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

          :root {{
            --bg-base: {theme['bg_base']};
            --bg-a: {theme['bg_a']};
            --bg-b: {theme['bg_b']};
            --bg-c: {theme['bg_c']};
            --hero-a: {theme['hero_a']};
            --hero-b: {theme['hero_b']};
            --hero-c: {theme['hero_c']};
            --surface: {theme['surface']};
            --surface-strong: {theme['surface_strong']};
            --text: {theme['text']};
            --muted: {theme['muted']};
            --border: {theme['border']};
            --accent: {theme['accent']};
            --accent-soft: {theme['accent_soft']};
            --accent-warm: {theme['accent_warm']};
            --chart-text: {theme['chart_text']};
            --chart-grid: {theme['chart_grid']};
            --chart-bg: {theme['chart_bg']};
            --shadow: {theme['shadow']};
            --input-bg: {theme['input_bg']};
            --input-border: {theme['input_border']};
            --button-bg: {theme['button_bg']};
            --button-border: {theme['button_border']};
            --button-text: {theme['button_text']};
            --chip-bg: {theme['chip_bg']};
            --chip-text: {theme['chip_text']};
            --table-bg: {theme['table_bg']};
            --table-header-bg: {theme['table_header_bg']};
            --table-header-text: {theme['table_header_text']};
            --table-text: {theme['table_text']};
            --table-border: {theme['table_border']};
          }}

          html, body, [class*="css"] {{
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
            color: var(--text);
            font-size: 16px;
            line-height: 1.45;
          }}

          [data-testid="stMarkdownContainer"] p,
          [data-testid="stMarkdownContainer"] li,
          [data-testid="stMarkdownContainer"] span {{
            color: var(--text);
          }}

          [data-testid="stCaptionContainer"] p {{
            color: var(--muted) !important;
          }}

          .stApp {{
            color: var(--text);
            background:
              radial-gradient(1200px 700px at 0% -10%, var(--bg-a), transparent 56%),
              radial-gradient(900px 540px at 100% 0%, var(--bg-b), transparent 52%),
              radial-gradient(1000px 700px at 50% 110%, var(--bg-c), transparent 60%),
              linear-gradient(165deg, var(--bg-base) 0%, var(--bg-base) 100%);
          }}

          [data-testid="stSidebar"] > div:first-child {{
            background: var(--surface);
            border-right: 1px solid var(--border);
          }}

          [data-testid="stSidebar"] * {{
            color: var(--text) !important;
          }}

          [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: var(--muted) !important;
          }}

          [data-testid="stWidgetLabel"] p {{
            color: var(--text) !important;
            font-size: 0.93rem;
            font-weight: 600;
            letter-spacing: 0.01em;
          }}

          [data-testid="stHeader"] {{
            background: transparent;
          }}

          .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2.3rem;
          }}

          h1, h2, h3 {{
            font-family: "Space Grotesk", "Manrope", sans-serif;
            color: var(--text);
          }}

          .hero-card {{
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1rem 1.25rem;
            background:
              linear-gradient(125deg, var(--hero-a) 0%, var(--hero-b) 55%, var(--hero-c) 100%),
              linear-gradient(130deg, var(--surface-strong), var(--surface));
            box-shadow: var(--shadow);
            backdrop-filter: blur(8px);
            animation: fadeInUp 420ms ease;
          }}

          .hero-title {{
            margin: 0;
            font-size: 2.05rem;
            line-height: 1.1;
            letter-spacing: 0.01em;
          }}

          .metric-card {{
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.8rem 0.95rem;
            background: linear-gradient(135deg, var(--surface-strong), var(--surface));
            box-shadow: var(--shadow);
            animation: fadeInUp 460ms ease;
          }}

          .metric-label {{
            margin: 0;
            color: var(--muted);
            font-size: 0.8rem;
            letter-spacing: 0.03em;
            text-transform: uppercase;
          }}

          .metric-value {{
            margin: 0.2rem 0 0;
            color: var(--text);
            font-size: 1.42rem;
            font-weight: 800;
            line-height: 1.1;
          }}

          .metric-sub {{
            margin-top: 0.12rem;
            color: var(--muted);
            font-size: 0.78rem;
          }}

          [data-testid="stTabs"] [role="tablist"] {{
            border-bottom: none !important;
            gap: 0.55rem;
            padding-bottom: 0.25rem;
          }}

          .stTabs [data-testid="stMarkdownContainer"] p {{
            font-size: 1.04rem;
            font-weight: 700;
            line-height: 1;
            white-space: nowrap;
          }}

          [data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
            display: none !important;
            opacity: 0 !important;
          }}

          [data-testid="stTabs"] button[role="tab"]::after {{
            display: none !important;
          }}

          [data-testid="stTabs"] button[role="tab"] {{
            color: var(--text) !important;
            min-height: 3rem !important;
            min-width: 10rem !important;
            padding: 0.38rem 1.25rem !important;
            border-bottom: none !important;
            box-shadow: none !important;
            border-radius: 999px !important;
            border: 1px solid var(--border) !important;
            background: linear-gradient(135deg, var(--surface-strong), var(--surface)) !important;
            margin: 0 !important;
          }}

          [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: var(--text) !important;
            border-color: var(--accent) !important;
            background: linear-gradient(135deg, var(--accent-soft), var(--surface-strong)) !important;
            box-shadow: inset 0 0 0 1px var(--accent) !important;
          }}

          [data-baseweb="input"] input,
          [data-baseweb="base-input"] input,
          [data-baseweb="textarea"] textarea {{
            background: var(--input-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--input-border) !important;
          }}

          [data-baseweb="select"] > div,
          [data-baseweb="popover"] [role="listbox"] {{
            background: var(--input-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--input-border) !important;
          }}

          [data-baseweb="tag"] {{
            background: var(--chip-bg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
          }}

          [data-baseweb="tag"] * {{
            color: var(--chip-text) !important;
            font-weight: 600 !important;
          }}

          [data-baseweb="popover"] [aria-selected="true"] {{
            background: var(--accent-soft) !important;
            color: var(--text) !important;
          }}

          .stButton > button,
          .stFormSubmitButton > button {{
            background: linear-gradient(135deg, var(--button-bg), var(--accent-soft)) !important;
            color: var(--button-text) !important;
            border: 1px solid var(--button-border) !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em;
            border-radius: 13px !important;
            min-height: 2.7rem !important;
            box-shadow: 0 6px 18px rgba(79, 109, 230, 0.18);
          }}

          .stButton > button:hover,
          .stFormSubmitButton > button:hover {{
            filter: brightness(1.02);
            border-color: var(--button-border);
            transform: translateY(-1px);
          }}

          .stButton > button:focus,
          .stFormSubmitButton > button:focus {{
            outline: none;
            box-shadow: 0 0 0 0.18rem var(--accent-soft);
          }}

          [data-testid="stExpander"] {{
            border: 1px solid var(--border) !important;
            border-radius: 16px !important;
            background: linear-gradient(135deg, var(--surface-strong), var(--surface)) !important;
            box-shadow: var(--shadow);
            overflow: hidden;
          }}

          [data-testid="stExpander"] > details {{
            border: none !important;
            background: transparent !important;
          }}

          [data-testid="stExpander"] > details > summary {{
            color: var(--text) !important;
            font-weight: 700 !important;
            font-size: 1.04rem !important;
            background: transparent !important;
          }}

          [data-testid="stExpander"] > details > summary:hover {{
            background: transparent !important;
          }}

          [data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {{
            color: var(--text) !important;
          }}

          [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {{
            color: var(--text) !important;
          }}

          [data-baseweb="slider"] [role="slider"] {{
            border-color: var(--accent);
            background: var(--accent);
          }}

          [data-baseweb="slider"] [data-testid="stTickBarMin"] {{
            background: var(--accent);
          }}

          [data-testid="stVegaLiteChart"] {{
            background: var(--chart-bg) !important;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.35rem 0.45rem 0.2rem 0.45rem;
            box-shadow: var(--shadow);
          }}

          [data-testid="stVegaLiteChart"] svg text {{
            fill: var(--chart-text) !important;
          }}

          [data-testid="stVegaLiteChart"] svg .domain,
          [data-testid="stVegaLiteChart"] svg .tick line,
          [data-testid="stVegaLiteChart"] svg .grid line {{
            stroke: var(--chart-grid) !important;
          }}

          [data-testid="stTable"] table {{
            background: var(--table-bg) !important;
            color: var(--table-text) !important;
            border: 1px solid var(--table-border) !important;
            border-radius: 12px;
            overflow: hidden;
          }}

          [data-testid="stTable"] th {{
            background: var(--table-header-bg) !important;
            color: var(--table-header-text) !important;
            font-weight: 700 !important;
          }}

          [data-testid="stTable"] td {{
            color: var(--table-text) !important;
            border-top: 1px solid var(--table-border) !important;
          }}

          [data-testid="stDataFrame"] div[role="grid"] {{
            background: var(--table-bg) !important;
            color: var(--table-text) !important;
          }}

          @keyframes fadeInUp {{
            from {{
              transform: translateY(7px);
              opacity: 0;
            }}
            to {{
              transform: translateY(0);
              opacity: 1;
            }}
          }}

          @media (max-width: 900px) {{
            .hero-title {{
              font-size: 1.55rem;
            }}
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _safe_get(url: str, params: list[tuple[str, Any]] | None = None) -> Any:
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    return response.json()


def _safe_post(url: str, payload: dict[str, Any]) -> Any:
    response = requests.post(url, json=payload, timeout=12)
    response.raise_for_status()
    return response.json()


def _safe_put(url: str, payload: dict[str, Any]) -> Any:
    response = requests.put(url, json=payload, timeout=12)
    response.raise_for_status()
    return response.json()


def fetch_options(api_base: str) -> dict[str, list[str]]:
    try:
        return _safe_get(f"{api_base}/meta/options")
    except requests.RequestException:
        return {"regions": [], "categories": [], "statuses": []}


def fetch_records(api_base: str, params: list[tuple[str, Any]]) -> pd.DataFrame:
    records = _safe_get(f"{api_base}/records", params=params)
    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for column in ["quantity", "unit_price", "discount", "revenue"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def _axis(
    theme: dict[str, str],
    *,
    title: str | None = None,
    fmt: str | None = None,
    label_angle: int = 0,
    grid: bool = True,
    tick_count: Any | None = None,
) -> alt.Axis:
    kwargs: dict[str, Any] = {
        "title": title,
        "labelColor": theme["chart_text"],
        "titleColor": theme["chart_text"],
        "domainColor": theme["chart_grid"],
        "tickColor": theme["chart_grid"],
        "gridColor": theme["chart_grid"],
        "labelFont": "Manrope",
        "titleFont": "Manrope",
        "labelFontSize": 14,
        "titleFontSize": 14,
        "labelFontWeight": 600,
        "titleFontWeight": 700,
        "labelOpacity": 1,
        "titleOpacity": 1,
        "labelAngle": label_angle,
        "grid": grid,
    }
    if fmt is not None:
        kwargs["format"] = fmt
    if tick_count is not None:
        kwargs["tickCount"] = tick_count
    return alt.Axis(**kwargs)


def _apply_chart_style(chart: alt.Chart, theme: dict[str, str]) -> alt.Chart:
    return (
        chart.configure_view(
            fill=theme["chart_bg"],
            stroke=theme["border"],
            strokeWidth=1,
        )
        .configure_axis(
            labelColor=theme["chart_text"],
            titleColor=theme["chart_text"],
            domainColor=theme["chart_grid"],
            tickColor=theme["chart_grid"],
            gridColor=theme["chart_grid"],
            gridOpacity=0.68,
            labelFont="Manrope",
            titleFont="Manrope",
            labelFontSize=14,
            titleFontSize=14,
            labelFontWeight=600,
            titleFontWeight=700,
        )
        .configure_title(
            color=theme["chart_text"],
            font="Space Grotesk",
            fontSize=22,
            fontWeight=700,
            anchor="start",
            offset=16,
        )
        .configure_legend(
            orient="top",
            direction="horizontal",
            titleColor=theme["chart_text"],
            labelColor=theme["chart_text"],
            labelFont="Manrope",
            titleFont="Manrope",
            labelFontSize=12,
            titleFontSize=13,
            symbolSize=120,
        )
        .configure(background="transparent")
    )


def build_revenue_flow_chart(df: pd.DataFrame, theme: dict[str, str]) -> alt.Chart:
    monthly_category = (
        df.assign(month=df["order_date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "category"], as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("record_id", "count"))
    )
    if monthly_category.empty:
        return _apply_chart_style(alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line(), theme)

    top_categories = (
        monthly_category.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)["category"]
        .head(4)
        .tolist()
    )
    plot_df = monthly_category[monthly_category["category"].isin(top_categories)].copy()
    month_range = pd.date_range(plot_df["month"].min(), plot_df["month"].max(), freq="MS")
    full_grid = pd.MultiIndex.from_product([month_range, top_categories], names=["month", "category"]).to_frame(
        index=False
    )
    plot_df = (
        full_grid.merge(plot_df, on=["month", "category"], how="left")
        .fillna({"revenue": 0.0, "orders": 0.0})
        .sort_values(["category", "month"])
    )
    plot_df["orders"] = plot_df["orders"].astype(int)

    monthly_total = (
        df.assign(month=df["order_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(total_revenue=("revenue", "sum"))
        .sort_values("month")
    )
    monthly_total["rolling_avg"] = monthly_total["total_revenue"].rolling(window=3, min_periods=1).mean()

    x_axis = _axis(
        theme,
        title="Month",
        label_angle=0,
        grid=False,
        tick_count=alt.TimeIntervalStep(unit="month", step=1),
        fmt="%b %Y",
    )
    y_axis = _axis(theme, title="Revenue", fmt=",.0f", grid=True)
    palette = [theme["chart_c1"], theme["chart_c2"], theme["chart_c3"], theme["chart_c4"]][: len(top_categories)]
    color_scale = alt.Scale(domain=top_categories, range=palette)

    lines = (
        alt.Chart(plot_df)
        .mark_line(strokeWidth=3.1, interpolate="monotone")
        .encode(
            x=alt.X("month:T", axis=x_axis),
            y=alt.Y("revenue:Q", axis=y_axis),
            color=alt.Color("category:N", title="Category", scale=color_scale),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%b %Y"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("revenue:Q", title="Revenue", format=",.2f"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
    )

    points = (
        alt.Chart(plot_df)
        .mark_circle(size=64, stroke=theme["chart_bg"], strokeWidth=1.4)
        .encode(
            x=alt.X("month:T", axis=x_axis),
            y=alt.Y("revenue:Q", axis=y_axis),
            color=alt.Color("category:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%b %Y"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("revenue:Q", title="Revenue", format=",.2f"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
    )

    trend = (
        alt.Chart(monthly_total)
        .mark_line(strokeDash=[8, 5], strokeWidth=2.2, color=theme["accent_warm"], opacity=0.9)
        .encode(
            x=alt.X("month:T", axis=x_axis),
            y=alt.Y("rolling_avg:Q", axis=y_axis),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%b %Y"),
                alt.Tooltip("rolling_avg:Q", title="3-Month Avg", format=",.2f"),
            ],
        )
    )

    last_points = plot_df.sort_values("month").groupby("category", as_index=False).tail(1)
    labels = (
        alt.Chart(last_points)
        .mark_text(align="left", dx=8, dy=-6, fontSize=11, fontWeight=700)
        .encode(
            x=alt.X("month:T"),
            y=alt.Y("revenue:Q"),
            text=alt.Text("category:N"),
            color=alt.Color("category:N", scale=color_scale, legend=None),
        )
    )

    chart = alt.layer(trend, lines, points, labels).properties(
        height=390,
        title="Monthly Revenue Trend by Category",
    )
    return _apply_chart_style(chart, theme)


def build_region_category_chart(df: pd.DataFrame, theme: dict[str, str]) -> alt.Chart:
    matrix = (
        df.groupby(["region", "category"], as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("record_id", "count"),
            avg_discount=("discount", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    if matrix.empty:
        return _apply_chart_style(alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_rect(), theme)

    region_order = matrix.groupby("region")["revenue"].sum().sort_values(ascending=False).index.tolist()
    category_order = matrix.groupby("category")["revenue"].sum().sort_values(ascending=False).index.tolist()
    region_totals = (
        matrix.groupby("region", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"))
        .sort_values("revenue", ascending=False)
    )

    x_axis = _axis(theme, title="Region", label_angle=0, grid=False)
    y_axis = _axis(theme, title="Category", label_angle=0, grid=False)

    heat = (
        alt.Chart(matrix)
        .mark_rect(cornerRadius=5)
        .encode(
            x=alt.X("region:N", sort=region_order, axis=x_axis),
            y=alt.Y("category:N", sort=category_order, axis=y_axis),
            color=alt.Color(
                "revenue:Q",
                title="Revenue",
                scale=alt.Scale(range=[theme["heat_low"], theme["heat_high"]]),
            ),
            tooltip=[
                alt.Tooltip("region:N", title="Region"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("revenue:Q", title="Revenue", format=",.2f"),
                alt.Tooltip("orders:Q", title="Orders"),
                alt.Tooltip("avg_discount:Q", title="Avg discount", format=".1%"),
            ],
        )
    )

    bubbles = (
        alt.Chart(matrix)
        .mark_circle(opacity=0.34, stroke=theme["chart_bg"], strokeWidth=1.0, color=theme["accent"])
        .encode(
            x=alt.X("region:N", sort=region_order, axis=x_axis),
            y=alt.Y("category:N", sort=category_order, axis=y_axis),
            size=alt.Size("orders:Q", title="Orders", scale=alt.Scale(range=[120, 1500])),
            tooltip=[
                alt.Tooltip("region:N", title="Region"),
                alt.Tooltip("category:N", title="Category"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
    )

    labels = (
        alt.Chart(matrix)
        .mark_text(fontSize=12, fontWeight=700, color=theme["chart_text"])
        .encode(
            x=alt.X("region:N", sort=region_order, axis=x_axis),
            y=alt.Y("category:N", sort=category_order, axis=y_axis),
            text=alt.Text("revenue:Q", format=".2s"),
        )
    )

    matrix_chart = (heat + bubbles + labels).properties(
        width=700,
        height=330,
        title="Category x Region Performance",
    )

    bar_axis_x = _axis(theme, title="Regional Revenue", fmt=",.0f", grid=True)
    bar_axis_y = _axis(theme, title=None, grid=False)
    region_palette = [theme["chart_c1"], theme["chart_c2"], theme["chart_c3"], theme["chart_c4"]]
    bars = (
        alt.Chart(region_totals)
        .mark_bar(cornerRadius=6)
        .encode(
            y=alt.Y("region:N", sort=region_order, axis=bar_axis_y),
            x=alt.X("revenue:Q", axis=bar_axis_x),
            color=alt.Color(
                "region:N",
                scale=alt.Scale(domain=region_order, range=region_palette[: len(region_order)]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("region:N", title="Region"),
                alt.Tooltip("revenue:Q", title="Revenue", format=",.2f"),
                alt.Tooltip("orders:Q", title="Orders"),
            ],
        )
    )

    bar_labels = (
        alt.Chart(region_totals)
        .mark_text(align="left", dx=6, fontSize=11, fontWeight=700, color=theme["chart_text"])
        .encode(
            y=alt.Y("region:N", sort=region_order, axis=bar_axis_y),
            x=alt.X("revenue:Q", axis=bar_axis_x),
            text=alt.Text("revenue:Q", format=".2s"),
        )
    )

    totals_chart = (bars + bar_labels).properties(
        width=290,
        height=330,
        title="Regional Totals",
    )

    chart = alt.hconcat(matrix_chart, totals_chart, spacing=18)
    return _apply_chart_style(chart, theme)


def render_metric_card(column: Any, label: str, value: str, subtitle: str) -> None:
    column.markdown(
        f"""
        <div class="metric-card">
          <p class="metric-label">{label}</p>
          <p class="metric-value">{value}</p>
          <p class="metric-sub">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("### Display")
    dark_mode = st.toggle(
        "Dark mode",
        value=bool(st.session_state.dark_mode),
        help="Switch between soft pastel day mode and cinematic night mode.",
    )
    st.session_state.dark_mode = dark_mode


theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
inject_theme(theme)

with st.sidebar:
    st.markdown("### Connection")
    api_base_url = st.text_input("FastAPI base URL", value=str(st.session_state.api_base_url)).rstrip("/")
    st.session_state.api_base_url = api_base_url

    if st.button("Check API health", width="stretch"):
        try:
            health = _safe_get(f"{api_base_url}/health")
            st.success(f"API status: {health.get('status', 'ok')}")
        except requests.RequestException as exc:
            st.error(f"Connection failed: {exc}")

    st.caption("Run backend first: uvicorn src.parquet_api:app --reload")

st.markdown(
    """
    <div class="hero-card">
      <h1 class="hero-title">Sales Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

options = fetch_options(api_base_url)

dashboard_tab, records_tab = st.tabs(["Dashboard", "Records"])


with dashboard_tab:
    c1, c2, c3 = st.columns([1.15, 1.15, 1])
    selected_regions = c1.multiselect("Region", options["regions"], default=options["regions"])
    selected_categories = c2.multiselect("Category", options["categories"], default=options["categories"])
    search_text = c3.text_input("Search customer or product")

    default_start = date.today() - timedelta(days=365)
    default_end = date.today()

    d1, d2 = st.columns([1.4, 1])
    date_range = d1.date_input("Date range", value=(default_start, default_end))
    record_limit = int(d2.number_input("Record limit", min_value=50, max_value=2000, value=400, step=50))

    with st.expander("Advanced filters", expanded=False):
        a1, a2, a3 = st.columns(3)
        selected_statuses = a1.multiselect("Status", options["statuses"], default=options["statuses"])
        min_revenue = a2.number_input("Min revenue", min_value=0.0, value=0.0, step=50.0)
        max_revenue = a3.number_input("Max revenue (0 = no cap)", min_value=0.0, value=0.0, step=50.0)

    if isinstance(date_range, (tuple, list)):
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = end_date = date_range[0]
        else:
            start_date, end_date = default_start, default_end
    else:
        start_date = end_date = date_range

    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    params: list[tuple[str, Any]] = [("limit", record_limit)]
    params.extend(("region", value) for value in selected_regions)
    params.extend(("category", value) for value in selected_categories)
    params.extend(("status", value) for value in selected_statuses)
    params.append(("start_date", start_date.isoformat()))
    params.append(("end_date", end_date.isoformat()))

    if min_revenue > 0:
        params.append(("min_revenue", float(min_revenue)))
    if max_revenue > 0:
        params.append(("max_revenue", float(max_revenue)))
    if search_text.strip():
        params.append(("q", search_text.strip()))

    try:
        filtered_df = fetch_records(api_base_url, params)
    except requests.RequestException as exc:
        st.error(f"Could not query records from API: {exc}")
        filtered_df = pd.DataFrame()

    if filtered_df.empty:
        st.info("No records match the current filter set.")
    else:
        total_revenue = float(filtered_df["revenue"].sum())
        avg_order = float(filtered_df["revenue"].mean())

        m1, m2, m3 = st.columns(3)
        render_metric_card(m1, "Rows", f"{len(filtered_df):,}", "Records returned")
        render_metric_card(m2, "Revenue", f"${total_revenue:,.0f}", "Filtered total")
        render_metric_card(m3, "Avg Order", f"${avg_order:,.2f}", "Per record")

        st.altair_chart(build_revenue_flow_chart(filtered_df, theme), width="stretch")
        st.altair_chart(build_region_category_chart(filtered_df, theme), width="stretch")

        with st.expander("View data table", expanded=False):
            table_df = filtered_df.sort_values("order_date", ascending=False).copy()
            table_df["order_date"] = table_df["order_date"].dt.date
            preview = table_df.head(min(len(table_df), 120))
            st.caption(f"Showing {len(preview)} records")
            st.table(preview)


with records_tab:
    with st.expander("Create record", expanded=True):
        with st.form("create_record_form", clear_on_submit=True):
            row1_col1, row1_col2 = st.columns(2)
            order_date = row1_col1.date_input("Order date", value=date.today(), key="create_order_date")
            customer_name = row1_col2.text_input("Customer name", value="", key="create_customer_name")

            row2_col1, row2_col2, row2_col3 = st.columns(3)
            region_default = options["regions"][0] if options["regions"] else "North America"
            category_default = options["categories"][0] if options["categories"] else "Hardware"
            status_default = options["statuses"][0] if options["statuses"] else "completed"

            region = row2_col1.text_input("Region", value=region_default, key="create_region")
            category = row2_col2.text_input("Category", value=category_default, key="create_category")
            status = row2_col3.text_input("Status", value=status_default, key="create_status")

            row3_col1, row3_col2, row3_col3 = st.columns(3)
            product_name = row3_col1.text_input("Product", value="", key="create_product")
            quantity = row3_col2.number_input(
                "Quantity", min_value=1, max_value=500, value=1, step=1, key="create_quantity"
            )
            unit_price = row3_col3.number_input(
                "Unit price", min_value=0.01, value=50.0, step=1.0, key="create_unit_price"
            )

            discount = st.slider(
                "Discount", min_value=0.0, max_value=0.9, value=0.05, step=0.01, key="create_discount"
            )

            create_submitted = st.form_submit_button("Create record", width="stretch")

        if create_submitted:
            payload = {
                "order_date": order_date.isoformat(),
                "customer_name": customer_name.strip(),
                "region": region.strip(),
                "category": category.strip(),
                "product_name": product_name.strip(),
                "quantity": int(quantity),
                "unit_price": float(unit_price),
                "discount": float(discount),
                "status": status.strip(),
            }
            try:
                created = _safe_post(f"{api_base_url}/records", payload)
                st.success(f"Record #{created['record_id']} created. Revenue ${created['revenue']:,.2f}")
                st.json(created)
            except requests.RequestException as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Create failed: {detail}")

    with st.expander("Update record", expanded=False):
        try:
            editable_df = fetch_records(api_base_url, params=[("limit", 600)])
        except requests.RequestException as exc:
            st.error(f"Could not load records for editing: {exc}")
            editable_df = pd.DataFrame()

        if editable_df.empty:
            st.info("No records available for editing.")
        else:
            record_ids = editable_df["record_id"].sort_values(ascending=False).tolist()
            selected_record_id = st.selectbox("Select record ID", record_ids, key="edit_record_select")
            row = editable_df.loc[editable_df["record_id"] == selected_record_id].iloc[0]

            with st.form("update_record_form"):
                up1_col1, up1_col2 = st.columns(2)
                upd_order_date = up1_col1.date_input(
                    "Order date", value=row["order_date"].date(), key="upd_order_date"
                )
                upd_customer_name = up1_col2.text_input(
                    "Customer name", value=str(row["customer_name"]), key="upd_customer_name"
                )

                up2_col1, up2_col2, up2_col3 = st.columns(3)
                upd_region = up2_col1.text_input("Region", value=str(row["region"]), key="upd_region")
                upd_category = up2_col2.text_input("Category", value=str(row["category"]), key="upd_category")
                upd_status = up2_col3.text_input("Status", value=str(row["status"]), key="upd_status")

                up3_col1, up3_col2, up3_col3 = st.columns(3)
                upd_product_name = up3_col1.text_input(
                    "Product", value=str(row["product_name"]), key="upd_product"
                )
                upd_quantity = up3_col2.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=500,
                    value=int(row["quantity"]),
                    step=1,
                    key="upd_quantity",
                )
                upd_unit_price = up3_col3.number_input(
                    "Unit price",
                    min_value=0.01,
                    value=float(row["unit_price"]),
                    step=1.0,
                    key="upd_unit_price",
                )

                upd_discount = st.slider(
                    "Discount",
                    min_value=0.0,
                    max_value=0.9,
                    value=float(row["discount"]),
                    step=0.01,
                    key="upd_discount",
                )

                update_submitted = st.form_submit_button("Update record", width="stretch")

            if update_submitted:
                payload = {
                    "order_date": upd_order_date.isoformat(),
                    "customer_name": upd_customer_name.strip(),
                    "region": upd_region.strip(),
                    "category": upd_category.strip(),
                    "product_name": upd_product_name.strip(),
                    "quantity": int(upd_quantity),
                    "unit_price": float(upd_unit_price),
                    "discount": float(upd_discount),
                    "status": upd_status.strip(),
                }
                try:
                    updated = _safe_put(f"{api_base_url}/records/{selected_record_id}", payload)
                    st.success(f"Record #{updated['record_id']} updated. New revenue ${updated['revenue']:,.2f}")
                    st.json(updated)
                except requests.RequestException as exc:
                    detail = exc.response.text if exc.response is not None else str(exc)
                    st.error(f"Update failed: {detail}")
