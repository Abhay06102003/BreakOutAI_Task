from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import os
from py2neo import Graph
load_dotenv()
from llama_index.core import KnowledgeGraphIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from IPython.display import Markdown, display  
import pickle     

class KG():
    def __init__(self, Web_path):
        """_summary_

        Args:
            Web_path (Path of Folder): Load PDF stored in this path.
        """
        self.path = Web_path
        llm = Groq(model="llama-3.1-8b-instant", api_key= os.getenv("Groq_key"))
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 512
        self.graph_store = Neo4jGraphStore(
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            url=os.getenv("NEO4J_URI"),
            database="neo4j",
        )
        self.storage_context = StorageContext.from_defaults(graph_store=self.graph_store)
        self.index = self.build_knowledge_graph()

    def build_knowledge_graph(self):
        """_summary_

        Returns:
            KnowledgeGraphIndex: Knowledge Graph Index built from the documents.
        """
        documents = SimpleDirectoryReader(
            self.path,
        ).load_data()
        index = KnowledgeGraphIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            max_triplets_per_chunk=2,
            show_progress=True
        )
        return index

    def query(self, question):
        """_summary_

        Args:
            question (str): Question to be asked.

        Returns:
            Response: Response to the question.
        """
        query_engine = self.index.as_query_engine(
            include_text=True, response_mode="tree_summarize"
        )
        response = query_engine.query(question)
        return response

if __name__ == "__main__":
    # Load the PDFs
    path = "data"
    kg = KG(path)

    # Query the knowledge graph
    questions = [
        "What is Microsoft's current net worth?",
        "What was Microsoft's annual revenue in the last fiscal year?",
        "How much profit did Microsoft make in 2023?"    ]
    for question in questions:
        response = kg.query(question)
        print(response)