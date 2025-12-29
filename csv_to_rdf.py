import csv
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import XSD
import re

# ---------- Settings ----------
CSV_FILE = "data/wiki_db_cleaned.csv"
OUTPUT_FILE = "data/wiki_db_cleaned.ttl"
BASE_URI = "http://example.org/movie/"
ex = Namespace(BASE_URI)

# ---------- Helper function: generate clean URI ----------
def to_uri(text):
    """
    Convert a string into a safe URI:
    - Strip leading/trailing spaces
    - Replace spaces with underscores
    - Remove special characters
    """
    text = text.strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^A-Za-z0-9_]", "", text)
    return URIRef(BASE_URI + text)

# ---------- Create RDF Graph ----------
g = Graph()
g.bind("ex", ex)

# ---------- Read CSV ----------
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        movie_uri = to_uri(row["title"])

        # title (mandatory)
        g.add((movie_uri, ex.title, Literal(row["title"])))

        # year (check empty and numeric)
        year = row.get("year", "").strip()
        if year.isdigit():
            g.add((movie_uri, ex.year, Literal(year, datatype=XSD.gYear)))

        # runtime (check empty and numeric)
        runtime = row.get("runtime", "").strip()
        if runtime.replace(".","").isdigit():
            g.add((movie_uri, ex.runtime, Literal(runtime, datatype=XSD.float)))

        # directors (multiple allowed, skip empty)
        directors = row.get("directors", "").strip()
        if directors:
            for d in re.split(r"[|,]", directors):
                d = d.strip()
                if d:
                    g.add((movie_uri, ex.director, to_uri(d)))

        genres = row.get("genre", "").strip()
        if genres:
            for d in re.split(r"[|,]", genres):
                d = d.strip()
                if d:
                    g.add((movie_uri, ex.genre, to_uri(d)))

        # actors (multiple allowed, skip empty)
        actors = row.get("actors", "").strip()
        if actors:
            for a in re.split(r"[|,]", actors):
                a = a.strip()
                if a:
                    g.add((movie_uri, ex.actor, to_uri(a)))

# ---------- Serialize RDF to Turtle ----------
g.serialize(OUTPUT_FILE, format="turtle")
print(f"RDF successfully written to {OUTPUT_FILE}")
