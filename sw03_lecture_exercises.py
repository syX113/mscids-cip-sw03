import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell
def cell_imports():
    import csv
    import gzip
    import importlib
    import json
    import tempfile
    from pathlib import Path

    import marimo as mo

    return Path, csv, gzip, importlib, json, mo, tempfile


@app.cell
def cell_optional_import(importlib):
    def optional_import(module_name):
        if importlib.util.find_spec(module_name) is None:
            return None
        return importlib.import_module(module_name)

    return (optional_import,)


@app.cell(hide_code=True)
def cell_title(mo):
    mo.md(r"""
    # SW03 Basic Exercises: Storage and APIs

    This notebook contains practical exercises.

    Rule for students:
    - Edit only lines marked with `TODO`.
    - Complete all TODOs in each exercise.
    - Enter code where `### FILL HERE ###` is shown.

    Recommended command:

    ```bash
    marimo edit sw03_lecture_exercises.py
    ```
    """)
    return


@app.cell(hide_code=True)
def cell_exercise_list(mo):
    mo.md(r"""
    ## Exercise List

    1. Introduction: Create markdown output in Marimo
    2. Introduction: Create table preview and summary
    3. File I/O: Write and read CSV
    4. File I/O: Write and read Parquet, then compare size to CSV
    5. Compression: Create gzip report
    6. Compression: Compare gzip levels
    7. API: Create a small FastAPI app
    8. API: Call an endpoint and parse JSON

    Each exercise prints `pass` or `fail`.
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
    with path.open("r", newline="\", encoding="utf-8") as file_handle:
    reader = csv.DictReader(file_handle)
    rows = list(reader)

    # clamp a numeric value
    level = min(9, max(1, int(level)))

    # safe URL join
    base = str(base_url).rstrip("/")
    path = "/" + str(path).lstrip("/")
    url = f"{base}{path}"
    ```
    """)
    return


@app.cell
def cell_shared_data():
    sample_rows = [
        {"id": 1, "city": "Zurich", "qty": 2, "unit_price": 3.5},
        {"id": 2, "city": "Bern", "qty": 5, "unit_price": 1.2},
        {"id": 3, "city": "Basel", "qty": 3, "unit_price": 4.0},
        {"id": 4, "city": "Geneva", "qty": 4, "unit_price": 3.5},
    ]
    sample_text = "storage-compression-api-" * 200
    return sample_rows, sample_text


@app.cell(hide_code=True)
def exercise1_prompt(mo):
    mo.md(r"""
    ## Exercise 1 (Introduction): Create Markdown Output

    Implement `build_intro_markdown(mo_module, title, topic)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A formatted string should be used.
    - Reuse both function inputs: `title` and `topic`.
    """)
    return


@app.cell
def exercise1(mo):
    def build_intro_markdown(mo_module, title, topic):
        # TODO (Exercise 1): edit the following line
        topic_text = ""  # ### FILL HERE ###

        # TODO (Exercise 1): edit the following line
        markdown_text = ""  # ### FILL HERE ###
        widget = mo_module.md(markdown_text)
        return {"text": markdown_text, "widget": widget}

    result_ex1 = build_intro_markdown(mo, "Welcome", "files, compression, and APIs")
    check_passed_ex1 = (
        isinstance(result_ex1, dict)
        and result_ex1["text"]
        == "### Welcome\nThis notebook practices **files, compression, and APIs**."
        and result_ex1["widget"] is not None
    )
    print("pass" if check_passed_ex1 else "fail")
    return


@app.cell(hide_code=True)
def exercise2_prompt(mo):
    mo.md(r"""
    ## Exercise 2 (Introduction): Table Preview and Summary

    Implement `create_preview_table(mo_module, rows)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A list operation should be used to get column names.
    - A table widget method from `mo_module.ui` should be used.
    """)
    return


@app.cell
def exercise2(mo, sample_rows):
    def create_preview_table(mo_module, rows):
        # TODO (Exercise 2): edit the following line
        row_count = 0  # ### FILL HERE ###

        # TODO (Exercise 2): edit the following line
        columns = []  # ### FILL HERE ###

        # TODO (Exercise 2): edit the following line
        widget = None  # ### FILL HERE ###
        return {"row_count": row_count, "columns": columns, "widget": widget}

    result_ex2 = create_preview_table(mo, sample_rows)
    check_passed_ex2 = (
        isinstance(result_ex2, dict)
        and result_ex2["row_count"] == len(sample_rows)
        and result_ex2["columns"] == ["id", "city", "qty", "unit_price"]
        and result_ex2["widget"] is not None
    )
    print("pass" if check_passed_ex2 else "fail")
    return


@app.cell(hide_code=True)
def exercise3_prompt(mo):
    mo.md(r"""
    ## Exercise 3 (File I/O): Write and Read CSV

    Implement `write_and_read_csv(rows, file_path)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A dictionary writer and dictionary reader should be used.
    - One TODO should convert the reader output to a list.
    - One TODO should set the final row count.
    """)
    return


@app.cell
def exercise3(Path, csv, sample_rows, tempfile):
    def write_and_read_csv(rows, file_path):
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        columns = list(rows[0].keys()) if rows else []

        with path_obj.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        with path_obj.open("r", newline="", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            # TODO (Exercise 3): edit the following line
            loaded_rows = []  # ### FILL HERE ###

        # TODO (Exercise 3): edit the following line
        row_count_value = 0  # ### FILL HERE ###

        return {
            "row_count": row_count_value,
            "file_size": int(path_obj.stat().st_size) if path_obj.exists() else 0,
            "columns": columns,
        }

    with tempfile.TemporaryDirectory() as temp_dir_ex3:
        csv_path_ex3 = Path(temp_dir_ex3) / "exercise3.csv"
        result_ex3 = write_and_read_csv(sample_rows, csv_path_ex3.as_posix())

    check_passed_ex3 = (
        isinstance(result_ex3, dict)
        and result_ex3["row_count"] == len(sample_rows)
        and result_ex3["file_size"] > 0
        and result_ex3["columns"] == ["id", "city", "qty", "unit_price"]
    )
    print("pass" if check_passed_ex3 else "fail")
    return (write_and_read_csv,)


@app.cell(hide_code=True)
def exercise4_prompt(mo):
    mo.md(r"""
    ## Exercise 4 (File I/O): Parquet and CSV Comparison

    Implement `write_parquet_and_compare(rows, parquet_path, csv_path)`.

    Complete all TODO lines in the code cell.

    Hint:
    - Optional imports should be used for parquet support.
    - A ratio should compare parquet size against CSV size.
    """)
    return


@app.cell
def exercise4(
    Path,
    optional_import,
    sample_rows,
    tempfile,
    write_and_read_csv,
):
    def write_parquet_and_compare(rows, parquet_path, csv_path):
        pyarrow_module = optional_import("pyarrow")
        parquet_module = optional_import("pyarrow.parquet")

        csv_result = write_and_read_csv(rows, csv_path)
        # TODO (Exercise 4): edit the following line
        csv_bytes = 0  # ### FILL HERE ###

        if pyarrow_module is None or parquet_module is None:
            return {
                "csv_bytes": csv_bytes,
                "parquet_bytes": -1,
                "size_ratio_parquet_to_csv": None,
                "row_count": -1,
            }

        parquet_file = Path(parquet_path)
        parquet_file.parent.mkdir(parents=True, exist_ok=True)

        table = pyarrow_module.Table.from_pylist(rows)
        parquet_module.write_table(table, parquet_file.as_posix())
        table_read_back = parquet_module.read_table(parquet_file.as_posix())

        parquet_bytes = int(parquet_file.stat().st_size)
        # TODO (Exercise 4): edit the following line
        size_ratio = None  # ### FILL HERE ###

        return {
            "csv_bytes": csv_bytes,
            "parquet_bytes": parquet_bytes,
            "size_ratio_parquet_to_csv": size_ratio,
            "row_count": int(table_read_back.num_rows),
        }

    with tempfile.TemporaryDirectory() as temp_dir_ex4:
        parquet_path_ex4 = Path(temp_dir_ex4) / "exercise4.parquet"
        csv_path_ex4 = Path(temp_dir_ex4) / "exercise4.csv"
        result_ex4 = write_parquet_and_compare(
            sample_rows,
            parquet_path_ex4.as_posix(),
            csv_path_ex4.as_posix(),
        )

    if result_ex4["parquet_bytes"] == -1:
        check_passed_ex4 = (
            result_ex4["csv_bytes"] > 0
            and result_ex4["size_ratio_parquet_to_csv"] is None
            and result_ex4["row_count"] == -1
        )
    else:
        check_passed_ex4 = (
            result_ex4["csv_bytes"] > 0
            and result_ex4["parquet_bytes"] > 0
            and result_ex4["size_ratio_parquet_to_csv"] is not None
            and result_ex4["row_count"] == len(sample_rows)
        )

    print("pass" if check_passed_ex4 else "fail")
    return


@app.cell(hide_code=True)
def exercise5_prompt(mo):
    mo.md(r"""
    ## Exercise 5 (Compression): Create gzip Report

    Implement `gzip_report(text_payload, level=6)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A byte length method should be used.
    - The compression ratio should compare compressed size to raw size.
    """)
    return


@app.cell
def exercise5(gzip, sample_text):
    def gzip_report(text_payload, level=6):
        payload_bytes = str(text_payload).encode("utf-8")
        # TODO (Exercise 5): edit the following line
        raw_bytes = 0  # ### FILL HERE ###
        compression_level = min(9, max(1, int(level)))

        compressed_payload = gzip.compress(payload_bytes, compresslevel=compression_level)
        compressed_bytes = len(compressed_payload)

        # TODO (Exercise 5): edit the following line
        compression_ratio = 1.0  # ### FILL HERE ###

        return {
            "raw_bytes": raw_bytes,
            "compressed_bytes": compressed_bytes,
            "compression_ratio": compression_ratio,
        }

    result_ex5 = gzip_report(sample_text, 6)
    check_passed_ex5 = (
        isinstance(result_ex5, dict)
        and result_ex5["raw_bytes"] > 0
        and result_ex5["compressed_bytes"] > 0
        and 0 < result_ex5["compression_ratio"] < 1
    )
    print("pass" if check_passed_ex5 else "fail")
    return (gzip_report,)


@app.cell(hide_code=True)
def exercise6_prompt(mo):
    mo.md(r"""
    ## Exercise 6 (Compression): Compare gzip Levels

    Implement `compare_gzip_levels(text_payload, levels)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A dictionary key function should be used to find the smallest value.
    - After finding the best key, retrieve its value from the same dictionary.
    """)
    return


@app.cell
def exercise6(gzip_report, sample_text):
    def compare_gzip_levels(text_payload, levels):
        compressed_by_level = {}
        for level in levels:
            report = gzip_report(text_payload, level)
            compressed_by_level[int(level)] = report["compressed_bytes"]

        if not compressed_by_level:
            return {
                "compressed_by_level": {},
                "best_level": None,
                "best_bytes": None,
            }

        # TODO (Exercise 6): edit the following line
        best_level = None  # ### FILL HERE ###
        # TODO (Exercise 6): edit the following line
        best_bytes = None  # ### FILL HERE ###

        return {
            "compressed_by_level": compressed_by_level,
            "best_level": best_level,
            "best_bytes": best_bytes,
        }

    result_ex6 = compare_gzip_levels(sample_text, [1, 6, 9])
    check_passed_ex6 = (
        isinstance(result_ex6, dict)
        and set(result_ex6["compressed_by_level"].keys()) == {1, 6, 9}
        and result_ex6["best_level"] in {1, 6, 9}
        and isinstance(result_ex6["best_bytes"], int)
    )
    print("pass" if check_passed_ex6 else "fail")
    return


@app.cell(hide_code=True)
def exercise7_prompt(mo):
    mo.md(r"""
    ## Exercise 7 (API): Create FastAPI App

    Implement `create_hello_api(optional_import_fn)`.

    Complete all TODO lines in the code cell.

    Hint:
    - A FastAPI object should be created from the imported class.
    - Both endpoints should return small dictionaries.
    """)
    return


@app.cell
def exercise7(optional_import):
    def create_hello_api(optional_import_fn):
        fastapi_module = optional_import_fn("fastapi")
        if fastapi_module is None:
            return None

        FastAPI = fastapi_module.FastAPI
        api = FastAPI(title="sw03-exercise-api")

        @api.get("/hello")
        def hello():
            # TODO (Exercise 7): edit the following line
            return {"message": "### FILL HERE ###"}

        @api.get("/status")
        def status():
            # TODO (Exercise 7): edit the following line
            return {"status": "### FILL HERE ###"}

        return api

    api_ex7 = create_hello_api(optional_import)
    if api_ex7 is None:
        check_passed_ex7 = True
    else:
        route_paths_ex7 = {getattr(route, "path", "") for route in api_ex7.routes}
        hello_route_ex7 = next(
            (
                route
                for route in api_ex7.routes
                if getattr(route, "path", "") == "/hello"
                and "GET" in getattr(route, "methods", set())
            ),
            None,
        )
        status_route_ex7 = next(
            (
                route
                for route in api_ex7.routes
                if getattr(route, "path", "") == "/status"
                and "GET" in getattr(route, "methods", set())
            ),
            None,
        )
        check_passed_ex7 = (
            "/hello" in route_paths_ex7
            and "/status" in route_paths_ex7
            and hello_route_ex7 is not None
            and status_route_ex7 is not None
            and hello_route_ex7.endpoint() == {"message": "hello from api"}
            and status_route_ex7.endpoint() == {"status": "ok"}
        )

    print("pass" if check_passed_ex7 else "fail")
    return


@app.cell(hide_code=True)
def exercise8_prompt(mo):
    mo.md(r"""
    ## Exercise 8 (API): Call Endpoint and Parse JSON

    Implement `call_json_endpoint(base_url, path, opener)`.

    Complete all TODO lines in the code cell.

    Hint:
    - Build the URL from base and path parts.
    - The final `ok` value should depend on both the status code and payload type.
    """)
    return


@app.cell
def exercise8(json):
    def call_json_endpoint(base_url, path, opener):
        normalized_base = str(base_url).rstrip("/")
        normalized_path = "/" + str(path).lstrip("/")

        # TODO (Exercise 8): edit the following line
        url = "### FILL HERE ###"

        try:
            response = opener(url, timeout=2)
            payload = json.loads(response.read().decode("utf-8"))
            status = getattr(response, "status", None)
            # TODO (Exercise 8): edit the following line
            ok = False  # ### FILL HERE ###
            return {
                "ok": ok,
                "url": url,
                "status": status,
                "payload": payload,
            }
        except Exception as exc:
            return {
                "ok": False,
                "url": url,
                "status": None,
                "payload": str(exc),
            }

    class FakeResponse:
        def __init__(self, payload_bytes, status=200):
            self.payload_bytes = payload_bytes
            self.status = status

        def read(self):
            return self.payload_bytes

    def fake_opener(url, timeout=2):
        del url
        del timeout
        payload = json.dumps({"message": "hello from api"}).encode("utf-8")
        return FakeResponse(payload, status=200)

    result_ex8 = call_json_endpoint("http://127.0.0.1:8000", "/hello", fake_opener)
    check_passed_ex8 = result_ex8 == {
        "ok": True,
        "url": "http://127.0.0.1:8000/hello",
        "status": 200,
        "payload": {"message": "hello from api"},
    }
    print("pass" if check_passed_ex8 else "fail")
    return


@app.cell(hide_code=True)
def final_note(mo):
    mo.md(r"""
    ## Optional Manual API Run

    To test a real API in a terminal, save this as `hello_api.py`:

    ```python
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/hello")
    def hello():
        return {"message": "hello from api"}
    ```

    Then run:

    ```bash
    uvicorn hello_api:app --reload
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
