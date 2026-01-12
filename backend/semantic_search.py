import os
import logging
import chromadb
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    def __init__(self, persistence_directory="../data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persistence_directory)
        self.collection = self.client.get_or_create_collection(name="movie_embeddings")
        # Load model lazily or here? Here is fine for a service.
        logging.info("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        logging.info("Embedding model loaded.")

    def count(self):
        return self.collection.count()

    def index_movies(self, movies):
        """
        movies: list of dict {'uri': str, 'text': str}
        """
        if not movies:
            return
        
        batch_size = 500
        total = len(movies)
        logging.info(f"Indexing {total} movies in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            batch = movies[i:i+batch_size]
            ids = [m['uri'] for m in batch]
            documents = [m['text'] for m in batch]
            
            # encode
            embeddings = self.model.encode(documents).tolist()
            
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings
            )
            logging.info(f"Indexed {i + len(batch)}/{total}")
            
    def search(self, query_text, n_results=5):
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            if results and results['ids']:
                return [
                    {"id": id, "score": dist, "text": doc} 
                    for id, dist, doc in zip(results['ids'][0], results['distances'][0], results['documents'][0])
                ]
            return []
        except Exception as e:
            logging.error(f"Semantic search error: {e}")
            return []
