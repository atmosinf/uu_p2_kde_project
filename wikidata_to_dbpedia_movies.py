import pandas as pd
import requests
import time

# =========================
# Config
# =========================
INPUT_CSV = "./data/wiki_5y/merged_2.csv"
OUTPUT_CSV = "./data/wiki_db_2.csv"

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
DBPEDIA_SPARQL = "https://dbpedia.org/sparql"

HEADERS = {
    "User-Agent": "MovieDataIntegration/1.0 (student project)"
}

# =========================
# Helper: run SPARQL query
# =========================
def run_sparql(endpoint, query):
    headers = {
        "User-Agent": "MovieDataIntegration/1.0 (student project)",
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        endpoint,
        data={"query": query},
        headers=headers,
        timeout=120
    )

    if response.status_code != 200:
        print("HTTP status:", response.status_code)
        print(response.text[:500])
        response.raise_for_status()

    return response.json()["results"]["bindings"]

def normalize_qid(value):
    if isinstance(value, str) and value.startswith("http"):
        return value.rsplit("/", 1)[-1]
    return value

# =========================
# Step 1: QID -> DBpedia URI
# =========================
def get_dbpedia_uris(qids, batch_size=50, sleep_time=1):
    mapping = {}
    for i in range(0, len(qids), batch_size):
        batch = qids[i:i + batch_size]
        print(f"  Wikidata batch {i}–{i + len(batch) - 1}")

        values = " ".join(f"<http://www.wikidata.org/entity/{qid}>" for qid in batch)

        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?dbpediaMovie ?wikidata WHERE {{
            VALUES ?wikidata {{ {values} }}
            ?dbpediaMovie owl:sameAs ?wikidata .
        }}
        """

        try:
            results = run_sparql(DBPEDIA_SPARQL, query)
            for r in results:
                wikidata_qid = r["wikidata"]["value"].rsplit("/", 1)[-1]
                dbpedia_uri = r["dbpediaMovie"]["value"]
                mapping[wikidata_qid] = dbpedia_uri
        except Exception as e:
            print(f"Batch failed: {e}")

        time.sleep(sleep_time)

    return mapping



# =========================
# Step 2: DBpedia movie data
# =========================
def get_movie_data(dbpedia_uris):
    if not dbpedia_uris:
        return {}

    values = " ".join(f"<{uri}>" for uri in dbpedia_uris)

    query = f"""
    SELECT
      ?film
      ?title
      ?year
      ?runtime
      (GROUP_CONCAT(DISTINCT ?directorName; separator=", ") AS ?directors)
      (GROUP_CONCAT(DISTINCT ?actorName; separator=", ") AS ?actors)
    WHERE {{
      VALUES ?film {{ {values} }}

      ?film rdf:type dbo:Film .

      ?film rdfs:label ?title .
      FILTER(lang(?title) = "en")

      OPTIONAL {{
        ?film dbo:releaseDate ?date .
        BIND(YEAR(?date) AS ?year)
      }}

      OPTIONAL {{ ?film dbo:runtime ?runtime }}

      OPTIONAL {{
        ?film dbo:director ?director .
        ?director rdfs:label ?directorName .
        FILTER(lang(?directorName) = "en")
      }}

      OPTIONAL {{
        ?film dbo:starring ?actor .
        ?actor rdfs:label ?actorName .
        FILTER(lang(?actorName) = "en")
      }}
    }}
    GROUP BY ?film ?title ?year ?runtime
    """

    results = run_sparql(DBPEDIA_SPARQL, query)

    data = {}
    for r in results:
        film_uri = r["film"]["value"]
        data[film_uri] = {
            "title_dbpedia": r.get("title", {}).get("value"),
            "year_dbpedia": r.get("year", {}).get("value"),
            "runtime": r.get("runtime", {}).get("value"),
            "directors": r.get("directors", {}).get("value"),
            "actors": r.get("actors", {}).get("value"),
        }

    return data

# =========================
# Main
# =========================
def main():
    print("Loading CSV...")
    df = pd.read_csv(INPUT_CSV)

    if "movie" not in df.columns:
        raise ValueError("Input CSV must contain a 'movie' column")

    def normalize_qid(value):
        if isinstance(value, str) and value.startswith("http"):
            return value.rsplit("/", 1)[-1]
        return value

    df["qid"] = df["movie"].apply(normalize_qid)

    qids = df["qid"].dropna().unique().tolist()
    print(f"Found {len(qids)} QIDs")

    print("Querying Wikidata for DBpedia URIs...")
    qid_to_dbpedia = get_dbpedia_uris(qids)

    df["dbpedia_uri"] = df["qid"].map(qid_to_dbpedia)

    time.sleep(1)

    dbpedia_uris = df["dbpedia_uri"].dropna().unique().tolist()
    print(f"Found {len(dbpedia_uris)} DBpedia URIs")

    print("Querying DBpedia for movie data...")
    movie_data = get_movie_data(dbpedia_uris)

    df["title_dbpedia"] = df["dbpedia_uri"].map(
        lambda x: movie_data.get(x, {}).get("title_dbpedia")
    )
    df["year_dbpedia"] = df["dbpedia_uri"].map(
        lambda x: movie_data.get(x, {}).get("year_dbpedia")
    )
    df["runtime_dbpedia"] = df["dbpedia_uri"].map(
        lambda x: movie_data.get(x, {}).get("runtime")
    )
    df["directors_dbpedia"] = df["dbpedia_uri"].map(
        lambda x: movie_data.get(x, {}).get("directors")
    )
    df["actors_dbpedia"] = df["dbpedia_uri"].map(
        lambda x: movie_data.get(x, {}).get("actors")
    )

    df = df.drop(columns=["dbpedia_uri"])

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Done, Output saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
