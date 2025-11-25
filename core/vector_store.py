"""
TarkBot Vector Store Module
Simple numpy-based vector storage and retrieval
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple


class VectorStore:
    """Simple numpy-based vector store for embeddings"""

    def __init__(
        self,
        vectors_file: str = "data/vectors.npy",
        metadata_file: str = "data/metadata.pkl",
    ):
        self.vectors_file = vectors_file
        self.metadata_file = metadata_file
        self.vectors = None
        self.metadata = []

        # Create data directory
        os.makedirs(os.path.dirname(vectors_file), exist_ok=True)

        # Load existing data
        self.load_data()

    def load_data(self):
        """Load vectors and metadata from disk"""
        try:
            if os.path.exists(self.vectors_file):
                self.vectors = np.load(self.vectors_file)
                print(f"Loaded {len(self.vectors)} vectors")

            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                print(f"Loaded metadata for {len(self.metadata)} documents")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.vectors = None
            self.metadata = []

    def save_data(self):
        """Save vectors and metadata to disk"""
        if self.vectors is not None:
            np.save(self.vectors_file, self.vectors)
            print(f"Saved {len(self.vectors)} vectors")

        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"Saved metadata for {len(self.metadata)} documents")

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add vectors and metadata to the store"""
        # Convert to numpy array if needed
        if not isinstance(vectors, np.ndarray):
            vectors = np.array(vectors)

        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        vectors_normalized = vectors / norms

        # Append to existing vectors
        if self.vectors is None:
            self.vectors = vectors_normalized
        else:
            self.vectors = np.vstack([self.vectors, vectors_normalized])

        # Store metadata
        self.metadata.extend(metadata)

        print(f"Added {len(vectors)} vectors to store")

    def search(
        self, query_vector: np.ndarray, k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors using cosine similarity"""
        if self.vectors is None or len(self.vectors) == 0:
            return []

        # Normalize query vector
        norm = np.linalg.norm(query_vector)
        if norm == 0:
            return []
        query_normalized = query_vector / norm

        # Compute cosine similarities
        similarities = np.dot(self.vectors, query_normalized)

        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_indices:
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(similarities[idx])))

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return {
            "total_vectors": len(self.vectors) if self.vectors is not None else 0,
            "dimension": self.vectors.shape[1] if self.vectors is not None else 0,
            "vectors_file": self.vectors_file,
            "metadata_file": self.metadata_file,
        }

    def reset(self):
        """Reset the store (for testing)"""
        self.vectors = None
        self.metadata = []
        # Remove files if they exist
        for file_path in [self.vectors_file, self.metadata_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        print("Store reset")


if __name__ == "__main__":
    # Test vector store
    store = VectorStore()

    # Test data
    test_vectors = np.random.rand(10, 768).astype(np.float32)
    test_metadata = [
        {"id": f"doc_{i}", "text": f"Document {i}", "title": f"Title {i}"}
        for i in range(10)
    ]

    # Add vectors
    store.add_vectors(test_vectors, test_metadata)

    # Search
    query = np.random.rand(768).astype(np.float32)
    results = store.search(query, k=3)

    print(f"Search results: {len(results)}")
    for metadata, score in results:
        print(f"  {metadata['id']}: {score:.3f}")

    # Save and load
    store.save_index()
    store.load_index()
    print("Index saved and loaded successfully")
