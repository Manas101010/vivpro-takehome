import pytest
from fastapi.testclient import TestClient

from app import catalog, main


@pytest.fixture
def client():
    with TestClient(main.app) as client:
        yield client


@pytest.fixture
def synthetic_catalog(monkeypatch):
    monkeypatch.setattr(main, "songs", [
        {"id": "e", "title": " beta  version ", "tempo": None},
        {"id": "c", "title": "BETA VERSION", "tempo": 10},
        {"id": "a", "title": "alpha", "tempo": 2},
        {"id": "d", "title": None, "tempo": None},
        {"id": "b", "title": "zeta", "tempo": 10},
    ])


def test_default_page(client):
    response = client.get("/songs")
    assert response.status_code == 200
    assert response.json() == {
        "items": sorted(main.songs, key=lambda song: song["id"])[:10],
        "total": 25,
        "page": 1,
        "size": 10,
        "total_pages": 3,
    }


@pytest.mark.parametrize(("page", "start", "stop"), [
    (1, 0, 10), (2, 10, 20), (3, 20, 25), (4, 25, 25),
])
def test_page_boundaries(client, page, start, stop):
    response = client.get("/songs", params={"page": page})
    assert response.status_code == 200
    assert response.json() == {
        "items": sorted(main.songs, key=lambda song: song["id"])[start:stop],
        "total": 25,
        "page": page,
        "size": 10,
        "total_pages": 3,
    }


def test_maximum_page_size(client):
    response = client.get("/songs", params={"size": 100})
    assert response.status_code == 200
    assert len(response.json()["items"]) == response.json()["total"] == 25
    assert response.json()["total_pages"] == 1


@pytest.mark.parametrize("params", [
    {"page": 0}, {"page": "-1"}, {"page": "1.5"}, {"page": "abc"},
    {"size": 0}, {"size": 101}, {"size": "1.5"}, {"size": "abc"},
    {"sort_by": "artist"}, {"sort_by": "ID"}, {"order": "DESC"}, {"order": "sideways"},
])
def test_invalid_list_parameters(client, params):
    assert client.get("/songs", params=params).status_code == 422


def test_global_sort_happens_before_pagination(client, synthetic_catalog):
    response = client.get("/songs", params={
        "page": 2, "size": 1, "sort_by": "tempo", "order": "desc",
    })
    assert response.status_code == 200
    assert response.json() == {
        "items": [{"id": "c", "title": "BETA VERSION", "tempo": 10}],
        "total": 5,
        "page": 2,
        "size": 1,
        "total_pages": 5,
    }


@pytest.mark.parametrize(("field", "order", "expected"), [
    ("tempo", "asc", ["a", "b", "c", "d", "e"]),
    ("tempo", "desc", ["b", "c", "a", "d", "e"]),
    ("title", "asc", ["a", "c", "e", "b", "d"]),
    ("title", "desc", ["b", "c", "e", "a", "d"]),
    ("id", "desc", ["e", "d", "c", "b", "a"]),
])
def test_sort_order_nulls_and_ties(client, synthetic_catalog, field, order, expected):
    response = client.get("/songs", params={"sort_by": field, "order": order})
    assert response.status_code == 200
    assert [song["id"] for song in response.json()["items"]] == expected


@pytest.mark.parametrize("field", [
    "id", "title", "danceability", "energy", "mood", "acousticness", "tempo",
    "duration_ms", "num_sections", "num_segments", "valence",
])
def test_every_catalog_field_is_sortable(client, field):
    response = client.get("/songs", params={"sort_by": field, "size": 100})
    assert response.status_code == 200
    values = [song[field] for song in response.json()["items"]]
    if field == "title":
        values = [value.casefold() for value in values]
    present = sorted(value for value in values if value is not None)
    assert len(values) == 25
    assert values == present + [None] * (len(values) - len(present))


def test_duplicate_title_search_returns_complete_records(client):
    response = client.get("/songs/search", params={"title": "  pErFeCT\t"})
    assert response.status_code == 200
    by_id = {song["id"]: song for song in main.songs}
    assert response.json() == {
        "items": [by_id["0tgVpDi06FyKpA1z0VMD4v"], by_id["7dNsHhGeGU5MV01r06O8gK"]],
        "total": 2,
    }


@pytest.mark.parametrize(("query", "display_title"), [
    ("  NAI\u0308VE  ", "Naïve"),
    ("CAFE\u0301\t del\n  MAR", "Café del Mar"),
    (" never  GONNA\t give you UP ", "Never Gonna Give You Up"),
])
def test_title_normalization_preserves_display(client, query, display_title):
    response = client.get("/songs/search", params={"title": query})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == display_title


def test_normalizes_stored_title_whitespace(client, synthetic_catalog):
    response = client.get("/songs/search", params={"title": "beta version"})
    assert response.status_code == 200
    assert response.json() == {"items": [main.songs[1], main.songs[0]], "total": 2}


@pytest.mark.parametrize("query", ["Unknown", "Never Gonna", "Naive"])
def test_search_no_match(client, query):
    response = client.get("/songs/search", params={"title": query})
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


@pytest.mark.parametrize("params", [{}, {"title": ""}, {"title": " \t\u2003\n"}])
def test_invalid_search_title(client, params):
    assert client.get("/songs/search", params=params).status_code == 422


def test_empty_catalog(client, monkeypatch):
    monkeypatch.setattr(main, "songs", [])
    listing = client.get("/songs")
    search = client.get("/songs/search", params={"title": "Perfect"})
    assert listing.status_code == search.status_code == 200
    assert listing.json() == {"items": [], "total": 0, "page": 1, "size": 10, "total_pages": 0}
    assert search.json() == {"items": [], "total": 0}


def test_load_catalog_from_another_working_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert catalog.load_catalog() == main.songs
