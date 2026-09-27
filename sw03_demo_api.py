"""FastAPI app that persists normalized sales data to Parquet files.

Run with:
    uvicorn sw03_demo_api:app            # add --reload only while you edit this file

The four small lookup tables (regions, countries, categories, products) share one generic set of
endpoints. Sales, the resource the lecture follows, have every verb written out at the bottom.
"""

import math
import shutil
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from threading import Lock
from typing import Annotated, Any, NamedTuple

import pandas as pd
from fastapi import FastAPI, HTTPException, Path as PathParam, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
SEED_DIR = DATA_DIR / "seed"
DEFAULT_SALES_LIMIT = 5000


class Table(NamedTuple):
    file: str  # the Parquet file in data/
    id_col: str
    parent: str | None = None  # the table it points at: a country points at a region
    child: str | None = None  # the table that points at it: sales point at a country

    @property
    def noun(self) -> str:  # "region_id" -> "region"
        return self.id_col.removesuffix("_id")


TABLES = {
    "regions": Table("sales_regions.parquet", "region_id", child="countries"),
    "countries": Table("countries.parquet", "country_id", parent="regions", child="sales"),
    "categories": Table("categories.parquet", "category_id", child="products"),
    "products": Table("products.parquet", "product_id", parent="categories", child="sales"),
    "sales": Table("sales.parquet", "sale_id"),
}

# Documented in /docs so students see which errors an endpoint can actually return.
NOT_FOUND = {404: {"description": "No row with that id."}}
BAD_REQUEST = {400: {"description": "The request broke a rule, for example a duplicate name or an unknown id."}}
PARTIAL_PUT = "Fields you leave out keep their current value (the HTTP standard would call this PATCH)."

# Every rule is written once, here, and reused wherever the field appears.
Name = Annotated[str, Field(min_length=1, max_length=120)]
Text = Annotated[str, Field(min_length=1, max_length=300)]
Price = Annotated[float, Field(gt=0, allow_inf_nan=False)]  # JSON 1e999 arrives as inf; ints refuse it anyway
Ref = Annotated[int, Field(ge=1)]  # an id that points at a row in another table
Units = Annotated[int, Field(ge=1, le=100_000)]
Rating = Annotated[int, Field(ge=1, le=5)]
SaleDate = Annotated[date, Field(ge=date(2000, 1, 1), le=date(2100, 12, 31), description="Between 2000-01-01 and 2100-12-31.")]


class Input(BaseModel):
    """What a client may send: stray whitespace is trimmed, unknown fields are refused (422)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RegionCreate(Input):
    name: Name
    description: Text


class RegionUpdate(Input):
    name: Name | None = None
    description: Text | None = None


class Region(BaseModel):
    region_id: int
    name: str
    description: str


class CountryCreate(Input):
    name: Name
    region_id: Ref


class CountryUpdate(Input):
    name: Name | None = None
    region_id: Ref | None = None


class Country(BaseModel):
    country_id: int
    name: str
    region_id: int
    region_name: str


class CategoryCreate(Input):
    name: Name
    description: Text


class CategoryUpdate(Input):
    name: Name | None = None
    description: Text | None = None


class Category(BaseModel):
    category_id: int
    name: str
    description: str


class ProductCreate(Input):
    name: Name
    price: Price
    description: Text
    category_id: Ref


class ProductUpdate(Input):
    name: Name | None = None
    price: Price | None = None
    description: Text | None = None
    category_id: Ref | None = None


class Product(BaseModel):
    product_id: int
    name: str
    price: float
    description: str
    category_id: int
    category_name: str


class SaleCreate(Input):
    """A new sale. There is no total_price: the server computes it from units_sold and the product's price."""

    sale_date: SaleDate
    product_id: Ref
    country_id: Ref
    units_sold: Units
    customer_rating: Rating


class SaleUpdate(Input):
    sale_date: SaleDate | None = None
    product_id: Ref | None = None
    country_id: Ref | None = None
    units_sold: Units | None = None
    customer_rating: Rating | None = None


class Sale(BaseModel):
    """A stored sale plus the names of everything it points at."""

    sale_id: int
    sale_date: date
    units_sold: int
    total_price: float
    customer_rating: int
    product_id: int
    product_name: str
    category_id: int
    category_name: str
    country_id: int
    country_name: str
    region_id: int
    region_name: str


# ponytail: one lock around every read-modify-write of the Parquet files; a real
# database takes over this job once there is more than one server process.
lock = Lock()
# ponytail: kept in memory, which is enough because data/ is reset on every start.
highest_id: dict[str, int] = {}  # per table, the highest id that existed since the start


def reset(table: str) -> None:
    shutil.copyfile(SEED_DIR / TABLES[table].file, DATA_DIR / TABLES[table].file)


def read(table: str) -> pd.DataFrame:
    if not (DATA_DIR / TABLES[table].file).exists():
        reset(table)  # restore only the table that vanished
    return pd.read_parquet(DATA_DIR / TABLES[table].file)


def write(table: str, df: pd.DataFrame) -> None:
    df.to_parquet(DATA_DIR / TABLES[table].file, index=False)


def next_id(table: str, df: pd.DataFrame) -> int:
    """One past the highest id that ever existed, so the id of a deleted row is never handed out again."""
    stored = int(df[TABLES[table].id_col].max()) if len(df) else 0
    highest_id[table] = max(stored, highest_id.get(table, 0)) + 1
    return highest_id[table]


def row_index(df: pd.DataFrame, table: str, row_id: int) -> int:
    """Where the row with this id sits in df, or 404."""
    matches = df.index[df[TABLES[table].id_col] == row_id]
    if matches.empty:
        raise HTTPException(404, f"{TABLES[table].noun.capitalize()} not found")
    return int(matches[0])


def require_exists(table: str, row_id: int) -> pd.Series:
    """The row an id in the request points at, or 400: the request is well formed but asks for the impossible."""
    df = read(table)
    match = df[df[TABLES[table].id_col] == row_id]
    if match.empty:
        raise HTTPException(400, f"{TABLES[table].noun.capitalize()} id {row_id} does not exist")
    return match.iloc[0]


def with_parent_name(table: str, df: pd.DataFrame) -> pd.DataFrame:
    """Add the name of the row each row points at (a country gets region_name), so clients need no join."""
    parent = TABLES[table].parent
    if parent is None:
        return df
    fk = TABLES[parent].id_col
    names = read(parent)[[fk, "name"]].rename(columns={"name": f"{TABLES[parent].noun}_name"})
    return df.merge(names, on=fk, how="left")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Every start begins from the same known data: data/ is reset from data/seed/."""
    for table, t in TABLES.items():
        reset(table)
        highest_id[table] = int(read(table)[t.id_col].max())
    yield


app = FastAPI(
    title="Sales Analysis API",
    version="3.0.0",
    description=(
        "Teaching API for SW03. It is the **logic tier** of a three-tier stack: "
        "Parquet files underneath (data tier), a notebook or Streamlit app on top "
        "(presentation tier).\n\n"
        "Every table supports the four REST verbs: `GET`, `POST`, `PUT`, `DELETE`. "
        "`PUT` here is a *partial* update: fields you leave out keep their current value. "
        "The HTTP standard calls that `PATCH` and expects a `PUT` to replace the whole row; "
        "this API uses `PUT` for both to keep to four verbs.\n\n"
        "On every start, `data/` is reset from `data/seed/`, so you can experiment freely."
    ),
    openapi_tags=[
        {"name": "Service", "description": "Is the API alive, and what values may I choose?"},
        {"name": "Regions", "description": "Sales regions. A region groups countries."},
        {"name": "Countries", "description": "Countries. Each country belongs to one region."},
        {"name": "Categories", "description": "Product categories."},
        {"name": "Products", "description": "Products. Each product belongs to one category."},
        {"name": "Sales", "description": "Individual sales, enriched with product, category, country and region names."},
    ],
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def unprocessable(request: Request, exc: RequestValidationError) -> JSONResponse:
    """FastAPI's own 422, except that a NaN or Infinity it echoes back goes out as text: JSON has no such number."""
    finite = {float: lambda f: f if math.isfinite(f) else str(f)}
    return JSONResponse({"detail": jsonable_encoder(exc.errors(), custom_encoder=finite)}, status_code=422)


@app.get("/", tags=["Service"])
def root() -> dict[str, str]:
    """Friendly landing message. Open /docs for the interactive documentation."""
    return {"message": "Sales Analysis API is running. Open /docs to try it out."}


@app.get("/health", tags=["Service"])
def health() -> dict[str, str]:
    """Liveness check. Answers {"status": "ok"} when the API is reachable."""
    return {"status": "ok"}


@app.get("/meta/options", tags=["Service"])
def meta_options() -> dict[str, Any]:
    """Every value the filters accept: region, country, category and product names, plus the date range."""
    with lock:
        names = {table: sorted(read(table)["name"]) for table in TABLES if table != "sales"}
        dates = read("sales")["sale_date"]
    return names | {
        "min_date": dates.min().date() if len(dates) else None,
        "max_date": dates.max().date() if len(dates) else None,
    }


# --- Regions, countries, categories, products: one generic set of endpoints ---


def add_lookup_endpoints(table: str, model: type[BaseModel], create: type[BaseModel], update: type[BaseModel]) -> None:
    """Register the same five endpoints for one lookup table, e.g. GET /regions/{region_id}."""
    t = TABLES[table]
    tag, one = table.title(), f"/{table}/{{{t.id_col}}}"
    RowId = Annotated[int, PathParam(alias=t.id_col, ge=1)]
    parent = TABLES[t.parent] if t.parent else None
    joined = f" with their {parent.noun} name" if parent else ""
    points = f" and {parent.id_col} must point at an existing {parent.noun}" if parent else ""

    @app.get(f"/{table}", response_model=list[model], tags=[tag], name=f"list_{table}",
             description=f"List all {table}{joined}, sorted by name.")
    def list_rows() -> list[dict[str, Any]]:
        with lock:
            return with_parent_name(table, read(table)).sort_values("name").to_dict("records")

    @app.get(one, response_model=model, tags=[tag], responses=NOT_FOUND, name=f"get_{t.noun}",
             description=f"Fetch one {t.noun} by id.")
    def get_row(row_id: RowId) -> dict[str, Any]:
        with lock:
            df = with_parent_name(table, read(table))
            return df.loc[row_index(df, table, row_id)].to_dict()

    def check_rules(df: pd.DataFrame, values: dict[str, Any], row_id: int | None = None) -> None:
        """Business rules (400): the name is new, ignoring case, and a parent id points at a real row."""
        if "name" in values:
            clash = (df["name"].str.casefold() == values["name"].casefold()) & (df[t.id_col] != row_id)
            if clash.any():
                raise HTTPException(400, f"{t.noun.capitalize()} name '{values['name']}' already exists")
        if parent and parent.id_col in values:
            require_exists(t.parent, values[parent.id_col])

    @app.post(f"/{table}", response_model=model, status_code=201, tags=[tag], responses=BAD_REQUEST,
              name=f"create_{t.noun}", description=f"Create a {t.noun}. The name must be new{points}.")
    def create_row(payload: create) -> dict[str, Any]:
        with lock:
            df = read(table)
            new = payload.model_dump()
            check_rules(df, new)
            new[t.id_col] = next_id(table, df)
            write(table, pd.concat([df, pd.DataFrame([new])], ignore_index=True))
            return with_parent_name(table, pd.DataFrame([new])).iloc[0].to_dict()

    @app.put(one, response_model=model, tags=[tag], responses=NOT_FOUND | BAD_REQUEST,
             name=f"update_{t.noun}", description=f"Update a {t.noun}. {PARTIAL_PUT}")
    def update_row(row_id: RowId, payload: update) -> dict[str, Any]:
        with lock:
            df = read(table)
            i = row_index(df, table, row_id)
            changes = payload.model_dump(exclude_none=True)
            check_rules(df, changes, row_id)
            for column, value in changes.items():
                df.at[i, column] = value
            write(table, df)
            return with_parent_name(table, df.loc[[i]]).iloc[0].to_dict()

    @app.delete(one, status_code=204, tags=[tag], responses=NOT_FOUND | BAD_REQUEST,
                name=f"delete_{t.noun}", description=f"Delete a {t.noun}. Refused while {t.child} still point at it.")
    def delete_row(row_id: RowId) -> None:
        with lock:
            df = read(table)
            i = row_index(df, table, row_id)
            if used_by := int((read(t.child)[t.id_col] == row_id).sum()):
                raise HTTPException(400, f"{t.noun.capitalize()} {row_id} still has {t.child} ({used_by} row(s) still reference it)")
            write(table, df.drop(i))


add_lookup_endpoints("regions", Region, RegionCreate, RegionUpdate)
add_lookup_endpoints("countries", Country, CountryCreate, CountryUpdate)
add_lookup_endpoints("categories", Category, CategoryCreate, CategoryUpdate)
add_lookup_endpoints("products", Product, ProductCreate, ProductUpdate)


# --- Sales: every verb written out, because this is the resource the lecture follows ---

SaleId = Annotated[int, PathParam(ge=1)]


def enriched_sales() -> pd.DataFrame:
    """Sales joined to every name they point at: product, category, country and region."""
    products = with_parent_name("products", read("products")).rename(columns={"name": "product_name"})
    countries = with_parent_name("countries", read("countries")).rename(columns={"name": "country_name"})
    return (
        read("sales")
        .merge(products[["product_id", "product_name", "category_id", "category_name"]], on="product_id", how="left")
        .merge(countries[["country_id", "country_name", "region_id", "region_name"]], on="country_id", how="left")
    )


def sale_record(sale_id: int) -> dict[str, Any]:
    """One sale with every name it points at, or 404."""
    sales = enriched_sales()
    return sales.loc[row_index(sales, "sales", sale_id)].to_dict()


@app.get("/sales", response_model=list[Sale], tags=["Sales"], responses=BAD_REQUEST)
def list_sales(
    *,  # FastAPI passes every filter by name
    region: Annotated[list[str] | None, Query(description="Keep only these region names.")] = None,
    country: Annotated[list[str] | None, Query(description="Keep only these country names.")] = None,
    product: Annotated[list[str] | None, Query(description="Keep only these product names.")] = None,
    category: Annotated[list[str] | None, Query(description="Keep only these category names.")] = None,
    start_date: Annotated[date | None, Query(description="Earliest sale date to include.")] = None,
    end_date: Annotated[date | None, Query(description="Latest sale date to include.")] = None,
    min_rating: Rating | None = None,
    max_rating: Rating | None = None,
    limit: Annotated[int, Query(ge=1, le=20000, description="Maximum rows returned, newest first.")] = DEFAULT_SALES_LIMIT,
) -> list[dict[str, Any]]:
    """Search sales. Every filter is optional; combining them narrows the result."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date must be on or before end_date")
    if min_rating and max_rating and min_rating > max_rating:
        raise HTTPException(400, "min_rating must be less than or equal to max_rating")
    with lock:
        sales = enriched_sales()
    for column, wanted in (("region_name", region), ("country_name", country), ("product_name", product), ("category_name", category)):
        if wanted:
            sales = sales[sales[column].isin(wanted)]
    if start_date:
        sales = sales[sales["sale_date"] >= pd.Timestamp(start_date)]
    if end_date:
        sales = sales[sales["sale_date"] <= pd.Timestamp(end_date)]
    if min_rating:
        sales = sales[sales["customer_rating"] >= min_rating]
    if max_rating:
        sales = sales[sales["customer_rating"] <= max_rating]
    return sales.sort_values(["sale_date", "sale_id"], ascending=False).head(limit).to_dict("records")


@app.get("/sales/{sale_id}", response_model=Sale, tags=["Sales"], responses=NOT_FOUND)
def get_sale(sale_id: SaleId) -> dict[str, Any]:
    """Fetch one sale by id, enriched with product, category, country and region names."""
    with lock:
        return sale_record(sale_id)


@app.post("/sales", response_model=Sale, status_code=201, tags=["Sales"], responses=BAD_REQUEST)
def create_sale(payload: SaleCreate) -> dict[str, Any]:
    """Record a sale. The server computes total_price as units_sold x the product's price."""
    with lock:
        product = require_exists("products", payload.product_id)  # 400 when it points at nothing
        require_exists("countries", payload.country_id)
        sales = read("sales")
        new = payload.model_dump() | {
            "sale_id": next_id("sales", sales),
            "sale_date": pd.Timestamp(payload.sale_date),  # the file stores a datetime column
            "total_price": round(float(product["price"]) * payload.units_sold, 2),
        }
        write("sales", pd.concat([sales, pd.DataFrame([new])], ignore_index=True))
        return sale_record(new["sale_id"])


@app.put("/sales/{sale_id}", response_model=Sale, tags=["Sales"], responses=NOT_FOUND | BAD_REQUEST)
def update_sale(sale_id: SaleId, payload: SaleUpdate) -> dict[str, Any]:
    """Update a sale. Fields you leave out keep their current value (the HTTP standard would call this PATCH).

    total_price is recomputed only when units_sold or product_id actually change, so editing just
    the rating keeps the stored total.
    """
    with lock:
        sales = read("sales")
        i = row_index(sales, "sales", sale_id)
        old = sales.loc[i].to_dict()
        new = old | payload.model_dump(exclude_none=True)
        product = require_exists("products", new["product_id"])  # 400 when it points at nothing
        require_exists("countries", new["country_id"])
        new["sale_date"] = pd.Timestamp(new["sale_date"])
        if (new["units_sold"], new["product_id"]) != (old["units_sold"], old["product_id"]):
            new["total_price"] = round(float(product["price"]) * new["units_sold"], 2)
        for column, value in new.items():
            sales.at[i, column] = value
        write("sales", sales)
        return sale_record(sale_id)


@app.delete("/sales/{sale_id}", status_code=204, tags=["Sales"], responses=NOT_FOUND)
def delete_sale(sale_id: SaleId) -> None:
    """Delete a sale. Nothing points at a sale, so it is never refused; a second delete answers 404."""
    with lock:
        sales = read("sales")
        write("sales", sales.drop(row_index(sales, "sales", sale_id)))
