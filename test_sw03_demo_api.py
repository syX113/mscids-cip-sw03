"""Self-check for sw03_demo_api.py. No test framework needed.

    python test_sw03_demo_api.py

Stop the API first. This starts its own in-process copy, which resets data/ from data/seed/ and
then edits those same files, so a running server would see its data change underneath it.
It prints one line per check and exits non-zero if anything fails.
"""

import pandas as pd
from fastapi.testclient import TestClient

import sw03_demo_api as api

checks: list[tuple[str, bool]] = []


def check(name: str, actual: object, expected: object) -> None:
    checks.append((f"{name}: {actual!r}", actual == expected))


slip = {"sale_date": "2026-03-01", "product_id": 1, "country_id": 3, "units_sold": 10, "customer_rating": 5}

# Entering the block starts the API, which resets data/.
with TestClient(api.app) as client:
    # --- the endpoints answer at all -------------------------------------------
    for path in ("/", "/health", "/meta/options", "/regions", "/countries", "/categories", "/products"):
        check(f"GET {path}", client.get(path).status_code, 200)

    # --- the default answer is the whole dataset, not a silent 2000-row slice ---
    check("GET /sales is complete", len(client.get("/sales").json()), 3360)

    # --- GET by id joins in the names a row points at ---------------------------
    check("country has its region", client.get("/countries/3").json()["region_name"], "Europe")
    check("product has its category", client.get("/products/1").json()["category_name"], "Hardware")

    # --- name filters on /sales, as Streamlit sends them -----------------------
    rows = client.get("/sales", params={"region": "Europe", "product": "Edge Sensor X1"}).json()
    check("filter by names", {(r["region_name"], r["product_name"]) for r in rows}, {("Europe", "Edge Sensor X1")})

    # --- DELETE answers 204 then 404, and a deleted id is never handed out again -
    check("DELETE the newest sale", client.delete("/sales/3360").status_code, 204)
    check("DELETE it twice", client.delete("/sales/3360").status_code, 404)

    # --- POST /sales: five fields in, thirteen back, the server owns the total ---
    created = client.post("/sales", json=slip).json()
    check("POST /sales skips the deleted id", created["sale_id"], 3361)
    check("POST /sales returns 13 fields", len(created), 13)
    check("server computes 10 x 195.00", created["total_price"], 1950.0)
    check("a client-sent total is refused", client.post("/sales", json={**slip, "total_price": 5.5}).status_code, 422)

    # --- a stored total survives an unrelated edit, but follows units_sold ------
    sale = client.get("/sales/5").json()
    form = {k: sale[k] for k in ("sale_date", "product_id", "country_id", "units_sold")}  # Streamlit sends every field
    check("rating-only PUT keeps the total", client.put("/sales/5", json={**form, "customer_rating": 1}).json()["total_price"], sale["total_price"])
    price = client.get(f"/products/{sale['product_id']}").json()["price"]
    changed = client.put("/sales/5", json={"units_sold": sale["units_sold"] + 1}).json()
    check("units change recomputes", changed["total_price"], round(price * (sale["units_sold"] + 1), 2))

    # --- partial PUT: pandas 3 needs a real datetime, and null means "leave it" -
    check("PUT /sales with sale_date", client.put("/sales/1", json={"sale_date": "2024-06-02"}).status_code, 200)
    check("PUT price=null is a no-op", client.put("/products/1", json={"price": None}).json()["price"], 195.0)

    # --- DELETE refuses to orphan rows ------------------------------------------
    check("DELETE a region in use", client.delete("/regions/1").status_code, 400)
    spare = client.post("/regions", json={"name": "Temp", "description": "throwaway"}).json()
    check("DELETE an unused region", client.delete(f"/regions/{spare['region_id']}").status_code, 204)

    # --- rejected input becomes 400 or 422, never 500 --------------------------
    check("duplicate name", client.post("/regions", json={"name": "US", "description": "d"}).status_code, 400)
    check("unknown region_id", client.post("/countries", json={"name": "X", "region_id": 999}).status_code, 400)
    check("start after end", client.get("/sales", params={"start_date": "2024-06-01", "end_date": "2024-01-01"}).status_code, 400)
    check("missing sale", client.get("/sales/999999").status_code, 404)
    check("rating out of range", client.post("/sales", json={**slip, "customer_rating": 9}).status_code, 422)
    check("date out of range", client.put("/sales/2", json={"sale_date": "0001-01-01"}).status_code, 422)
    check("whitespace-only name", client.post("/regions", json={"name": "   ", "description": "d"}).status_code, 422)
    check("unknown field", client.put("/sales/9", json={"units_sol": 25}).status_code, 422)
    raw = {"headers": {"content-type": "application/json"}}  # Python's JSON reads 1e999 as inf and accepts NaN
    check("infinite price", client.post("/products", content='{"name": "X", "price": 1e999, "description": "d", "category_id": 1}', **raw).status_code, 422)
    check("NaN units", client.put("/sales/9", content='{"units_sold": NaN}', **raw).status_code, 422)

    # --- the lecture reads data/sales.parquet directly: same 7 columns, same order -
    check("sales file columns", list(pd.read_parquet(api.DATA_DIR / "sales.parquet").columns), list(pd.read_parquet(api.SEED_DIR / "sales.parquet").columns))

    # --- /docs is grouped, because students are sent there to learn -------------
    tags = {t for path in client.get("/openapi.json").json()["paths"].values() for op in path.values() for t in op.get("tags", [])}
    check("Swagger groups", sorted(tags), ["Categories", "Countries", "Products", "Regions", "Sales", "Service"])

failed = [name for name, passed in checks if not passed]
for name, passed in checks:
    print(f"  {'ok  ' if passed else 'FAIL'} {name}")
print(f"\n{len(checks) - len(failed)} passed, {len(failed)} failed")
raise SystemExit(1 if failed else 0)
