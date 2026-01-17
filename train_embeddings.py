# Generates embeddings for all movie entities
import csv
import numpy as np
from rdflib import Graph
from pykeen.triples import TriplesFactory
from pykeen.models import RotatE
from pykeen.training import SLCWATrainingLoop
from backend.vocab import EX

RDF_PATH = "data/wiki_db_cleaned.ttl"
OUTPUT_CSV = "data/movie_embeddings.csv"

#Values for training the model
EMBEDDING_DIM = 64
EPOCHS = 20
BATCH_SIZE = 512

#Parse graph
g = Graph()
g.parse(RDF_PATH, format="turtle")

#Store every triple as a string in a NumPy array
triples = []
for s, p, o in g:
    triples.append((str(s), str(p), str(o)))
triples = np.array(triples, dtype=str)

#Needed for creating and training the model
triples_factory = TriplesFactory.from_labeled_triples(triples)


model = RotatE(triples_factory=triples_factory, embedding_dim=EMBEDDING_DIM, random_seed=42) #Initialize the RotatE model
training_loop = SLCWATrainingLoop(model=model, triples_factory=triples_factory) #Procedure for single-link prediction
training_loop.train(num_epochs=EPOCHS, batch_size=BATCH_SIZE, triples_factory=triples_factory) #Actually trains the model

#Extract all entity embeddings and their corresponding embedding index
all_embeddings = model.entity_representations[0]().detach().cpu().numpy()
entity_to_id = triples_factory.entity_to_id

# Retrieve all movie entities (subjects with a title)
movie_uris = set(str(s) for s in g.subjects(predicate=EX.title))

#Store movie embeddings in a CSV file
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    header = ["movie_uri"] + [f"e{i}" for i in range(EMBEDDING_DIM)] #first row is header
    writer.writerow(header)

    #Iterates through each movie entity and save its embedding
    for uri in movie_uris:
        if uri not in entity_to_id:
            continue
        vec = all_embeddings[entity_to_id[uri]]
        writer.writerow([uri] + vec.tolist())
