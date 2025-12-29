# Developer Replication Guide

This guide is designed for a developer starting with **only** the initial data and ontology files. It walks through every step required to build the current "Movie Explorer" web application.

> **Note to Developer**: Use the links provided in "Reference Implementation" to cross-check your code against the working solution in this repository.

## Prerequisites
- Python 3.9+
- Node.js 18+
- Git

---

## Part 1: Backend Implementation

We will create a Python FastAPI backend to serve the movie data from the RDF file (`data/wiki_db_cleaned.ttl`).

### 1. Setup Environment
1. Create a `backend` directory in the project root.
2. Create `backend/requirements.txt` with dependencies (`fastapi`, `uvicorn`, `rdflib`, `pydantic`).
3. Install: `pip install -r backend/requirements.txt`

*   **Reference Implementation**: [`backend/requirements.txt`](file:///workspaces/uu_p2_kde_project/backend/requirements.txt)

### 2. RDF Namespaces
Create `backend/vocab.py` to define the RDF namespaces used in our data.

*   **Reference Implementation**: [`backend/vocab.py`](file:///workspaces/uu_p2_kde_project/backend/vocab.py)

### 3. SPARQL Query Engine
This is the core logic. It loads the Turtle file (.ttl) and executes queries.
Create `backend/query_engine.py`.

**Key Logic**:
- Load using `rdflib.Graph`.
- Aggregation is done in Python to assume clean lists for `genres`, `directors`, `actors`.
- Use `FILTER(REGEX(?title, "{value}", "i"))` for case-insensitive title search.

*   **Reference Implementation**: [`backend/query_engine.py`](file:///workspaces/uu_p2_kde_project/backend/query_engine.py)

### 4. FastAPI App entry point
Create `backend/main.py`.
- Enable `CORSMiddleware` (allow `http://localhost:3000`).
- Expose `/options` (GET) and `/search` (GET).

*   **Reference Implementation**: [`backend/main.py`](file:///workspaces/uu_p2_kde_project/backend/main.py)

### 5. Run the Backend
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Part 2: Frontend Implementation

We will use **Next.js 15** with **Tailwind CSS**.

### 1. Initialize Project & Install Deps
Run this in the project root:
```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --no-src-dir --app --import-alias "@/*" --use-npm
cd frontend
npm install axios framer-motion lucide-react clsx
```

### 2. API Client
Create `frontend/lib/api.ts` to genericize `axios` calls to your backend.

*   **Reference Implementation**: [`frontend/lib/api.ts`](file:///workspaces/uu_p2_kde_project/frontend/lib/api.ts)

### 3. Styles
Update `frontend/app/globals.css` for dark mode themes.

*   **Reference Implementation**: [`frontend/app/globals.css`](file:///workspaces/uu_p2_kde_project/frontend/app/globals.css)

### 4. Types
Define your TypeScript interfaces (e.g., `Movie`, `FilterOptions`).

*   **Reference Implementation**: [`frontend/types.ts`](file:///workspaces/uu_p2_kde_project/frontend/types.ts)

### 5. Components
Create `frontend/components/`:
- **`Sidebar.tsx`**: Filter inputs and Search button.
  *   **Reference**: [`frontend/components/Sidebar.tsx`](file:///workspaces/uu_p2_kde_project/frontend/components/Sidebar.tsx)
- **`MovieCard.tsx`**: Display card with `framer-motion` animations.
  *   **Reference**: [`frontend/components/MovieCard.tsx`](file:///workspaces/uu_p2_kde_project/frontend/components/MovieCard.tsx)

### 6. Main Page Layout
Connect state (`movies`, `loading`) to the UI in `frontend/app/page.tsx`.

*   **Reference Implementation**: [`frontend/app/page.tsx`](file:///workspaces/uu_p2_kde_project/frontend/app/page.tsx)

### 7. Run the Frontend
```bash
npm run dev
```

---

## Part 3: Configuration

1. **`.gitignore`**: ensure you ignore python cache and node_modules.

*   **Reference Implementation**: [`root .gitignore`](file:///workspaces/uu_p2_kde_project/.gitignore)
