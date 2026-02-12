import marimo

__generated_with = "0.19.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import csv
    import importlib
    import json
    import tempfile
    from pathlib import Path

    import marimo as mo

    return Path, csv, importlib, json, mo, tempfile


@app.cell
def _(importlib):
    def optional_import(module_name):
        if importlib.util.find_spec(module_name) is None:
            return None
        return importlib.import_module(module_name)

    return (optional_import,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SW03 Basic Exercises: Storage and APIs

    This notebook contains basic, practical exercises.

    Topics:
    - write and read Parquet
    - compare CSV and Parquet size
    - basic compression check
    - create and call a simple API

    Recommended command:

    ```bash
    marimo edit sw03_lecture_exercises.py
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise List

    1. Write a Parquet file
    2. Read a Parquet file
    3. Write a CSV file
    4. Read a CSV file
    5. Compare CSV and Parquet size
    6. Simple gzip compression report
    7. Create a simple API (`GET /hello`)
    8. Call API from Python
    9. Row vs column I/O estimate

    Checks are directly in each exercise code cell.
    Each cell prints only: `pass` or `fail`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## References

    - Parquet / PyArrow: https://arrow.apache.org/docs/python/
    - Parquet format: https://parquet.apache.org/
    - CSV module: https://docs.python.org/3/library/csv.html
    - gzip module: https://docs.python.org/3/library/gzip.html
    - FastAPI: https://fastapi.tiangolo.com/
    """)
    return


@app.cell
def _():
    sample_rows = [
        {"id": 1, "city": "Zurich", "qty": 2, "unit_price": 3.5},
        {"id": 2, "city": "Bern", "qty": 5, "unit_price": 1.2},
        {"id": 3, "city": "Basel", "qty": 3, "unit_price": 4.0},
        {"id": 4, "city": "Geneva", "qty": 4, "unit_price": 3.5},
    ]
    sample_text = "storage-compression-api-" * 150
    return sample_rows, sample_text


@app.cell
def _(mo, sample_rows):
    mo.ui.table(sample_rows, label="Shared sample rows")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 1: Write a Parquet File

    `write_parquet_file(rows, file_path)`

    Expected behavior:
    - return `-1` if pyarrow is missing
    - otherwise write file and return positive file size
    """)
    return


@app.cell
def _(Path, optional_import, sample_rows, tempfile):
    def write_parquet_file(rows, file_path):
        pa = optional_import("pyarrow")
        pq = optional_import("pyarrow.parquet")
        if pa is None or pq is None:
            return -1

        _path = Path(file_path)
        _path.parent.mkdir(parents=True, exist_ok=True)
        _table = pa.Table.from_pylist(rows)

        pq.write_table(_table, _path.as_posix())

        if not _path.exists():
            return 0
        return int(_path.stat().st_size)

    _pyarrow_ready = optional_import("pyarrow") is not None and optional_import(
        "pyarrow.parquet"
    ) is not None
    with tempfile.TemporaryDirectory() as _tmp:
        _path = Path(_tmp) / "ex1.parquet"
        _size = write_parquet_file(sample_rows, _path.as_posix())

    _ok = (_size == -1) if not _pyarrow_ready else (_size > 0)
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 2: Read a Parquet File

    `read_parquet_count(file_path)`

    Expected behavior:
    - return `-1` if pyarrow is missing
    - return `0` if file does not exist
    - return row count when file exists
    """)
    return


@app.cell
def _(Path, optional_import, sample_rows, tempfile):
    def read_parquet_count(file_path):
        pa = optional_import("pyarrow")
        pq = optional_import("pyarrow.parquet")
        if pa is None or pq is None:
            return -1

        _path = Path(file_path)
        if not _path.exists():
            return 0

        _table = pq.read_table(_path.as_posix())
        return int(_table.num_rows)

    _pyarrow_ready = optional_import("pyarrow") is not None and optional_import(
        "pyarrow.parquet"
    ) is not None
    if not _pyarrow_ready:
        _ok = read_parquet_count("missing.parquet") == -1
    else:
        _pa = optional_import("pyarrow")
        _pq = optional_import("pyarrow.parquet")
        with tempfile.TemporaryDirectory() as _tmp:
            _path = Path(_tmp) / "ex2.parquet"
            _table = _pa.Table.from_pylist(sample_rows)
            _pq.write_table(_table, _path.as_posix())
            _count = read_parquet_count(_path.as_posix())
        _ok = _count == len(sample_rows)

    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 3: Write a CSV File

    `write_csv_file(rows, file_path)`

    Expected behavior:
    - write header and rows
    - return file size in bytes
    """)
    return


@app.cell
def _(Path, csv, sample_rows, tempfile):
    def write_csv_file(rows, file_path):
        _path = Path(file_path)
        _path.parent.mkdir(parents=True, exist_ok=True)

        _fieldnames = list(rows[0].keys()) if rows else []
        with _path.open("w", newline="", encoding="utf-8") as _f:
            _writer = csv.DictWriter(_f, fieldnames=_fieldnames)
            _writer.writeheader()
            _writer.writerows(rows)

        return int(_path.stat().st_size) if _path.exists() else 0

    with tempfile.TemporaryDirectory() as _tmp:
        _path = Path(_tmp) / "ex3.csv"
        _size = write_csv_file(sample_rows, _path.as_posix())
    _ok = _size > 0
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 4: Read a CSV File

    `read_csv_count(file_path)`

    Expected behavior:
    - return `0` for missing file
    - return row count for existing file
    """)
    return


@app.cell
def _(Path, csv, sample_rows, tempfile):
    def read_csv_count(file_path):
        _path = Path(file_path)
        if not _path.exists():
            return 0

        with _path.open("r", newline="", encoding="utf-8") as _f:
            _reader = csv.DictReader(_f)
            return len(list(_reader))

    with tempfile.TemporaryDirectory() as _tmp:
        _path = Path(_tmp) / "ex4.csv"
        _fieldnames = list(sample_rows[0].keys())
        with _path.open("w", newline="", encoding="utf-8") as _f:
            _writer = csv.DictWriter(_f, fieldnames=_fieldnames)
            _writer.writeheader()
            _writer.writerows(sample_rows)
        _count = read_csv_count(_path.as_posix())
    _ok = _count == len(sample_rows)
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 5: Compare CSV and Parquet Size

    `compare_csv_parquet_sizes(rows)`

    Return dictionary with keys:
    - `csv_bytes`
    - `parquet_bytes` (`-1` if parquet unavailable)
    - `delta_bytes` (`parquet_bytes - csv_bytes`, or `None` if unavailable)
    """)
    return


@app.cell
def _(Path, csv, optional_import, sample_rows, tempfile):
    def compare_csv_parquet_sizes(rows):
        pa = optional_import("pyarrow")
        pq = optional_import("pyarrow.parquet")

        with tempfile.TemporaryDirectory() as _tmp:
            _csv_path = Path(_tmp) / "sample.csv"
            _fieldnames = list(rows[0].keys()) if rows else []
            with _csv_path.open("w", newline="", encoding="utf-8") as _f:
                _writer = csv.DictWriter(_f, fieldnames=_fieldnames)
                _writer.writeheader()
                _writer.writerows(rows)
            _csv_bytes = int(_csv_path.stat().st_size)

            if pa is None or pq is None:
                return {
                    "csv_bytes": _csv_bytes,
                    "parquet_bytes": -1,
                    "delta_bytes": None,
                }

            _parquet_path = Path(_tmp) / "sample.parquet"
            _table = pa.Table.from_pylist(rows)
            pq.write_table(_table, _parquet_path.as_posix())
            _parquet_bytes = int(_parquet_path.stat().st_size)

            _delta = _parquet_bytes - _csv_bytes

            return {
                "csv_bytes": _csv_bytes,
                "parquet_bytes": _parquet_bytes,
                "delta_bytes": _delta,
            }

    _out = compare_csv_parquet_sizes(sample_rows)
    _ok = (
        isinstance(_out, dict)
        and "csv_bytes" in _out
        and "parquet_bytes" in _out
        and "delta_bytes" in _out
        and _out["csv_bytes"] > 0
        and (
            (_out["parquet_bytes"] == -1 and _out["delta_bytes"] is None)
            or (_out["parquet_bytes"] > 0 and _out["delta_bytes"] == _out["parquet_bytes"] - _out["csv_bytes"])
        )
    )
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 6: Simple gzip Compression Report

    `gzip_report(text_payload, level=6)`

    Return dictionary with:
    - `raw_bytes`
    - `compressed_bytes`
    - `ratio`
    """)
    return


@app.cell
def _(sample_text):
    def gzip_report(text_payload, level=6):
        import gzip

        _payload_bytes = str(text_payload).encode("utf-8")
        _raw = len(_payload_bytes)
        _level = min(9, max(1, int(level)))

        _compressed = gzip.compress(_payload_bytes, compresslevel=_level)

        _compressed_bytes = len(_compressed)
        _ratio = (_compressed_bytes / _raw) if _raw else 0.0
        return {
            "raw_bytes": int(_raw),
            "compressed_bytes": int(_compressed_bytes),
            "ratio": float(round(_ratio, 4)),
        }

    _out = gzip_report(sample_text, 6)
    _ok = (
        isinstance(_out, dict)
        and _out["raw_bytes"] > 0
        and _out["compressed_bytes"] > 0
        and 0 < _out["ratio"] < 1
    )
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 7: Create a Simple API

    `create_hello_api()`

    Expected behavior:
    - return `None` if FastAPI missing
    - otherwise create endpoint `GET /hello`
    - endpoint response: `{"message": "hello from api"}`
    """)
    return


@app.cell
def _(optional_import):
    def create_hello_api():
        fastapi_module = optional_import("fastapi")
        if fastapi_module is None:
            return None

        FastAPI = fastapi_module.FastAPI
        _app = FastAPI(title="sw03-hello-api")

        @_app.get("/hello")
        def hello():
            return {"message": "hello from api"}

        return _app

    _api = create_hello_api()
    if _api is None:
        _ok = True
    else:
        _route = next(
            (
                _r
                for _r in _api.routes
                if getattr(_r, "path", "") == "/hello"
                and "GET" in getattr(_r, "methods", set())
            ),
            None,
        )
        _ok = _route is not None and _route.endpoint() == {"message": "hello from api"}

    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 8: Call API from Python

    `call_hello_with_python(base_url, urlopen_fn)`

    Expected behavior:
    - call `/hello`
    - parse JSON
    - return dictionary with keys: `ok`, `url`, `status`, `payload`
    """)
    return


@app.cell
def _(json):
    def call_hello_with_python(base_url, urlopen_fn):
        _url = f"{str(base_url).rstrip('/')}/hello"
        try:
            _response = urlopen_fn(_url, timeout=2)

            _payload = json.loads(_response.read().decode("utf-8"))

            _status = getattr(_response, "status", None) if _response is not None else None
            return {
                "ok": bool(_status == 200 and isinstance(_payload, dict)),
                "url": _url,
                "status": _status,
                "payload": _payload,
            }
        except Exception as _exc:
            return {
                "ok": False,
                "url": _url,
                "status": None,
                "payload": str(_exc),
            }

    class _FakeResponse:
        def __init__(self, _payload_bytes, _status=200):
            self._payload_bytes = _payload_bytes
            self.status = _status

        def read(self):
            return self._payload_bytes

    def _fake_urlopen(_url, timeout=2):
        _body = json.dumps({"message": "hello from api"}).encode("utf-8")
        return _FakeResponse(_body, _status=200)

    _result = call_hello_with_python("http://127.0.0.1:8000", _fake_urlopen)
    _ok = _result == {
        "ok": True,
        "url": "http://127.0.0.1:8000/hello",
        "status": 200,
        "payload": {"message": "hello from api"},
    }
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exercise 9: Row vs Column I/O Estimate

    `estimate_io_bytes(num_rows, total_columns, selected_columns, bytes_per_value=8)`

    Formulas:

    $$
    \text{row\_bytes} = N \times C_{total} \times B
    $$

    $$
    \text{column\_bytes} = N \times C_{selected} \times B
    $$

    """)
    return


@app.cell
def _():
    def estimate_io_bytes(num_rows, total_columns, selected_columns, bytes_per_value=8):
        _n = max(0, int(num_rows))
        _c_total = max(1, int(total_columns))
        _c_sel = min(_c_total, max(0, int(selected_columns)))
        _b = max(1, int(bytes_per_value))

        _row_bytes = _n * _c_total * _b

        _col_bytes = _n * _c_sel * _b

        _ratio = (_col_bytes / _row_bytes) if _row_bytes else 0.0
        return {
            "row_bytes": int(_row_bytes),
            "column_bytes": int(_col_bytes),
            "column_vs_row_ratio": float(round(_ratio, 4)),
        }

    _out = estimate_io_bytes(1_000_000, 20, 4, 8)
    _ok = _out == {
        "row_bytes": 160_000_000,
        "column_bytes": 32_000_000,
        "column_vs_row_ratio": 0.2,
    }
    print("pass" if _ok else "fail")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Browser Call

    After Exercise 7 is complete, create and run this (API) app in a terminal:

    ```python
    # hello_api.py
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/hello")
    def hello():
        return {"message": "hello from api"}
    ```

    Start server:

    ```bash
    uvicorn hello_api:app --reload
    ```

    Open in browser:
    - `http://127.0.0.1:8000/hello`
    - `http://127.0.0.1:8000/docs`
    """)
    return


if __name__ == "__main__":
    app.run()
