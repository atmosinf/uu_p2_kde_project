import rdflib
from rdflib import Graph, Literal, URIRef
from backend.vocab import EX
import logging
import sys

class QueryEngine:
    def __init__(self, rdf_file: str):
        self.g = Graph()
        self.g.parse(rdf_file, format="turtle")
        logging.info(f"Loaded {len(self.g)} triples from {rdf_file}")

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
        genres = [str(row.label) for row in self.g.query(q_genre)]

        # Query Actors (limit to top 100 most frequent to avoid UI bloat or full list)
        q_actor = """
        PREFIX ex: <http://example.org/movie/>
        SELECT ?label (COUNT(?m) as ?count) WHERE {
            ?m ex:actor ?a .
            BIND(REPLACE(STR(?a), "^.*\\\\/", "") AS ?label)
        } GROUP BY ?label ORDER BY DESC(?count) LIMIT 200
        """
        actors = [str(row.label) for row in self.g.query(q_actor)]

        # Query Directors
        q_director = """
        PREFIX ex: <http://example.org/movie/>
        SELECT DISTINCT ?label WHERE {
            ?m ex:director ?d .
            BIND(REPLACE(STR(?d), "^.*\\\\/", "") AS ?label)
        } ORDER BY ?label
        """
        directors = [str(row.label) for row in self.g.query(q_director)]

        return {"genres": genres, "actors": actors, "directors": directors}

    def search_movies(self, title=None, genre=None, year_start=None, year_end=None, actor=None, director=None, limit=50):
        """Dynamic SPARQL query builder with optimized two-step execution."""

        # Step 1: Find matching movies (ID, title, year, runtime)
        # We avoid fetching genres, actors, directors here to prevent Cartesian product
        
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
            # Use REGEX for case-insensitive search
            query_body += f'\nFILTER(REGEX(?title, "{title}", "i"))'
        
        if genre:
            # If filtering by genre, we check existence but don't project it yet
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

        # Apply LIMIT at the SPARQL level!
        query_body += f"LIMIT {limit}"

        movies_map = {}
        
        try:
            # logging.info(f"Query Step 1: {query_body}")
            for row in self.g.query(query_body):
                m_uri = str(row.movie)
                movies_map[m_uri] = {
                    "id": m_uri,
                    "title": str(row.title),
                    "year": str(row.year) if row.year else None,
                    "runtime": str(row.runtime) if row.runtime else None,
                    "genres": [],
                    "directors": [],
                    "actors": [],
                    "similarity": 0 # Kept for compatibility if needed
                }
        except Exception as e:
            logging.error(f"SPARQL Error in Step 1: {e}")
            return []

        if not movies_map:
            return []

        # Step 2: Fetch Details for found movies
        movie_uris = list(movies_map.keys())
        # Construct VALUES block: (<uri1>) (<uri2>) ...
        uris_str = " ".join([f"<{uri}>" for uri in movie_uris])

        # Helper to fetch multi-valued attributes
        def fetch_attribute(attr_name, target_list):
            q_attr = f"""
            PREFIX ex: <http://example.org/movie/>
            SELECT ?movie ?val WHERE {{
                VALUES ?movie {{ {uris_str} }}
                ?movie ex:{attr_name} ?val .
            }}
            """
            try:
                for row in self.g.query(q_attr):
                    m_uri = str(row.movie)
                    if m_uri in movies_map:
                        val = str(row.val).split('/')[-1]
                        movies_map[m_uri][target_list].append(val)
            except Exception as e:
                logging.error(f"SPARQL Error fetching {attr_name}: {e}")

        fetch_attribute("genre", "genres")
        fetch_attribute("director", "directors")
        fetch_attribute("actor", "actors")

        # Convert to list and ensure sorted attributes
        results = list(movies_map.values())
        for m in results:
             m["genres"].sort()
             m["directors"].sort()
             m["actors"].sort()
        
        # Re-sort results to match the original ORDER BY from Step 1 (dict iteration preserves insertion order in modern Python, but just in case)
        # Actually, since we populated movies_map from the query result, the keys are in order.
        # But let's keep the explicit sort if needed.
        # The Step 1 query already sorted by year.
        
        logging.info(f"Search returned {len(results)} results")
        return results
