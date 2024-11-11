from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import os
from py2neo import Graph
from llama_index.core import KnowledgeGraphIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from IPython.display import Markdown, display
import pickle

class KG:
    def __init__(self, Web_path):
        """Initialize Knowledge Graph with the given path.

        Args:
            Web_path (str): Path of folder containing documents.
        """
        self.path = Web_path
        llm = Groq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("Groq_key"),
            temperature=0.1
        )
        embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            cache_folder="embedding_cache"
        )
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 2048
        Settings.embed_batch_size = 32
        
        self.graph_store = Neo4jGraphStore(
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            url=os.getenv("NEO4J_URI"),
            database="neo4j",
        )
        self.storage_context = StorageContext.from_defaults(graph_store=self.graph_store)
        
        # Add caching for documents
        self.cache_file = os.path.join(Web_path, "kg_cache.pkl")
        
        self.index = self.build_knowledge_graph()

    def build_knowledge_graph(self):
        """Build Knowledge Graph from documents.

        Returns:
            KnowledgeGraphIndex: Knowledge Graph Index built from the documents.
        """
        # Try to load from cache first
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
                
        documents = SimpleDirectoryReader(self.path).load_data()
        index = KnowledgeGraphIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            max_triplets_per_chunk=8,
            show_progress=True,
            include_embeddings=True,
        )
        
        # Cache the index
        with open(self.cache_file, 'wb') as f:
            pickle.dump(index, f)
            
        return index

    def query(self, question):
        """Query the knowledge graph and return response text.

        Args:
            question (str): Question to be asked.

        Returns:
            str: Response text
        """
        query_engine = self.index.as_query_engine(
            include_text=True,
            response_mode="tree_summarize",
            streaming=True
        )
        response = query_engine.query(question)
        # Convert streaming response to string for serialization
        return str(response)