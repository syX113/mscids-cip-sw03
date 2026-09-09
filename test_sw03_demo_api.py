"""Self-check for sw03_demo_api.py. No test framework needed.

Run it with the API stopped (it starts its own in-process copy):

    python test_sw03_demo_api.py

It prints one line per check and exits non-zero if anything fails.
Importing the API resets data/ from data/seed/, so this never harms your data.
"""

from fastapi.testclient import TestClient

import sw03_demo_api as api

client = TestClient(api.app)
checks: list[tuple[str, bool]] = []


def check(name: str, actual: object, expected: object) -> None:
    checks.append((f"{name}: {actual!r}", actual == expected))


# --- the endpoints answer at all -------------------------------------------
for path in ("/", "/health", "/meta/options", "/regions", "/countries", "/categories", "/products"):
    check(f"GET {path}", client.get(path).status_code, 200)

# --- pandas 3 no longer coerces a date into a datetime column ---------------
check("PUT /sales with sale_date", client.put("/sales/1", json={"sale_date": "2024-06-02"}).status_code, 200)

# --- an explicit null must not poison a typed column ------------------------
check("PUT price=null is a no-op", client.put("/products/1", json={"price": None}).status_code, 200)
check("GET /products still works", client.get("/products").status_code, 200)

# --- a stored total survives an unrelated edit, but follows units_sold ------
client.put("/sales/5", json={"total_price": 999.0})
client.put("/sales/5", json={"customer_rating": 2})
check("manual total kept", client.get("/sales/5").json()["total_price"], 999.0)

sale = client.get("/sales/6").json()
client.put("/sales/6", json={"units_sold": sale["units_sold"] + 1})
check("total recomputed", client.get("/sales/6").json()["total_price"] != sale["total_price"], True)

# --- the default answer is the whole dataset, not a silent 2000-row slice ---
check("GET /sales is complete", len(client.get("/sales").json()), 3360)

# --- DELETE exists and refuses to orphan rows ------------------------------
check("DELETE a sale", client.delete("/sales/3").status_code, 204)
check("DELETE it twice", client.delete("/sales/3").status_code, 404)
check("DELETE a region in use", client.delete("/regions/1").status_code, 400)
spare = client.post("/regions", json={"name": "Temp", "description": "throwaway"}).json()
check("DELETE an unused region", client.delete(f"/regions/{spare['region_id']}").status_code, 204)

# --- rejected input becomes 400 or 422, never 500 --------------------------
check("duplicate name", client.post("/regions", json={"name": "US", "description": "d"}).status_code, 400)
check("unknown region_id", client.post("/countries", json={"name": "X", "region_id": 999}).status_code, 400)
check("start after end", client.get("/sales", params={"start_date": "2024-06-01", "end_date": "2024-01-01"}).status_code, 400)
check("missing sale", client.get("/sales/999999").status_code, 404)
check(
    "rating out of range",
    client.post("/sales", json={"sale_date": "2024-01-01", "product_id": 1, "country_id": 1, "units_sold": 1, "customer_rating": 9}).status_code,
    422,
)

# --- /docs is grouped, because students are sent there to learn -------------
tags = {t for path in client.get("/openapi.json").json()["paths"].values() for op in path.values() for t in op.get("tags", [])}
check("Swagger groups", sorted(tags), ["Categories", "Countries", "Products", "Regions", "Sales", "Service"])

failed = [name for name, passed in checks if not passed]
for name, passed in checks:
    print(f"  {'ok  ' if passed else 'FAIL'} {name}")
print(f"\n{len(checks) - len(failed)} passed, {len(failed)} failed")
raise SystemExit(1 if failed else 0)
