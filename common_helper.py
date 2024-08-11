
# import openai

# def create_embedding(text):
#     embedding_model = 'text-embedding-ada-002'
#     embedding = openai.Embedding.create(input = [text], model=embedding_model)['data'][0]['embedding']

#     return embedding


from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    # Generate the embedding for the given text using CPU
    embedding = model.encode(text)
    return embedding

