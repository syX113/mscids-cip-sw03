"""FastAPI app that persists normalized sales data to Parquet files.

Run with:
    uvicorn parquet_api:app --reload
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
TABLE_PATHS = {
    "regions": DATA_DIR / "sales_regions.parquet",
    "countries": DATA_DIR / "countries.parquet",
    "categories": DATA_DIR / "categories.parquet",
    "products": DATA_DIR / "products.parquet",
    "sales": DATA_DIR / "sales.parquet",
}
SEED_VERSION = "2026-02-11-regression-v2"
SEED_VERSION_PATH = DATA_DIR / ".seed_version"


def _model_dump(model: BaseModel, **kwargs: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(**kwargs)
    return model.dict(**kwargs)


def _clean_text(value: str) -> str:
    return value.strip()


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
        if not self._is_store_valid():
            self._seed_store()
            return
        if self._read_seed_version() != SEED_VERSION:
            self._seed_store()

    def _read_seed_version(self) -> str:
        if not SEED_VERSION_PATH.exists():
            return ""
        try:
            return SEED_VERSION_PATH.read_text(encoding="utf-8").strip()
        except Exception:
            return ""

    def _write_seed_version(self) -> None:
        SEED_VERSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        SEED_VERSION_PATH.write_text(SEED_VERSION, encoding="utf-8")

    def _is_store_valid(self) -> bool:
        required_columns = {
            "regions": {"region_id", "name", "description"},
            "countries": {"country_id", "name", "region_id"},
            "categories": {"category_id", "name", "description"},
            "products": {"product_id", "name", "price", "description", "category_id"},
            "sales": {"sale_id", "sale_date", "product_id", "country_id", "units_sold", "total_price", "customer_rating"},
        }

        for table_name, path in self.table_paths.items():
            if not path.exists():
                return False
            try:
                df = pd.read_parquet(path)
            except Exception:
                return False
            if not required_columns[table_name].issubset(set(df.columns)):
                return False

        try:
            countries = pd.read_parquet(self.table_paths["countries"])
            regions = pd.read_parquet(self.table_paths["regions"])
            products = pd.read_parquet(self.table_paths["products"])
            categories = pd.read_parquet(self.table_paths["categories"])
            sales = pd.read_parquet(self.table_paths["sales"])
        except Exception:
            return False

        if not set(countries["region_id"].dropna().astype(int).tolist()).issubset(
            set(regions["region_id"].dropna().astype(int).tolist())
        ):
            return False
        if not set(products["category_id"].dropna().astype(int).tolist()).issubset(
            set(categories["category_id"].dropna().astype(int).tolist())
        ):
            return False
        if not set(sales["product_id"].dropna().astype(int).tolist()).issubset(
            set(products["product_id"].dropna().astype(int).tolist())
        ):
            return False
        if not set(sales["country_id"].dropna().astype(int).tolist()).issubset(
            set(countries["country_id"].dropna().astype(int).tolist())
        ):
            return False

        return True

    def _seed_store(self) -> None:
        regions = pd.DataFrame(
            [
                {"region_id": 1, "name": "US", "description": "United States sales region"},
                {"region_id": 2, "name": "Europe", "description": "European sales region"},
                {"region_id": 3, "name": "Asia", "description": "Asia-Pacific sales region"},
                {"region_id": 4, "name": "Africa", "description": "African sales region"},
            ]
        )

        categories = pd.DataFrame(
            [
                {"category_id": 1, "name": "Hardware", "description": "Physical devices and components"},
                {"category_id": 2, "name": "Software", "description": "Licenses and digital subscriptions"},
                {"category_id": 3, "name": "Services", "description": "Consulting and managed services"},
            ]
        )

        countries = pd.DataFrame(
            [
                {"country_id": 1, "name": "United States", "region_id": 1},
                {"country_id": 2, "name": "Canada", "region_id": 1},
                {"country_id": 3, "name": "Germany", "region_id": 2},
                {"country_id": 4, "name": "United Kingdom", "region_id": 2},
                {"country_id": 5, "name": "Japan", "region_id": 3},
                {"country_id": 6, "name": "India", "region_id": 3},
                {"country_id": 7, "name": "South Africa", "region_id": 4},
                {"country_id": 8, "name": "Kenya", "region_id": 4},
            ]
        )

        products = pd.DataFrame(
            [
                {
                    "product_id": 1,
                    "name": "Edge Sensor X1",
                    "price": 195.0,
                    "description": "Industrial sensor package for telemetry capture",
                    "category_id": 1,
                },
                {
                    "product_id": 2,
                    "name": "Gateway Node Pro",
                    "price": 420.0,
                    "description": "Ruggedized gateway for distributed edge infrastructure",
                    "category_id": 1,
                },
                {
                    "product_id": 3,
                    "name": "Ops Console",
                    "price": 99.0,
                    "description": "Monitoring and response software subscription",
                    "category_id": 2,
                },
                {
                    "product_id": 4,
                    "name": "Forecast Studio",
                    "price": 149.0,
                    "description": "Demand forecasting and analytics suite",
                    "category_id": 2,
                },
                {
                    "product_id": 5,
                    "name": "Deployment Sprint",
                    "price": 2500.0,
                    "description": "Two-week onboarding and deployment service",
                    "category_id": 3,
                },
                {
                    "product_id": 6,
                    "name": "Managed Success",
                    "price": 1800.0,
                    "description": "Quarterly customer success management package",
                    "category_id": 3,
                },
                {
                    "product_id": 7,
                    "name": "Customer Care Pack",
                    "price": 980.0,
                    "description": "Lightweight managed care service add-on",
                    "category_id": 3,
                },
            ]
        )

        sales = self._seed_sales(regions=regions, countries=countries, categories=categories, products=products)

        self._write("regions", regions)
        self._write("countries", countries)
        self._write("categories", categories)
        self._write("products", products)
        self._write("sales", sales)
        self._write_seed_version()

    def _seed_sales(
        self,
        *,
        regions: pd.DataFrame,
        countries: pd.DataFrame,
        categories: pd.DataFrame,
        products: pd.DataFrame,
    ) -> pd.DataFrame:
        def _add_months(base: date, delta: int) -> date:
            month_index = (base.month - 1) + delta
            year = base.year + month_index // 12
            month = month_index % 12 + 1
            return date(year, month, 1)

        region_revenue_factor = {"US": 1.17, "Europe": 1.09, "Asia": 1.01, "Africa": 0.92}
        region_units_factor = {"US": 1.16, "Europe": 1.08, "Asia": 1.0, "Africa": 0.94}
        region_rating_offset = {"US": 0.22, "Europe": 0.12, "Asia": 0.05, "Africa": -0.18}
        category_revenue_factor = {"Hardware": 1.16, "Software": 1.05, "Services": 1.34}
        category_units_factor = {"Hardware": 1.12, "Software": 1.03, "Services": 0.78}
        category_rating_base = {"Hardware": 3.35, "Software": 3.62, "Services": 3.98}
        country_rating_offset = {
            "United States": 0.20,
            "Canada": 0.08,
            "Germany": 0.12,
            "United Kingdom": 0.06,
            "Japan": 0.10,
            "India": -0.04,
            "South Africa": -0.12,
            "Kenya": -0.08,
        }

        products_lookup = products.set_index("product_id").to_dict(orient="index")
        region_name_by_id = regions.set_index("region_id")["name"].to_dict()
        country_name_by_id = countries.set_index("country_id")["name"].to_dict()
        category_name_by_id = categories.set_index("category_id")["name"].to_dict()

        rows: list[dict[str, Any]] = []
        sale_id = 1
        anchor = date.today().replace(day=1)
        start_month = _add_months(anchor, -23)

        for month_idx in range(24):
            month_start = _add_months(start_month, month_idx)
            month = month_start.month
            seasonal_revenue_factor = 1.16 if month in (10, 11, 12) else 1.07 if month in (4, 5, 6) else 0.93
            seasonal_rating_offset = 0.18 if month in (11, 12) else 0.06 if month in (6, 7) else -0.03 if month in (1, 2) else 0.0

            for country_row in countries.itertuples(index=False):
                country_id = int(country_row.country_id)
                region_id = int(country_row.region_id)
                region_name = region_name_by_id[region_id]
                country_name = country_name_by_id[country_id]
                country_wave = 1.0 + (((country_id + month_idx) % 5) - 2) * 0.028

                for product_row in products.itertuples(index=False):
                    product_id = int(product_row.product_id)
                    category_id = int(product_row.category_id)
                    category_name = category_name_by_id[category_id]

                    order_count = 2 + ((month_idx + country_id + product_id) % 2)
                    for order_idx in range(order_count):
                        base_units = 6 + ((month_idx * 4 + country_id * 3 + product_id * 5 + order_idx * 7) % 44)
                        units_sold = max(
                            2,
                            int(
                                round(
                                    base_units
                                    * region_units_factor[region_name]
                                    * category_units_factor[category_name]
                                )
                            ),
                        )
                        day_offset = (2 + product_id * 3 + country_id + month_idx + order_idx * 6) % 27
                        sale_date = month_start + timedelta(days=day_offset)

                        base_price = float(products_lookup[product_id]["price"])
                        pricing_wave = 1.0 + ((((month_idx + product_id + order_idx) % 7) - 3) * 0.013)
                        discount = 0.02 + (((month_idx + country_id + order_idx) % 7) * 0.018)
                        if region_name == "Africa":
                            discount += 0.015
                        discount = min(discount, 0.23)

                        effective_unit_price = (
                            base_price
                            * seasonal_revenue_factor
                            * region_revenue_factor[region_name]
                            * category_revenue_factor[category_name]
                            * country_wave
                            * pricing_wave
                            * (1 - discount)
                        )
                        total_price = round(max(1.0, units_sold * effective_unit_price), 2)

                        noise = (((month_idx * 7 + country_id * 11 + product_id * 13 + order_idx * 17) % 100) / 100.0 - 0.5) * 0.55
                        rating_raw = (
                            category_rating_base[category_name]
                            + region_rating_offset[region_name]
                            + country_rating_offset[country_name]
                            + (discount * 1.35)
                            - (units_sold * 0.011)
                            + seasonal_rating_offset
                            + noise
                        )
                        customer_rating = int(max(1, min(5, round(rating_raw))))

                        rows.append(
                            {
                                "sale_id": sale_id,
                                "sale_date": sale_date,
                                "product_id": product_id,
                                "country_id": country_id,
                                "units_sold": units_sold,
                                "total_price": total_price,
                                "customer_rating": customer_rating,
                            }
                        )
                        sale_id += 1

        df = pd.DataFrame(rows)
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        return df

    def _read(self, table_name: str) -> pd.DataFrame:
        path = self.table_paths[table_name]
        if not path.exists():
            self._ensure_store()
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

    def _get_enriched_countries(self, countries: pd.DataFrame | None = None, regions: pd.DataFrame | None = None) -> pd.DataFrame:
        countries_df = countries.copy() if countries is not None else self._read("countries")
        regions_df = regions.copy() if regions is not None else self._read("regions")
        region_lookup = regions_df.rename(columns={"name": "region_name"})[["region_id", "region_name"]]
        return countries_df.merge(region_lookup, on="region_id", how="left")

    def _get_enriched_products(self, products: pd.DataFrame | None = None, categories: pd.DataFrame | None = None) -> pd.DataFrame:
        products_df = products.copy() if products is not None else self._read("products")
        categories_df = categories.copy() if categories is not None else self._read("categories")
        category_lookup = categories_df.rename(columns={"name": "category_name"})[["category_id", "category_name"]]
        return products_df.merge(category_lookup, on="category_id", how="left")

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
            record = _model_dump(payload)
            record["name"] = _clean_text(record["name"])
            record["description"] = _clean_text(record["description"])
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

            patch = _model_dump(payload, exclude_unset=True)
            row_index = idx[0]

            if "name" in patch:
                patch["name"] = _clean_text(str(patch["name"]))
                self._ensure_unique_name(
                    regions,
                    col="name",
                    value=patch["name"],
                    entity_name="Region",
                    id_col="region_id",
                    ignore_id=region_id,
                )
            if "description" in patch:
                patch["description"] = _clean_text(str(patch["description"]))

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

            record = _model_dump(payload)
            record["name"] = _clean_text(record["name"])
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

            patch = _model_dump(payload, exclude_unset=True)
            row_index = idx[0]

            if "region_id" in patch and regions.loc[regions["region_id"] == patch["region_id"]].empty:
                raise ValueError(f"Region id {patch['region_id']} does not exist")
            if "name" in patch:
                patch["name"] = _clean_text(str(patch["name"]))
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
            record = _model_dump(payload)
            record["name"] = _clean_text(record["name"])
            record["description"] = _clean_text(record["description"])
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

            patch = _model_dump(payload, exclude_unset=True)
            row_index = idx[0]

            if "name" in patch:
                patch["name"] = _clean_text(str(patch["name"]))
                self._ensure_unique_name(
                    categories,
                    col="name",
                    value=patch["name"],
                    entity_name="Category",
                    id_col="category_id",
                    ignore_id=category_id,
                )
            if "description" in patch:
                patch["description"] = _clean_text(str(patch["description"]))

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

            record = _model_dump(payload)
            record["name"] = _clean_text(record["name"])
            record["description"] = _clean_text(record["description"])
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

            patch = _model_dump(payload, exclude_unset=True)
            row_index = idx[0]

            if "category_id" in patch and categories.loc[categories["category_id"] == patch["category_id"]].empty:
                raise ValueError(f"Category id {patch['category_id']} does not exist")
            if "name" in patch:
                patch["name"] = _clean_text(str(patch["name"]))
                self._ensure_unique_name(
                    products,
                    col="name",
                    value=patch["name"],
                    entity_name="Product",
                    id_col="product_id",
                    ignore_id=product_id,
                )
            if "description" in patch:
                patch["description"] = _clean_text(str(patch["description"]))

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
        limit: int = 2000,
    ) -> list[dict[str, Any]]:
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be on or before end_date")
        if min_rating and max_rating and min_rating > max_rating:
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

        filtered = filtered.sort_values("sale_date", ascending=False).head(limit)
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

            record = _model_dump(payload)
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

            patch = _model_dump(payload, exclude_unset=True)

            if "product_id" in patch and products.loc[products["product_id"] == patch["product_id"]].empty:
                raise ValueError(f"Product id {patch['product_id']} does not exist")
            if "country_id" in patch and countries.loc[countries["country_id"] == patch["country_id"]].empty:
                raise ValueError(f"Country id {patch['country_id']} does not exist")

            explicit_total = patch.get("total_price") if "total_price" in patch else None

            for key, value in patch.items():
                if key == "total_price" and value is None:
                    continue
                sales.at[row_index, key] = value

            if explicit_total is None:
                product_id = int(sales.at[row_index, "product_id"])
                units_sold = int(sales.at[row_index, "units_sold"])
                unit_price_match = products.loc[products["product_id"] == product_id, "price"]
                if unit_price_match.empty:
                    raise ValueError(f"Product id {product_id} does not exist")
                sales.at[row_index, "total_price"] = round(float(unit_price_match.iloc[0]) * units_sold, 2)

            self._write("sales", sales)

        return self.get_sale(sale_id)


repo = SalesRepository(TABLE_PATHS)
app = FastAPI(title="Sales Analysis API", version="2.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Sales Analysis API is running.",
        "data_dir": str(DATA_DIR),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/meta/options")
def meta_options() -> dict[str, Any]:
    return repo.options()


@app.get("/regions", response_model=list[SalesRegion])
def list_regions() -> list[SalesRegion]:
    return [SalesRegion(**r) for r in repo.list_regions()]


@app.get("/regions/{region_id}", response_model=SalesRegion)
def get_region(region_id: int) -> SalesRegion:
    region = repo.get_region(region_id)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return SalesRegion(**region)


@app.post("/regions", response_model=SalesRegion, status_code=201)
def create_region(payload: SalesRegionCreate) -> SalesRegion:
    try:
        created = repo.create_region(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SalesRegion(**created)


@app.put("/regions/{region_id}", response_model=SalesRegion)
def update_region(region_id: int, payload: SalesRegionUpdate) -> SalesRegion:
    try:
        updated = repo.update_region(region_id=region_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Region not found")
    return SalesRegion(**updated)


@app.get("/countries", response_model=list[Country])
def list_countries() -> list[Country]:
    return [Country(**r) for r in repo.list_countries()]


@app.get("/countries/{country_id}", response_model=Country)
def get_country(country_id: int) -> Country:
    country = repo.get_country(country_id)
    if country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return Country(**country)


@app.post("/countries", response_model=Country, status_code=201)
def create_country(payload: CountryCreate) -> Country:
    try:
        created = repo.create_country(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Country(**created)


@app.put("/countries/{country_id}", response_model=Country)
def update_country(country_id: int, payload: CountryUpdate) -> Country:
    try:
        updated = repo.update_country(country_id=country_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return Country(**updated)


@app.get("/categories", response_model=list[Category])
def list_categories() -> list[Category]:
    return [Category(**r) for r in repo.list_categories()]


@app.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int) -> Category:
    category = repo.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category(**category)


@app.post("/categories", response_model=Category, status_code=201)
def create_category(payload: CategoryCreate) -> Category:
    try:
        created = repo.create_category(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Category(**created)


@app.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: int, payload: CategoryUpdate) -> Category:
    try:
        updated = repo.update_category(category_id=category_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return Category(**updated)


@app.get("/products", response_model=list[Product])
def list_products() -> list[Product]:
    return [Product(**r) for r in repo.list_products()]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    product = repo.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)


@app.post("/products", response_model=Product, status_code=201)
def create_product(payload: ProductCreate) -> Product:
    try:
        created = repo.create_product(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Product(**created)


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductUpdate) -> Product:
    try:
        updated = repo.update_product(product_id=product_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**updated)


@app.get("/sales", response_model=list[Sale])
def list_sales(
    region: list[str] | None = Query(default=None),
    country: list[str] | None = Query(default=None),
    product: list[str] | None = Query(default=None),
    category: list[str] | None = Query(default=None),
    start_date: date | None = None,
    end_date: date | None = None,
    min_rating: int | None = Query(default=None, ge=1, le=5),
    max_rating: int | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=2000, ge=1, le=20000),
) -> list[Sale]:
    try:
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
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [Sale(**r) for r in records]


@app.get("/sales/{sale_id}", response_model=Sale)
def get_sale(sale_id: int) -> Sale:
    sale = repo.get_sale(sale_id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return Sale(**sale)


@app.post("/sales", response_model=Sale, status_code=201)
def create_sale(payload: SaleCreate) -> Sale:
    try:
        created = repo.create_sale(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Sale(**created)


@app.put("/sales/{sale_id}", response_model=Sale)
def update_sale(sale_id: int, payload: SaleUpdate) -> Sale:
    try:
        updated = repo.update_sale(sale_id=sale_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if updated is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return Sale(**updated)
