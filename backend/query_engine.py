import logging
import sys
import time
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import requests

class QueryEngine:
    def __init__(self, blazegraph_url: str = "http://blazegraph:9999/bigdata/namespace/kb/sparql"):
        self.endpoint = blazegraph_url

    def _get_sparql(self):
        """Creates a new SPARQLWrapper instance."""
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setReturnFormat(JSON)
        return sparql

    def is_connected(self):
        """Checks if Blazegraph is reachable."""
        try:
            sparql = self._get_sparql()
            sparql.setQuery("ASK { ?s ?p ?o }")
            sparql.query()
            return True
        except Exception:
            return False

    def has_movies(self):
        """Checks if movie data is loaded."""
        try:
            sparql = self._get_sparql()
            sparql.setQuery("PREFIX ex: <http://example.org/movie/> ASK { ?s ex:title ?o }")
            ret = sparql.query().convert()
            # SPARQLWrapper JSON result for ASK is boolean
            return ret["boolean"]
        except Exception:
            return False

    def upload_ttl(self, file_path: str):
        """Uploads a TTL file to Blazegraph via HTTP POST."""
        url = self.endpoint 
        
        logging.info(f"Starting upload of {file_path} to {self.endpoint}...")
        
        with open(file_path, "rb") as f:
            data = f.read()
            
        headers = {
            "Content-Type": "application/x-turtle",
        }
        
        response = requests.post(self.endpoint, data=data, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Failed to upload data: {response.text}")
            raise Exception(f"Blazegraph upload failed: {response.status_code}")
            
        logging.info(f"Successfully uploaded {len(data)} bytes.")

    def get_options(self):
        """Returns unique genres, actors, directors for dropdowns."""
        # Query Genres
        logging.info("Fetching options...")
        q_genre = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?g WHERE {
            ?m ex:genre ?g .
        } ORDER BY ?g
        """
        genres_uris = self._execute_query_list(q_genre, "g")
        genres = [uri.split("/")[-1] for uri in genres_uris]
        genres = sorted(list(set(genres))) # Ensure unique and sorted
        logging.info(f"Fetched {len(genres)} genres")

        # Query Actors (limit to top 200 most frequent)
        logging.info("Fetching actors...")
        q_actor = """
        PREFIX ex: <http://example.org/movie/>
        SELECT ?a (COUNT(?m) as ?count) WHERE {
            ?m ex:actor ?a .
        } GROUP BY ?a ORDER BY DESC(?count) LIMIT 5000
        """
        actors_uris = self._execute_query_list(q_actor, "a")
        actors = [uri.split("/")[-1] for uri in actors_uris]
        logging.info(f"Fetched {len(actors)} actors")

        # Query Directors
        logging.info("Fetching directors...")
        q_director = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?d WHERE {
            ?m ex:director ?d .
        } ORDER BY ?d
        """
        directors_uris = self._execute_query_list(q_director, "d")
        directors = [uri.split("/")[-1] for uri in directors_uris]
        directors = sorted(list(set(directors)))
        logging.info(f"Fetched {len(directors)} directors")

        return {"genres": genres, "actors": actors, "directors": directors}

    def _execute_query_list(self, query, var_name):
        try:
            sparql = self._get_sparql()
            sparql.setQuery(query)
            results = sparql.query().convert()
            return [r[var_name]["value"] for r in results["results"]["bindings"]]
        except Exception as e:
            logging.error(f"SPARQL Error: {e}")
            return []

    def search_movies(self, title=None, genre=None, year_start=None, year_end=None, actor=None, director=None, limit=50):
        """Dynamic SPARQL query builder."""
        
        query_body = """
        PREFIX ex: <http://example.org/movie/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT DISTINCT ?movie ?title ?year ?runtime
        WHERE {
            ?movie ex:title ?title .
            OPTIONAL { ?movie ex:year ?year }
            OPTIONAL { ?movie ex:runtime ?runtime }
        """

        # Filters
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
            logging.info(f"Query Step 1: {query_body}")
            sparql = self._get_sparql()
            sparql.setQuery(query_body)
            results = sparql.query().convert()
            
            for row in results["results"]["bindings"]:
                m_uri = row["movie"]["value"]
                movies_map[m_uri] = {
                    "id": m_uri,
                    "title": row["title"]["value"],
                    "year": row["year"]["value"] if "year" in row else None,
                    "runtime": row["runtime"]["value"] if "runtime" in row else None,
                    "genres": [],
                    "directors": [],
                    "actors": [],
                }
        except Exception as e:
            logging.error(f"SPARQL Error in Step 1: {e}")
            return []

        if not movies_map:
            return []

        # Step 2: Fetch Details
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
                sparql = self._get_sparql()
                sparql.setQuery(q_attr)
                res = sparql.query().convert()
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
        
        logging.info(f"Search returned {len(results)} results")
        return results

    def get_movies_by_uris(self, movie_uris):
        """Fetches details for a specific list of movie URIs."""
        if not movie_uris:
            return []
            
        uris_str = " ".join([f"<{uri}>" for uri in movie_uris])
        
        # Query basic info
        q_basic = f"""
        PREFIX ex: <http://example.org/movie/>
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
            sparql = self._get_sparql()
            sparql.setQuery(q_basic)
            results = sparql.query().convert()
            
            for row in results["results"]["bindings"]:
                m_uri = row["movie"]["value"]
                movies_map[m_uri] = {
                    "id": m_uri,
                    "title": row["title"]["value"],
                    "year": row["year"]["value"] if "year" in row else None,
                    "runtime": row["runtime"]["value"] if "runtime" in row else None,
                    "genres": [],
                    "directors": [],
                    "actors": [],
                }
        except Exception as e:
            logging.exception(f"Error fetching movie basics: {e}")
            return []

        # Re-use the batch fetch logic for details
        # (This is a simplified version of what is in search_movies - could be DRYed further)
        details_uris_str = " ".join([f"<{uri}>" for uri in movies_map.keys()])
        
        def fetch_attribute(attr_name, target_list):
            q_attr = f"""
            PREFIX ex: <http://example.org/movie/>
            SELECT ?movie ?val WHERE {{
                VALUES ?movie {{ {details_uris_str} }}
                ?movie ex:{attr_name} ?val .
            }}
            """
            try:
                sparql = self._get_sparql()
                sparql.setQuery(q_attr)
                res = sparql.query().convert()
                for row in res["results"]["bindings"]:
                    m_uri = row["movie"]["value"]
                    if m_uri in movies_map:
                        val = row["val"]["value"].split('/')[-1]
                        movies_map[m_uri][target_list].append(val)
            except Exception as e:
                 logging.error(f"Error fetching {attr_name}: {e}")

        fetch_attribute("genre", "genres")
        fetch_attribute("director", "directors")
        fetch_attribute("actor", "actors")
        
        # Return in the order of the input URIs to maintain similarity ranking
        ordered_results = []
        for uri in movie_uris:
            if uri in movies_map:
                ordered_results.append(movies_map[uri])
                
        return ordered_results
