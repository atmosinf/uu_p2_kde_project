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
BLAZEGRAPH_URL = os.getenv("BLAZEGRAPH_URL", "http://blazegraph:9999/blazegraph/sparql")
engine = QueryEngine(BLAZEGRAPH_URL)

try:
    from backend.semantic_search import SemanticSearch
    semantic_search = SemanticSearch()
except Exception as e:
    print(f"WARNING: Semantic Search failed to initialize: {e}")
    semantic_search = None

@app.on_event("startup")
def startup_event():
    from backend.loader import init_db
    
    # Paths to data files
    base_dir = os.path.dirname(__file__)
    data_files = [
        os.path.join(base_dir, "../data/wiki_db_cleaned.ttl"),
        os.path.join(base_dir, "../ontology/ontology.ttl")
    ]
    
    print("DEBUG: Initializing Database...", flush=True)
    try:
        init_db(data_files)
    except Exception as e:
        print(f"WARNING: Database initialization failed: {e}", flush=True)

    # Initialize Embeddings
    if semantic_search:
        print("DEBUG: Checking Embeddings Index...", flush=True)
        try:
            if semantic_search.count() == 0:
                print("DEBUG: Index empty. Fetching movies from Blazegraph...", flush=True)
                movies = engine.get_all_movies()
                if movies:
                     semantic_search.index_movies(movies)
                else:
                     print("WARNING: No movies found in Blazegraph to index.", flush=True)
            else:
                print(f"DEBUG: Embeddings index has {semantic_search.count()} items.", flush=True)
        except Exception as e:
            print(f"WARNING: Embedding indexing failed: {e}", flush=True)

@app.get("/")
def read_root():
    return {"message": "Movie Explorer API is running with Blazegraph & Semantic Search"}

@app.get("/options")
def get_filter_options():
    return engine.get_options()

@app.get("/search/semantic")
def search_semantic(query: str, limit: int = 10):
    if not semantic_search:
        return []
        
    print(f"DEBUG: Semantic search for '{query}'", flush=True)
    results = semantic_search.search(query, n_results=limit)
    
    if not results:
        return []

    # Get URIs
    uris = [r['id'] for r in results]
    
    # Enrich with details
    return engine.get_movie_details(uris)

@app.get("/search")
def search_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    actor: Optional[str] = None,
    director: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    limit: int = 50
):
    print(f"DEBUG: Received search request - Title: {title}, Genre: {genre}", flush=True)
    return engine.search_movies(
        title=title,
        genre=genre,
        actor=actor,
        director=director,
        year_start=year_start,
        year_end=year_end,
        limit=limit
    )
