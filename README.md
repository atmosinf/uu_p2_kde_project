# Movie & Actor Relationship Explorer

A semantic web application illustrating relationships between movies, actors, directors, and genres using a knowledge graph backend.

## 🚀 Quick Start (Docker)

The easiest way to run the application is with Docker Compose.

1.  **Build and Start**:
    ```bash
    docker-compose up --build -d
    ```

2.  **Access the App**:
    Open [http://localhost:3000](http://localhost:3000)

3.  **Stop**:
    ```bash
    docker-compose down
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