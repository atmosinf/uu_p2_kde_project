# Movie & Actor Relationship Explorer

A semantic web application illustrating relationships between movies, actors, directors, and genres using a knowledge graph backend.

## 🚀 Quick Start (Docker)

The easiest way to run the application is with Docker Compose. This starts the **Frontend** (Next.js), **Backend** (FastAPI), and **Knowledge Graph** (Blazegraph).

### Prerequisites
1.  **Docker & Docker Compose** installed.
2.  **Data Files**: Ensure the `data/` directory contains:
    *   `movie_embeddings.csv` (Required for "Find Similar" AI features)
    *   `wiki_db_cleaned.ttl` (Main dataset, loaded automatically on first run)

### Steps

1.  **Build and Start**:
    ```bash
    docker-compose up --build -d
    ```
    *Note: The first run might take a minute to initialize the graph database.*

2.  **Access the Application**:
    *   **Frontend**: [http://localhost:3000](http://localhost:3000)
    *   **Blazegraph Admin**: [http://localhost:9999/bigdata](http://localhost:9999/bigdata)
    *   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

3.  **Stop**:
    ```bash
    docker-compose down
    ```

### 🧹 Heavy Reset (Clearing Database)

If you modify the ontology or `ttl` data files and need to reload them, you must clear the database volume:

```bash
# Stop and remove volumes (Deletes persistent database)
docker-compose down -v

# Start again (Data will be re-uploaded)
docker-compose up --build -d
```

## 🛠 Manual Setup

If you prefer running without Docker:

### 1. Backend (FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run the server (Port 8000)
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start the server (Port 3000)
npm start -- -p 3000
```

## 🏗 Architecture

- **Frontend**: Next.js 15, React 19, Tailwind CSS (Premium Dark Theme)
- **Backend**: Python FastAPI, rdflib (SPARQL Query Engine)
- **Data**: RDF Turtle file (`data/wiki_db_cleaned.ttl`)
## 🔧 Troubleshooting

### Changes not verified? (Docker Caching)

If you modify configuration or code but don't see the changes in Docker, the build cache might be stale. Force a clean rebuild:

```bash
# Rebuild the frontend without cache
docker-compose build --no-cache frontend

# Recreate the containers to pick up the new image
docker-compose up -d --force-recreate
```
