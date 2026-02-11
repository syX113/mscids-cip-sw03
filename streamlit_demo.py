"""Streamlit UI for the normalized Sales Analysis dashboard.

Run with:
    streamlit run streamlit_demo.py
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import requests

# Fallback compatibility for environments with protobuf/streamlit mismatch.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
import streamlit as st

st.set_page_config(
    page_title="Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

REQUEST_TIMEOUT_SECONDS = 12
META_CACHE_TTL_SECONDS = 90
ENTITY_CACHE_TTL_SECONDS = 90
SALES_CACHE_TTL_SECONDS = 25

if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://127.0.0.1:8000"
if "flash_success" not in st.session_state:
    st.session_state.flash_success = ""

PASTEL_CATEGORICAL_COLORS = [
    "#73cdd4",
    "#8fdcbe",
    "#a8e8d0",
    "#b6dff4",
    "#c4e6ff",
    "#f3df9a",
    "#f7ebb9",
    "#9dd6f5",
    "#89c5ef",
    "#7bc7b7",
]
PASTEL_HEATMAP_RANGE = ["#fff8d6", "#e7f8d9", "#c8efe3", "#9adfed", "#79c3e8"]
REGRESSION_TREND_COLOR = "#3f8b8f"


def inject_theme() -> None:
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400&display=swap');

          :root {
            --bg-a: #edf9fb;
            --bg-b: #f8feff;
            --bg-c: #f5fdf4;
            --bg-d: #fffdf2;
            --surface: #ffffff;
            --surface-soft: #f9feff;
            --text: #000000;
            --border: #d7e9ea;
            --border-strong: #bfdcdf;
            --accent: #76c9cf;
            --accent-soft: #d8f2f3;
            --accent-mint: #bde9cd;
            --accent-yellow: #f4e7ad;
            --shadow-soft: 0 5px 14px rgba(61, 113, 123, 0.08);
            --chart-grid: #d6e8ea;
            --chart-bg: #ffffff;
            --table-header: #eaf8f7;
          }

          .stApp {
            background:
              radial-gradient(840px 520px at -8% 0%, rgba(180, 234, 239, 0.42), transparent 60%),
              radial-gradient(920px 520px at 105% -5%, rgba(194, 239, 214, 0.39), transparent 60%),
              radial-gradient(720px 440px at 50% 105%, rgba(251, 239, 187, 0.32), transparent 64%),
              linear-gradient(180deg, var(--bg-a) 0%, var(--bg-b) 38%, var(--bg-c) 72%, var(--bg-d) 100%);
            color: var(--text);
          }

          html, body, [class*="css"] {
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          p, span, label, li, div, small {
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          b, strong, th {
            font-weight: 400 !important;
          }

          h1, h2, h3 {
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
            font-weight: 400;
            color: var(--text) !important;
            letter-spacing: 0.01em;
          }

          .block-container {
            padding-top: 1.1rem;
            padding-bottom: 2rem;
          }

          .hero {
            border: 1px solid var(--border-strong);
            border-radius: 22px;
            padding: 1.15rem 1.25rem;
            background: linear-gradient(135deg, #ffffff 0%, #f3fbfc 58%, #f7fffb 100%);
            box-shadow: var(--shadow-soft);
            margin-bottom: 0.95rem;
          }

          .hero h1 {
            margin: 0;
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 400;
          }

          .hero p {
            margin: 0.38rem 0 0;
            font-weight: 400;
          }

          [data-testid="stSidebar"] > div:first-child {
            background: #ffffff;
            border-right: 1px solid var(--border);
          }

          [data-testid="stSidebar"] * {
            color: var(--text) !important;
          }

          [data-testid="stTabs"] [role="tablist"] {
            border-bottom: none !important;
            gap: 0.55rem;
            padding-bottom: 0.3rem;
          }

          [data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
            display: none !important;
          }

          [data-testid="stTabs"] button[role="tab"] {
            white-space: nowrap !important;
            width: auto !important;
            min-width: fit-content !important;
            min-height: 2.7rem !important;
            height: auto !important;
            padding: 0.38rem 1.02rem !important;
            border-radius: 999px !important;
            border: 1px solid var(--border) !important;
            background: linear-gradient(145deg, #ffffff, #f6fbfd) !important;
            color: var(--text) !important;
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif !important;
            font-size: 1.02rem !important;
            font-weight: 400 !important;
            line-height: 1.12 !important;
            box-shadow: none !important;
          }

          [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            border-color: #78c9cf !important;
            background: linear-gradient(145deg, #ffffff 0%, #ddf4f6 58%, #e6f6ea 100%) !important;
            box-shadow: inset 0 0 0 1px rgba(118, 201, 207, 0.35) !important;
          }

          [data-testid="stWidgetLabel"] p {
            color: var(--text) !important;
            font-weight: 400 !important;
            font-size: 0.95rem !important;
          }

          [data-baseweb="input"] > div,
          [data-baseweb="base-input"] > div,
          [data-baseweb="textarea"] > div,
          [data-baseweb="select"] > div {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
            transition: border-color 140ms ease, box-shadow 140ms ease;
          }

          [data-baseweb="input"] input,
          [data-baseweb="base-input"] input,
          [data-baseweb="textarea"] textarea,
          [data-baseweb="select"] input {
            color: var(--text) !important;
            background: #ffffff !important;
            font-weight: 400;
          }

          [data-baseweb="input"] > div:focus-within,
          [data-baseweb="base-input"] > div:focus-within,
          [data-baseweb="textarea"] > div:focus-within,
          [data-baseweb="select"] > div:focus-within {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 0.16rem rgba(118, 201, 207, 0.25) !important;
          }

          [data-baseweb="popover"] [role="listbox"] {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
          }

          [data-baseweb="popover"] [role="option"],
          [data-baseweb="popover"] [role="option"] * {
            color: var(--text) !important;
            background: #ffffff !important;
          }

          [data-baseweb="popover"] [aria-selected="true"] {
            background: #e5f5f6 !important;
          }

          div[data-baseweb="popover"] [data-baseweb="calendar"] {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            box-shadow: 0 6px 18px rgba(61, 113, 123, 0.12) !important;
          }

          div[data-baseweb="popover"] [data-baseweb="calendar"] * {
            color: var(--text) !important;
            fill: var(--text) !important;
            background: transparent !important;
            font-weight: 400 !important;
          }

          div[data-baseweb="popover"] [data-baseweb="calendar"] button {
            background: #ffffff !important;
            color: var(--text) !important;
          }

          div[data-baseweb="popover"] [data-baseweb="calendar"] [aria-selected="true"],
          div[data-baseweb="popover"] [data-baseweb="calendar"] [aria-pressed="true"] {
            background: #dff3f4 !important;
            color: var(--text) !important;
          }

          div[data-baseweb="popover"] [data-baseweb="calendar"] [aria-label*="keyboard selected"] {
            background: #eaf7f8 !important;
          }

          [data-baseweb="tag"] {
            background: linear-gradient(135deg, #e5f6f7, #effbf4) !important;
            border: 1px solid #b8dde0 !important;
            border-radius: 9px !important;
          }

          [data-baseweb="tag"] * {
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          [data-testid="stNumberInputContainer"] button {
            background: linear-gradient(145deg, #e4f6f7, #f3faec) !important;
            border-left: 1px solid var(--border) !important;
            color: var(--text) !important;
          }

          [data-testid="stDateInput"] * {
            color: var(--text) !important;
          }

          [data-testid="stDateInput"] [data-baseweb="input"] > div,
          [data-testid="stDateInput"] [data-baseweb="base-input"] > div,
          [data-testid="stDateInput"] input {
            background: #ffffff !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
          }

          [data-baseweb="slider"] [role="slider"] {
            background: var(--accent) !important;
            border-color: var(--accent) !important;
          }

          [data-baseweb="slider"] [data-testid="stTickBarMin"] {
            background: var(--accent) !important;
          }

          .stButton > button,
          .stFormSubmitButton > button {
            min-height: 2.65rem !important;
            border-radius: 12px !important;
            border: 1px solid #b9dfe1 !important;
            background: linear-gradient(145deg, #e3f5f6 0%, #eefbe6 100%) !important;
            color: var(--text) !important;
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif !important;
            font-weight: 400 !important;
            box-shadow: 0 4px 12px rgba(93, 173, 177, 0.12);
          }

          .stButton > button:hover,
          .stFormSubmitButton > button:hover {
            border-color: var(--accent) !important;
            filter: brightness(1.01);
          }

          [data-testid="stMetric"] {
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            background: linear-gradient(140deg, #ffffff, #f5fcff) !important;
            box-shadow: var(--shadow-soft);
            padding: 0.5rem 0.75rem;
          }

          [data-testid="stMetricLabel"],
          [data-testid="stMetricLabel"] * {
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          [data-testid="stMetricValue"] {
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif !important;
            font-size: 1.38rem !important;
            font-weight: 400 !important;
            color: var(--text) !important;
          }

          [data-testid="stAlert"] {
            border-radius: 12px;
            border: 1px solid var(--border) !important;
          }

          [data-testid="stExpander"] {
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            background: linear-gradient(135deg, #ffffff, #f7fdff) !important;
            box-shadow: var(--shadow-soft);
            overflow: hidden;
          }

          [data-testid="stExpander"] summary,
          [data-testid="stExpander"] summary * {
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          [data-testid="stVegaLiteChart"] {
            background: var(--chart-bg) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            box-shadow: var(--shadow-soft);
            padding: 0.35rem 0.4rem 0.08rem !important;
          }

          [data-testid="stVegaLiteChart"] svg text {
            fill: var(--text) !important;
          }

          [data-testid="stVegaLiteChart"] svg .domain,
          [data-testid="stVegaLiteChart"] svg .tick line,
          [data-testid="stVegaLiteChart"] svg .grid line {
            stroke: var(--chart-grid) !important;
          }

          [data-testid="stDataFrame"] div[role="grid"] {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
          }

          [data-testid="stDataFrame"] {
            --gdg-bg-cell: #ffffff;
            --gdg-bg-cell-medium: #f6fcfd;
            --gdg-bg-header: #eaf8f7;
            --gdg-bg-header-hovered: #e2f3f4;
            --gdg-bg-header-has-focus: #e2f3f4;
            --gdg-bg-icon-header: #d2ecee;
            --gdg-bg-search-result: #f3faeb;
            --gdg-border-color: #d8e9eb;
            --gdg-fg-cell: #000000;
            --gdg-fg-header: #000000;
            --gdg-fg-icon-header: #2c7378;
            --gdg-text-dark: #000000;
            --gdg-text-medium: #2f4345;
            --gdg-text-light: #5a7072;
            --gdg-link-color: #2b7f86;
          }

          [data-testid="stDataFrame"] canvas {
            background: #ffffff !important;
          }

          [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"],
          [data-testid="stDataFrame"] [data-testid="StyledDataFrameResizable"] {
            background: #ffffff !important;
            border-radius: 12px !important;
          }

          [data-testid="stDataFrame"] [data-testid="stToolbar"],
          [data-testid="stDataFrame"] [data-testid="stStatusWidget"] {
            background: #ffffff !important;
            color: var(--text) !important;
          }

          [data-testid="stDataFrame"] [role="columnheader"] {
            background: var(--table-header) !important;
            color: var(--text) !important;
            border-color: var(--border) !important;
            font-weight: 400 !important;
          }

          [data-testid="stDataFrame"] [role="gridcell"],
          [data-testid="stDataFrame"] [role="rowheader"] {
            background: #ffffff !important;
            color: var(--text) !important;
            border-color: #e5f0f1 !important;
          }

          [data-testid="stTable"] table {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px;
          }

          [data-testid="stTable"] th {
            background: var(--table-header) !important;
            color: var(--text) !important;
            font-weight: 400 !important;
          }

          [data-testid="stTable"] td {
            background: #ffffff !important;
            color: var(--text) !important;
            border-top: 1px solid #e5f0f1 !important;
          }

          [data-testid="stCaptionContainer"] p {
            color: var(--text) !important;
            opacity: 0.85;
          }

          [data-testid="stElementToolbar"] {
            background: rgba(255, 255, 255, 0.94) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 12px rgba(61, 113, 123, 0.12) !important;
          }

          [data-testid="stElementToolbar"] * {
            color: var(--text) !important;
          }

          .vega-tooltip {
            background: rgba(255, 255, 255, 0.98) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            box-shadow: 0 6px 16px rgba(61, 113, 123, 0.12) !important;
            font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif !important;
            font-size: 0.92rem !important;
            padding: 0.45rem 0.62rem !important;
          }

          .vega-tooltip table {
            border-collapse: collapse !important;
          }

          .vega-tooltip th,
          .vega-tooltip td {
            color: var(--text) !important;
            border: none !important;
            background: transparent !important;
            font-weight: 400 !important;
            padding: 0.16rem 0.28rem !important;
          }

          .vega-tooltip hr {
            border: 0 !important;
            border-top: 1px solid #e1ecee !important;
            margin: 0.2rem 0 !important;
          }

          @media (max-width: 980px) {
            [data-testid="stTabs"] button[role="tab"] {
              font-size: 0.95rem !important;
              padding: 0.35rem 0.85rem !important;
            }

            .hero h1 {
              font-size: 1.65rem;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _build_url(api_base: str, path: str) -> str:
    return f"{api_base.rstrip('/')}{path}"


def _parse_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except Exception:
        payload = response.text.strip()

    if isinstance(payload, dict) and "detail" in payload:
        detail = payload["detail"]
    else:
        detail = payload
    return f"{response.status_code} - {detail}"


def _request_json(
    method: str,
    api_base: str,
    path: str,
    *,
    params: list[tuple[str, Any]] | None = None,
    payload: dict[str, Any] | None = None,
) -> Any:
    url = _build_url(api_base, path)
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc

    if response.status_code >= 400:
        raise RuntimeError(_parse_error_detail(response))

    if not response.content:
        return None
    return response.json()


def _safe_get(api_base: str, path: str, params: list[tuple[str, Any]] | None = None) -> Any:
    return _request_json("GET", api_base, path, params=params)


def _safe_post(api_base: str, path: str, payload: dict[str, Any]) -> Any:
    return _request_json("POST", api_base, path, payload=payload)


def _safe_put(api_base: str, path: str, payload: dict[str, Any]) -> Any:
    return _request_json("PUT", api_base, path, payload=payload)


def _freeze_params(params: list[tuple[str, Any]]) -> tuple[tuple[str, str], ...]:
    return tuple((str(k), str(v)) for k, v in params)


def clear_data_caches() -> None:
    st.cache_data.clear()


@st.cache_data(show_spinner=False, ttl=META_CACHE_TTL_SECONDS)
def fetch_meta_options(api_base: str) -> dict[str, Any]:
    return _safe_get(api_base, "/meta/options")


@st.cache_data(show_spinner=False, ttl=ENTITY_CACHE_TTL_SECONDS)
def fetch_regions(api_base: str) -> list[dict[str, Any]]:
    return _safe_get(api_base, "/regions")


@st.cache_data(show_spinner=False, ttl=ENTITY_CACHE_TTL_SECONDS)
def fetch_countries(api_base: str) -> list[dict[str, Any]]:
    return _safe_get(api_base, "/countries")


@st.cache_data(show_spinner=False, ttl=ENTITY_CACHE_TTL_SECONDS)
def fetch_categories(api_base: str) -> list[dict[str, Any]]:
    return _safe_get(api_base, "/categories")


@st.cache_data(show_spinner=False, ttl=ENTITY_CACHE_TTL_SECONDS)
def fetch_products(api_base: str) -> list[dict[str, Any]]:
    return _safe_get(api_base, "/products")


@st.cache_data(show_spinner=False, ttl=SALES_CACHE_TTL_SECONDS)
def fetch_sales(api_base: str, params_key: tuple[tuple[str, str], ...]) -> pd.DataFrame:
    records = _safe_get(api_base, "/sales", params=[(k, v) for k, v in params_key])
    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    for col in ["units_sold", "total_price", "customer_rating"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _axis(title: str | None = None, fmt: str | None = None, label_angle: int = 0) -> alt.Axis:
    args: dict[str, Any] = {
        "title": title,
        "labelColor": "#000000",
        "titleColor": "#000000",
        "labelFont": "Manrope",
        "titleFont": "Manrope",
        "labelFontSize": 11,
        "titleFontSize": 11,
        "domainColor": "#d7e9ea",
        "tickColor": "#d7e9ea",
        "gridColor": "#e5f1f2",
        "labelAngle": label_angle,
        "labelFontWeight": 400,
        "titleFontWeight": 400,
    }
    if fmt is not None:
        args["format"] = fmt
    return alt.Axis(**args)


def _configure_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure_view(stroke="#d7e9ea", strokeWidth=0.7)
        .configure_axis(
            labelFont="Manrope",
            titleFont="Manrope",
            labelFontWeight=400,
            titleFontWeight=400,
        )
        .configure_legend(
            labelFont="Manrope",
            titleFont="Manrope",
            orient="top",
            labelColor="#000000",
            titleColor="#000000",
            labelFontSize=11,
            titleFontSize=11,
            labelFontWeight=400,
            titleFontWeight=400,
        )
        .configure_title(font="Manrope", fontSize=19, fontWeight=400, anchor="start", color="#000000")
        .configure(background="transparent")
    )


def build_line_chart(
    df: pd.DataFrame,
    *,
    metric_column: str,
    metric_title: str,
    compare_column: str,
    compare_title: str,
    split_by_category: bool,
) -> alt.Chart:
    line_df = df.copy()
    line_df["month"] = line_df["sale_date"].dt.to_period("M").dt.to_timestamp()

    group_cols = ["month", compare_column]
    tooltip_cols: list[alt.Tooltip] = [
        alt.Tooltip("month:T", title="Month", format="%b %Y"),
        alt.Tooltip(f"{compare_column}:N", title=compare_title),
        alt.Tooltip("metric_value:Q", title=metric_title, format=",.2f" if metric_column == "total_price" else ",.0f"),
    ]

    if split_by_category and compare_column != "category_name":
        group_cols.append("category_name")
        tooltip_cols.append(alt.Tooltip("category_name:N", title="Category"))

    grouped = (
        line_df.groupby(group_cols, as_index=False)
        .agg(metric_value=(metric_column, "sum"))
        .sort_values("month")
    )

    if grouped.empty:
        return _configure_chart(alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line()).properties(
            height=420,
            title="Monthly Sales Analysis",
        )

    y_fmt = ",.0f" if metric_column == "units_sold" else ",.2f"

    base = alt.Chart(grouped).encode(
        x=alt.X("month:T", axis=_axis("Month"), title="Month"),
        y=alt.Y("metric_value:Q", axis=_axis(metric_title, fmt=y_fmt), title=metric_title),
        color=alt.Color(
            f"{compare_column}:N",
            title=compare_title,
            scale=alt.Scale(range=PASTEL_CATEGORICAL_COLORS),
        ),
        tooltip=tooltip_cols,
    )

    if split_by_category and compare_column != "category_name":
        chart = base.mark_line(point=True, strokeWidth=1.6).encode(strokeDash=alt.StrokeDash("category_name:N", title="Category"))
    else:
        chart = base.mark_line(point=True, strokeWidth=1.6)

    return _configure_chart(chart).properties(height=420, title="Monthly Sales Analysis")


def build_heatmap(
    df: pd.DataFrame,
    *,
    row_column: str,
    row_title: str,
    col_column: str,
    col_title: str,
    metric_label: str,
) -> alt.Chart:
    metric_map: dict[str, tuple[str, str]] = {
        "Total Sales": ("total_price", "sum"),
        "Units Sold": ("units_sold", "sum"),
        "Average Rating": ("customer_rating", "mean"),
    }
    metric_col, agg = metric_map[metric_label]

    grouped = (
        df.groupby([row_column, col_column], as_index=False)
        .agg(metric_value=(metric_col, agg))
        .sort_values([row_column, col_column])
    )

    if grouped.empty:
        return _configure_chart(alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_rect()).properties(
            height=420,
            title="Heatmap Comparison",
        )

    value_format = ",.2f" if metric_label == "Total Sales" else ",.0f" if metric_label == "Units Sold" else ".2f"

    heat = alt.Chart(grouped).mark_rect(cornerRadius=4).encode(
        x=alt.X(f"{col_column}:N", axis=_axis(col_title, label_angle=-20), sort="-y"),
        y=alt.Y(f"{row_column}:N", axis=_axis(row_title), sort="-x"),
        color=alt.Color(
            "metric_value:Q",
            title=metric_label,
            scale=alt.Scale(range=PASTEL_HEATMAP_RANGE),
        ),
        tooltip=[
            alt.Tooltip(f"{row_column}:N", title=row_title),
            alt.Tooltip(f"{col_column}:N", title=col_title),
            alt.Tooltip("metric_value:Q", title=metric_label, format=value_format),
        ],
    )

    text = alt.Chart(grouped).mark_text(font="Manrope", fontSize=11).encode(
        x=alt.X(f"{col_column}:N", sort="-y"),
        y=alt.Y(f"{row_column}:N", sort="-x"),
        text=alt.Text("metric_value:Q", format=".2s"),
        color=alt.value("#000000"),
    )

    return _configure_chart((heat + text).properties(height=420, title="Heatmap Comparison"))


def prepare_regression_data(df: pd.DataFrame, level: str) -> pd.DataFrame:
    if level == "Sale":
        out = df.copy()
        out["entity"] = out["sale_id"].astype(int).astype(str)
        out["avg_rating"] = out["customer_rating"].astype(float)
        out["avg_order_value"] = out["total_price"].astype(float)
        out["avg_units_sold"] = out["units_sold"].astype(float)
        out["total_sales"] = out["total_price"].astype(float)
        out["total_units_sold"] = out["units_sold"].astype(float)
        out["color_group"] = out["category_name"].astype(str)
        return out[
            [
                "entity",
                "avg_rating",
                "avg_order_value",
                "avg_units_sold",
                "total_sales",
                "total_units_sold",
                "color_group",
            ]
        ]

    base = df.copy()
    base["month"] = base["sale_date"].dt.to_period("M").dt.to_timestamp()
    base["month_label"] = base["month"].dt.strftime("%Y-%m")

    if level in ("Product", "Product (monthly)"):
        grouped = (
            base.groupby(["product_name", "category_name", "month", "month_label"], as_index=False)
            .agg(
                avg_rating=("customer_rating", "mean"),
                avg_order_value=("total_price", "mean"),
                avg_units_sold=("units_sold", "mean"),
                total_sales=("total_price", "sum"),
                total_units_sold=("units_sold", "sum"),
            )
            .rename(columns={"product_name": "base_entity"})
        )
        grouped["entity"] = grouped["base_entity"] + " | " + grouped["month_label"]
        grouped["color_group"] = grouped["category_name"].astype(str)
        return grouped[["entity", "avg_rating", "avg_order_value", "avg_units_sold", "total_sales", "total_units_sold", "color_group"]]

    if level in ("Category", "Category (monthly)"):
        grouped = (
            base.groupby(["category_name", "month", "month_label"], as_index=False)
            .agg(
                avg_rating=("customer_rating", "mean"),
                avg_order_value=("total_price", "mean"),
                avg_units_sold=("units_sold", "mean"),
                total_sales=("total_price", "sum"),
                total_units_sold=("units_sold", "sum"),
            )
            .rename(columns={"category_name": "base_entity"})
        )
        grouped["entity"] = grouped["base_entity"] + " | " + grouped["month_label"]
        grouped["color_group"] = grouped["base_entity"].astype(str)
        return grouped[["entity", "avg_rating", "avg_order_value", "avg_units_sold", "total_sales", "total_units_sold", "color_group"]]

    if level in ("Country", "Country (monthly)"):
        grouped = (
            base.groupby(["country_name", "region_name", "month", "month_label"], as_index=False)
            .agg(
                avg_rating=("customer_rating", "mean"),
                avg_order_value=("total_price", "mean"),
                avg_units_sold=("units_sold", "mean"),
                total_sales=("total_price", "sum"),
                total_units_sold=("units_sold", "sum"),
            )
            .rename(columns={"country_name": "base_entity"})
        )
        grouped["entity"] = grouped["base_entity"] + " | " + grouped["month_label"]
        grouped["color_group"] = grouped["region_name"].astype(str)
        return grouped[["entity", "avg_rating", "avg_order_value", "avg_units_sold", "total_sales", "total_units_sold", "color_group"]]

    grouped = (
        base.groupby(["region_name", "month", "month_label"], as_index=False)
        .agg(
            avg_rating=("customer_rating", "mean"),
            avg_order_value=("total_price", "mean"),
            avg_units_sold=("units_sold", "mean"),
            total_sales=("total_price", "sum"),
            total_units_sold=("units_sold", "sum"),
        )
        .rename(columns={"region_name": "base_entity"})
    )
    grouped["entity"] = grouped["base_entity"] + " | " + grouped["month_label"]
    grouped["color_group"] = grouped["base_entity"].astype(str)
    return grouped[["entity", "avg_rating", "avg_order_value", "avg_units_sold", "total_sales", "total_units_sold", "color_group"]]


def build_regression_chart(reg_df: pd.DataFrame, x_column: str, x_title: str) -> tuple[alt.Chart | None, float | None, float | None, float | None]:
    plot_df = reg_df.copy()
    plot_df = plot_df.dropna(subset=[x_column, "avg_rating"])

    if len(plot_df) < 2 or plot_df[x_column].nunique() < 2:
        return None, None, None, None

    x = plot_df[x_column].astype(float).to_numpy()
    y = plot_df["avg_rating"].astype(float).to_numpy()

    slope, intercept = np.polyfit(x, y, 1)
    y_pred = slope * x + intercept
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - y_pred) ** 2)
    r_squared = 0.0 if ss_tot == 0 else float(1 - (ss_res / ss_tot))

    x_min = float(np.min(x))
    x_max = float(np.max(x))
    line_domain = np.linspace(x_min, x_max, 100)
    line_df = pd.DataFrame(
        {
            "x": line_domain,
            "y": slope * line_domain + intercept,
        }
    )

    points = alt.Chart(plot_df).mark_circle(size=90, opacity=0.62).encode(
        x=alt.X(f"{x_column}:Q", title=x_title, axis=_axis(x_title, fmt=",.2f" if "sales" in x_column or "value" in x_column else ",.0f")),
        y=alt.Y("avg_rating:Q", title="Average Customer Rating", scale=alt.Scale(domain=[1, 5]), axis=_axis("Average Customer Rating", fmt=".2f")),
        color=alt.Color(
            "color_group:N",
            title="Color Group",
            scale=alt.Scale(range=PASTEL_CATEGORICAL_COLORS),
        ),
        tooltip=[
            alt.Tooltip("entity:N", title="Entity"),
            alt.Tooltip(f"{x_column}:Q", title=x_title, format=",.2f" if "sales" in x_column or "value" in x_column else ",.0f"),
            alt.Tooltip("avg_rating:Q", title="Avg rating", format=".2f"),
            alt.Tooltip("total_sales:Q", title="Total sales", format=",.2f"),
            alt.Tooltip("total_units_sold:Q", title="Total units", format=",.0f"),
        ],
    )

    trend = alt.Chart(line_df).mark_line(color=REGRESSION_TREND_COLOR, strokeWidth=1.8).encode(
        x=alt.X("x:Q"),
        y=alt.Y("y:Q"),
    )

    chart = _configure_chart((points + trend).properties(height=420, title="Regression: Customer Satisfaction Trend"))
    return chart, float(slope), float(intercept), r_squared


def add_multi_param(params: list[tuple[str, Any]], key: str, values: list[str]) -> None:
    for value in values:
        params.append((key, value))


inject_theme()
st.markdown(
    """
    <div class="hero">
      <h1>Sales Analysis Dashboard</h1>
      <p>Explore sales by region, country, product, and category with API-backed records management.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.flash_success:
    st.success(st.session_state.flash_success)
    st.session_state.flash_success = ""

with st.sidebar:
    st.subheader("API Configuration")
    api_base_input = st.text_input(
        "FastAPI Base URL",
        value=str(st.session_state.api_base_url),
        help="Example: http://127.0.0.1:8000",
    )
    cleaned = api_base_input.strip().rstrip("/")
    if not cleaned:
        cleaned = "http://127.0.0.1:8000"

    if cleaned != st.session_state.api_base_url:
        st.session_state.api_base_url = cleaned
        clear_data_caches()

    st.caption("Backend command: `uvicorn src.parquet_api:app --reload`")

api_base_url = str(st.session_state.api_base_url)

try:
    health = _safe_get(api_base_url, "/health")
    if health.get("status") == "ok":
        st.sidebar.success("API is reachable")
except RuntimeError as exc:
    st.sidebar.error(f"API connection failed: {exc}")
    st.stop()


dashboard_tab, records_tab = st.tabs(["Dashboard", "Records"])

with dashboard_tab:
    try:
        options = fetch_meta_options(api_base_url)
    except RuntimeError as exc:
        st.error(f"Could not load filter options: {exc}")
        st.stop()

    region_options = options.get("regions", [])
    country_options = options.get("countries", [])
    category_options = options.get("categories", [])
    product_options = options.get("products", [])

    c1, c2, c3, c4 = st.columns(4)
    selected_regions = c1.multiselect("Sales Region", region_options, default=region_options)
    selected_countries = c2.multiselect("Country", country_options, default=country_options)
    selected_categories = c3.multiselect("Category", category_options, default=category_options)
    selected_products = c4.multiselect("Product", product_options, default=product_options)

    min_date_raw = options.get("min_date")
    max_date_raw = options.get("max_date")
    if min_date_raw and max_date_raw:
        min_date = pd.to_datetime(min_date_raw).date()
        max_date = pd.to_datetime(max_date_raw).date()
    else:
        max_date = date.today()
        min_date = max_date - timedelta(days=365)

    picked_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(picked_range, tuple) and len(picked_range) == 2:
        start_date, end_date = picked_range
    elif isinstance(picked_range, list) and len(picked_range) == 2:
        start_date, end_date = picked_range[0], picked_range[1]
    else:
        start_date, end_date = min_date, max_date

    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    if not all([selected_regions, selected_countries, selected_categories, selected_products]):
        sales_df = pd.DataFrame()
    else:
        params: list[tuple[str, Any]] = []
        add_multi_param(params, "region", selected_regions)
        add_multi_param(params, "country", selected_countries)
        add_multi_param(params, "category", selected_categories)
        add_multi_param(params, "product", selected_products)
        params.append(("start_date", start_date.isoformat()))
        params.append(("end_date", end_date.isoformat()))
        params.append(("limit", 20000))

        try:
            with st.spinner("Loading dashboard data..."):
                sales_df = fetch_sales(api_base_url, _freeze_params(params))
        except RuntimeError as exc:
            st.error(f"Could not load sales data: {exc}")
            sales_df = pd.DataFrame()

    if sales_df.empty:
        st.info("No sales data matches the current filters.")
    else:
        sales_df = sales_df.dropna(subset=["sale_date", "total_price", "units_sold", "customer_rating"]).copy()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Transactions", f"{len(sales_df):,}")
        m2.metric("Total Sales", f"${sales_df['total_price'].sum():,.2f}")
        m3.metric("Units Sold", f"{int(sales_df['units_sold'].sum()):,}")
        m4.metric("Avg Rating", f"{sales_df['customer_rating'].mean():.2f} / 5")

        st.markdown("### 1) Sales Line Analysis")
        lc1, lc2, lc3 = st.columns(3)
        line_metric = lc1.selectbox("Metric", ["Total Sales", "Units Sold"], index=0)
        line_compare = lc2.selectbox("Compare lines by", ["Sales Region", "Country", "Category", "Product"], index=0)
        split_by_category = lc3.checkbox("Split by category", value=True)

        metric_map = {
            "Total Sales": ("total_price", "Total Sales"),
            "Units Sold": ("units_sold", "Units Sold"),
        }
        compare_map = {
            "Sales Region": ("region_name", "Sales Region"),
            "Country": ("country_name", "Country"),
            "Category": ("category_name", "Category"),
            "Product": ("product_name", "Product"),
        }

        metric_col, metric_title = metric_map[line_metric]
        compare_col, compare_title = compare_map[line_compare]

        line_chart = build_line_chart(
            sales_df,
            metric_column=metric_col,
            metric_title=metric_title,
            compare_column=compare_col,
            compare_title=compare_title,
            split_by_category=split_by_category,
        )
        st.altair_chart(line_chart, width="stretch")

        st.markdown("### 2) Sales Heatmap")
        hc1, hc2, hc3 = st.columns(3)
        heat_row = hc1.selectbox("Row axis", ["Sales Region", "Country"], index=1)
        heat_col = hc2.selectbox("Column axis", ["Category", "Product"], index=0)
        heat_metric = hc3.selectbox("Heatmap metric", ["Total Sales", "Units Sold", "Average Rating"], index=0)

        heat_row_map = {"Sales Region": ("region_name", "Sales Region"), "Country": ("country_name", "Country")}
        heat_col_map = {"Category": ("category_name", "Category"), "Product": ("product_name", "Product")}
        row_col, row_title = heat_row_map[heat_row]
        col_col, col_title = heat_col_map[heat_col]

        heatmap_chart = build_heatmap(
            sales_df,
            row_column=row_col,
            row_title=row_title,
            col_column=col_col,
            col_title=col_title,
            metric_label=heat_metric,
        )
        st.altair_chart(heatmap_chart, width="stretch")

        st.markdown("### 3) Interactive Regression")
        rc1, rc2 = st.columns(2)
        regression_level = rc1.selectbox(
            "Aggregation level",
            ["Product (monthly)", "Country (monthly)", "Category (monthly)", "Sales Region (monthly)", "Sale"],
            index=0,
        )
        rc1.caption("Monthly levels create denser regression points while preserving grouping context.")
        regression_x = rc2.selectbox(
            "Predictor (X)",
            ["Average Order Value", "Average Units Sold", "Total Sales", "Total Units Sold"],
            index=0,
        )

        regression_df = prepare_regression_data(sales_df, level=regression_level)
        x_map = {
            "Average Order Value": ("avg_order_value", "Average Order Value"),
            "Average Units Sold": ("avg_units_sold", "Average Units Sold"),
            "Total Sales": ("total_sales", "Total Sales"),
            "Total Units Sold": ("total_units_sold", "Total Units Sold"),
        }
        x_col, x_title = x_map[regression_x]

        regression_chart, slope, intercept, r_squared = build_regression_chart(regression_df, x_column=x_col, x_title=x_title)
        if regression_chart is None:
            st.info("Not enough variability in the current filtered data to fit a regression line.")
        else:
            st.altair_chart(regression_chart, width="stretch")
            st.caption(
                f"Model: rating = {slope:.4f} x {x_title.lower()} + {intercept:.4f} | R² = {r_squared:.4f}"
            )

        with st.expander("Show full filtered sales table", expanded=False):
            table_columns = [
                "sale_id",
                "sale_date",
                "region_name",
                "country_name",
                "category_name",
                "product_name",
                "units_sold",
                "total_price",
                "customer_rating",
            ]
            table_df = sales_df[table_columns].sort_values("sale_date", ascending=False).copy()
            table_df["sale_date"] = table_df["sale_date"].dt.date
            st.dataframe(table_df, width="stretch", hide_index=True)

with records_tab:
    try:
        regions = fetch_regions(api_base_url)
        countries = fetch_countries(api_base_url)
        categories = fetch_categories(api_base_url)
        products = fetch_products(api_base_url)
        sales_for_records = fetch_sales(api_base_url, _freeze_params([("limit", 5000)]))
    except RuntimeError as exc:
        st.error(f"Could not load records data: {exc}")
        st.stop()

    region_labels = [f"{r['name']} (#{r['region_id']})" for r in regions]
    region_by_label = {f"{r['name']} (#{r['region_id']})": r for r in regions}
    region_label_by_id = {int(r["region_id"]): f"{r['name']} (#{r['region_id']})" for r in regions}

    category_labels = [f"{c['name']} (#{c['category_id']})" for c in categories]
    category_by_label = {f"{c['name']} (#{c['category_id']})": c for c in categories}
    category_label_by_id = {int(c["category_id"]): f"{c['name']} (#{c['category_id']})" for c in categories}

    product_labels = [f"{p['name']} | ${float(p['price']):.2f} (#{p['product_id']})" for p in products]
    product_by_label = {f"{p['name']} | ${float(p['price']):.2f} (#{p['product_id']})": p for p in products}
    product_label_by_id = {
        int(p["product_id"]): f"{p['name']} | ${float(p['price']):.2f} (#{p['product_id']})" for p in products
    }

    country_labels = [f"{c['name']} ({c['region_name']}) (#{c['country_id']})" for c in countries]
    country_by_label = {f"{c['name']} ({c['region_name']}) (#{c['country_id']})": c for c in countries}
    country_label_by_id = {
        int(c["country_id"]): f"{c['name']} ({c['region_name']}) (#{c['country_id']})" for c in countries
    }

    region_tab, country_tab, category_tab, product_tab, sales_tab = st.tabs(
        ["Sales Regions", "Countries", "Categories", "Products", "Sales"]
    )

    with region_tab:
        st.subheader("Sales Regions")

        with st.form("create_region_form", clear_on_submit=True):
            new_region_name = st.text_input("Region name")
            new_region_desc = st.text_area("Region description")
            create_region_submitted = st.form_submit_button("Create region")

        if create_region_submitted:
            payload = {
                "name": new_region_name.strip(),
                "description": new_region_desc.strip(),
            }
            try:
                created = _safe_post(api_base_url, "/regions", payload)
                clear_data_caches()
                st.session_state.flash_success = f"Region #{created['region_id']} created"
                st.rerun()
            except RuntimeError as exc:
                st.error(f"Create region failed: {exc}")

        if regions:
            region_choice = st.selectbox("Select region to update", region_labels, key="region_update_choice")
            selected_region = region_by_label[region_choice]
            with st.form(f"update_region_form_{selected_region['region_id']}"):
                upd_region_name = st.text_input(
                    "Region name",
                    value=str(selected_region["name"]),
                    key=f"upd_region_name_{selected_region['region_id']}",
                )
                upd_region_desc = st.text_area(
                    "Region description",
                    value=str(selected_region["description"]),
                    key=f"upd_region_desc_{selected_region['region_id']}",
                )
                upd_region_submitted = st.form_submit_button("Update region")

            if upd_region_submitted:
                payload = {
                    "name": upd_region_name.strip(),
                    "description": upd_region_desc.strip(),
                }
                try:
                    _safe_put(api_base_url, f"/regions/{selected_region['region_id']}", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Region #{selected_region['region_id']} updated"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Update region failed: {exc}")

        if regions:
            st.dataframe(pd.DataFrame(regions).sort_values("region_id"), width="stretch", hide_index=True)
        else:
            st.info("No regions found.")

    with country_tab:
        st.subheader("Countries")

        if not regions:
            st.warning("Create at least one sales region before creating countries.")
        else:
            with st.form("create_country_form", clear_on_submit=True):
                new_country_name = st.text_input("Country name")
                new_country_region = st.selectbox("Sales region", region_labels, key="create_country_region")
                create_country_submitted = st.form_submit_button("Create country")

            if create_country_submitted:
                payload = {
                    "name": new_country_name.strip(),
                    "region_id": int(region_by_label[new_country_region]["region_id"]),
                }
                try:
                    created = _safe_post(api_base_url, "/countries", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Country #{created['country_id']} created"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Create country failed: {exc}")

        if countries and regions:
            country_choice = st.selectbox("Select country to update", country_labels, key="country_update_choice")
            selected_country = country_by_label[country_choice]

            default_region_label = region_label_by_id.get(int(selected_country["region_id"]), region_labels[0])
            region_index = region_labels.index(default_region_label) if default_region_label in region_labels else 0

            with st.form(f"update_country_form_{selected_country['country_id']}"):
                upd_country_name = st.text_input(
                    "Country name",
                    value=str(selected_country["name"]),
                    key=f"upd_country_name_{selected_country['country_id']}",
                )
                upd_country_region = st.selectbox(
                    "Sales region",
                    region_labels,
                    index=region_index,
                    key=f"upd_country_region_{selected_country['country_id']}",
                )
                upd_country_submitted = st.form_submit_button("Update country")

            if upd_country_submitted:
                payload = {
                    "name": upd_country_name.strip(),
                    "region_id": int(region_by_label[upd_country_region]["region_id"]),
                }
                try:
                    _safe_put(api_base_url, f"/countries/{selected_country['country_id']}", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Country #{selected_country['country_id']} updated"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Update country failed: {exc}")

        if countries:
            st.dataframe(pd.DataFrame(countries).sort_values("country_id"), width="stretch", hide_index=True)
        else:
            st.info("No countries found.")

    with category_tab:
        st.subheader("Categories")

        with st.form("create_category_form", clear_on_submit=True):
            new_category_name = st.text_input("Category name")
            new_category_desc = st.text_area("Category description")
            create_category_submitted = st.form_submit_button("Create category")

        if create_category_submitted:
            payload = {
                "name": new_category_name.strip(),
                "description": new_category_desc.strip(),
            }
            try:
                created = _safe_post(api_base_url, "/categories", payload)
                clear_data_caches()
                st.session_state.flash_success = f"Category #{created['category_id']} created"
                st.rerun()
            except RuntimeError as exc:
                st.error(f"Create category failed: {exc}")

        if categories:
            category_choice = st.selectbox("Select category to update", category_labels, key="category_update_choice")
            selected_category = category_by_label[category_choice]

            with st.form(f"update_category_form_{selected_category['category_id']}"):
                upd_category_name = st.text_input(
                    "Category name",
                    value=str(selected_category["name"]),
                    key=f"upd_category_name_{selected_category['category_id']}",
                )
                upd_category_desc = st.text_area(
                    "Category description",
                    value=str(selected_category["description"]),
                    key=f"upd_category_desc_{selected_category['category_id']}",
                )
                upd_category_submitted = st.form_submit_button("Update category")

            if upd_category_submitted:
                payload = {
                    "name": upd_category_name.strip(),
                    "description": upd_category_desc.strip(),
                }
                try:
                    _safe_put(api_base_url, f"/categories/{selected_category['category_id']}", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Category #{selected_category['category_id']} updated"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Update category failed: {exc}")

        if categories:
            st.dataframe(pd.DataFrame(categories).sort_values("category_id"), width="stretch", hide_index=True)
        else:
            st.info("No categories found.")

    with product_tab:
        st.subheader("Products")

        if not categories:
            st.warning("Create at least one category before creating products.")
        else:
            with st.form("create_product_form", clear_on_submit=True):
                new_product_name = st.text_input("Product name")
                new_product_price = st.number_input("Product price", min_value=0.01, value=100.0, step=1.0)
                new_product_desc = st.text_area("Product description")
                new_product_category = st.selectbox("Category", category_labels, key="create_product_category")
                create_product_submitted = st.form_submit_button("Create product")

            if create_product_submitted:
                payload = {
                    "name": new_product_name.strip(),
                    "price": float(new_product_price),
                    "description": new_product_desc.strip(),
                    "category_id": int(category_by_label[new_product_category]["category_id"]),
                }
                try:
                    created = _safe_post(api_base_url, "/products", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Product #{created['product_id']} created"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Create product failed: {exc}")

        if products and categories:
            product_choice = st.selectbox("Select product to update", product_labels, key="product_update_choice")
            selected_product = product_by_label[product_choice]

            default_category_label = category_label_by_id.get(int(selected_product["category_id"]), category_labels[0])
            category_index = category_labels.index(default_category_label) if default_category_label in category_labels else 0

            with st.form(f"update_product_form_{selected_product['product_id']}"):
                upd_product_name = st.text_input(
                    "Product name",
                    value=str(selected_product["name"]),
                    key=f"upd_product_name_{selected_product['product_id']}",
                )
                upd_product_price = st.number_input(
                    "Product price",
                    min_value=0.01,
                    value=float(selected_product["price"]),
                    step=1.0,
                    key=f"upd_product_price_{selected_product['product_id']}",
                )
                upd_product_desc = st.text_area(
                    "Product description",
                    value=str(selected_product["description"]),
                    key=f"upd_product_desc_{selected_product['product_id']}",
                )
                upd_product_category = st.selectbox(
                    "Category",
                    category_labels,
                    index=category_index,
                    key=f"upd_product_category_{selected_product['product_id']}",
                )
                upd_product_submitted = st.form_submit_button("Update product")

            if upd_product_submitted:
                payload = {
                    "name": upd_product_name.strip(),
                    "price": float(upd_product_price),
                    "description": upd_product_desc.strip(),
                    "category_id": int(category_by_label[upd_product_category]["category_id"]),
                }
                try:
                    _safe_put(api_base_url, f"/products/{selected_product['product_id']}", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Product #{selected_product['product_id']} updated"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Update product failed: {exc}")

        if products:
            st.dataframe(pd.DataFrame(products).sort_values("product_id"), width="stretch", hide_index=True)
        else:
            st.info("No products found.")

    with sales_tab:
        st.subheader("Sales")

        if not products or not countries:
            st.warning("Create at least one product and one country before creating sales.")
        else:
            with st.form("create_sale_form", clear_on_submit=True):
                create_sale_date = st.date_input("Sale date", value=date.today())
                create_sale_product = st.selectbox("Product", product_labels, key="create_sale_product")
                create_sale_country = st.selectbox("Country", country_labels, key="create_sale_country")
                create_sale_units = st.number_input("Units sold", min_value=1, value=10, step=1)
                create_sale_rating = st.slider("Customer rating", min_value=1, max_value=5, value=4)
                create_override_total = st.checkbox("Override total price", value=False, key="create_override_total")

                selected_create_product = product_by_label[create_sale_product]
                computed_total = round(float(selected_create_product["price"]) * int(create_sale_units), 2)
                st.caption(f"Computed total from product price: ${computed_total:,.2f}")

                override_total_value = computed_total
                if create_override_total:
                    override_total_value = st.number_input(
                        "Total price",
                        min_value=0.01,
                        value=float(computed_total),
                        step=1.0,
                    )

                create_sale_submitted = st.form_submit_button("Create sale")

            if create_sale_submitted:
                payload: dict[str, Any] = {
                    "sale_date": create_sale_date.isoformat(),
                    "product_id": int(selected_create_product["product_id"]),
                    "country_id": int(country_by_label[create_sale_country]["country_id"]),
                    "units_sold": int(create_sale_units),
                    "customer_rating": int(create_sale_rating),
                }
                if create_override_total:
                    payload["total_price"] = float(override_total_value)

                try:
                    created = _safe_post(api_base_url, "/sales", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Sale #{created['sale_id']} created"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Create sale failed: {exc}")

        if sales_for_records.empty or not products or not countries:
            st.info("No sales available for updating.")
        else:
            editable_sales = sales_for_records.sort_values("sale_date", ascending=False).copy()
            sales_options = []
            sale_by_label: dict[str, dict[str, Any]] = {}
            for row in editable_sales.to_dict(orient="records"):
                row_date = pd.to_datetime(row["sale_date"]).date()
                label = f"#{int(row['sale_id'])} | {row_date} | {row['product_name']} | {row['country_name']}"
                sales_options.append(label)
                sale_by_label[label] = row

            selected_sale_label = st.selectbox("Select sale to update", sales_options, key="sale_update_choice")
            selected_sale = sale_by_label[selected_sale_label]

            default_product_label = product_label_by_id.get(int(selected_sale["product_id"]), product_labels[0])
            default_country_label = country_label_by_id.get(int(selected_sale["country_id"]), country_labels[0])

            product_index = product_labels.index(default_product_label) if default_product_label in product_labels else 0
            country_index = country_labels.index(default_country_label) if default_country_label in country_labels else 0

            with st.form(f"update_sale_form_{int(selected_sale['sale_id'])}"):
                upd_sale_date = st.date_input(
                    "Sale date",
                    value=pd.to_datetime(selected_sale["sale_date"]).date(),
                    key=f"upd_sale_date_{int(selected_sale['sale_id'])}",
                )
                upd_sale_product = st.selectbox(
                    "Product",
                    product_labels,
                    index=product_index,
                    key=f"upd_sale_product_{int(selected_sale['sale_id'])}",
                )
                upd_sale_country = st.selectbox(
                    "Country",
                    country_labels,
                    index=country_index,
                    key=f"upd_sale_country_{int(selected_sale['sale_id'])}",
                )
                upd_sale_units = st.number_input(
                    "Units sold",
                    min_value=1,
                    value=int(selected_sale["units_sold"]),
                    step=1,
                    key=f"upd_sale_units_{int(selected_sale['sale_id'])}",
                )
                upd_sale_rating = st.slider(
                    "Customer rating",
                    min_value=1,
                    max_value=5,
                    value=int(selected_sale["customer_rating"]),
                    key=f"upd_sale_rating_{int(selected_sale['sale_id'])}",
                )
                upd_override_total = st.checkbox(
                    "Override total price",
                    value=False,
                    key=f"upd_override_total_{int(selected_sale['sale_id'])}",
                )

                selected_upd_product = product_by_label[upd_sale_product]
                computed_upd_total = round(float(selected_upd_product["price"]) * int(upd_sale_units), 2)
                st.caption(
                    f"Current stored total: ${float(selected_sale['total_price']):,.2f}. "
                    f"Computed from selected product price: ${computed_upd_total:,.2f}"
                )

                upd_total_value = computed_upd_total
                if upd_override_total:
                    upd_total_value = st.number_input(
                        "Total price",
                        min_value=0.01,
                        value=float(selected_sale["total_price"]),
                        step=1.0,
                        key=f"upd_total_value_{int(selected_sale['sale_id'])}",
                    )

                upd_sale_submitted = st.form_submit_button("Update sale")

            if upd_sale_submitted:
                payload = {
                    "sale_date": upd_sale_date.isoformat(),
                    "product_id": int(selected_upd_product["product_id"]),
                    "country_id": int(country_by_label[upd_sale_country]["country_id"]),
                    "units_sold": int(upd_sale_units),
                    "customer_rating": int(upd_sale_rating),
                }
                if upd_override_total:
                    payload["total_price"] = float(upd_total_value)

                try:
                    _safe_put(api_base_url, f"/sales/{int(selected_sale['sale_id'])}", payload)
                    clear_data_caches()
                    st.session_state.flash_success = f"Sale #{int(selected_sale['sale_id'])} updated"
                    st.rerun()
                except RuntimeError as exc:
                    st.error(f"Update sale failed: {exc}")

        if not sales_for_records.empty:
            preview_cols = [
                "sale_id",
                "sale_date",
                "region_name",
                "country_name",
                "category_name",
                "product_name",
                "units_sold",
                "total_price",
                "customer_rating",
            ]
            preview_sales = sales_for_records[preview_cols].sort_values("sale_date", ascending=False).copy()
            preview_sales["sale_date"] = pd.to_datetime(preview_sales["sale_date"]).dt.date
            st.dataframe(preview_sales.head(250), width="stretch", hide_index=True)
