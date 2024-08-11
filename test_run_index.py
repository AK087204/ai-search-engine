import requests
from xml.etree import ElementTree as ET
from datetime import datetime
import chromadb
from indexer import Indexer

# Initialize ChromaDB client and Indexer
client = chromadb.PersistentClient(path="db_test/")
chroma_collection_name = 'test2'
indexer = Indexer(client, chroma_collection_name)

# URL của sitemap chính
sitemap_index_url = 'https://link.springer.com/sitemap-index.xml'

# Truy xuất nội dung của sitemap chính
response = requests.get(sitemap_index_url)
sitemap_index_content = response.content

# Parse XML để lấy các URL của sitemap nhỏ
root = ET.fromstring(sitemap_index_content)
namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}  # Định nghĩa namespace

# Ngày giới hạn là năm 2019
date_limit = datetime(2024, 8, 8)

for sitemap in root.findall('ns:sitemap', namespaces):
    loc = sitemap.find('ns:loc', namespaces).text  # Lấy URL của từng sitemap nhỏ
    lastmod = sitemap.find('ns:lastmod', namespaces).text  # Lấy ngày lastmod
    
    # Chuyển lastmod thành đối tượng datetime
    lastmod_date = datetime.fromisoformat(lastmod)
    
    # Chỉ index những sitemap có lastmod từ 2024 trở đi
    if lastmod_date >= date_limit:
        print(f"Indexing website: {loc} with lastmod: {lastmod}")
        indexer.index_website(loc)