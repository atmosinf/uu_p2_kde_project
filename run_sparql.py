from rdflib import Graph, Namespace, Literal
from rdflib.namespace import XSD

file_turtle = "./data/wiki_db_cleaned.ttl"
ds = Namespace("http://example.org/movie/")

g = Graph()
g.parse(file_turtle, format="turtle")

def test_query(query, init_bindings=None):
    results = g.query(query, initBindings=init_bindings)
    done = []
    for r in results:
        row = {}
        for v in r.labels:
            row[v] = r[v].toPython() if r[v] is not None else None
        done.append(row)
    return done


#movies similarity based on shared genre/actor/director
movies_similarity = """
PREFIX ex: <http://example.org/movie/>
PREFIX ex: <http://example.org/movie/>

SELECT ?recommended ?title (COUNT(DISTINCT ?feature) AS ?score)
WHERE {
  ?selectedMovie (ex:genre|ex:actor|ex:director) ?feature.
  ?recommended   (ex:genre|ex:actor|ex:director) ?feature;
                 ex:title ?title.
  FILTER(?recommended != ?selectedMovie)
}
GROUP BY ?recommended ?title
HAVING (COUNT(DISTINCT ?feature) >= 2)
ORDER BY DESC(?score)
LIMIT 5
"""
results = test_query(movies_similarity, init_bindings={"selectedMovie": ds["Harry_Potter_and_the_Goblet_of_Fire"]})
print("Movie similarity:")
for row in results:
    print(row)

print("\n")
#movies sharing actors
movies_sharing_actors = """
PREFIX ex: <http://example.org/movie/>
SELECT ?movie ?title (COUNT(DISTINCT ?actor) AS ?sharedActors)
WHERE {
  ?movie ex:actor ?actor ;
         ex:title ?title .
  FILTER(?actor IN (?a1, ?a2))
}
GROUP BY ?movie ?title
HAVING (COUNT(DISTINCT ?actor) = 2)
ORDER BY DESC(?sharedActors)
LIMIT 5
"""
bindings = {"a1": ds.Daniel_Radcliffe,"a2": ds.Emma_Watson}
results = test_query(movies_sharing_actors, init_bindings=bindings)
print("Movies sharing actors:")
for row in results:
    print(row)

print("\n")
#movies with specific genres
movies_specific_genres = """
PREFIX ex: <http://example.org/movie/> 
SELECT ?movie ?title (COUNT(DISTINCT ?genre) AS ?numGenres) 
WHERE {
  ?movie ex:genre ?genre ;
         ex:title ?title .
  VALUES ?genre { ex:adventure ex:comedy ex:drama }  # esempio di generi
}
GROUP BY ?movie ?title 
HAVING (COUNT(DISTINCT ?genre) >= 2) 
ORDER BY DESC(?numGenres) 
LIMIT 5
"""
results = test_query(movies_specific_genres)
print("Movies with specific genres:")
for row in results:
    print(row)

print("\n")
#movies by a specific director
movies_specific_director = """
PREFIX ex: <http://example.org/movie/>
SELECT ?movie ?title ?year
WHERE {
  ?movie ex:director ?selectedDirector;
         ex:title ?title .
  OPTIONAL { ?movie ex:year ?year }
}
ORDER BY DESC(?year)
"""
results = test_query(movies_specific_director, init_bindings={"selectedDirector": ds["Ridley_Scott"]})
print("Movies by a specific director:")
for row in results:
    print(row)

print("\n")
#movies within a year range
movies_within_year_range = """
PREFIX ex: <http://example.org/movie/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?movie ?title ?year 
WHERE { 
    ?movie ex:title ?title ; 
        ex:year ?year . 
    FILTER(str(?year) >= "2015" && str(?year) <= "2020")
} 
ORDER BY DESC(?year) 
LIMIT 5
"""
results = test_query(movies_within_year_range)
print("Movies within a year range:")
for row in results:
    print(row)

print("\n")
#movies by runtime
movies_by_runtime = """
PREFIX ex: <http://example.org/movie/>
SELECT ?movie ?title ?runtime
WHERE {
  ?movie ex:title ?title ;
         ex:runtime ?runtime .
  FILTER(?runtime >= ?minRuntime && ?runtime <= ?maxRuntime)
}
ORDER BY ?runtime
LIMIT 5
"""
bindings = {"minRuntime": Literal(100, datatype=XSD.integer), "maxRuntime": Literal(150, datatype=XSD.integer)}
results = test_query(movies_by_runtime, init_bindings=bindings)
print("Movies by runtime:")
for row in results:
    print(row)

print("\n")
#movies with keywords in the title
movies_with_keywords = """
PREFIX ex: <http://example.org/movie/>
SELECT ?movie ?title
WHERE {
  ?movie ex:title ?title .
  FILTER(CONTAINS(LCASE(?title), LCASE(?keyword)))
}
LIMIT 5
"""
bindings = {"keyword": Literal("bye")}
results = test_query(movies_with_keywords, init_bindings=bindings)
print("Movies with keywords in the title:")
for row in results:
    print(row)

print("\n")
#most recent movie per person
most_recent_movie_per_person = """
PREFIX ex: <http://example.org/movie/>

SELECT ?person ?movie ?title ?year
WHERE {
  ?movie ex:title ?title ;
         ex:year ?year .
  { ?movie ex:director ?person } 
  UNION 
  { ?movie ex:actor ?person }
  FILTER(?person = ?selectedPerson)
}
ORDER BY DESC(?year)
LIMIT 1
"""

bindings = {"selectedPerson": ds.Daniel_Radcliffe}
results = test_query(most_recent_movie_per_person, init_bindings=bindings)
print("Most recent movie per person:")
for row in results:
    print(row)

print("\n")
#movies excluding a specific genre
movies_excluding_genre = """
PREFIX ex: <http://example.org/movie/>
SELECT ?movie ?title
WHERE {
  ?movie ex:title ?title .
  FILTER NOT EXISTS { ?movie ex:genre ?excludedGenre }
}
LIMIT 5
"""
bindings = {"excludedGenre": ds.horror}
results = test_query(movies_excluding_genre, init_bindings=bindings)
print("Movies excluding a specific genre:")
for row in results:
    print(row)

print("\n")
#movies with a specific genre but excluding a specific actor
movies_with_specific_genre_excluding_actor = """
SELECT ?movie ?title
WHERE {
  ?selectedMovie ex:genre ?genre .
  ?movie ex:genre ?genre ;
         ex:title ?title .
  FILTER(?movie != ?selectedMovie)
  FILTER NOT EXISTS { ?movie ex:actor ?excludedActor }
}
LIMIT 10
"""
bindings = {"selectedMovie": ds["Harry_Potter_and_the_Goblet_of_Fire"],
            "excludedActor": ds.Daniel_Radcliffe}
results = test_query(movies_with_specific_genre_excluding_actor, init_bindings=bindings)
print("Movies with a specific genre but excluding a specific actor:")
for row in results:
    print(row)