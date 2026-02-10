"""FastAPI app that persists records to a Parquet file.

Run with:
    uvicorn src.parquet_api:app --reload
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PARQUET_PATH = DATA_DIR / "sales_demo.parquet"


def _model_dump(model: BaseModel, **kwargs: Any) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(**kwargs)
    return model.dict(**kwargs)


class SalesRecord(BaseModel):
    record_id: int
    order_date: date
    customer_name: str = Field(min_length=1, max_length=80)
    region: str = Field(min_length=1, max_length=40)
    category: str = Field(min_length=1, max_length=40)
    product_name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=500)
    unit_price: float = Field(gt=0)
    discount: float = Field(ge=0, le=0.9)
    revenue: float = Field(ge=0)
    status: str = Field(min_length=1, max_length=20)


class SalesRecordCreate(BaseModel):
    order_date: date
    customer_name: str = Field(min_length=1, max_length=80)
    region: str = Field(min_length=1, max_length=40)
    category: str = Field(min_length=1, max_length=40)
    product_name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=500)
    unit_price: float = Field(gt=0)
    discount: float = Field(ge=0, le=0.9)
    status: str = Field(min_length=1, max_length=20)


class SalesRecordUpdate(BaseModel):
    order_date: date | None = None
    customer_name: str | None = Field(default=None, min_length=1, max_length=80)
    region: str | None = Field(default=None, min_length=1, max_length=40)
    category: str | None = Field(default=None, min_length=1, max_length=40)
    product_name: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: int | None = Field(default=None, ge=1, le=500)
    unit_price: float | None = Field(default=None, gt=0)
    discount: float | None = Field(default=None, ge=0, le=0.9)
    status: str | None = Field(default=None, min_length=1, max_length=20)


class RecordRepository:
    def __init__(self, parquet_path: Path) -> None:
        self.parquet_path = parquet_path
        self._lock = Lock()
        self._ensure_store()

    def _ensure_store(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.parquet_path.exists():
            seed_df = self._seed_data()
            self._write(seed_df)

    def _seed_data(self) -> pd.DataFrame:
        regions = ["North America", "Europe", "APAC", "LATAM"]
        categories = ["Hardware", "Software", "Services", "Accessories"]
        region_factor = {
            "North America": 1.22,
            "Europe": 1.05,
            "APAC": 0.96,
            "LATAM": 0.84,
        }
        category_factor = {
            "Hardware": 1.35,
            "Software": 1.12,
            "Services": 0.92,
            "Accessories": 0.65,
        }
        products = {
            "Hardware": ["Edge Sensor", "Gateway Pro", "Cloud Node"],
            "Software": ["Ops Suite", "Data Canvas", "Signal Studio"],
            "Services": ["Implementation", "Training", "Managed Support"],
            "Accessories": ["Mount Kit", "Power Adapter", "Travel Case"],
        }

        rows: list[dict[str, Any]] = []
        start_day = date.today() - timedelta(days=540)

        for i in range(1, 721):
            category = categories[(i + (i // 13)) % len(categories)]
            region = regions[(i + (i // 17)) % len(regions)]
            order_day = start_day + timedelta(days=(i * 3 + (i % 11)) % 510)

            month = order_day.month
            seasonal_factor = 1.18 if month in (10, 11, 12) else 1.08 if month in (4, 5, 6) else 0.94
            quantity = 2 + ((i * 5) % 14) + (1 if category == "Accessories" else 0)

            base_price = 28 + ((i * 7) % 55) * 2.1
            unit_price = round(base_price * category_factor[category] * region_factor[region] * seasonal_factor, 2)

            discount_raw = ((i % 6) * 0.02) + (0.02 if region == "LATAM" else 0.0)
            discount = round(min(discount_raw, 0.24), 2)
            revenue = round(quantity * unit_price * (1 - discount), 2)

            if i % 11 == 0:
                status = "returned"
            elif i % 5 == 0:
                status = "processing"
            else:
                status = "completed"

            rows.append(
                {
                    "record_id": i,
                    "order_date": order_day,
                    "customer_name": f"Customer {1000 + i}",
                    "region": region,
                    "category": category,
                    "product_name": products[category][i % 3],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount": discount,
                    "revenue": revenue,
                    "status": status,
                }
            )

        df = pd.DataFrame(rows)
        df["order_date"] = pd.to_datetime(df["order_date"])  # parquet-friendly datetime
        return df

    def _read(self) -> pd.DataFrame:
        if not self.parquet_path.exists():
            self._ensure_store()
        df = pd.read_parquet(self.parquet_path)
        df["order_date"] = pd.to_datetime(df["order_date"])
        return df

    def _write(self, df: pd.DataFrame) -> None:
        df_to_write = df.copy()
        df_to_write["order_date"] = pd.to_datetime(df_to_write["order_date"])
        df_to_write.to_parquet(self.parquet_path, index=False)

    def options(self) -> dict[str, list[str]]:
        with self._lock:
            df = self._read()

        return {
            "regions": sorted(df["region"].dropna().astype(str).unique().tolist()),
            "categories": sorted(df["category"].dropna().astype(str).unique().tolist()),
            "statuses": sorted(df["status"].dropna().astype(str).unique().tolist()),
        }

    def list_records(
        self,
        regions: list[str] | None = None,
        categories: list[str] | None = None,
        statuses: list[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_revenue: float | None = None,
        max_revenue: float | None = None,
        query: str | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        with self._lock:
            df = self._read()

        filtered = df

        if regions:
            filtered = filtered[filtered["region"].isin(regions)]
        if categories:
            filtered = filtered[filtered["category"].isin(categories)]
        if statuses:
            filtered = filtered[filtered["status"].isin(statuses)]
        if start_date:
            filtered = filtered[filtered["order_date"] >= pd.to_datetime(start_date)]
        if end_date:
            filtered = filtered[filtered["order_date"] <= pd.to_datetime(end_date)]
        if min_revenue is not None:
            filtered = filtered[filtered["revenue"] >= min_revenue]
        if max_revenue is not None:
            filtered = filtered[filtered["revenue"] <= max_revenue]
        if query:
            q = query.lower()
            filtered = filtered[
                filtered["customer_name"].fillna("").str.lower().str.contains(q)
                | filtered["product_name"].fillna("").str.lower().str.contains(q)
            ]

        filtered = filtered.sort_values("order_date", ascending=False).head(limit).copy()
        filtered["order_date"] = filtered["order_date"].dt.date

        return filtered.to_dict(orient="records")

    def get_record(self, record_id: int) -> dict[str, Any] | None:
        with self._lock:
            df = self._read()

        match = df[df["record_id"] == record_id]
        if match.empty:
            return None

        row = match.iloc[0].to_dict()
        row["order_date"] = pd.to_datetime(row["order_date"]).date()
        return row

    def create_record(self, payload: SalesRecordCreate) -> dict[str, Any]:
        with self._lock:
            df = self._read()
            next_id = int(df["record_id"].max()) + 1 if not df.empty else 1

            row = _model_dump(payload)
            row["record_id"] = next_id
            row["revenue"] = round(row["quantity"] * row["unit_price"] * (1 - row["discount"]), 2)

            updated = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            self._write(updated)

        row["order_date"] = pd.to_datetime(row["order_date"]).date()
        return row

    def update_record(self, record_id: int, payload: SalesRecordUpdate) -> dict[str, Any] | None:
        with self._lock:
            df = self._read()
            idx = df.index[df["record_id"] == record_id].tolist()
            if not idx:
                return None

            row_index = idx[0]
            patch = _model_dump(payload, exclude_unset=True)
            for key, value in patch.items():
                df.at[row_index, key] = value

            quantity = int(df.at[row_index, "quantity"])
            unit_price = float(df.at[row_index, "unit_price"])
            discount = float(df.at[row_index, "discount"])
            df.at[row_index, "revenue"] = round(quantity * unit_price * (1 - discount), 2)

            self._write(df)

            updated = df.loc[row_index].to_dict()
            updated["order_date"] = pd.to_datetime(updated["order_date"]).date()
            return updated


repo = RecordRepository(PARQUET_PATH)
app = FastAPI(title="Parquet Sales API", version="1.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Parquet Sales API is running.",
        "data_file": str(PARQUET_PATH),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/meta/options")
def meta_options() -> dict[str, list[str]]:
    return repo.options()


@app.get("/records", response_model=list[SalesRecord])
def list_records(
    region: list[str] | None = Query(default=None),
    category: list[str] | None = Query(default=None),
    status: list[str] | None = Query(default=None),
    start_date: date | None = None,
    end_date: date | None = None,
    min_revenue: float | None = Query(default=None, ge=0),
    max_revenue: float | None = Query(default=None, ge=0),
    q: str | None = None,
    limit: int = Query(default=1000, ge=1, le=10000),
) -> list[SalesRecord]:
    records = repo.list_records(
        regions=region,
        categories=category,
        statuses=status,
        start_date=start_date,
        end_date=end_date,
        min_revenue=min_revenue,
        max_revenue=max_revenue,
        query=q,
        limit=limit,
    )
    return [SalesRecord(**r) for r in records]


@app.get("/records/{record_id}", response_model=SalesRecord)
def get_record(record_id: int) -> SalesRecord:
    record = repo.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return SalesRecord(**record)


@app.post("/records", response_model=SalesRecord, status_code=201)
def create_record(payload: SalesRecordCreate) -> SalesRecord:
    created = repo.create_record(payload)
    return SalesRecord(**created)


@app.put("/records/{record_id}", response_model=SalesRecord)
def update_record(record_id: int, payload: SalesRecordUpdate) -> SalesRecord:
    updated = repo.update_record(record_id=record_id, payload=payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return SalesRecord(**updated)
