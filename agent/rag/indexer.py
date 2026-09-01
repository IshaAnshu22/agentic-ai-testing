import os
import faiss
import pickle
import yaml
from sentence_transformers import SentenceTransformer
from utils.logger import setup_logger
from rag.parsers import get_parser

logger = setup_logger("indexer")

class RAGIndexer:
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
        self.docs_dir = os.path.join(project_root, self.config["docs_dir"])
        self.index_path = os.path.join(project_root, self.config["index_path"])
        
        # We store chunks side by side with the index
        self.chunks_path = os.path.join(project_root, self.config["chunks_path"])
        
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        self.chunk_size = self.config["chunk_size"]
        self.chunk_overlap = self.config["chunk_overlap"]

    def _chunk_text(self, text, source):
        chunks = []
        words = text.split()
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            if not chunk_words:
                break
            chunk_text = " ".join(chunk_words)
            chunks.append({"text": chunk_text, "source": source})
        return chunks

    def index_documents(self):
        all_chunks = []
        
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir, exist_ok=True)
            logger.warning(f"Docs directory created at {self.docs_dir}. Please add .txt files.")
            return

        for filename in os.listdir(self.docs_dir):
            file_path = os.path.join(self.docs_dir, filename)
            if os.path.isfile(file_path):
                parser = get_parser(file_path)
                content = parser.parse(file_path)
                if content:
                    chunks = self._chunk_text(content, filename)
                    all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning("No chunks to index. Is the data directory empty?")
            return

        texts = [c["text"] for c in all_chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(index, self.index_path)
        with open(self.chunks_path, "wb") as f:
            pickle.dump(all_chunks, f)

        logger.info(f"Successfully indexed {len(all_chunks)} chunks to {self.index_path}")

if __name__ == "__main__":
    indexer = RAGIndexer()
    indexer.index_documents()
