"""
TarkBot Embeddings Module
Text processing and vector embeddings
"""

import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np


class TextEmbedder:
    """Handles text embedding using sentence transformers"""

    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        """Load the embedding model"""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Model loaded successfully")

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embeddings for text"""
        if self.model is None:
            self.load_model()

        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if self.model is None:
            self.load_model()

        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)


class TextChunker:
    """Handles text chunking for embedding"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def semantic_chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks respecting boundaries"""
        # Simple semantic chunking - split on double newlines (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_document(self, content: str, title: str = "") -> List[Dict[str, Any]]:
        """Chunk a document and return with metadata"""
        chunks = self.semantic_chunk(content)

        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunked_docs.append(
                {
                    "id": f"{title}_{i}",
                    "text": chunk,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
            )

        return chunked_docs


if __name__ == "__main__":
    # Test embedder
    embedder = TextEmbedder()
    test_text = "The AK-74N is a 5.45x39mm assault rifle."
    embedding = embedder.embed_text(test_text)
    print(f"Embedding shape: {embedding.shape}")

    # Test chunker
    chunker = TextChunker()
    long_text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    chunks = chunker.semantic_chunk(long_text)
    print(f"Number of chunks: {len(chunks)}")
