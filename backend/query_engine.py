import logging
from SPARQLWrapper import SPARQLWrapper, JSON

class QueryEngine:
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)
        logging.info(f"Initialized QueryEngine with endpoint: {endpoint_url}")

    def _query(self, query: str):
        """Executes a SPARQL query and returns JSON results."""
        self.sparql.setQuery(query)
        # Simple retry logic for transient connection errors
        import time
        for i in range(5):
            try:
                return self.sparql.query().convert()
            except Exception as e:
                # If connection refused or empty response, retry
                logging.warning(f"SPARQL Query attempt {i+1} failed: {e}")
                time.sleep(1)
        
        logging.error(f"SPARQL Query failed after retries.")
        return None

    def get_options(self):
        """Returns unique genres, actors, directors for dropdowns."""
        # Query Genres
        q_genre = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?label WHERE {
            ?m ex:genre ?g .
            BIND(REPLACE(STR(?g), "^.*\\\\/", "") AS ?label)
        } ORDER BY ?label
        """
        genres = []
        res = self._query(q_genre)
        if res:
             genres = [row["label"]["value"] for row in res["results"]["bindings"]]

        # Query Actors
        q_actor = """
        PREFIX ex: <http://example.org/movie/>
        SELECT ?label (COUNT(?m) as ?count) WHERE {
            ?m ex:actor ?a .
            BIND(REPLACE(STR(?a), "^.*\\\\/", "") AS ?label)
        } GROUP BY ?label ORDER BY DESC(?count) LIMIT 200
        """
        actors = []
        res = self._query(q_actor)
        if res:
            actors = [row["label"]["value"] for row in res["results"]["bindings"]]

        # Query Directors
        q_director = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?label WHERE {
            ?m ex:director ?d .
            BIND(REPLACE(STR(?d), "^.*\\\\/", "") AS ?label)
        } ORDER BY ?label
        """
        directors = []
        res = self._query(q_director)
        if res:
            directors = [row["label"]["value"] for row in res["results"]["bindings"]]

        return {"genres": genres, "actors": actors, "directors": directors}

    def search_movies(self, title=None, genre=None, year_start=None, year_end=None, actor=None, director=None, limit=50):
        """Dynamic SPARQL query builder with optimized two-step execution."""
        
        # Step 1: Find matching movies (ID, title, year, runtime)
        query_body = """
        PREFIX ex: <http://example.org/movie/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?movie ?title ?year ?runtime
        WHERE {
            ?movie ex:title ?title .
            OPTIONAL { ?movie ex:year ?year }
            OPTIONAL { ?movie ex:runtime ?runtime }
        """

        if title:
            query_body += f'\nFILTER(REGEX(?title, "{title}", "i"))'
        
        if genre:
            query_body += f'\n?movie ex:genre ?targetGenre . FILTER(STRENDS(STR(?targetGenre), "/{genre}"))'

        if actor:
             query_body += f'\n?movie ex:actor ?targetActor . FILTER(STRENDS(STR(?targetActor), "/{actor}"))'

        if director:
             query_body += f'\n?movie ex:director ?targetDirector . FILTER(STRENDS(STR(?targetDirector), "/{director}"))'

        if year_start:
             query_body += f'\nFILTER(?year >= "{year_start}"^^xsd:gYear)'
        
        if year_end:
             query_body += f'\nFILTER(?year <= "{year_end}"^^xsd:gYear)'

        query_body += """
        }
        ORDER BY DESC(?year)
        """
        query_body += f"LIMIT {limit}"

        movies_map = {}
        
        try:
            # logging.info(f"Query Step 1: {query_body}")
            res = self._query(query_body)
            if not res:
                return []
                
            for row in res["results"]["bindings"]:
                m_uri = row["movie"]["value"]
                movies_map[m_uri] = {
                    "id": m_uri,
                    "title": row["title"]["value"],
                    "year": row["year"]["value"] if "year" in row else None,
                    "runtime": row["runtime"]["value"] if "runtime" in row else None,
                    "genres": [],
                    "directors": [],
                    "actors": [],
                    "similarity": 0
                }
        except Exception as e:
            logging.error(f"SPARQL Error in Step 1: {e}")
            return []

        if not movies_map:
            return []

        # Step 2: Fetch Details for found movies
        movie_uris = list(movies_map.keys())
        uris_str = " ".join([f"<{uri}>" for uri in movie_uris])

        def fetch_attribute(attr_name, target_list):
            q_attr = f"""
            PREFIX ex: <http://example.org/movie/>
            SELECT ?movie ?val WHERE {{
                VALUES ?movie {{ {uris_str} }}
                ?movie ex:{attr_name} ?val .
            }}
            """
            try:
                res = self._query(q_attr)
                if res:
                    for row in res["results"]["bindings"]:
                        m_uri = row["movie"]["value"]
                        if m_uri in movies_map:
                            val = row["val"]["value"].split('/')[-1]
                            movies_map[m_uri][target_list].append(val)
            except Exception as e:
                logging.error(f"SPARQL Error fetching {attr_name}: {e}")

        fetch_attribute("genre", "genres")
        fetch_attribute("director", "directors")
        fetch_attribute("actor", "actors")

        results = list(movies_map.values())
        for m in results:
             m["genres"].sort()
             m["directors"].sort()
             m["actors"].sort()
        
        return results

    def get_movie_details(self, uris):
        """Fetches full movie details for a list of URIs."""
        if not uris:
            return []
            
        uris_str = " ".join([f"<{uri}>" for uri in uris])
        
        # Step 1: Basic Info
        query_body = f"""
        PREFIX ex: <http://example.org/movie/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?movie ?title ?year ?runtime
        WHERE {{
            VALUES ?movie {{ {uris_str} }}
            ?movie ex:title ?title .
            OPTIONAL {{ ?movie ex:year ?year }}
            OPTIONAL {{ ?movie ex:runtime ?runtime }}
        }}
        """
        
        movies_map = {}
        try:
            res = self._query(query_body)
            if res:
                for row in res["results"]["bindings"]:
                    m_uri = row["movie"]["value"]
                    movies_map[m_uri] = {
                        "id": m_uri,
                        "title": row["title"]["value"],
                        "year": row["year"]["value"] if "year" in row else None,
                        "runtime": row["runtime"]["value"] if "runtime" in row else None,
                        "genres": [],
                        "directors": [],
                        "actors": [],
                        "similarity": 0
                    }
        except Exception as e:
            logging.error(f"Error fetching basic info: {e}")
            return []

        # Step 2: enrich
        # Reuse logic? For now duplicate for speed.
        def fetch_attribute(attr_name, target_list):
            q_attr = f"""
            PREFIX ex: <http://example.org/movie/>
            SELECT ?movie ?val WHERE {{
                VALUES ?movie {{ {uris_str} }}
                ?movie ex:{attr_name} ?val .
            }}
            """
            try:
                res = self._query(q_attr)
                if res:
                    for row in res["results"]["bindings"]:
                        m_uri = row["movie"]["value"]
                        if m_uri in movies_map:
                            val = row["val"]["value"].split('/')[-1]
                            movies_map[m_uri][target_list].append(val)
            except Exception as e:
                logging.error(f"SPARQL Error fetching {attr_name}: {e}")

        fetch_attribute("genre", "genres")
        fetch_attribute("director", "directors")
        fetch_attribute("actor", "actors")

        results = list(movies_map.values())
        for m in results:
             m["genres"].sort()
             m["directors"].sort()
             m["actors"].sort()
             
        return results

    def get_all_movies(self):
        """Fetches all movies with titles and genres for indexing."""
        query = """
        PREFIX ex: <http://example.org/movie/>
        SELECT ?movie ?title (GROUP_CONCAT(?genreText; separator=", ") AS ?genres) WHERE {
            ?movie ex:title ?title .
            OPTIONAL { 
                ?movie ex:genre ?g . 
                BIND(REPLACE(STR(?g), "^.*\\\\/", "") AS ?genreText)
            }
        } GROUP BY ?movie ?title
        """
        movies = []
        seen_uris = set()
        try:
            res = self._query(query)
            if res:
                for row in res["results"]["bindings"]:
                    uri = row["movie"]["value"]
                    if uri in seen_uris:
                        continue
                    seen_uris.add(uri)
                    
                    title = row["title"]["value"]
                    genres = row["genres"]["value"] if "genres" in row else ""
                    # Combine Title and Genres for richer embedding context
                    # e.g. "Dune - Science Fiction, Adventure"
                    combined_text = f"{title}"
                    if genres:
                        combined_text += f" - Genres: {genres}"
                        
                    movies.append({
                        "uri": uri,
                        "text": combined_text
                    })
        except Exception as e:
            logging.error(f"Error fetching all movies: {e}")
        return movies
