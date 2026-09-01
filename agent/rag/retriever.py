import os
import faiss
import pickle
import yaml
from sentence_transformers import SentenceTransformer
from utils.logger import setup_logger

logger = setup_logger("retriever")

class RAGRetriever:
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(project_root, "config.yaml")
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f).get("rag", {})
        except Exception as e:
            logger.error(f"Failed to load RAG config: {e}")
            self.config = {}

        self.model_name = self.config["embedding_model"]
        self.index_path = os.path.join(project_root, self.config["index_path"])
        self.chunks_path = os.path.join(project_root, self.config["chunks_path"])
        self.top_k = self.config["top_k"]
        self.similarity_threshold = self.config["similarity_threshold"]

        self.model = None
        self.index = None
        self.chunks = []
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.chunks_path, "rb") as f:
                self.chunks = pickle.load(f)
            self.model = SentenceTransformer(self.model_name)
            logger.info("Loaded FAISS index and chunks.")
        else:
            logger.warning("Index or chunks not found. RAG will return empty results.")

    def query(self, text: str) -> list[dict]:
        if not self.index or not self.model:
            return []

        query_embedding = self.model.encode([text])
        distances, indices = self.index.search(query_embedding, self.top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            dist = distances[0][i]
            # Since L2 distance is used, smaller is more similar.
            # Using threshold as max distance allowed.
            if dist <= self.similarity_threshold or self.similarity_threshold == 0:
                results.append({
                    "text": self.chunks[idx]["text"],
                    "source": self.chunks[idx]["source"],
                    "distance": float(dist)
                })

        logger.debug(f"RAG retrieved {len(results)} chunks for query: '{text}'", extra={"extra_info": {"query": text, "results": results}})
        return results
