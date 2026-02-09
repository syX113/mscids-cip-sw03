"""Standalone FastAPI app used by the lecture notebook demo.

Run locally with:
    uvicorn src.demo_api:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Lecture API")


class Item(BaseModel):
    id: int
    name: str
    price: float


items: dict[int, Item] = {}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return items.get(item_id, {"error": "not found"})


@app.post("/items")
def create_item(item: Item):
    items[item.id] = item
    return item
