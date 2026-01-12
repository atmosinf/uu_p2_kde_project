import os
import logging
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

# Configuration
BLAZEGRAPH_URL = os.getenv("BLAZEGRAPH_URL", "http://blazegraph:9999/blazegraph/sparql")

def check_blazegraph_status():
    """Checks if Blazegraph is up and running."""
    try:
        response = requests.get(BLAZEGRAPH_URL.replace("/sparql", "/status"))
        return response.status_code == 200
    except:
        return False

def load_file(file_path):
    """Loads a turtle file into Blazegraph."""
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return False
    
    logging.info(f"Loading {file_path} into Blazegraph...")
    
    with open(file_path, 'rb') as f:
        data = f.read()
        
    headers = {'Content-Type': 'text/turtle'}
    response = requests.post(BLAZEGRAPH_URL, data=data, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Failed to load {file_path}: {response.text}")
        return False
        
    logging.info(f"Successfully loaded {file_path}")
    return True

def init_db(data_files):
    """Checks if DB is empty, if so, loads data."""
    sparql = SPARQLWrapper(BLAZEGRAPH_URL)
    sparql.setQuery("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
    sparql.setReturnFormat(JSON)
    
    import time
    
    max_retries = 30
    retry_delay = 2
    count = -1
    
    for i in range(max_retries):
        try:
            results = sparql.query().convert()
            count = int(results["results"]["bindings"][0]["count"]["value"])
            logging.info(f"Current triple count in Blazegraph: {count}")
            break
        except Exception as e:
            if i < max_retries - 1:
                logging.warning(f"Waiting for Blazegraph... (Attempt {i+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logging.error(f"Could not connect to Blazegraph after {max_retries} attempts: {e}")
                return

    if count == 0:
        logging.info("Database is empty. Initializing...")
        for f in data_files:
            load_file(f)
    else:
        logging.info("Database already contains data. Skipping initialization.")
