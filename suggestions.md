# Suggestions for Improvements (KDE Project)

Based on the analysis of your project, here are some suggestions to enhance the "Knowledge and Data Engineering" aspects. These changes will help demonstrate a deeper understanding of Semantic Web concepts.

## 1. Formal Ontology Definition
**Current State:** The project uses an *implicit* schema. Movies have properties like `ex:title` and `ex:director`, but they are not explicitly typed as `ex:Movie`.
**Suggestion:** Explicitly define an Ontology using `RDFS` or `OWL`.

*   **Define Classes:** Explicitly assert that "Dune" is a `a ex:Movie`.
    *   `ex:Movie`, `ex:Person`, `ex:Genre`, `ex:Director`, `ex:Actor`.
*   **Define Properties:** Define domains and ranges.
    *   `ex:directedBy`: Domain = `ex:Movie`, Range = `ex:Director`.
*   **Benefit:** This formally models the domain, which is a core part of KDE.

**How to implement:**
1.  Create a file `ontology/schema.ttl`.
2.  Update `csv_to_rdf.py` to add `rdf:type` statements (e.g., `g.add((movie_uri, RDF.type, ex.Movie))`).

## 2. Reasoning and Inference
**Current State:** Queries match exact patterns. If you search for "Action", you only get movies explicitly tagged "Action".
**Suggestion:** Use a hierarchy to enable inference.

*   **Genre Hierarchy:** Define strict subclasses.
    *   `ex:SpaghettiWestern` `rdfs:subClassOf` `ex:Western`.
    *   `ex:SciFi` `rdfs:subClassOf` `ex:SpeculativeFiction`.
*   **Inference:** When you query for "Western", the reasoner (Blazegraph) will automatically include "Spaghetti Westerns" without you needing to change the query to `UNION`.
*   **Benefit:** Shows the power of semantic search over standard SQL/document search.

## 3. Data Validation with SHACL
**Current State:** Data quality depends on the Python preprocessing script.
**Suggestion:** Use SHACL (Shapes Constraint Language) to validate the RDF graph.

*   **Create Shapes:** Define constraints, e.g., "Every Movie MUST have exactly one Title and at least one Genre".
*   **Validation:** Run a validation script to ensure your Knowledge Graph is consistent.
*   **Benefit:** Strictly separates data quality rules from ingestion code.

## 4. Federated Queries
**Current State:** You have a script `wikidata_to_dbpedia_movies.py` that pre-fetches data.
**Suggestion:** Execute federated queries directly from Blazegraph (Service clause) or your backend.

*   **Live Enrichment:** Instead of pre-downloading, you could (for specific deep-dives) query Wikidata live for extra info like "Awards won".
*   **Benefit:** Demonstrates connecting the Web of Data (Linked Data principles).

## 5. Advanced Recommender System (Graph Embeddings)
**Current State:** Recommendations currently use count-based overlap (SPARQL aggregations).
**Suggestion:** Implement Graph Embeddings (like RDF2Vec or TransE).

*   **Embeddings:** Represent nodes as vectors. Similar movies will be close in vector space.
*   **Validation:** You can visually plot these 2D/3D to show clusters of similar movies.
*   **Benefit:** Can find "semantically similar" movies that might not share the exact same genre or actor, capturing latent relationships.
