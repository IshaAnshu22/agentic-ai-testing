import json
from tools.base import BaseTool
from rag.retriever import RAGRetriever
from utils.logger import setup_logger

logger = setup_logger("rag_tool")

class RAGTool(BaseTool):
    name = "rag_search"
    description = "Searches the local knowledge base for relevant documents. Requires 'query'."

    def __init__(self):
        self.retriever = RAGRetriever()

    def execute(self, **kwargs) -> str:
        query = kwargs.get("query")
        if not query:
            return "Error: Missing 'query' parameter."

        try:
            results = self.retriever.query(query)
            if not results:
                return "No relevant documents found."
            
            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append(f"Source: {r['source']}\nText: {r['text']}")
            
            final_output = "\n\n---\n\n".join(formatted_results)
            logger.debug("RAG tool executed.", extra={"extra_info": {"query": query, "num_results": len(results)}})
            return final_output
        except Exception as e:
            logger.error(f"RAG tool error: {e}")
            return f"Error executing RAG search: {e}"
