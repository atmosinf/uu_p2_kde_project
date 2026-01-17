import csv
import numpy as np

class EmbeddingEngine:
    def __init__(self, embedding_file: str):
        self.embeddings = {}

        #Open embeddings CSV file
        with open(embedding_file, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  #Skip header row

            for row in reader:
                uri = row[0]  #First column is movie URI
                
                # Parse complex numbers (remove parens if any, just in case)
                vec_data = []
                for x in row[1:]:
                    x_clean = x.replace('(', '').replace(')', '')
                    vec_data.append(complex(x_clean))

                #The rest are vectors
                # specific strategy for RotatE/Complex embeddings:
                # We flatten the complex vector into a real vector of 2x dimensions
                # [Re(z1), Im(z1), Re(z2), Im(z2)...]
                # This allows standard cosine similarity to work effectively for clustering.
                c_vec = np.array(vec_data, dtype=np.complex64)
                real_vec = np.concatenate([c_vec.real, c_vec.imag])
                
                self.embeddings[uri] = real_vec.astype(np.float32)

    def get_similar_movies(self, target_movie_uri: str, top_n: int = 10):
        if target_movie_uri not in self.embeddings:
            return []

        target_vec = self.embeddings[target_movie_uri]
        sims = []

        for movie_uri, vec in self.embeddings.items():
            if movie_uri == target_movie_uri:
                continue 

            # RotatE is a distance-based model. 
            # Entities near each other in the vector space are similar.
            # We use Euclidean Distance (L2 norm) to measure this.
            dist = np.linalg.norm(target_vec - vec)
            
            sims.append((movie_uri, float(dist)))

        # Sort by ASCENDING distance (smaller is more similar)
        sims.sort(key=lambda x: x[1])
        print(sims[:top_n])
        return sims[:top_n]