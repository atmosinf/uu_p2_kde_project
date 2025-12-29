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
        """Dynamic SPARQL query builder with Python-side aggregation."""
        
        query_body = """
        PREFIX ex: <http://example.org/movie/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?movie ?title ?year ?runtime ?g ?d ?a
        WHERE {
            ?movie ex:title ?title .
            OPTIONAL { ?movie ex:year ?year }
            OPTIONAL { ?movie ex:runtime ?runtime }
            OPTIONAL { ?movie ex:genre ?g }
            OPTIONAL { ?movie ex:director ?d }
            OPTIONAL { ?movie ex:actor ?a }
        """

        # Filters
        if title:
            # Use REGEX for case-insensitive search (more robust in rdflib than LCASE sometimes)
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
        """

        movies_map = {}
        
        try:
            # logging.info(f"Query: {query_body}") 
            for row in self.g.query(query_body):
                m_uri = str(row.movie)
                
                if m_uri not in movies_map:
                    movies_map[m_uri] = {
                        "id": m_uri,
                        "title": str(row.title),
                        "year": str(row.year) if row.year else None,
                        "runtime": str(row.runtime) if row.runtime else None,
                        "genres": set(),
                        "directors": set(),
                        "actors": set(),
                        "similarity": 0
                    }
                
                if row.g:
                    movies_map[m_uri]["genres"].add(str(row.g).split('/')[-1])
                if row.d:
                    movies_map[m_uri]["directors"].add(str(row.d).split('/')[-1])
                if row.a:
                    movies_map[m_uri]["actors"].add(str(row.a).split('/')[-1])

        except Exception as e:
            logging.error(f"SPARQL Error: {e}")
            return []
            
        # Convert sets to lists and apply limit
        results = []
        for m in list(movies_map.values()):
             m["genres"] = sorted(list(m["genres"]))
             m["directors"] = sorted(list(m["directors"]))
             m["actors"] = sorted(list(m["actors"]))
             results.append(m)
        
        # Sort by year desc
        results.sort(key=lambda x: x['year'] or "0", reverse=True)
        
        logging.info(f"Search returned {len(results)} results")
        return results[:limit]
