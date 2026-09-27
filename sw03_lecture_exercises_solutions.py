import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def cell_title(mo):
    mo.md(r"""
    # SW03 Basic Exercises: Storage and APIs (Solutions)

    The same cells as `sw03_lecture_exercises.py`, with every `### FILL HERE ###` line filled
    in. Every cell prints `pass`.

    ```bash
    marimo edit sw03_lecture_exercises_solutions.py
    ```
    """)
    return


@app.cell(hide_code=True)
def cell_exercise_list(mo):
    mo.md(r"""
    ## Exercise List

    1. Introduction: Create markdown output in marimo
    2. Introduction: Create a table preview and summary
    3. File I/O (Chapter 2): Write and read CSV
    4. File I/O (Chapters 2-3): Write and read Parquet, then compare its size to CSV
    5. Compression (Chapter 4): Create a gzip report
    6. Compression (Chapter 4): Compare gzip levels
    7. API (Chapter 8): Create a small FastAPI app
    8. API (Chapter 6): Call an endpoint and parse JSON
    """)
    return


@app.cell(hide_code=True)
def syntax_cheatsheet(mo):
    mo.md(r"""
    ## Quick Syntax Cheatsheet

    ```python
    # f-string
    text = f"Hello {name}"

    # CSV read pattern
    with path.open("r", newline='', encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        rows = list(reader)

    # count the rows you just read
    row_count = len(rows)

    # pick the dictionary key with the smallest value
    best_key = min(sizes_by_key, key=sizes_by_key.get)

    # join a base URL and a path
    url = f"{base}{path}"
    ```
    """)
    return


@app.cell
def cell_imports():
    import csv
    import gzip
    import json
    import tempfile
    from pathlib import Path

    import marimo as mo

    return Path, csv, gzip, json, mo, tempfile


@app.cell
def cell_shared_data():
    sample_rows = [
        {"id": 1, "city": "Zurich", "qty": 2, "unit_price": 3.5},
        {"id": 2, "city": "Bern", "qty": 5, "unit_price": 1.2},
        {"id": 3, "city": "Basel", "qty": 3, "unit_price": 4.0},
        {"id": 4, "city": "Geneva", "qty": 4, "unit_price": 3.5},
    ]
    sample_text = "storage-compression-api-" * 200

    # 4 rows: CSV 85 B vs Parquet ~1.4 KB (schema + footer dominate).
    # 2,000 rows: Parquet is ~35% of the CSV, which is why Exercise 4 uses the bulk rows.
    sample_rows_bulk = [
        {**row, "id": batch * len(sample_rows) + row["id"]}
        for batch in range(500)
        for row in sample_rows
    ]
    return sample_rows, sample_rows_bulk, sample_text


@app.cell(hide_code=True)
def exercise1_prompt(mo):
    mo.md(r"""
    ## Exercise 1 (Introduction): Create Markdown Output

    Implement `build_intro_markdown(title, topic)`.

    Expected behavior:
    - `text` is `### <title>`, a newline, then `This notebook practices **<topic>**.`
    - `widget` is `mo.md(text)`, shown below the cell
    - return `{"text": ..., "widget": ...}`

    Hint: one f-string that uses `title` and `topic`; `\n` is the newline.
    """)
    return


@app.cell
def exercise1_solution(mo):
    def build_intro_markdown(title, topic):
        markdown_text = f"### {title}\nThis notebook practices **{topic}**."
        widget = mo.md(markdown_text)
        return {"text": markdown_text, "widget": widget}

    result_ex1 = build_intro_markdown("Welcome", "files, compression, and APIs")
    check_passed_ex1 = (
        result_ex1["text"]
        == "### Welcome\nThis notebook practices **files, compression, and APIs**."
    )
    print("pass" if check_passed_ex1 else "fail")
    result_ex1["widget"]
    return


@app.cell(hide_code=True)
def exercise2_prompt(mo):
    mo.md(r"""
    ## Exercise 2 (Introduction): Table Preview and Summary

    Implement `create_preview_table(rows)`.

    Expected behavior:
    - `row_count` is the number of rows
    - `columns` lists the column names, taken from the keys of the first row
    - `widget` is an interactive `mo.ui.table` of the rows, shown below the cell

    Hint: `len()` counts the rows; the keys of `rows[0]` are the column names.
    """)
    return


@app.cell
def exercise2_solution(mo, sample_rows):
    def create_preview_table(rows):
        row_count = len(rows)

        columns = list(rows[0].keys())

        widget = mo.ui.table(rows, label="Sample rows")
        return {"row_count": row_count, "columns": columns, "widget": widget}

    result_ex2 = create_preview_table(sample_rows)
    check_passed_ex2 = (
        result_ex2["row_count"] == len(sample_rows)
        and result_ex2["columns"] == ["id", "city", "qty", "unit_price"]
        and isinstance(result_ex2["widget"], mo.ui.table)
    )
    print("pass" if check_passed_ex2 else "fail")
    result_ex2["widget"]
    return


@app.cell(hide_code=True)
def exercise3_prompt(mo):
    mo.md(r"""
    ## Exercise 3 (File I/O, Chapter 2): Write and Read CSV

    Implement `write_and_read_csv(rows, file_path)`.

    Expected behavior:
    - write the rows to a CSV file with a header, then read them back
    - return `row_count`, `file_size`, `columns` and `loaded_rows` (the rows read from the file)

    Hint: `list(reader)` collects every row; count the rows you read back, not the ones you wrote.

    Notice: CSV hands every value back as a string (Chapter 2), so `qty` 2 returns as `"2"`.
    """)
    return


@app.cell
def exercise3_solution(Path, csv, sample_rows, tempfile):
    def write_and_read_csv(rows, file_path):
        columns = list(rows[0].keys())

        with file_path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        with file_path.open("r", newline="", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            loaded_rows = list(reader)

        row_count = len(loaded_rows)

        return {
            "row_count": row_count,
            "file_size": file_path.stat().st_size,
            "columns": columns,
            "loaded_rows": loaded_rows,
        }

    with tempfile.TemporaryDirectory() as temp_dir_ex3:
        result_ex3 = write_and_read_csv(sample_rows, Path(temp_dir_ex3) / "exercise3.csv")

    check_passed_ex3 = (
        result_ex3["row_count"] == len(sample_rows)
        and len(result_ex3["loaded_rows"]) == len(sample_rows)
        # the rows really came back out of the file: CSV turned qty 2 into the string "2"
        and result_ex3["loaded_rows"][0]["qty"] == "2"
    )
    print("pass" if check_passed_ex3 else "fail")
    return (write_and_read_csv,)


@app.cell(hide_code=True)
def exercise4_prompt(mo):
    mo.md(r"""
    ## Exercise 4 (File I/O, Chapters 2-3): Parquet and CSV Comparison

    Implement `write_parquet_and_compare(rows, parquet_path, csv_path)`.

    Expected behavior:
    - write the rows as CSV (with `write_and_read_csv` from Exercise 3) and as Parquet
    - read the Parquet file back and count its rows
    - return `csv_bytes`, `parquet_bytes`, `size_ratio_parquet_to_csv` and `row_count`

    Hint: the CSV size is already in the Exercise 3 result; the ratio is
    `parquet_bytes / csv_bytes` (below 1 means Parquet is smaller).
    """)
    return


@app.cell
def exercise4_solution(Path, sample_rows_bulk, tempfile, write_and_read_csv):
    import pyarrow as pa
    import pyarrow.parquet as pq

    def write_parquet_and_compare(rows, parquet_path, csv_path):
        csv_result = write_and_read_csv(rows, csv_path)
        csv_bytes = csv_result["file_size"]

        table = pa.Table.from_pylist(rows)
        pq.write_table(table, parquet_path)
        table_read_back = pq.read_table(parquet_path)
        parquet_bytes = parquet_path.stat().st_size

        size_ratio = round(parquet_bytes / csv_bytes, 4)

        return {
            "csv_bytes": csv_bytes,
            "parquet_bytes": parquet_bytes,
            "size_ratio_parquet_to_csv": size_ratio,
            "row_count": table_read_back.num_rows,
        }

    with tempfile.TemporaryDirectory() as temp_dir_ex4:
        csv_path_ex4 = Path(temp_dir_ex4) / "exercise4.csv"
        result_ex4 = write_parquet_and_compare(
            sample_rows_bulk, Path(temp_dir_ex4) / "exercise4.parquet", csv_path_ex4
        )
        csv_size_ex4 = csv_path_ex4.stat().st_size

    check_passed_ex4 = (
        result_ex4["csv_bytes"] == csv_size_ex4
        and result_ex4["row_count"] == len(sample_rows_bulk)
        and result_ex4["size_ratio_parquet_to_csv"] is not None
        # really parquet / csv, not the other way round
        and round(result_ex4["size_ratio_parquet_to_csv"], 4)
        == round(result_ex4["parquet_bytes"] / result_ex4["csv_bytes"], 4)
        and result_ex4["size_ratio_parquet_to_csv"] < 1
    )
    print("pass" if check_passed_ex4 else "fail")
    result_ex4
    return


@app.cell(hide_code=True)
def exercise5_prompt(mo):
    mo.md(r"""
    ## Exercise 5 (Compression, Chapter 4): Create gzip Report

    Implement `gzip_report(text_payload, level=6)`.

    Expected behavior:
    - encode the text as UTF-8 and compress it with gzip at `level`
    - return `raw_bytes`, `compressed_bytes` and `compression_ratio`

    Hint: use `len()` on the encoded bytes; the ratio is `compressed_bytes / raw_bytes`.
    """)
    return


@app.cell
def exercise5_solution(gzip, sample_text):
    def gzip_report(text_payload, level=6):
        payload_bytes = text_payload.encode("utf-8")
        raw_bytes = len(payload_bytes)

        compressed_payload = gzip.compress(payload_bytes, compresslevel=level)
        compressed_bytes = len(compressed_payload)

        compression_ratio = round(compressed_bytes / raw_bytes, 4)

        return {
            "raw_bytes": raw_bytes,
            "compressed_bytes": compressed_bytes,
            "compression_ratio": compression_ratio,
        }

    result_ex5 = gzip_report(sample_text, 6)
    check_passed_ex5 = (
        result_ex5["raw_bytes"] == len(sample_text.encode("utf-8"))
        # bytes, not characters: "Zürich" is 6 characters but 7 UTF-8 bytes
        and gzip_report("Zürich", 6)["raw_bytes"] == 7
        # really compressed / raw, not just some number below 1
        and round(result_ex5["compression_ratio"], 4)
        == round(result_ex5["compressed_bytes"] / result_ex5["raw_bytes"], 4)
    )
    print("pass" if check_passed_ex5 else "fail")
    return (gzip_report,)


@app.cell(hide_code=True)
def exercise6_prompt(mo):
    mo.md(r"""
    ## Exercise 6 (Compression, Chapter 4): Compare gzip Levels

    Implement `compare_gzip_levels(text_payload, levels)`.

    Expected behavior:
    - compress the text once per level with `gzip_report` from Exercise 5
    - return `compressed_by_level` (level → bytes), `best_level` (smallest output) and
      `best_bytes` (its size)

    Hint: `min(..., key=...)` finds the level; look its size up in the same dictionary.
    Then look at the sizes below the cell: does level 9 beat level 6?
    """)
    return


@app.cell
def exercise6_solution(gzip_report, sample_text):
    def compare_gzip_levels(text_payload, levels):
        compressed_by_level = {}
        for level in levels:
            compressed_by_level[level] = gzip_report(text_payload, level)["compressed_bytes"]

        best_level = min(compressed_by_level, key=compressed_by_level.get)
        best_bytes = compressed_by_level[best_level]

        return {
            "compressed_by_level": compressed_by_level,
            "best_level": best_level,
            "best_bytes": best_bytes,
        }

    result_ex6 = compare_gzip_levels(sample_text, [1, 6, 9])
    sizes_ex6 = result_ex6["compressed_by_level"]
    check_passed_ex6 = (
        result_ex6["best_level"] in sizes_ex6
        and result_ex6["best_bytes"] == sizes_ex6[result_ex6["best_level"]] == min(sizes_ex6.values())
    )
    print("pass" if check_passed_ex6 else "fail")
    sizes_ex6
    return


@app.cell(hide_code=True)
def exercise7_prompt(mo):
    mo.md(r"""
    ## Exercise 7 (API, Chapter 8): Create a FastAPI App

    Implement `create_hello_api()`.

    Expected behavior:
    - `GET /hello` returns `{"message": "hello from api"}`
    - `GET /status` returns `{"status": "ok"}`

    Hint: an endpoint just returns a dictionary; FastAPI turns it into JSON. The check calls
    your app through FastAPI's `TestClient`, which sends HTTP requests to it in-process (no
    server needed), so path, verb and JSON must all match.
    """)
    return


@app.cell
def exercise7_solution():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    def create_hello_api():
        api = FastAPI(title="sw03-exercise-api")

        @api.get("/hello")
        def hello():
            return {"message": "hello from api"}

        @api.get("/status")
        def status():
            return {"status": "ok"}

        return api

    client_ex7 = TestClient(create_hello_api())
    check_passed_ex7 = (
        client_ex7.get("/hello").json() == {"message": "hello from api"}
        and client_ex7.get("/status").json() == {"status": "ok"}
    )
    print("pass" if check_passed_ex7 else "fail")
    return


@app.cell(hide_code=True)
def exercise8_prompt(mo):
    mo.md(r"""
    ## Exercise 8 (API, Chapter 6): Call an Endpoint and Parse JSON

    Implement `call_json_endpoint(base_url, path, opener)`. `opener` works like
    `urllib.request.urlopen`: call it with a URL and it returns a response with `.read()`
    and `.status`. `urlopen` is the standard library's version of the `requests` calls from
    Chapter 6: `.status` instead of `.status_code`, `.read()` plus `json.loads` instead of `.json()`.

    Expected behavior:
    - call `base_url` + `path` (the code already strips stray slashes)
    - parse the JSON body
    - return `ok`, `url`, `status` and `payload`

    Hint: `ok` is true for any 2xx status (200 OK, 201 Created, ...).
    """)
    return


@app.cell
def exercise8_solution(json):
    from functools import partial

    def call_json_endpoint(base_url, path, opener):
        normalized_base = base_url.rstrip("/")
        normalized_path = "/" + path.lstrip("/")

        url = f"{normalized_base}{normalized_path}"

        try:
            response = opener(url, timeout=2)
            payload = json.loads(response.read().decode("utf-8"))
            status = response.status
            ok = 200 <= status < 300
            return {"ok": ok, "url": url, "status": status, "payload": payload}
        except Exception as exc:
            return {"ok": False, "url": url, "status": None, "payload": str(exc)}

    # Stands in for urllib.request.urlopen, so the check needs no running server:
    # anything with .read() and .status works as a response.
    class FakeResponse:
        def __init__(self, payload_bytes, status):
            self.payload_bytes = payload_bytes
            self.status = status

        def read(self):
            return self.payload_bytes

    def fake_opener(url, timeout=2, status=200):
        payload = json.dumps({"message": "hello from api"}).encode("utf-8")
        return FakeResponse(payload, status)

    # the stray "/" after the port must not end up in the url
    result_ex8 = call_json_endpoint("http://127.0.0.1:8000/", "/hello", fake_opener)
    # ok follows the status: 201 Created is a success too, 404 Not Found is not
    ok_by_status_ex8 = {
        code: call_json_endpoint(
            "http://127.0.0.1:8000", "/hello", partial(fake_opener, status=code)
        )["ok"]
        for code in (201, 404)
    }
    check_passed_ex8 = result_ex8 == {
        "ok": True,
        "url": "http://127.0.0.1:8000/hello",
        "status": 200,
        "payload": {"message": "hello from api"},
    } and ok_by_status_ex8 == {201: True, 404: False}
    print("pass" if check_passed_ex8 else "fail")
    return


@app.cell(hide_code=True)
def final_note(mo):
    mo.md(r"""
    ## Optional: Call the Real API

    Start the demo API (see the README), then swap the fake opener for the real one in a new
    cell:

    ```python
    import urllib.request

    call_json_endpoint("http://127.0.0.1:8000", "/health", urllib.request.urlopen)
    # {'ok': True, 'url': 'http://127.0.0.1:8000/health', 'status': 200, 'payload': {'status': 'ok'}}
    ```

    Unlike the fake, the real `urlopen` raises for a 4xx or 5xx answer, so `/sales/999999`
    lands in the `except` branch: `ok` is `False` and `status` is `None`.
    """)
    return


if __name__ == "__main__":
    app.run()
