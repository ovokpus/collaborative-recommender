import sys
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
from app import main, recommender  # noqa: E402

ROWS = [  # user, name, movie, rating, ts
    (0, "Ann", 1, 5, 1), (0, "Ann", 2, 4, 1),
    (1, "Ben", 1, 5, 1), (1, "Ben", 2, 4, 1), (1, "Ben", 3, 5, 1),
    (2, "Cat", 4, 5, 1), (2, "Cat", 1, 1, 1),
]
TITLES = pd.DataFrame({"item_id": [1, 2, 3, 4], "title": ["A", "B", "C", "D"]})


def make():
    df = pd.DataFrame(ROWS, columns=["User_ID", "User_Names", "Movie_ID", "Rating", "Timestamp"])
    return recommender.Recommender(df, TITLES)


def test_recommends_unseen_from_similar_user():
    recs = make().recommend("Ann", k=1, top_n=2)
    assert recs[0]["title"] == "C"
    assert all(r["title"] not in {"A", "B"} for r in recs)


def test_rating_distribution():
    d = make().rating_distribution(1)
    assert d["counts"] == {"1": 1, "2": 0, "3": 0, "4": 0, "5": 2}


def test_api(monkeypatch):
    r = make()
    monkeypatch.setattr(recommender, "get", lambda: r)
    c = TestClient(main.app)
    assert c.get("/users").json()["users"] == ["Ann", "Ben", "Cat"]
    assert c.get("/recommendations/Ann?k=1").status_code == 200
    assert c.get("/recommendations/Nobody").status_code == 404
    assert c.get("/movies/99/ratings").status_code == 404


def test_real_dataset_loads():
    r = recommender.load(str(Path(__file__).resolve().parents[1] / "data"))
    assert len(r.users) > 900 and len(r.recommend(r.users[0])) == 10
