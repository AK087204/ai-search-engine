from search_engine import SearchEngine
import chromadb
from dotenv import load_dotenv
load_dotenv()
# Initialize ChromaDB client
client = chromadb.PersistentClient(path="db/")

# ChromaDB collection name (should match the one used during indexing)
chroma_collection_name = 'test'

search_engine = SearchEngine(chroma_client=client, chroma_collection_name=chroma_collection_name)
test_query=""" Advancement in Lung Cancer """
result = search_engine.similarity_search(test_query)
print(result)
