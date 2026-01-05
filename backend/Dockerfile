FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (if any needed for rdflib/compilation)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to /app
# We need the 'data' directory and 'backend' code structure to be preserved relative to each other if possible,
# or we adjust the COPY strategy.
# Based on the file structure:
# /workspaces/uu_p2_kde_project/
#   backend/
#   data/
# The backend code imports from backend package and reads data from ../data

# Let's verify the build context strategy. 
# Usually, we'd build from the root.
# Assuming build context is root:
COPY . .

# Run uvicorn
# We set Python path to include current directory
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
