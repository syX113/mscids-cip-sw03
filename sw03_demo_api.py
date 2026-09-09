"""FastAPI app that persists normalized sales data to Parquet files.

Run with:
    uvicorn sw03_demo_api:app --reload
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Path as PathParam, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
TABLE_PATHS = {
    "regions": DATA_DIR / "sales_regions.parquet",
    "countries": DATA_DIR / "countries.parquet",
    "categories": DATA_DIR / "categories.parquet",
    "products": DATA_DIR / "products.parquet",
    "sales": DATA_DIR / "sales.parquet",
}
SEED_DATA_DIR = DATA_DIR / "seed"
SEED_TABLE_PATHS = {table_name: SEED_DATA_DIR / table_path.name for table_name, table_path in TABLE_PATHS.items()}
DEFAULT_SALES_LIMIT = 5000

# Documented in /docs so students see which errors an endpoint can actually return.
NOT_FOUND = {404: {"description": "No row with that id."}}
BAD_REQUEST = {400: {"description": "The request broke a rule, for example a duplicate name or an unknown id."}}


def _clean_required_text(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty")
    return cleaned


class SalesRegion(BaseModel):
    region_id: int
    name: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1, max_length=240)


class SalesRegionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1, max_length=240)


class SalesRegionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    description: str | None = Field(default=None, min_length=1, max_length=240)


class Country(BaseModel):
    country_id: int
    name: str = Field(min_length=1, max_length=80)
    region_id: int
    region_name: str = Field(min_length=1, max_length=40)


class CountryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    region_id: int = Field(ge=1)


class CountryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    region_id: int | None = Field(default=None, ge=1)


class Category(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=240)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=240)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, min_length=1, max_length=240)


class Product(BaseModel):
    product_id: int
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=300)
    category_id: int
    category_name: str


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=300)
    category_id: int = Field(ge=1)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    price: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1, max_length=300)
    category_id: int | None = Field(default=None, ge=1)


class Sale(BaseModel):
    sale_id: int
    sale_date: date
    units_sold: int = Field(ge=1)
    total_price: float = Field(gt=0)
    customer_rating: int = Field(ge=1, le=5)
    product_id: int
    product_name: str
    category_id: int
    category_name: str
    country_id: int
    country_name: str
    region_id: int
    region_name: str


class SaleCreate(BaseModel):
    sale_date: date
    product_id: int = Field(ge=1)
    country_id: int = Field(ge=1)
    units_sold: int = Field(ge=1, le=100000)
    total_price: float | None = Field(default=None, gt=0)
    customer_rating: int = Field(ge=1, le=5)


class SaleUpdate(BaseModel):
    sale_date: date | None = None
    product_id: int | None = Field(default=None, ge=1)
    country_id: int | None = Field(default=None, ge=1)
    units_sold: int | None = Field(default=None, ge=1, le=100000)
    total_price: float | None = Field(default=None, gt=0)
    customer_rating: int | None = Field(default=None, ge=1, le=5)


class SalesRepository:
    def __init__(self, table_paths: dict[str, Path]) -> None:
        self.table_paths = table_paths
        self._lock = Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Always reset working parquet files from the seed set at API startup.
        self._seed_store()

    @staticmethod
    def _required_columns() -> dict[str, set[str]]:
        return {
            "regions": {"region_id", "name", "description"},
            "countries": {"country_id", "name", "region_id"},
            "categories": {"category_id", "name", "description"},
            "products": {"product_id", "name", "price", "description", "category_id"},
            "sales": {"sale_id", "sale_date", "product_id", "country_id", "units_sold", "total_price", "customer_rating"},
        }

    def _seed_store(self) -> None:
        required_columns = self._required_columns()
        missing_seed_tables = [
            table_name for table_name, seed_path in SEED_TABLE_PATHS.items() if not seed_path.exists()
        ]
        if missing_seed_tables:
            missing_list = ", ".join(missing_seed_tables)
            raise RuntimeError(
                f"Missing seed parquet files for tables: {missing_list}. "
                f"Expected files in '{SEED_DATA_DIR}'."
            )

        for table_name in self.table_paths:
            seed_df = pd.read_parquet(SEED_TABLE_PATHS[table_name])
            if not required_columns[table_name].issubset(set(seed_df.columns)):
                raise RuntimeError(
                    f"Seed parquet for '{table_name}' is missing required columns. "
                    f"Expected at least: {sorted(required_columns[table_name])}"
                )
            self._write(table_name, seed_df)

    def _read(self, table_name: str) -> pd.DataFrame:
        path = self.table_paths[table_name]
        if not path.exists():
            # Restore only the table that vanished; the other four keep their data.
            self._write(table_name, pd.read_parquet(SEED_TABLE_PATHS[table_name]))
        df = pd.read_parquet(path)
        if table_name == "sales" and "sale_date" in df.columns:
            df["sale_date"] = pd.to_datetime(df["sale_date"])
        return df

    def _write(self, table_name: str, df: pd.DataFrame) -> None:
        path = self.table_paths[table_name]
        data = df.copy()
        if table_name == "sales" and "sale_date" in data.columns:
            data["sale_date"] = pd.to_datetime(data["sale_date"])
        path.parent.mkdir(parents=True, exist_ok=True)
        data.to_parquet(path, index=False)

    @staticmethod
    def _next_id(df: pd.DataFrame, id_col: str) -> int:
        if df.empty:
            return 1
        return int(df[id_col].max()) + 1

    @staticmethod
    def _ensure_unique_name(
        df: pd.DataFrame,
        *,
        col: str,
        value: str,
        entity_name: str,
        id_col: str,
        ignore_id: int | None = None,
    ) -> None:
        candidate = value.strip().lower()
        if not candidate:
            raise ValueError(f"{entity_name} name cannot be empty")

        normalized = df[col].fillna("").astype(str).str.strip().str.lower()
        duplicates = normalized == candidate
        if ignore_id is not None:
            duplicates = duplicates & (df[id_col].astype(int) != int(ignore_id))
        if duplicates.any():
            raise ValueError(f"{entity_name} name '{value.strip()}' already exists")

    @staticmethod
    def _get_enriched_countries(countries: pd.DataFrame, regions: pd.DataFrame) -> pd.DataFrame:
        """Add each country's region name, so the client does not have to join it itself."""
        region_lookup = regions.rename(columns={"name": "region_name"})[["region_id", "region_name"]]
        return countries.merge(region_lookup, on="region_id", how="left")

    @staticmethod
    def _get_enriched_products(products: pd.DataFrame, categories: pd.DataFrame) -> pd.DataFrame:
        """Add each product's category name."""
        category_lookup = categories.rename(columns={"name": "category_name"})[["category_id", "category_name"]]
        return products.merge(category_lookup, on="category_id", how="left")

    def _get_enriched_sales(self) -> pd.DataFrame:
        sales = self._read("sales")
        products = self._read("products").rename(
            columns={
                "name": "product_name",
                "price": "product_price",
            }
        )
        categories = self._read("categories").rename(columns={"name": "category_name"})
        countries = self._read("countries").rename(columns={"name": "country_name"})
        regions = self._read("regions").rename(columns={"name": "region_name"})

        if sales.empty:
            return pd.DataFrame(
                columns=[
                    "sale_id",
                    "sale_date",
                    "units_sold",
                    "total_price",
                    "customer_rating",
                    "product_id",
                    "product_name",
                    "category_id",
                    "category_name",
                    "country_id",
                    "country_name",
                    "region_id",
                    "region_name",
                ]
            )

        merged = sales.merge(products[["product_id", "product_name", "product_price", "category_id"]], on="product_id", how="left")
        merged = merged.merge(categories[["category_id", "category_name"]], on="category_id", how="left")
        merged = merged.merge(countries[["country_id", "country_name", "region_id"]], on="country_id", how="left")
        merged = merged.merge(regions[["region_id", "region_name"]], on="region_id", how="left")

        if merged["total_price"].isna().any():
            recalculated = (merged["units_sold"] * merged["product_price"]).round(2)
            merged["total_price"] = merged["total_price"].fillna(recalculated)

        merged["sale_date"] = pd.to_datetime(merged["sale_date"])
        return merged

    @staticmethod
    def _format_sales_records(df: pd.DataFrame) -> list[dict[str, Any]]:
        if df.empty:
            return []

        ordered = df[
            [
                "sale_id",
                "sale_date",
                "units_sold",
                "total_price",
                "customer_rating",
                "product_id",
                "product_name",
                "category_id",
                "category_name",
                "country_id",
                "country_name",
                "region_id",
                "region_name",
            ]
        ].copy()
        ordered["sale_date"] = ordered["sale_date"].dt.date
        return ordered.to_dict(orient="records")

    def options(self) -> dict[str, Any]:
        with self._lock:
            regions = self._read("regions")
            countries = self._read("countries")
            categories = self._read("categories")
            products = self._read("products")
            sales = self._read("sales")

        min_date = None
        max_date = None
        if not sales.empty:
            sales["sale_date"] = pd.to_datetime(sales["sale_date"])
            min_date = sales["sale_date"].min().date().isoformat()
            max_date = sales["sale_date"].max().date().isoformat()

        return {
            "regions": regions.sort_values("name")["name"].tolist(),
            "countries": countries.sort_values("name")["name"].tolist(),
            "categories": categories.sort_values("name")["name"].tolist(),
            "products": products.sort_values("name")["name"].tolist(),
            "ratings": [1, 2, 3, 4, 5],
            "min_date": min_date,
            "max_date": max_date,
        }

    def list_regions(self) -> list[dict[str, Any]]:
        with self._lock:
            regions = self._read("regions")
        return regions.sort_values("name").to_dict(orient="records")

    def get_region(self, region_id: int) -> dict[str, Any] | None:
        with self._lock:
            regions = self._read("regions")
        match = regions.loc[regions["region_id"] == region_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def create_region(self, payload: SalesRegionCreate) -> dict[str, Any]:
        with self._lock:
            regions = self._read("regions")
            record = payload.model_dump()
            record["name"] = _clean_required_text(str(record["name"]), field_name="Region name")
            record["description"] = _clean_required_text(
                str(record["description"]), field_name="Region description"
            )
            self._ensure_unique_name(
                regions,
                col="name",
                value=record["name"],
                entity_name="Region",
                id_col="region_id",
            )
            record["region_id"] = self._next_id(regions, "region_id")
            updated = pd.concat([regions, pd.DataFrame([record])], ignore_index=True)
            self._write("regions", updated)

        return record

    def update_region(self, region_id: int, payload: SalesRegionUpdate) -> dict[str, Any] | None:
        with self._lock:
            regions = self._read("regions")
            idx = regions.index[regions["region_id"] == region_id].tolist()
            if not idx:
                return None

            patch = payload.model_dump(exclude_unset=True, exclude_none=True)
            row_index = idx[0]

            if "name" in patch:
                patch["name"] = _clean_required_text(str(patch["name"]), field_name="Region name")
                self._ensure_unique_name(
                    regions,
                    col="name",
                    value=patch["name"],
                    entity_name="Region",
                    id_col="region_id",
                    ignore_id=region_id,
                )
            if "description" in patch:
                patch["description"] = _clean_required_text(
                    str(patch["description"]), field_name="Region description"
                )

            for key, value in patch.items():
                regions.at[row_index, key] = value

            self._write("regions", regions)
            return regions.loc[row_index].to_dict()

    def list_countries(self) -> list[dict[str, Any]]:
        with self._lock:
            countries = self._read("countries")
            regions = self._read("regions")
            enriched = self._get_enriched_countries(countries=countries, regions=regions)
        return enriched.sort_values("name").to_dict(orient="records")

    def get_country(self, country_id: int) -> dict[str, Any] | None:
        with self._lock:
            countries = self._read("countries")
            regions = self._read("regions")
            enriched = self._get_enriched_countries(countries=countries, regions=regions)
        match = enriched.loc[enriched["country_id"] == country_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def create_country(self, payload: CountryCreate) -> dict[str, Any]:
        with self._lock:
            countries = self._read("countries")
            regions = self._read("regions")
            if regions.loc[regions["region_id"] == payload.region_id].empty:
                raise ValueError(f"Region id {payload.region_id} does not exist")

            record = payload.model_dump()
            record["name"] = _clean_required_text(str(record["name"]), field_name="Country name")
            self._ensure_unique_name(
                countries,
                col="name",
                value=record["name"],
                entity_name="Country",
                id_col="country_id",
            )
            record["country_id"] = self._next_id(countries, "country_id")

            updated = pd.concat([countries, pd.DataFrame([record])], ignore_index=True)
            self._write("countries", updated)

            region_name = regions.loc[regions["region_id"] == record["region_id"], "name"].iloc[0]
            return {**record, "region_name": region_name}

    def update_country(self, country_id: int, payload: CountryUpdate) -> dict[str, Any] | None:
        with self._lock:
            countries = self._read("countries")
            regions = self._read("regions")
            idx = countries.index[countries["country_id"] == country_id].tolist()
            if not idx:
                return None

            patch = payload.model_dump(exclude_unset=True, exclude_none=True)
            row_index = idx[0]

            if "region_id" in patch and regions.loc[regions["region_id"] == patch["region_id"]].empty:
                raise ValueError(f"Region id {patch['region_id']} does not exist")
            if "name" in patch:
                patch["name"] = _clean_required_text(str(patch["name"]), field_name="Country name")
                self._ensure_unique_name(
                    countries,
                    col="name",
                    value=patch["name"],
                    entity_name="Country",
                    id_col="country_id",
                    ignore_id=country_id,
                )

            for key, value in patch.items():
                countries.at[row_index, key] = value

            self._write("countries", countries)

            enriched = self._get_enriched_countries(countries=countries, regions=regions)
            return enriched.loc[enriched["country_id"] == country_id].iloc[0].to_dict()

    def list_categories(self) -> list[dict[str, Any]]:
        with self._lock:
            categories = self._read("categories")
        return categories.sort_values("name").to_dict(orient="records")

    def get_category(self, category_id: int) -> dict[str, Any] | None:
        with self._lock:
            categories = self._read("categories")
        match = categories.loc[categories["category_id"] == category_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def create_category(self, payload: CategoryCreate) -> dict[str, Any]:
        with self._lock:
            categories = self._read("categories")
            record = payload.model_dump()
            record["name"] = _clean_required_text(str(record["name"]), field_name="Category name")
            record["description"] = _clean_required_text(
                str(record["description"]), field_name="Category description"
            )
            self._ensure_unique_name(
                categories,
                col="name",
                value=record["name"],
                entity_name="Category",
                id_col="category_id",
            )
            record["category_id"] = self._next_id(categories, "category_id")
            updated = pd.concat([categories, pd.DataFrame([record])], ignore_index=True)
            self._write("categories", updated)

        return record

    def update_category(self, category_id: int, payload: CategoryUpdate) -> dict[str, Any] | None:
        with self._lock:
            categories = self._read("categories")
            idx = categories.index[categories["category_id"] == category_id].tolist()
            if not idx:
                return None

            patch = payload.model_dump(exclude_unset=True, exclude_none=True)
            row_index = idx[0]

            if "name" in patch:
                patch["name"] = _clean_required_text(str(patch["name"]), field_name="Category name")
                self._ensure_unique_name(
                    categories,
                    col="name",
                    value=patch["name"],
                    entity_name="Category",
                    id_col="category_id",
                    ignore_id=category_id,
                )
            if "description" in patch:
                patch["description"] = _clean_required_text(
                    str(patch["description"]), field_name="Category description"
                )

            for key, value in patch.items():
                categories.at[row_index, key] = value

            self._write("categories", categories)
            return categories.loc[row_index].to_dict()

    def list_products(self) -> list[dict[str, Any]]:
        with self._lock:
            products = self._read("products")
            categories = self._read("categories")
            enriched = self._get_enriched_products(products=products, categories=categories)
        return enriched.sort_values("name").to_dict(orient="records")

    def get_product(self, product_id: int) -> dict[str, Any] | None:
        with self._lock:
            products = self._read("products")
            categories = self._read("categories")
            enriched = self._get_enriched_products(products=products, categories=categories)
        match = enriched.loc[enriched["product_id"] == product_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def create_product(self, payload: ProductCreate) -> dict[str, Any]:
        with self._lock:
            products = self._read("products")
            categories = self._read("categories")
            if categories.loc[categories["category_id"] == payload.category_id].empty:
                raise ValueError(f"Category id {payload.category_id} does not exist")

            record = payload.model_dump()
            record["name"] = _clean_required_text(str(record["name"]), field_name="Product name")
            record["description"] = _clean_required_text(
                str(record["description"]), field_name="Product description"
            )
            self._ensure_unique_name(
                products,
                col="name",
                value=record["name"],
                entity_name="Product",
                id_col="product_id",
            )
            record["product_id"] = self._next_id(products, "product_id")

            updated = pd.concat([products, pd.DataFrame([record])], ignore_index=True)
            self._write("products", updated)

            category_name = categories.loc[categories["category_id"] == record["category_id"], "name"].iloc[0]
            return {**record, "category_name": category_name}

    def update_product(self, product_id: int, payload: ProductUpdate) -> dict[str, Any] | None:
        with self._lock:
            products = self._read("products")
            categories = self._read("categories")
            idx = products.index[products["product_id"] == product_id].tolist()
            if not idx:
                return None

            patch = payload.model_dump(exclude_unset=True, exclude_none=True)
            row_index = idx[0]

            if "category_id" in patch and categories.loc[categories["category_id"] == patch["category_id"]].empty:
                raise ValueError(f"Category id {patch['category_id']} does not exist")
            if "name" in patch:
                patch["name"] = _clean_required_text(str(patch["name"]), field_name="Product name")
                self._ensure_unique_name(
                    products,
                    col="name",
                    value=patch["name"],
                    entity_name="Product",
                    id_col="product_id",
                    ignore_id=product_id,
                )
            if "description" in patch:
                patch["description"] = _clean_required_text(
                    str(patch["description"]), field_name="Product description"
                )

            for key, value in patch.items():
                products.at[row_index, key] = value

            self._write("products", products)

            enriched = self._get_enriched_products(products=products, categories=categories)
            return enriched.loc[enriched["product_id"] == product_id].iloc[0].to_dict()

    def list_sales(
        self,
        *,
        regions: list[str] | None = None,
        countries: list[str] | None = None,
        products: list[str] | None = None,
        categories: list[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_rating: int | None = None,
        max_rating: int | None = None,
        limit: int = DEFAULT_SALES_LIMIT,
    ) -> list[dict[str, Any]]:
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be on or before end_date")
        if min_rating is not None and max_rating is not None and min_rating > max_rating:
            raise ValueError("min_rating must be less than or equal to max_rating")

        with self._lock:
            enriched = self._get_enriched_sales()

        filtered = enriched

        if regions:
            filtered = filtered[filtered["region_name"].isin(regions)]
        if countries:
            filtered = filtered[filtered["country_name"].isin(countries)]
        if products:
            filtered = filtered[filtered["product_name"].isin(products)]
        if categories:
            filtered = filtered[filtered["category_name"].isin(categories)]
        if start_date:
            filtered = filtered[filtered["sale_date"] >= pd.to_datetime(start_date)]
        if end_date:
            filtered = filtered[filtered["sale_date"] <= pd.to_datetime(end_date)]
        if min_rating is not None:
            filtered = filtered[filtered["customer_rating"] >= min_rating]
        if max_rating is not None:
            filtered = filtered[filtered["customer_rating"] <= max_rating]

        filtered = filtered.sort_values(["sale_date", "sale_id"], ascending=[False, False]).head(limit)
        return self._format_sales_records(filtered)

    def get_sale(self, sale_id: int) -> dict[str, Any] | None:
        with self._lock:
            enriched = self._get_enriched_sales()

        match = enriched.loc[enriched["sale_id"] == sale_id]
        if match.empty:
            return None
        return self._format_sales_records(match)[0]

    def create_sale(self, payload: SaleCreate) -> dict[str, Any]:
        with self._lock:
            sales = self._read("sales")
            products = self._read("products")
            countries = self._read("countries")

            product_match = products.loc[products["product_id"] == payload.product_id]
            if product_match.empty:
                raise ValueError(f"Product id {payload.product_id} does not exist")
            if countries.loc[countries["country_id"] == payload.country_id].empty:
                raise ValueError(f"Country id {payload.country_id} does not exist")

            record = payload.model_dump()
            record["sale_id"] = self._next_id(sales, "sale_id")

            if record.get("total_price") is None:
                unit_price = float(product_match.iloc[0]["price"])
                record["total_price"] = round(unit_price * int(record["units_sold"]), 2)

            updated = pd.concat([sales, pd.DataFrame([record])], ignore_index=True)
            self._write("sales", updated)

        created = self.get_sale(int(record["sale_id"]))
        if created is None:
            raise ValueError("Failed to read created sale")
        return created

    def update_sale(self, sale_id: int, payload: SaleUpdate) -> dict[str, Any] | None:
        with self._lock:
            sales = self._read("sales")
            products = self._read("products")
            countries = self._read("countries")

            idx = sales.index[sales["sale_id"] == sale_id].tolist()
            if not idx:
                return None
            row_index = idx[0]

            patch = payload.model_dump(exclude_unset=True, exclude_none=True)

            if "product_id" in patch and products.loc[products["product_id"] == patch["product_id"]].empty:
                raise ValueError(f"Product id {patch['product_id']} does not exist")
            if "country_id" in patch and countries.loc[countries["country_id"] == patch["country_id"]].empty:
                raise ValueError(f"Country id {patch['country_id']} does not exist")

            for key, value in patch.items():
                if key == "sale_date":
                    value = pd.Timestamp(value)
                sales.at[row_index, key] = value

            # Recompute the total only when the numbers it is derived from changed,
            # so a deliberately stored total survives an unrelated edit.
            if "total_price" not in patch and ("units_sold" in patch or "product_id" in patch):
                product_id = int(sales.at[row_index, "product_id"])
                units_sold = int(sales.at[row_index, "units_sold"])
                unit_price_match = products.loc[products["product_id"] == product_id, "price"]
                if unit_price_match.empty:
                    raise ValueError(f"Product id {product_id} does not exist")
                sales.at[row_index, "total_price"] = round(float(unit_price_match.iloc[0]) * units_sold, 2)

            self._write("sales", sales)

        return self.get_sale(sale_id)

    def _delete_row(self, table_name: str, id_col: str, row_id: int) -> bool:
        table = self._read(table_name)
        if table.loc[table[id_col] == row_id].empty:
            return False
        self._write(table_name, table.loc[table[id_col] != row_id])
        return True

    @staticmethod
    def _refuse_if_referenced(child: pd.DataFrame, fk_col: str, value: int, message: str) -> None:
        used_by = int((child[fk_col] == value).sum())
        if used_by:
            raise ValueError(f"{message} ({used_by} row(s) still reference it)")

    def delete_region(self, region_id: int) -> bool:
        with self._lock:
            self._refuse_if_referenced(
                self._read("countries"), "region_id", region_id,
                f"Region {region_id} still has countries",
            )
            return self._delete_row("regions", "region_id", region_id)

    def delete_country(self, country_id: int) -> bool:
        with self._lock:
            self._refuse_if_referenced(
                self._read("sales"), "country_id", country_id,
                f"Country {country_id} still has sales",
            )
            return self._delete_row("countries", "country_id", country_id)

    def delete_category(self, category_id: int) -> bool:
        with self._lock:
            self._refuse_if_referenced(
                self._read("products"), "category_id", category_id,
                f"Category {category_id} still has products",
            )
            return self._delete_row("categories", "category_id", category_id)

    def delete_product(self, product_id: int) -> bool:
        with self._lock:
            self._refuse_if_referenced(
                self._read("sales"), "product_id", product_id,
                f"Product {product_id} still has sales",
            )
            return self._delete_row("products", "product_id", product_id)

    def delete_sale(self, sale_id: int) -> bool:
        with self._lock:
            return self._delete_row("sales", "sale_id", sale_id)


repo = SalesRepository(TABLE_PATHS)
app = FastAPI(
    title="Sales Analysis API",
    version="3.0.0",
    description=(
        "Teaching API for SW03. It is the **logic tier** of a three-tier stack: "
        "Parquet files underneath (data tier), a notebook or Streamlit app on top "
        "(presentation tier).\n\n"
        "Every table supports the four REST verbs: `GET`, `POST`, `PUT`, `DELETE`. "
        "`PUT` here is a *partial* update - fields you leave out keep their current value.\n\n"
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
)


@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Turn a rejected business rule into 400 Bad Request instead of a 500 crash."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


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
    return repo.options()


# --- Regions ---------------------------------------------------------------

@app.get("/regions", response_model=list[SalesRegion], tags=["Regions"])
def list_regions() -> list[SalesRegion]:
    """List all regions, sorted by name."""
    return [SalesRegion(**r) for r in repo.list_regions()]


@app.get("/regions/{region_id}", response_model=SalesRegion, tags=["Regions"], responses=NOT_FOUND)
def get_region(region_id: int = PathParam(..., ge=1)) -> SalesRegion:
    """Fetch one region by id."""
    region = repo.get_region(region_id)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return SalesRegion(**region)


@app.post("/regions", response_model=SalesRegion, status_code=201, tags=["Regions"], responses=BAD_REQUEST)
def create_region(payload: SalesRegionCreate) -> SalesRegion:
    """Create a region. The name must not already exist."""
    return SalesRegion(**repo.create_region(payload))


@app.put("/regions/{region_id}", response_model=SalesRegion, tags=["Regions"], responses=NOT_FOUND | BAD_REQUEST)
def update_region(payload: SalesRegionUpdate, region_id: int = PathParam(..., ge=1)) -> SalesRegion:
    """Update a region. Fields you leave out keep their current value."""
    updated = repo.update_region(region_id=region_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return SalesRegion(**updated)


@app.delete("/regions/{region_id}", status_code=204, tags=["Regions"], responses=NOT_FOUND | BAD_REQUEST)
def delete_region(region_id: int = PathParam(..., ge=1)) -> None:
    """Delete a region. Refused while countries still belong to it."""
    if not repo.delete_region(region_id):
        raise HTTPException(status_code=404, detail="Region not found")


# --- Countries -------------------------------------------------------------

@app.get("/countries", response_model=list[Country], tags=["Countries"])
def list_countries() -> list[Country]:
    """List all countries with their region name, sorted by name."""
    return [Country(**r) for r in repo.list_countries()]


@app.get("/countries/{country_id}", response_model=Country, tags=["Countries"], responses=NOT_FOUND)
def get_country(country_id: int = PathParam(..., ge=1)) -> Country:
    """Fetch one country by id."""
    country = repo.get_country(country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return Country(**country)


@app.post("/countries", response_model=Country, status_code=201, tags=["Countries"], responses=BAD_REQUEST)
def create_country(payload: CountryCreate) -> Country:
    """Create a country. The region_id must already exist."""
    return Country(**repo.create_country(payload))


@app.put("/countries/{country_id}", response_model=Country, tags=["Countries"], responses=NOT_FOUND | BAD_REQUEST)
def update_country(payload: CountryUpdate, country_id: int = PathParam(..., ge=1)) -> Country:
    """Update a country. Fields you leave out keep their current value."""
    updated = repo.update_country(country_id=country_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return Country(**updated)


@app.delete("/countries/{country_id}", status_code=204, tags=["Countries"], responses=NOT_FOUND | BAD_REQUEST)
def delete_country(country_id: int = PathParam(..., ge=1)) -> None:
    """Delete a country. Refused while sales still reference it."""
    if not repo.delete_country(country_id):
        raise HTTPException(status_code=404, detail="Country not found")


# --- Categories ------------------------------------------------------------

@app.get("/categories", response_model=list[Category], tags=["Categories"])
def list_categories() -> list[Category]:
    """List all categories, sorted by name."""
    return [Category(**r) for r in repo.list_categories()]


@app.get("/categories/{category_id}", response_model=Category, tags=["Categories"], responses=NOT_FOUND)
def get_category(category_id: int = PathParam(..., ge=1)) -> Category:
    """Fetch one category by id."""
    category = repo.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category(**category)


@app.post("/categories", response_model=Category, status_code=201, tags=["Categories"], responses=BAD_REQUEST)
def create_category(payload: CategoryCreate) -> Category:
    """Create a category. The name must not already exist."""
    return Category(**repo.create_category(payload))


@app.put("/categories/{category_id}", response_model=Category, tags=["Categories"], responses=NOT_FOUND | BAD_REQUEST)
def update_category(payload: CategoryUpdate, category_id: int = PathParam(..., ge=1)) -> Category:
    """Update a category. Fields you leave out keep their current value."""
    updated = repo.update_category(category_id=category_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category(**updated)


@app.delete("/categories/{category_id}", status_code=204, tags=["Categories"], responses=NOT_FOUND | BAD_REQUEST)
def delete_category(category_id: int = PathParam(..., ge=1)) -> None:
    """Delete a category. Refused while products still belong to it."""
    if not repo.delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")


# --- Products --------------------------------------------------------------

@app.get("/products", response_model=list[Product], tags=["Products"])
def list_products() -> list[Product]:
    """List all products with their category name, sorted by name."""
    return [Product(**r) for r in repo.list_products()]


@app.get("/products/{product_id}", response_model=Product, tags=["Products"], responses=NOT_FOUND)
def get_product(product_id: int = PathParam(..., ge=1)) -> Product:
    """Fetch one product by id."""
    product = repo.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)


@app.post("/products", response_model=Product, status_code=201, tags=["Products"], responses=BAD_REQUEST)
def create_product(payload: ProductCreate) -> Product:
    """Create a product. The name must be new and the category_id must already exist."""
    return Product(**repo.create_product(payload))


@app.put("/products/{product_id}", response_model=Product, tags=["Products"], responses=NOT_FOUND | BAD_REQUEST)
def update_product(payload: ProductUpdate, product_id: int = PathParam(..., ge=1)) -> Product:
    """Update a product. Fields you leave out keep their current value."""
    updated = repo.update_product(product_id=product_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**updated)


@app.delete("/products/{product_id}", status_code=204, tags=["Products"], responses=NOT_FOUND | BAD_REQUEST)
def delete_product(product_id: int = PathParam(..., ge=1)) -> None:
    """Delete a product. Refused while sales still reference it."""
    if not repo.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")


# --- Sales -----------------------------------------------------------------

@app.get("/sales", response_model=list[Sale], tags=["Sales"], responses=BAD_REQUEST)
def list_sales(
    region: list[str] | None = Query(default=None, description="Keep only these region names."),
    country: list[str] | None = Query(default=None, description="Keep only these country names."),
    product: list[str] | None = Query(default=None, description="Keep only these product names."),
    category: list[str] | None = Query(default=None, description="Keep only these category names."),
    start_date: date | None = Query(default=None, description="Earliest sale date to include."),
    end_date: date | None = Query(default=None, description="Latest sale date to include."),
    min_rating: int | None = Query(default=None, ge=1, le=5),
    max_rating: int | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=DEFAULT_SALES_LIMIT, ge=1, le=20000, description="Maximum rows returned, newest first."),
) -> list[Sale]:
    """Search sales. Every filter is optional; combining them narrows the result."""
    records = repo.list_sales(
        regions=region,
        countries=country,
        products=product,
        categories=category,
        start_date=start_date,
        end_date=end_date,
        min_rating=min_rating,
        max_rating=max_rating,
        limit=limit,
    )
    return [Sale(**r) for r in records]


@app.get("/sales/{sale_id}", response_model=Sale, tags=["Sales"], responses=NOT_FOUND)
def get_sale(sale_id: int = PathParam(..., ge=1)) -> Sale:
    """Fetch one sale by id, enriched with product, category, country and region names."""
    sale = repo.get_sale(sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return Sale(**sale)


@app.post("/sales", response_model=Sale, status_code=201, tags=["Sales"], responses=BAD_REQUEST)
def create_sale(payload: SaleCreate) -> Sale:
    """Record a sale. Leave total_price out and it is computed as units_sold x product price."""
    return Sale(**repo.create_sale(payload))


@app.put("/sales/{sale_id}", response_model=Sale, tags=["Sales"], responses=NOT_FOUND | BAD_REQUEST)
def update_sale(payload: SaleUpdate, sale_id: int = PathParam(..., ge=1)) -> Sale:
    """Update a sale. Changing units_sold or product_id recomputes total_price."""
    updated = repo.update_sale(sale_id=sale_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return Sale(**updated)


@app.delete("/sales/{sale_id}", status_code=204, tags=["Sales"], responses=NOT_FOUND)
def delete_sale(sale_id: int = PathParam(..., ge=1)) -> None:
    """Delete a sale. Nothing references a sale, so this always succeeds."""
    if not repo.delete_sale(sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")
