"""
TarkBot Tests
Basic functionality tests
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.scraper import TarkovWikiScraper
from core.embeddings import TextEmbedder, TextChunker
from core.vector_store import VectorStore


def test_scraper():
    """Test wiki scraper"""
    print("Testing scraper...")
    scraper = TarkovWikiScraper()

    # Test with a simple page
    test_url = "https://escapefromtarkov.fandom.com/wiki/AK-74N"
    page = scraper.scrape_page(test_url, "weapons")

    if page:
        print(f"✓ Scraped page: {page.title}")
        print(f"  Content length: {len(page.content)}")
        print(f"  Metadata keys: {list(page.metadata.keys())}")
        return True
    else:
        print("✗ Failed to scrape page")
        return False


def test_embedder():
    """Test text embedder"""
    print("\nTesting embedder...")
    embedder = TextEmbedder()

    test_text = "The AK-74N is a 5.45x39mm assault rifle."
    embedding = embedder.embed_text(test_text)

    if embedding is not None and len(embedding) == 768:
        print(f"✓ Generated embedding with shape: {embedding.shape}")
        return True
    else:
        print("✗ Failed to generate embedding")
        return False


def test_chunker():
    """Test text chunker"""
    print("\nTesting chunker...")
    chunker = TextChunker()

    test_text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    chunks = chunker.semantic_chunk(test_text)

    if len(chunks) > 0:
        print(f"✓ Created {len(chunks)} chunks")
        return True
    else:
        print("✗ Failed to create chunks")
        return False


def test_vector_store():
    """Test vector store"""
    print("\nTesting vector store...")
    store = VectorStore()

    # Reset for clean test
    store.reset()

    # Test data
    import numpy as np

    test_vectors = np.random.rand(5, 768).astype(np.float32)
    test_metadata = [
        {"id": f"test_{i}", "text": f"Test document {i}"} for i in range(5)
    ]

    # Add vectors
    store.add_vectors(test_vectors, test_metadata)

    # Search
    query = np.random.rand(768).astype(np.float32)
    results = store.search(query, k=2)

    if len(results) > 0:
        print(f"✓ Vector search returned {len(results)} results")
        return True
    else:
        print("✗ Vector search failed")
        return False


def main():
    """Run all tests"""
    print("Running TarkBot tests...\n")

    tests = [test_scraper, test_embedder, test_chunker, test_vector_store]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
