import chromadb
from indexer import Indexer
import requests
from bs4 import BeautifulSoup
from common_helper import create_embedding
from queries import queries

def get_arxiv_metadata(query, max_results=5):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',  # or 'lastUpdatedDate', 'submittedDate'
        'sortOrder': 'descending'
    }

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'xml')

    entries = soup.find_all('entry')
    metadata_list = []

    for entry in entries:
        title = entry.title.text.strip()
        authors = ', '.join(author.find('name').text for author in entry.find_all('author'))
        abstract = entry.summary.text.strip()
        link = entry.id.text.strip()


        metadata = {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'link': link
        }
        metadata_list.append(metadata)

    return metadata_list

def get_arxiv_allmetadata(queries, max_result=5):
    all_metadata = []
    seen_titles = set()

    for query in queries:
        metadata_list = get_arxiv_metadata(query, max_results=max_result)
        for metadata in metadata_list:
            if metadata['title'] not in seen_titles:
                seen_titles.add(metadata['title'])
                all_metadata.append(metadata)
    return all_metadata


# Initialize ChromaDB client and Indexer
client = chromadb.PersistentClient(path="db/")
chroma_collection_name = 'database'
indexer = Indexer(client, chroma_collection_name)

max_result = 10

all_metadata = get_arxiv_allmetadata(queries, max_result)

for doc in all_metadata:
    title_abstract = doc['title'] + " " + doc['abstract']
    embedding = create_embedding(title_abstract)
    indexer.insert_embedding(embedding, title_abstract, doc['link'])
    print(f"Processing {doc['title']}: {doc['link']}")



