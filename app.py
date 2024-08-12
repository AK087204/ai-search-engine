import streamlit as st
from search_engine import SearchEngine
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="db/")

# ChromaDB collection name (should match the one used during indexing)
chroma_collection_name = 'database'

# Initialize search engine
search_engine = SearchEngine(chroma_client=client, chroma_collection_name=chroma_collection_name)

# Streamlit UI
st.title("Scientific Document Search Engine")

# Input query from user
user_query = st.text_input("Enter your search query:", "")

# Execute search when the user submits a query
if st.button("Search"):
    if user_query:
        result = search_engine.similarity_search(user_query)
        
        # Display results
        st.write("### Search Results:")
        if result and result.get('summaries'):
            for i, (summary, source) in enumerate(zip(result['summaries'], result['sources'])):
                st.write(f"**{i+1}. Title:** {summary['title']}")
                st.write(f"**Summary:** {summary['summary']}")
                st.write(f"**Source:** [Link]({source})\n")
        else:
            st.write("No results found.")
    else:
        st.write("Please enter a search query.")
