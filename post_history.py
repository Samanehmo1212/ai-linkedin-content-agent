# This module manages approved post history and checks topic
# and post similarity using embeddings.
import os
import json
from openai import OpenAI
from semantic_retrieval import cosine_similarity

client = OpenAI()

def get_text_embedding(text):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding

def check_topic_similarity(
    company_file_path,
    new_topic,
    new_angle
):

    history = load_post_history(company_file_path)

    if not history:
        return {
            "similarity": 0.0,
            "matched_topic": "",
            "matched_angle": ""
        }

    new_text = f"{new_topic} — {new_angle}"
    new_embedding = get_text_embedding(new_text)

    best_similarity = 0.0
    best_topic = ""
    best_angle = ""

    for post in history:

        old_embedding = post.get(
            "topic_angle_embedding"
        )

        if not old_embedding:
            continue

        similarity = cosine_similarity(
            new_embedding,
            old_embedding
        )

        if similarity > best_similarity:
            best_similarity = similarity
            best_topic = post.get("topic", "")
            best_angle = post.get("angle", "")

    return {
        "similarity": best_similarity,
        "matched_topic": best_topic,
        "matched_angle": best_angle
    }

def check_post_similarity(
    company_file_path,
    post_data
):

    history = load_post_history(
        company_file_path
    )

    if not history:
        return {
            "similarity": 0.0,
            "matched_post": ""
        }

    full_post_text = (
        f'{post_data.get("hook", "")}\n'
        f'{post_data.get("post", "")}\n'
        f'{post_data.get("cta", "")}'
    )

    new_embedding = get_text_embedding(
        full_post_text
    )

    best_similarity = 0.0
    best_post = ""

    for old_post in history:

        old_embedding = old_post.get(
            "post_embedding"
        )

        if not old_embedding:
            continue

        similarity = cosine_similarity(
            new_embedding,
            old_embedding
        )

        if similarity > best_similarity:
            best_similarity = similarity
            best_post = old_post.get("post", "")

    return {
        "similarity": best_similarity,
        "matched_post": best_post
    }

def get_post_history_file(company_file_path):

    company_folder = os.path.dirname(company_file_path)

    history_file = os.path.join(
        company_folder,
        "post_history.json"
    )

    return history_file
def load_post_history(company_file_path):

    history_file = get_post_history_file(
        company_file_path
    )

    if not os.path.exists(history_file):
        return []

    with open(history_file, "r", encoding="utf-8") as file:
        return json.load(file)

def save_approved_post(
    company_file_path,
    topic,
    angle,
    post_data
):

    history = load_post_history(
        company_file_path
    )

    history_file = get_post_history_file(
        company_file_path
    )

    #topic_angle_text = f"{topic} — {angle}"
    #topic_angle_embedding = get_text_embedding(topic_angle_text)

    topic_angle_text = f"{topic} — {angle}"
    topic_angle_embedding = get_text_embedding(topic_angle_text)

    full_post_text = (
        f'{post_data.get("hook", "")}\n'
        f'{post_data.get("post", "")}\n'
        f'{post_data.get("cta", "")}'
    )

    post_embedding = get_text_embedding(full_post_text)

    history.append({
        "topic": topic,
        "angle": angle,
        "topic_angle_embedding": topic_angle_embedding,
        "hook": post_data.get("hook", ""),
        "post": post_data.get("post", ""),
        "cta": post_data.get("cta", ""),
        "hashtags": post_data.get("hashtags", []),
        "post_embedding": post_embedding,
    })

    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=2
        )

    return history_file