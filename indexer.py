import requests
from bs4 import BeautifulSoup
from common_helper import create_embedding
import numpy as np
from dotenv import load_dotenv
import os
load_dotenv()

JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")

class Indexer:

    def __init__(self, chroma_client, chroma_collection_name):
        self.chroma_client = chroma_client
        self.chroma_collection_name = chroma_collection_name
        self.collection = self.chroma_client.get_or_create_collection(chroma_collection_name)

    def get_html_sitemap(self, url):
        response = requests.get(url)
  
        soup = BeautifulSoup(response.content, "xml")
  
        # Find the body element and extract its inner text
        links = []
  
        locations = soup.find_all("loc")
        for location in locations:
            url = location.get_text()
            links.append(url)
  
        return links
  

    #We can use LLM to clean after use jina ai data, but this way take money
    def get_html_body_content(self, url, max_token=256):
        
        headers = {
            'Authorization': 'Bearer {JINAAI_API_KEY}'
        }

        response = requests.get(url, headers)
        
        # Get the content of the response as a string
        response_text = response.text

        # Find the index of the word "References"
        references_index = response_text.find("References\n----------")
        
        # Extract content before "References"
        if references_index != -1:
            content_before_references = response_text[:references_index]
        else:
            content_before_references = response_text
        
        # Chuyển đổi văn bản thành danh sách các token
        tokens = content_before_references.split()
        
        # Nếu số lượng token vượt quá max_token, cắt bớt văn bản
        if len(tokens) > max_token:
            content_before_references = " ".join(tokens[:max_token])
        
        return content_before_references

  
    def index_website(self, website_url):
        limit = 5
        links = self.get_html_sitemap(website_url)
        for link in links[:limit]:
            print(link)
            try:
                content = self.get_html_body_content(link)
                self.add_html_to_vectordb(content, link)
            except:
                print("unable to process: " + link)
  
    def add_html_to_vectordb(self, content, path):
        embedding = create_embedding(content)

        self.insert_embedding(embedding, content, path)
  
    def insert_embedding(self, embedding, text, path):
        try:
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            # Insert the embedding into ChromaDB
            self.collection.add(
                ids=path,
                embeddings=embedding,
                documents=text,
            )
        except Exception as e:
            print(f"Failed to insert embedding. Error: {e}")
