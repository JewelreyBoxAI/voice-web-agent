import os
import faiss
import json
import numpy as np
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.retrievers.document_compressors import EmbeddingsFilter
from typing import List, Tuple, Optional
import logging

# Logger setup
logger = logging.getLogger("memory_manager")

# ENV setup (✅ Guard clause)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, "☠️ OPENAI_API_KEY not found in environment"

# Init Embeddings
embedding_model = OpenAIEmbeddings()

# Load intents configuration for fallback URL injection
ROOT = os.path.dirname(os.path.abspath(__file__))
intents_file = os.path.join(ROOT, "prompts", "intents.json")
try:
    with open(intents_file, "r", encoding="utf-8") as f:
        INTENTS = json.load(f)
except FileNotFoundError:
    logger.warning(f"Intents file not found at {intents_file}")
    INTENTS = {}

# ----------------------------------------------------------------------------
# LOADERS (merged logic from loaders.py)
# ----------------------------------------------------------------------------
def load_documents_from_jsonl(path: str) -> List[Document]:
    """
    Load documents from a .jsonl file. Each line should be a JSON object
    with at least 'content' and optionally 'metadata'.
    """
    docs = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            content = data.get('content')
            metadata = data.get('metadata', {})
            if content:
                docs.append(Document(page_content=content, metadata=metadata))
    return docs

# ----------------------------------------------------------------------------
# INDEX BUILDER (merged logic from index_builder.py)
# ----------------------------------------------------------------------------
def build_faiss_index(docs: List[Document], index_path: str) -> FAISS:
    """
    Create or overwrite a FAISS index from the given documents.
    Saves index to disk at index_path.
    """
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(index_path)
    return vectorstore

# ----------------------------------------------------------------------------
# SEMANTIC RETRIEVER WITH FALLBACKS
# ----------------------------------------------------------------------------
def load_faiss_index(index_path: str) -> Optional[FAISS]:
    try:
        return FAISS.load_local(index_path, embedding_model)
    except Exception as e:
        print(f"☠️ Failed to load FAISS index: {e}")
        return None

def semantic_retrieve(query: str, index_path: str, k: int = 3, threshold: float = 0.75) -> List[Tuple[str, float]]:
    """
    Perform semantic search with optional reranking and fallback filtering.
    """
    index = load_faiss_index(index_path)
    if not index:
        return []

    compressor = EmbeddingsFilter(embeddings=embedding_model, similarity_threshold=threshold)
    retriever = index.as_retriever(search_type="similarity", search_kwargs={"k": k})
    retriever_with_filter = compressor | retriever

    results = retriever_with_filter.get_relevant_documents(query)
    return [(doc.page_content, doc.metadata.get("score", 0.0)) for doc in results]

# ----------------------------------------------------------------------------
# ROUTING BY SUBINDEX (optional hierarchical retrieval)
# ----------------------------------------------------------------------------
def get_route_index_path(intent: str) -> str:
    intent_map = {
        "faq": "./indexes/faqs",
        "products": "./indexes/products",
        "services": "./indexes/services",
        "design": "./indexes/design"
    }
    return intent_map.get(intent, "./indexes/default")

def hierarchical_retrieve(query: str, intent: str) -> List[Tuple[str, float]]:
    index_path = get_route_index_path(intent)
    return semantic_retrieve(query, index_path)

# ----------------------------------------------------------------------------
# URL INJECTION LOGIC (centralized memory control)
# ----------------------------------------------------------------------------
def get_relevant_url(user_input: str) -> Optional[str]:
    """
    Get the most relevant URL for user input using intent matching.
    Returns single URL or None if no match found.
    """
    user_input_lower = user_input.lower()
    for intent_key, intent_data in INTENTS.items():
        for synonym in intent_data["synonyms"]:
            if synonym in user_input_lower:
                return intent_data['url']
    return None

def inject_fallback_if_needed(user_input: str, response: str, semantic_results: List[Tuple[str, float]] = None) -> str:
    """
    Inject URL into response based on intent matching or semantic results.
    Ensures only ONE URL is injected per message.
    """
    # Try intent-based URL injection first
    url = get_relevant_url(user_input)
    if url:
        return response + f"\n\n🔗 You can explore that here: {url}"
    
    # If semantic results available, try to extract URL from metadata
    if semantic_results:
        for content, score in semantic_results:
            # This would need metadata with URLs from FAISS index
            # For now, fallback to intent system only
            pass
    
    # No match, no injection
    return response

def inject_relevant_url(user_input: str, response: str) -> str:
    """
    Legacy compatibility function - redirects to inject_fallback_if_needed.
    Maintains backward compatibility with existing app.py integration.
    """
    return inject_fallback_if_needed(user_input, response)

# ----------------------------------------------------------------------------
# DEBUG / TEST DRIVER
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    index_path = "./indexes/products"
    query = "custom lab diamond engagement ring"
    results = semantic_retrieve(query, index_path)

    print("\n💎 Top Matches:")
    for content, score in results:
        print(f"- ({score:.2f}) {content[:100]}...")
    
    # Test URL injection
    test_query = "I want to see diamonds"
    test_response = "Here are some diamond options for you."
    final_response = inject_relevant_url(test_query, test_response)
    print(f"\n🔗 URL Injection Test:\nInput: {test_query}\nOutput: {final_response}") 