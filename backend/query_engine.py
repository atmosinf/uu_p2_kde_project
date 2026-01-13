import logging
import sys
import time
from SPARQLWrapper import SPARQLWrapper, JSON, POST, DIGEST
import requests

class QueryEngine:
    def __init__(self, blazegraph_url: str = "http://blazegraph:9999/bigdata/namespace/kb/sparql"):
        self.endpoint = blazegraph_url
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)

    def is_connected(self):
        """Checks if Blazegraph is reachable."""
        try:
            # Simple query to check connection
            self.sparql.setQuery("ASK { ?s ?p ?o }")
            self.sparql.query()
            return True
        except Exception:
            return False

    def has_movies(self):
        """Checks if movie data is loaded."""
        try:
            self.sparql.setQuery("PREFIX ex: <http://example.org/movie/> ASK { ?s ex:title ?o }")
            ret = self.sparql.query().convert()
            # SPARQLWrapper JSON result for ASK is boolean
            return ret["boolean"]
        except Exception:
            return False

    def upload_ttl(self, file_path: str):
        """Uploads a TTL file to Blazegraph via HTTP POST."""
        url = self.endpoint # The SPARQL endpoint can often accept data via POST with correct headers, but the standard REST API is better.
        # Blazegraph REST API for data loading: /blazegraph/dataloader or just POST to the endpoint with Content-Type.
        # Efficient way for Blazegraph: POST to /blazegraph/sparql with UPDATE or using the proper DataLoader.
        # Actually, simpler way: POST body to the endpoint with correct content-type for insertion.
        
        # Let's use the REST API approach for 'File Upload' style or just a raw post.
        # Docs: https://github.com/blazegraph/database/wiki/REST_API#insert
        
        logging.info(f"Starting upload of {file_path} to {self.endpoint}...")
        
        with open(file_path, "rb") as f:
            data = f.read()
            
        headers = {
            "Content-Type": "application/x-turtle",
        }
        
        # Blazegraph endpoint usually allows POSTing data directly to .../sparql for some setups, 
        # but the standard way is often just POST /blazegraph/namespace/kb/sparql
        response = requests.post(self.endpoint, data=data, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Failed to upload data: {response.text}")
            raise Exception(f"Blazegraph upload failed: {response.status_code}")
            
        logging.info(f"Successfully uploaded {len(data)} bytes.")

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
        genres = self._execute_query_list(q_genre, "label")

        # Query Actors (limit to top 200 most frequent)
        q_actor = """
        PREFIX ex: <http://example.org/movie/>
        SELECT ?label (COUNT(?m) as ?count) WHERE {
            ?m ex:actor ?a .
            BIND(REPLACE(STR(?a), "^.*\\\\/", "") AS ?label)
        } GROUP BY ?label ORDER BY DESC(?count) LIMIT 200
        """
        actors = self._execute_query_list(q_actor, "label")

        # Query Directors
        q_director = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?label WHERE {
            ?m ex:director ?d .
            BIND(REPLACE(STR(?d), "^.*\\\\/", "") AS ?label)
        } ORDER BY ?label
        """
        directors = self._execute_query_list(q_director, "label")

        return {"genres": genres, "actors": actors, "directors": directors}

    def _execute_query_list(self, query, var_name):
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
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
            self.sparql.setQuery(query_body)
            results = self.sparql.query().convert()
            
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
                self.sparql.setQuery(q_attr)
                res = self.sparql.query().convert()
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
