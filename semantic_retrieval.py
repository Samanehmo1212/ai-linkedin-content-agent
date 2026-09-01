import json
import os
import math

from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
def load_company_info():
    with open("company_info.json", "r", encoding="utf-8") as file:
        return json.load(file)

def cosine_similarity(vector_a, vector_b):
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    return dot_product / (magnitude_a * magnitude_b)
    
def create_chunks(data):
    chunks = []

    def extract(value, path=""):
        if isinstance(value, dict):
            for key, item in value.items():
                new_path = f"{path} {key}".strip()
                extract(item, new_path)

        elif isinstance(value, list):
            for item in value:
                extract(item, path)

        elif isinstance(value, str):
            chunk = f"{path}: {value}".strip()
            chunks.append(chunk)

    extract(data)

    return chunks

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

def semantic_search(question, chunk_data, top_k=5):
    question_embedding = get_embedding(question)

    scored_results = []

    excluded_sections = [
        "website:",
        "contact_email:",
        "future_article_topics",
        "linkedin_strategy",
        "call_to_action",
        "content_creation_process",
        "lead_generation",
        "linkedin_formatting"
    ]

    for item in chunk_data:
        text = item["text"]

        if any(section in text for section in excluded_sections):
            continue

        similarity = cosine_similarity(
            question_embedding,
            item["embedding"]
        )

        scored_results.append(
            (similarity, text)
        )

    scored_results.sort(reverse=True)

    return scored_results[:top_k]

def save_chunk_embeddings(chunks):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    chunk_data = []

    for chunk, item in zip(chunks, response.data):
        chunk_data.append({
            "text": chunk,
            "embedding": item.embedding
        })

    with open("chunk_embeddings.json", "w", encoding="utf-8") as file:
        json.dump(chunk_data, file)

    print("Chunk embeddings saved successfully.")

def load_chunk_embeddings():
    with open("chunk_embeddings.json", "r", encoding="utf-8") as file:
        return json.load(file)

def retrieve_semantic_context(question, top_k=5):
    chunk_data = load_chunk_embeddings()

    results = semantic_search(
        question,
        chunk_data,
        top_k=top_k
    )

    context_parts = []

    for similarity, text in results:
        context_parts.append(text)

    return "\n".join(context_parts)
   
if __name__ == "__main__":
    chunk_data = load_chunk_embeddings()

    question = "What does Vahvero do?"

    results = semantic_search(
        question,
        chunk_data,
        top_k=5
    )

    print("\nTop semantic matches:\n")

    for similarity, chunk in results:
        print(similarity, "-", chunk)