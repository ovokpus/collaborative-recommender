from fastapi import FastAPI, HTTPException, Query

from . import recommender

app = FastAPI(title="Collaborative Recommender API", version="1.0.0",
              description="User-based collaborative filtering over 100k MovieLens-style ratings.")


@app.on_event("startup")
def warm():
    recommender.get()


@app.get("/health")
def health():
    r = recommender.get()
    return {"status": "ok", "users": len(r.users), "movies": int(r.titles.Movie_ID.nunique())}


@app.get("/users")
def users():
    return {"users": recommender.get().users}


@app.get("/users/{user_name}/history")
def history(user_name: str, limit: int = Query(10, ge=1, le=50)):
    try:
        return {"user": user_name, "top_rated": recommender.get().user_history(user_name, limit)}
    except KeyError:
        raise HTTPException(404, f"unknown user {user_name!r}")


@app.get("/recommendations/{user_name}")
def recommend(user_name: str, k: int = Query(10, ge=1, le=100), top_n: int = Query(10, ge=1, le=50)):
    try:
        return {"user": user_name, "k": k, "recommendations": recommender.get().recommend(user_name, k, top_n)}
    except KeyError:
        raise HTTPException(404, f"unknown user {user_name!r}")


@app.get("/movies/{movie_id}/ratings")
def ratings(movie_id: int):
    d = recommender.get().rating_distribution(movie_id)
    if d["title"] is None:
        raise HTTPException(404, "movie not found or unrated")
    return d
