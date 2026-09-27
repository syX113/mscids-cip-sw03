"""Streamlit front end for the Sales Analysis API: a dashboard plus create/update forms.

Start the API first, then run:
    streamlit run sw03_demo_streamlit.py

Font, colours and the chart palette live in .streamlit/config.toml.
"""

import statistics
from collections.abc import Callable
from datetime import date
from typing import Any

import altair as alt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Sales Analysis Dashboard", page_icon=":material/monitoring:", layout="wide")

DEFAULT_API_URL = "http://127.0.0.1:8000"
API_COMMAND = "uvicorn sw03_demo_api:app --host 127.0.0.1 --port 8000"

# What the dashboard can group by (label -> column) and measure (label -> column, aggregation, d3 number format).
# Money is in francs: "$" in a d3 format prints the currency the chart theme below sets, "CHF ".
DIMENSIONS = {
    "Sales Region": "region_name",
    "Country": "country_name",
    "Category": "category_name",
    "Product": "product_name",
}
METRICS = {
    "Total Sales": ("total_price", "sum", "$.3~s"),
    "Units Sold": ("units_sold", "sum", ",.0f"),
    "Average Rating": ("customer_rating", "mean", ".2f"),
}
PREDICTORS = {
    "Average Order Value": ("total_price", "mean", "$,.0f"),
    "Average Units Sold": ("units_sold", "mean", ",.1f"),
    "Total Sales": ("total_price", "sum", "$,.0f"),
    "Total Units Sold": ("units_sold", "sum", ",.0f"),
}
REGRESSION_LEVELS = {  # level -> (one dot per ..., coloured by)
    "Product (monthly)": ("product_name", "Category"),
    "Country (monthly)": ("country_name", "Sales Region"),
    "Category (monthly)": ("category_name", "Category"),
    "Sales Region (monthly)": ("region_name", "Sales Region"),
    "Sale": ("sale_id", "Category"),
}
# Human headers for every table the app shows.
COLUMNS = {
    "sale_id": st.column_config.NumberColumn("Sale", format="#%d"),
    "region_id": st.column_config.NumberColumn("Region #"),
    "country_id": st.column_config.NumberColumn("Country #"),
    "category_id": st.column_config.NumberColumn("Category #"),
    "product_id": st.column_config.NumberColumn("Product #"),
    "name": "Name",
    "description": "Description",
    "price": st.column_config.NumberColumn("Unit price", format="CHF %,.2f"),
    "sale_date": st.column_config.DateColumn("Date", format="D MMM YYYY"),
    "region_name": "Region",
    "country_name": "Country",
    "category_name": "Category",
    "product_name": "Product",
    "units_sold": st.column_config.NumberColumn("Units", format="%,d"),
    "total_price": st.column_config.NumberColumn("Total", format="CHF %,.2f"),
    "customer_rating": st.column_config.NumberColumn("Rating", format="%d ★"),
}
# Sales tables show the names the API joined in, not the ids behind them.
SALE_COLUMNS = [
    "sale_date",
    "region_name",
    "country_name",
    "category_name",
    "product_name",
    "units_sold",
    "total_price",
    "customer_rating",
]


@alt.theme.register("projector", enable=True)
def projector_theme() -> alt.theme.ThemeConfig:
    """On top of Streamlit's chart theme: darker, larger axis and legend text, no chart background, francs."""
    text = {"labelColor": "#3f5b5f", "titleColor": "#3f5b5f", "labelFontSize": 13, "titleFontSize": 14}
    francs = {"number": {"decimal": ".", "thousands": ",", "grouping": [3], "currency": ["CHF ", ""]}}
    return {"config": {"background": "transparent", "axis": text, "legend": text, "locale": francs}}


def error_text(response: requests.Response) -> str:
    try:
        detail = response.json()["detail"]
    except (ValueError, KeyError, TypeError):
        detail = response.text.strip()
    if isinstance(detail, list):  # 422 from pydantic: one entry per rejected field
        detail = "\n".join(f"- **{error['loc'][-1]}**: {error['msg']}" for error in detail)
    return f"{response.status_code} {response.reason}\n\n{detail}"


def api(method: str, url: str, **kwargs: Any) -> Any:
    """One request to the API: the JSON body, or a RuntimeError that reads well on screen."""
    try:
        response = requests.request(method, url, timeout=5, **kwargs)
        if response.ok:
            return response.json()
    except requests.RequestException as exc:  # no connection, a timeout, or a body that is not JSON
        raise RuntimeError(f"No usable answer from {url} ({type(exc).__name__})") from None
    raise RuntimeError(error_text(response))


# Short TTLs, so changes made from /docs or the notebook show up here within seconds.
@st.cache_data(ttl="15s", show_spinner=False)
def fetch_json(url: str) -> Any:
    return api("GET", url)


@st.cache_data(ttl="15s", show_spinner="Loading sales…")
def fetch_sales(url: str, params: dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(api("GET", url, params=params))  # requests repeats list values: ?region=Asia&region=Europe
    if not df.empty:
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        df["month"] = df["sale_date"].dt.to_period("M").dt.to_timestamp()
    return df


def line_chart(df: pd.DataFrame, metric: str, compare: str, split_by_category: bool) -> alt.Chart:
    column, agg, fmt = METRICS[metric]
    groups = ["month", DIMENSIONS[compare]] + (["category_name"] if split_by_category else [])
    monthly = df.groupby(groups, as_index=False).agg(value=(column, agg))
    chart = (
        alt.Chart(monthly)
        .mark_line(point=not split_by_category, strokeWidth=2)
        .encode(
            x=alt.X("month:T", title="Month", axis=alt.Axis(format="%b %Y")),
            y=alt.Y("value:Q", title=metric, axis=alt.Axis(format=fmt)),
            color=alt.Color(f"{DIMENSIONS[compare]}:N", title=compare),
            tooltip=[
                alt.Tooltip("month:T", title="Month", format="%b %Y"),
                alt.Tooltip(f"{DIMENSIONS[compare]}:N", title=compare),
                *([alt.Tooltip("category_name:N", title="Category")] if split_by_category else []),
                alt.Tooltip("value:Q", title=metric, format=fmt),
            ],
        )
    )
    if split_by_category:
        dashes = alt.Scale(range=[[1, 0], [8, 4], [2, 3]])  # solid, dashed, dotted: tellable apart at a glance
        legend = alt.Legend(symbolType="stroke", symbolSize=500, symbolStrokeColor="#3f5b5f", symbolStrokeWidth=2)
        chart = chart.encode(
            strokeDash=alt.StrokeDash("category_name:N", title="Category", scale=dashes, legend=legend)
        )
    return chart.properties(height=380)


def heatmap(df: pd.DataFrame, rows: str, columns: str, metric: str) -> alt.LayerChart:
    column, agg, fmt = METRICS[metric]
    cells = df.groupby([DIMENSIONS[rows], DIMENSIONS[columns]], as_index=False).agg(value=(column, agg))
    ranked = alt.EncodingSortField("value", op=agg, order="descending")  # biggest row and column first
    base = alt.Chart(cells).encode(
        x=alt.X(
            f"{DIMENSIONS[columns]}:N",
            title=columns,
            sort=ranked,
            axis=alt.Axis(labelAngle=0, labelExpr="split(datum.label, ' ')", labelOverlap=False, labelFlush=False),
        ),
        y=alt.Y(f"{DIMENSIONS[rows]}:N", title=rows, sort=ranked),
    )
    rects = base.mark_rect(cornerRadius=4, stroke="white", strokeWidth=2).encode(
        color=alt.Color("value:Q", title=metric, legend=alt.Legend(format=fmt)),
        tooltip=[
            alt.Tooltip(f"{DIMENSIONS[rows]}:N", title=rows),
            alt.Tooltip(f"{DIMENSIONS[columns]}:N", title=columns),
            alt.Tooltip("value:Q", title=metric, format=fmt),
        ],
    )
    labels = base.mark_text(fontSize=13).encode(text=alt.Text("value:Q", format=fmt))
    return (rects + labels).properties(height=alt.Step(44))


def regression_points(df: pd.DataFrame, level: str) -> pd.DataFrame:
    """One row per dot: its average rating plus every predictor, aggregated at the chosen level."""
    entity, colour = REGRESSION_LEVELS[level]
    dot = "#" + df[entity].astype(str) if level == "Sale" else df[entity] + " | " + df["month"].dt.strftime("%Y-%m")
    return (
        df.groupby([dot.rename("Dot"), df[DIMENSIONS[colour]].rename(colour)])
        .agg(
            **{"Average Rating": ("customer_rating", "mean")},
            **{x: (column, agg) for x, (column, agg, _) in PREDICTORS.items()},
        )
        .reset_index()
    )


def regression_chart(points: pd.DataFrame, x: str, colour: str) -> tuple[alt.LayerChart, str] | None:
    try:
        slope, intercept = statistics.linear_regression(points[x], points["Average Rating"])
        r_squared = statistics.correlation(points[x], points["Average Rating"]) ** 2
    except statistics.StatisticsError:  # fewer than two dots, or a column that never varies
        return None
    x_format = PREDICTORS[x][2]
    dots = (
        alt.Chart(points)
        .mark_point(filled=True, size=70, opacity=0.7)
        .encode(
            x=alt.X(f"{x}:Q", scale=alt.Scale(zero=False), axis=alt.Axis(format=x_format)),
            y=alt.Y("Average Rating:Q", scale=alt.Scale(domain=[1, 5])),
            color=f"{colour}:N",
            shape=f"{colour}:N",  # a second cue next to colour, for colour-blind readers
            tooltip=["Dot", alt.Tooltip(f"{x}:Q", format=x_format), alt.Tooltip("Average Rating:Q", format=".2f")],
        )
    )
    trend = alt.Chart(points).transform_regression(x, "Average Rating").mark_line(color="#0b2a2e", strokeWidth=2.5)
    trend = trend.encode(x=f"{x}:Q", y="Average Rating:Q")
    sign = "+" if slope >= 0 else "−"
    caption = (
        f"Model: rating = {intercept:.2f} {sign} {abs(slope):.3g} × {x.lower()}"
        f" · R² = {r_squared:.2f} · n = {len(points):,} dots"
    )
    return (dots + trend).properties(height=420), caption


def dashboard(api_url: str) -> None:
    options = fetch_json(f"{api_url}/meta/options")
    first = date.fromisoformat(options["min_date"]) if options["min_date"] else date.today()  # None: no sales yet
    last = date.fromisoformat(options["max_date"]) if options["max_date"] else date.today()

    with st.container(border=True):
        c1, c2, c3 = st.columns([4, 3, 3])
        regions = c1.pills("Sales Region", options["regions"], selection_mode="multi")
        categories = c2.pills("Category", options["categories"], selection_mode="multi")
        picked = c3.date_input("Date range", (first, last), min_value=first, max_value=last, format="YYYY-MM-DD")
        c1, c2 = st.columns(2)
        countries = c1.multiselect("Country", options["countries"], placeholder="All countries")
        products = c2.multiselect("Product", options["products"], placeholder="All products")
        st.caption("A filter with nothing picked keeps everything.")
    start, end = picked if len(picked) == 2 else (first, last)
    params = {"region": regions, "country": countries, "category": categories, "product": products}
    sales = fetch_sales(f"{api_url}/sales", params | {"start_date": start, "end_date": end, "limit": 20000})
    if sales.empty:
        st.info("No sales match these filters.", icon=":material/filter_alt_off:")
        return

    total = sales["total_price"].sum()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Transactions", len(sales), format="%,d", border=True)
    k2.metric("Total Sales", f"CHF {total / 1e6:,.1f}M" if total >= 1e6 else f"CHF {total:,.0f}", border=True)
    k3.metric("Units Sold", int(sales["units_sold"].sum()), format="%,d", border=True)
    k4.metric("Average Rating", f"{sales['customer_rating'].mean():.2f} / 5", border=True)

    with st.container(border=True):
        st.subheader("Sales over time")
        c1, c2, c3 = st.columns(3, vertical_alignment="bottom")
        metric = c1.selectbox("Metric", list(METRICS))
        compare = c2.selectbox("Compare lines by", list(DIMENSIONS))
        split = c3.checkbox("Split by category", disabled=compare == "Category")
        st.altair_chart(line_chart(sales, metric, compare, split and compare != "Category"), width="stretch")

    with st.container(border=True):
        st.subheader("Sales heatmap")
        c1, c2, c3 = st.columns(3)
        rows = c1.selectbox("Rows", ["Sales Region", "Country"], index=1)
        columns = c2.selectbox("Columns", ["Category", "Product"])
        metric = c3.selectbox("Cell value", list(METRICS))
        st.altair_chart(heatmap(sales, rows, columns, metric), width="stretch")

    with st.container(border=True):
        st.subheader("What goes with a good rating?")
        c1, c2 = st.columns(2)
        level = c1.selectbox("Aggregation level", list(REGRESSION_LEVELS))
        x = c2.selectbox("Predictor (X)", list(PREDICTORS))
        st.caption(
            "Monthly levels average many sales into one dot: fewer, smoother dots"
            " and a higher R² than single sales support (lecture ch. 10)."
        )
        fitted = regression_chart(regression_points(sales, level), x, REGRESSION_LEVELS[level][1])
        if fitted is None:
            st.info("Too little variation in the filtered sales to fit a line.")
        else:
            st.altair_chart(fitted[0], width="stretch")
            st.caption(fitted[1])

    with st.expander("All filtered sales, newest first"):  # a constant label, so a filter click keeps it open
        st.dataframe(sales.set_index("sale_id"), column_order=SALE_COLUMNS, column_config=COLUMNS)


def save(method: str, url: str, payload: dict[str, Any], noun: str, id_col: str, pick_key: str) -> None:
    """Send one write. On success: toast, fresh data, and the edit box shows the saved row if it is listed."""
    try:
        row = api(method, url, json=payload)
    except RuntimeError as exc:
        st.error(str(exc), title=f"The API refused this {noun}", icon=":material/block:")
        return
    st.cache_data.clear()
    st.session_state.saves += 1  # new form keys, so the create forms start empty again
    st.session_state.reselect = {pick_key: row[id_col]}
    st.session_state.flash = f"{'Created' if method == 'POST' else 'Updated'} {noun} #{row[id_col]}"
    st.rerun()


def record_tab(
    api_url: str,
    noun: str,
    path: str,
    id_col: str,
    rows: list[dict[str, Any]],
    fields: Callable[[dict[str, Any]], dict[str, Any]],
    label: Callable[[dict[str, Any]], str],
    column_order: list[str] | None = None,
) -> None:
    """The table as the API returns it, then a create form and an edit form side by side."""
    table = pd.DataFrame(rows).set_index(id_col)
    # Lookup tables read in id order, so a new row lands at the bottom; sales stay newest first.
    st.dataframe(table if column_order else table.sort_index(), column_order=column_order, column_config=COLUMNS)
    by_id = {row[id_col]: row for row in rows}
    pick_key = f"pick {path}"
    new, edit = st.columns(2, gap="large")
    with new.container(border=True):
        st.subheader(f"New {noun}", anchor=False)
        with st.form(f"new {path} {st.session_state.saves}", border=False):
            payload = fields({})
            if st.form_submit_button(f"Create {noun}", type="primary", icon=":material/add:"):
                save("POST", f"{api_url}{path}", payload, noun, id_col, pick_key)
    with edit.container(border=True):
        st.subheader(f"Edit {noun}", anchor=False)
        picked = st.selectbox(f"Pick a {noun}", list(by_id), format_func=lambda i: label(by_id[i]), key=pick_key)
        with st.form(f"edit {path} {picked}", border=False):
            payload = fields(by_id[picked])
            if st.form_submit_button(f"Update {noun}", type="primary", icon=":material/save:"):
                save("PUT", f"{api_url}{path}/{picked}", payload, noun, id_col, pick_key)


def choose(
    label: str, rows: list[dict[str, Any]], id_col: str, current: dict[str, Any], text: Callable[[dict[str, Any]], str]
) -> Any:
    """A selectbox over rows that returns the id, preselecting the one the record points at now."""
    by_id = {row[id_col]: row for row in rows}
    ids = list(by_id)
    return st.selectbox(
        label, ids, index=ids.index(current[id_col]) if current else 0, format_func=lambda i: text(by_id[i])
    )


def records(api_url: str) -> None:
    regions, countries, categories, products = (
        fetch_json(f"{api_url}/{table}") for table in ("regions", "countries", "categories", "products")
    )
    sales = fetch_sales(f"{api_url}/sales", {"limit": 200}).to_dict("records")  # the API sends newest first

    def name(row: dict[str, Any]) -> str:
        return row["name"]

    def country_name(row: dict[str, Any]) -> str:
        return f"{row['name']} ({row['region_name']})"

    def product_name(row: dict[str, Any]) -> str:
        return f"{row['name']} · CHF {row['price']:,.2f}"

    def sale_name(row: dict[str, Any]) -> str:
        return f"#{row['sale_id']} · {row['sale_date']:%d %b %Y} · {row['product_name']} · {row['country_name']}"

    def described(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": st.text_input("Name", row.get("name", "")),
            "description": st.text_area("Description", row.get("description", "")),
        }

    def country(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": st.text_input("Name", row.get("name", "")),
            "region_id": choose("Sales region", regions, "region_id", row, name),
        }

    def product(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": st.text_input("Name", row.get("name", "")),
            "price": st.number_input(
                "Unit price (CHF)", min_value=0.01, value=row.get("price", 100.0), step=1.0, format="%.2f"
            ),
            "description": st.text_area("Description", row.get("description", "")),
            "category_id": choose("Category", categories, "category_id", row, name),
        }

    def sale(row: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "sale_date": st.date_input(
                "Sale date", row.get("sale_date", date.today()), format="YYYY-MM-DD"
            ).isoformat(),
            "product_id": choose("Product", products, "product_id", row, product_name),
            "country_id": choose("Country", countries, "country_id", row, country_name),
            "units_sold": st.number_input("Units sold", min_value=1, value=row.get("units_sold", 10), step=1),
            "customer_rating": st.slider("Customer rating", 1, 5, row.get("customer_rating", 4)),
        }
        if row:
            st.caption(
                f"Stored total: CHF {row['total_price']:,.2f}. The API recomputes it when units or product change."
            )
        else:
            st.caption("No total to type: the API computes units × unit price.")
        return payload

    region_tab, country_tab, category_tab, product_tab, sale_tab = st.tabs(
        ["Sales Regions", "Countries", "Categories", "Products", "Sales"]
    )
    with region_tab:
        record_tab(api_url, "region", "/regions", "region_id", regions, described, name)
    with country_tab:
        record_tab(api_url, "country", "/countries", "country_id", countries, country, country_name)
    with category_tab:
        record_tab(api_url, "category", "/categories", "category_id", categories, described, name)
    with product_tab:
        record_tab(api_url, "product", "/products", "product_id", products, product, product_name)
    with sale_tab:
        st.caption(
            "The 200 most recent sales by date. A sale saved with an older date drops out of this list;"
            " /docs reaches every sale."
        )
        record_tab(api_url, "sale", "/sales", "sale_id", sales, sale, sale_name, SALE_COLUMNS)


st.session_state.setdefault("saves", 0)
st.session_state.update(st.session_state.pop("reselect", {}))  # before any widget: select the row just saved
if flash := st.session_state.pop("flash", None):
    st.toast(flash, icon=":material/check_circle:")

# The look config.toml cannot express: a soft teal-to-cream page, a tinted hero card, larger tab labels,
# and less empty space above the hero (with the header strip transparent, also when the sidebar is collapsed).
st.html(
    """<style>
    .stApp {
      background:
        radial-gradient(840px 520px at -8% 0%, rgba(180, 234, 239, 0.42), transparent 60%),
        radial-gradient(920px 520px at 105% -5%, rgba(194, 239, 214, 0.39), transparent 60%),
        radial-gradient(720px 440px at 50% 105%, rgba(251, 239, 187, 0.32), transparent 64%),
        linear-gradient(180deg, #edf9fb 0%, #f8feff 38%, #f5fdf4 72%, #fffdf2 100%);
    }
    .st-key-hero { background: linear-gradient(120deg, #ffffff 0%, #eaf8f9 60%, #dff3f4 100%); }
    [data-testid="stTab"] p { font-size: 1.05rem; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { padding-top: 4rem; }
    </style>"""
)

api_base_url = st.sidebar.text_input("FastAPI base URL", DEFAULT_API_URL).strip().rstrip("/") or DEFAULT_API_URL

with st.container(border=True, key="hero"):
    st.title("Sales Analysis Dashboard", anchor=False)
    st.write(
        "Explore sales by region, country, product and category, and manage the records behind them through the API."
    )

try:
    healthy = api("GET", f"{api_base_url}/health") == {"status": "ok"}
    problem = "" if healthy else "It answered, but not like the Sales Analysis API."
except RuntimeError as exc:
    problem = str(exc)
if problem:
    st.error(f"Cannot reach the Sales Analysis API at **{api_base_url}**.", icon=":material/cloud_off:")
    st.write("Start it in another terminal, or fix the base URL in the sidebar:")
    st.code(API_COMMAND, language="bash")
    st.caption(problem)
    st.button("Try again", icon=":material/refresh:")
    st.stop()
st.sidebar.badge("API connected", icon=":material/check_circle:", color="green")

dashboard_tab, records_tab = st.tabs([":material/monitoring: Dashboard", ":material/table_edit: Records"])
with dashboard_tab:
    dashboard(api_base_url)
with records_tab:
    records(api_base_url)
