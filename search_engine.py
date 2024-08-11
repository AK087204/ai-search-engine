from common_helper import create_embedding
import openai
from dotenv import load_dotenv
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

class SearchEngine:
    def __init__(self, chroma_client, chroma_collection_name):
        self.chroma_client = chroma_client
        self.chroma_collection_name = chroma_collection_name
        self.collection = self.chroma_client.get_or_create_collection(chroma_collection_name)

    def query_chromadb(self, embedding):
        result_count = 10  # Lấy nhiều hơn số lượng kết quả mong muốn ban đầu để có thể lọc
        similarity_threshold = 0.9  # Ngưỡng để loại bỏ kết quả quá giống nhau

        results = self.collection.query(
            query_embeddings=embedding.tolist(),
            n_results=result_count
        )
        actual_result_count = min(len(results["documents"][0]), result_count)
        result_embeddings = []
        for i in range(actual_result_count):
            # Tính toán lại embedding từ document nếu cần
            result_embedding = create_embedding(results["documents"][0][i])
            result_embeddings.append(result_embedding)
            
        list_of_knowledge_base = []
        sources = []

        for i in range(actual_result_count):
            current_embedding = np.array(result_embeddings[i]).reshape(1, -1)

            if not list_of_knowledge_base:  # Nếu danh sách đang trống, thêm kết quả đầu tiên
                list_of_knowledge_base.append(results["documents"][0][i])
                sources.append(results["ids"][0][i])
            else:
                # Tính cosine similarity với các kết quả đã chọn
                similarities = cosine_similarity(current_embedding, np.array([np.array(e) for e in result_embeddings[:len(list_of_knowledge_base)]]))

                # Nếu tất cả độ tương đồng đều nhỏ hơn ngưỡng, thêm kết quả vào danh sách
                if np.all(similarities < similarity_threshold):
                    list_of_knowledge_base.append(results["documents"][0][i])
                    sources.append(results["ids"][0][i])

            # Nếu đủ kết quả, ngừng tìm kiếm
            if len(list_of_knowledge_base) >= 3:
                break

        return {
            'list_of_knowledge_base': list_of_knowledge_base,
            'sources': sources
        }

    def query_vector_db(self, embedding):
        return self.query_chromadb(embedding)


    # Thien Long task=))
    def ask_chatgpt(self, knowledge_base, user_query):
        system_content = """You are an AI coding assistant designed to help users with their programming needs based on the Knowledge Base provided.
        If you don't know the answer, say that you don't know the answer. You will only answer questions related to computer science; any other questions, you should say that it's out of your responsibilities.
        Only answer questions using data from the knowledge base and nothing else.
        """

        user_content = f"""
            Knowledge Base:
            ---
            {knowledge_base}
            ---
            User Query: {user_query}
            Answer:
        """
        system_message = {"role": "system", "content": system_content}
        user_message = {"role": "user", "content": user_content}

        chatgpt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[system_message, user_message])
        return chatgpt_response.choices[0].message.content

    def similarity_search(self, user_query):
        embedding = create_embedding(user_query)
        result = self.query_vector_db(embedding)
        
        summaries = []
        
        for content in result['list_of_knowledge_base']:
            # Nếu content là list, nối các phần tử thành một chuỗi
            if isinstance(content, list):
                content = "\n".join(content)
            
            # Create the messages list
            messages = [
                {"role": "system", "content": "You are a helpful assistant skilled in extracting titles and generating concise summaries of scientific documents."},
                {"role": "user", "content": f"{content}\nPlease extract the title and summarize this scientific document in 1 sentence."}
            ]
            chatgpt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            response = chatgpt_response['choices'][0]['message']['content']
            
            # Split the response into title and summary
            title_and_summary = response.split("\n", 1)
            title = title_and_summary[0].strip()  # Title is the first line
            summary = title_and_summary[1].strip() if len(title_and_summary) > 1 else ""
            title = title.replace("Title: ", "")
            summary = summary.replace("Summary: ", "")
            summaries.append({
                'title': title,
                'summary': summary
            })
        
        return {
            'summaries': summaries,
            'sources': result['sources'][0] if isinstance(result['sources'][0], list) else result['sources']
        }



    def search(self, user_query):
        embedding = create_embedding(user_query)
        result = self.query_vector_db(embedding)

       
        print(result)

        knowledge_base = result['list_of_knowledge_base']
        response = self.ask_chatgpt(knowledge_base, user_query)

        return {
            'sources': result['sources'],
            'response': response
        }
