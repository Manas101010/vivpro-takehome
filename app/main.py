"""FastAPI entry point for the read-only songs catalog."""

from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query

from app.catalog import SortField, load_catalog, paginate, search, title_key


app = FastAPI(title="Vivpro Songs")
songs = load_catalog()


@app.get("/songs")
def list_songs(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    sort_by: SortField = SortField.ID,
    order: Literal["asc", "desc"] = "asc",
):
    return paginate(songs, page, size, sort_by, descending=order == "desc")


@app.get("/songs/search")
def search_songs(title: str):
    query_key = title_key(title)
    if not query_key:
        raise HTTPException(status_code=422, detail="Title must contain non-whitespace text.")
    matches = search(songs, query_key)
    return {"items": matches, "total": len(matches)}
