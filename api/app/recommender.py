"""User-based collaborative filtering, extracted from CollaborativeFiltering.ipynb."""
import os
from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "data"))


class Recommender:
    def __init__(self, ratings: pd.DataFrame, titles: pd.DataFrame):
        self.titles = titles.rename(columns={"item_id": "Movie_ID", "title": "Movie_Title"})
        self.ratings = ratings.merge(self.titles, on="Movie_ID")
        users = self.ratings[["User_ID", "User_Names"]].drop_duplicates("User_ID")
        self.name_to_id = dict(zip(users.User_Names, users.User_ID))
        n_users = int(self.ratings.User_ID.max()) + 1
        n_movies = int(self.titles.Movie_ID.max())
        m = np.zeros((n_users, n_movies))
        m[self.ratings.User_ID.values, self.ratings.Movie_ID.values - 1] = self.ratings.Rating.values
        self.matrix = pd.DataFrame(m, columns=np.arange(1, n_movies + 1))
        self.similarity = cosine_similarity(m)

    @property
    def users(self) -> list[str]:
        return sorted(self.name_to_id)

    def recommend(self, user_name: str, k: int = 10, top_n: int = 10) -> list[dict]:
        if user_name not in self.name_to_id:
            raise KeyError(user_name)
        uid = self.name_to_id[user_name]
        sims = self.similarity[uid].copy()
        sims[uid] = -1  # exclude the user themselves
        k = min(k, len(sims) - 1)
        neighbours = self.matrix.index[np.argpartition(sims, -k)[-k:]]
        scores = self.matrix.loc[neighbours].mean(0).sort_values(ascending=False)
        seen = self.matrix.loc[uid].gt(0)
        scores = scores.drop(seen.index[seen]).head(top_n)
        t = self.titles.set_index("Movie_ID").Movie_Title
        return [
            {"movie_id": int(mid), "title": t.get(mid, str(mid)), "score": round(float(s), 3)}
            for mid, s in scores.items()
        ]

    def rating_distribution(self, movie_id: int) -> dict:
        r = self.ratings[self.ratings.Movie_ID == movie_id]
        counts = r.Rating.value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        return {
            "movie_id": movie_id,
            "title": r.Movie_Title.iloc[0] if len(r) else None,
            "counts": {str(k): int(v) for k, v in counts.items()},
            "mean": round(float(r.Rating.mean()), 2) if len(r) else None,
        }

    def user_history(self, user_name: str, limit: int = 10) -> list[dict]:
        uid = self.name_to_id[user_name]
        r = self.ratings[self.ratings.User_ID == uid].sort_values(["Rating", "Timestamp"], ascending=False)
        return [{"movie_id": int(a), "title": b, "rating": int(c)}
                for a, b, c in r[["Movie_ID", "Movie_Title", "Rating"]].head(limit).itertuples(index=False)]


def load(data_dir: str = DATA_DIR) -> Recommender:
    ratings = pd.read_csv(os.path.join(data_dir, "Movie_data.csv"),
                          names=["User_ID", "User_Names", "Movie_ID", "Rating", "Timestamp"])
    titles = pd.read_csv(os.path.join(data_dir, "Movie_Id_Titles.csv"))
    return Recommender(ratings, titles)


@lru_cache(maxsize=1)
def get() -> Recommender:
    return load()
