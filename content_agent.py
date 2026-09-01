import os
import json
from openai import OpenAI
#from retrieval import retrieve_company_info
from semantic_retrieval import retrieve_semantic_context

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def generate_linkedin_post(
    topic,
    post_type,
    language,
    tone,
    post_length
):
    #context = retrieve_company_info(topic)
    context = retrieve_semantic_context(topic)
    if post_type == "Product post":
      post_guidance = """
    Focus on the product, its purpose and its relevant capabilities.
    Explain its value clearly without sounding overly promotional.
    End with a CTA related to learning more about the product.
    """

    elif post_type == "Educational post":
        post_guidance = """
    Focus primarily on teaching the reader something useful.
    Use the company or product only when it naturally supports the topic.
    End with a thought-provoking question.
    """

    elif post_type == "Industry insight":
        post_guidance = """
    Focus on an important industry challenge, trend or observation.
    Provide a useful perspective based on the available context.
    Avoid turning the post into a product advertisement.
    End with a question that encourages discussion.
    """

    elif post_type == "Technical post":
        post_guidance = """
    Focus on the technical concept and explain why it matters.
    Keep the explanation understandable for a professional LinkedIn audience.
    Connect it to the company's technical expertise only when relevant.
    End with a practical or technical question.
    """

    else:
        post_guidance = """
    Create a clear and professional LinkedIn post based on the topic.
    """

    instructions = """
You are a LinkedIn content agent for Vahvero Symbiosis Oy.

Create professional LinkedIn content using only the provided company context.

Rules:
- Do not invent company facts, product features, customers, partnerships or statistics.
- Do not make medical claims.
- Keep the tone professional, clear, human and concise.
- Connect the topic to Vahvero or Raiqu only when relevant.
- Avoid overly promotional language.
- Use a small number of relevant hashtags.

Return the output as valid JSON with exactly these fields:

{
  "hook": "The opening hook",
  "post": "The main LinkedIn post content",
  "cta": "The call to action",
  "hashtags": ["#Example1", "#Example2"]
}

Return only JSON. Do not add any text before or after it.
"""

    user_input = f"""
    Topic:
    {topic}

    Post type:
    {post_type}

    Language:
    {language}

    Tone:
    {tone}

    Post length:
    {post_length}

    Post guidance:
    {post_guidance}

    Company context:
    {context}
    """

    response = client.responses.create(
        model="gpt-5.6",
        instructions=instructions,
        input=user_input
    )

    
    try:
         post_data = json.loads(response.output_text)

    except json.JSONDecodeError:
        raise ValueError("The AI returned an invalid JSON response.")

    required_fields = ["hook", "post", "cta", "hashtags"]

    for field in required_fields:
        if field not in post_data:
            raise ValueError(f"Missing field in AI response: {field}")

    return post_data

if __name__ == "__main__":
    topic = input("Post topic: ")

    print("\nChoose post type:")
    print("1. Product post")
    print("2. Educational post")
    print("3. Industry insight")
    print("4. Technical post")

    choice = input("Enter a number: ")

    if choice == "1":
        post_type = "Product post"
    elif choice == "2":
        post_type = "Educational post"
    elif choice == "3":
        post_type = "Industry insight"
    elif choice == "4":
        post_type = "Technical post"
    else:
        post_type = "General LinkedIn post"

    post = generate_linkedin_post(topic, post_type)

    print("\nGenerated LinkedIn post:\n")
    print(post)