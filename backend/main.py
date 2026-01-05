from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.query_engine import QueryEngine
import os
from typing import Optional

app = FastAPI(title="Movie Explorer API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Query Engine
# Adjust path if running from root or backend folder. Assuming running from root.
RDF_PATH = os.path.join(os.path.dirname(__file__), "../data/wiki_db_cleaned.ttl")
engine = QueryEngine(RDF_PATH)

@app.get("/")
def read_root():
    return {"message": "Movie Explorer API is running"}

@app.get("/options")
def get_filter_options():
    return engine.get_options()

@app.get("/search")
def search_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    actor: Optional[str] = None,
    director: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    print(f"DEBUG: Received search request - Title: {title}, Genre: {genre}", flush=True)
    limit: int = 50
):
    return engine.search_movies(
        title=title,
        genre=genre,
        actor=actor,
        director=director,
        year_start=year_start,
        year_end=year_end,
        limit=limit
    )
