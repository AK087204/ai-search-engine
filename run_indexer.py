import requests
from xml.etree import ElementTree as ET
from datetime import datetime
from chromadb.config import Settings
import chromadb
from indexer import Indexer
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize ChromaDB client and Indexer
client = chromadb.PersistentClient(path="db/")
chroma_collection_name = 'test'
indexer = Indexer(client, chroma_collection_name)

# URL của sitemap chính
sitemap_index_url = 'https://link.springer.com/sitemap-index.xml'

# Truy xuất nội dung của sitemap chính
response = requests.get(sitemap_index_url)
sitemap_index_content = response.content

# Parse XML để lấy các URL của sitemap nhỏ
root = ET.fromstring(sitemap_index_content)
namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}  # Định nghĩa namespace

# Xác định khoảng thời gian giới hạn (từ 2023 đến 2024)
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 8, 8)

# Danh sách các sitemaps cần index
sitemaps_to_index = []

for sitemap in root.findall('ns:sitemap', namespaces):
    loc = sitemap.find('ns:loc', namespaces).text  # Lấy URL của từng sitemap nhỏ
    
    # Kiểm tra nếu thẻ lastmod tồn tại
    lastmod_element = sitemap.find('ns:lastmod', namespaces)
    if lastmod_element is not None:
        lastmod = lastmod_element.text  # Lấy ngày lastmod
        lastmod_date = datetime.fromisoformat(lastmod)
        
        # Chỉ index những sitemap có lastmod trong khoảng từ 2023 đến 2024
        if start_date <= lastmod_date < end_date:
            sitemaps_to_index.append((loc, lastmod))
    else:
        # Nếu không có lastmod, có thể bỏ qua sitemap hoặc xử lý theo cách khác
        print(f"No lastmod found for sitemap: {loc}, skipping.")

# Hàm xử lý index cho từng sitemap
def process_sitemap(loc, lastmod):
    print(f"Indexing website: {loc} with lastmod: {lastmod}")
    indexer.index_website(loc)

# Sử dụng ThreadPoolExecutor để xử lý song song
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_sitemap, loc, lastmod) for loc, lastmod in sitemaps_to_index]
    
    # Chờ các tác vụ hoàn thành
    for future in as_completed(futures):
        future.result()  # Để bắt bất kỳ exception nào nếu có
