print("BACKEND STARTING...", flush=True)
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.query_engine import QueryEngine
from backend.embedding_engine import EmbeddingEngine
from typing import Optional
import requests
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

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
RDF_PATH = os.path.join(os.path.dirname(__file__), "../data/wiki_db_cleaned.ttl")
ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "../ontology/schema.ttl")
EMBEDDING_PATH = os.path.join(os.path.dirname(__file__), "../data/movie_embeddings.csv")

BLAZEGRAPH_URL = os.getenv("BLAZEGRAPH_URL", "http://blazegraph:8080/bigdata/namespace/kb/sparql")
engine = QueryEngine(BLAZEGRAPH_URL)

# Initialize Embedding Engine (Lazy or try-except to avoid crash if not trained)
embedding_engine = None
if os.path.exists(EMBEDDING_PATH):
    try:
        logging.info(f"Loading embeddings from {EMBEDDING_PATH}...")
        embedding_engine = EmbeddingEngine(EMBEDDING_PATH)
        logging.info("Embeddings loaded!")
    except Exception as e:
        logging.error(f"Failed to load embeddings: {e}")
else:
    logging.warning(f"Embedding file not found at {EMBEDDING_PATH}. Similarity search will be disabled.")


# Startup logic to wait for Blazegraph and load data
def wait_for_blazegraph():
    retries = 30
    while retries > 0:
        try:
            if engine.is_connected():
                logging.info("Blazegraph is ready and reachable.")
                return True
            else:
                # Connected but ASK failed or returned false (empty might be false implementation dependent)
                # actually is_connected catches exception. If it returns False, it might be just "connected but query failed" or "empty".
                # Let's assume exception = down.
                pass
        except Exception:
            pass
        
        logging.info(f"Waiting for Blazegraph... ({retries} retries left)")
        time.sleep(2)
        retries -= 1
    return False

# We need to distinguish between "Down" and "Empty".
# The query_engine.is_connected returns False on Exception. 
# We should probably check if we can query it.
# Let's just try to loop until we can at least reach it.

running_in_docker = os.getenv("BACKEND_URL") or os.path.exists("/.dockerenv")

if running_in_docker:
    logging.info("Checking Blazegraph status...")
    # 1. Wait for service to be up
    connected = False
    for i in range(30):
        try:
            requests.get("http://blazegraph:8080/bigdata")
            connected = True
            break
        except:
            time.sleep(2)
            logging.info("Waiting for Blazegraph container...")
    
    if connected:
        # 2. Check if data exists
        if not engine.has_movies():
            logging.info("Blazegraph is empty. Loading data...")
            try:
                engine.upload_ttl(RDF_PATH)
                logging.info("Data loaded successfully!")
            except Exception as e:
                logging.error(f"Failed to load data: {e}")
        
        # 3. Always try to load Ontology (it's small and idempotent usually, or we check if Exists)
        # For simplicity, we just upload it. If it fails (duplicates), it might be fine depending on Blazegraph config,
        # but Blazegraph doesn't error on duplicate triples, just ignores them.
        try:
             logging.info("Uploading Ontology...")
             engine.upload_ttl(ONTOLOGY_PATH)
             logging.info("Ontology uploaded!")
        except Exception as e:
             logging.error(f"Failed to load ontology: {e}")
        
        else:
            logging.info("Blazegraph already has data.")

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

@app.get("/similar")
def get_similar_movies(uri: str):
    if not embedding_engine:
        return []
    
    # 1. Get similar URIs
    # returns list of (uri, score)
    similar_pairs = embedding_engine.get_similar_movies(uri, top_n=5)
    
    if not similar_pairs:
        return []
        
    top_uris = [p[0] for p in similar_pairs]
    
    # 2. Fetch details for these URIs
    movies = engine.get_movies_by_uris(top_uris)
    
    return movies
