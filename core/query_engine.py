"""
TarkBot Query Engine Module
Handles question answering using RAG
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv
from .embeddings import TextEmbedder
from .vector_store import VectorStore

# Load environment variables from .env file
load_dotenv()


@dataclass
class QueryResult:
    """Result of a query"""

    text: str
    confidence: float
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class QueryEngine:
    """RAG-based question answering engine"""

    def __init__(
        self,
        embedder: TextEmbedder,
        vector_store: VectorStore,
        llm_model: str = "gemini-2.0-flash-lite",
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm_model = llm_model

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.llm_model)
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not set")

    def classify_query(self, query: str) -> str:
        """Classify query type for routing"""
        query_lower = query.lower()

        # Simple keyword-based classification
        if any(
            word in query_lower for word in ["best", "good", "recommend", "compare"]
        ):
            return "comparison"
        elif any(
            word in query_lower for word in ["where", "location", "find", "extract"]
        ):
            return "location"
        elif any(
            word in query_lower for word in ["how", "what", "requirements", "steps"]
        ):
            return "factual"
        else:
            return "factual"  # Default

    def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from vector store"""
        # Generate query embedding
        query_embedding = self.embedder.embed_text(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)

        # Extract metadata
        context_docs = []
        for metadata, score in results:
            context_docs.append(
                {
                    "text": metadata.get("text", ""),
                    "title": metadata.get("title", ""),
                    "score": score,
                    "source": metadata.get("url", ""),
                }
            )

        return context_docs

    def generate_response(
        self, query: str, context_docs: List[Dict[str, Any]], query_type: str
    ) -> str:
        """Generate response using LLM"""

        # Prepare context
        context_text = "\n\n".join(
            [
                f"Source: {doc['title']}\n{doc['text']}"
                for doc in context_docs[:3]  # Limit context length
            ]
        )

        # Create prompt based on query type
        if query_type == "comparison":
            prompt = f"""Based on the following Escape from Tarkov information, answer this comparison question:

Context:
{context_text}

Question: {query}

Provide a clear, concise comparison with specific stats and recommendations."""
        elif query_type == "location":
            prompt = f"""Based on the following Escape from Tarkov information, answer this location question:

Context:
{context_text}

Question: {query}

Provide specific location details and directions."""
        else:
            prompt = f"""Based on the following Escape from Tarkov information, answer this question:

Context:
{context_text}

Question: {query}

Provide a clear, accurate answer using the provided information."""

        try:
            if self.model is None:
                # Demo mode - return a simple response based on context
                if context_docs:
                    top_doc = context_docs[0]
                    return f"Based on the Tarkov wiki: {top_doc['text'][:200]}..."
                else:
                    return "I don't have information about that in my knowledge base yet. Try scraping some data first."

            # Create the prompt with system instructions
            full_prompt = f"""You are a helpful Escape from Tarkov expert. Answer questions accurately using only the provided context. If you don't know something, say so.

Context:
{context_text}

Question: {query}

Answer:"""

            response = self.model.generate_content(full_prompt)

            return response.text.strip()

        except Exception as e:
            # Fallback to demo mode for any API errors (quota, model not found, etc.)
            if context_docs:
                top_doc = context_docs[0]
                return f"[DEMO MODE - API unavailable] Based on the Tarkov wiki: {top_doc['text'][:200]}..."
            else:
                return "[DEMO MODE - API unavailable] I don't have information about that in my knowledge base yet."

    def ask(self, query: str) -> QueryResult:
        """Main query method"""
        # Classify query
        query_type = self.classify_query(query)

        # Retrieve context
        context_docs = self.retrieve_context(query)

        # Generate response
        if context_docs:
            response_text = self.generate_response(query, context_docs, query_type)
            confidence = sum(doc["score"] for doc in context_docs) / len(context_docs)
        else:
            response_text = "I don't have information about that in my knowledge base."
            confidence = 0.0

        # Prepare sources
        sources = [
            {
                "title": doc["title"],
                "url": doc.get("source", ""),
                "relevance": doc["score"],
            }
            for doc in context_docs
        ]

        return QueryResult(
            text=response_text,
            confidence=confidence,
            sources=sources,
            metadata={
                "query_type": query_type,
                "context_docs_count": len(context_docs),
            },
        )


if __name__ == "__main__":
    # Test query engine
    embedder = TextEmbedder()
    vector_store = VectorStore()
    engine = QueryEngine(embedder, vector_store)

    # Test classification
    test_queries = [
        "What's the best 7.62x39 ammo?",
        "Where do I extract from Customs?",
        "How do I unlock the Therapist?",
    ]

    for query in test_queries:
        query_type = engine.classify_query(query)
        print(f"'{query}' -> {query_type}")
