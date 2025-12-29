import rdflib
from rdflib import Graph

g = Graph()
g.parse("data/wiki_db_cleaned.ttl", format="turtle")
print(f"Loaded {len(g)} triples")

query = """
PREFIX ex: <http://example.org/movie/>
SELECT ?title WHERE {
    ?m ex:title ?title .
    FILTER(CONTAINS(LCASE(?title), "the"))
} LIMIT 5
"""

print("--- Simple Title Search ---")
for row in g.query(query):
    print(row.title)

print("\n--- Complex Query Check ---")
complex_query = """
PREFIX ex: <http://example.org/movie/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?movie ?title ?year ?runtime 
                (GROUP_CONCAT(DISTINCT ?g; separator=",") AS ?genres)
WHERE {
    ?movie ex:title ?title .
    OPTIONAL { ?movie ex:year ?year }
    OPTIONAL { ?movie ex:runtime ?runtime }
    OPTIONAL { ?movie ex:genre ?g }
    FILTER(CONTAINS(LCASE(?title), "the"))
}
GROUP BY ?movie ?title ?year ?runtime
LIMIT 5
"""

try:
    for row in g.query(complex_query):
        print(row.title, row.genres)
except Exception as e:
    print(f"Error: {e}")
