import os
import json
from openai import OpenAI
from semantic_retrieval import retrieve_semantic_context
from post_history import load_post_history

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def load_company_name(company_file_path):

    with open(company_file_path, "r", encoding="utf-8") as file:
        company_info = json.load(file)

    return company_info["company"]["name"]

def suggest_linkedin_topics(
    company_file_path,
    language
):

    company_name = load_company_name(company_file_path)
    company_rules = load_company_rules(company_file_path)
    global_rules = load_global_rules()

    with open(company_file_path, "r", encoding="utf-8") as file:
        company_knowledge = json.load(file)

    post_history = load_post_history(
    company_file_path
    )

    previous_topics = []

    for post in post_history:
        previous_topics.append({
            "topic": post.get("topic", ""),
            "angle": post.get("angle", "")
        })    

    instructions = f"""
You are a LinkedIn content strategist.

Suggest 5 useful LinkedIn post topics for this company.

Company:
{company_name}

Company knowledge:
{json.dumps(company_knowledge, ensure_ascii=False, indent=2)}


Company rules:
{json.dumps(company_rules, ensure_ascii=False, indent=2)}


Previously approved topics and angles:
{json.dumps(previous_topics, ensure_ascii=False, indent=2)}

Do not repeat or slightly rephrase these previous topics or angles.
Suggest genuinely new content ideas.

Language:
{language}

For each suggestion, provide:
- topic: the main subject of the post
- angle: the specific perspective or approach for that topic

The suggestions should be meaningfully different from each other.
Do not invent company facts.
Keep each topic and angle concise.

Return only valid JSON in this exact format:

{{
  "topics": [
    {{
      "topic": "...",
      "angle": "..."
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": instructions
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    return json.loads(result.strip())


def load_company_rules(company_file_path):

    company_folder = os.path.dirname(company_file_path)

    rules_file = os.path.join(
        company_folder,
        "rules.json"
    )

    if not os.path.exists(rules_file):
        return None

    with open(rules_file, "r", encoding="utf-8") as file:
        return json.load(file)

def load_global_rules():

    global_rules_file = os.path.join(
        "config",
        "global_rules.json"
    )

    with open(global_rules_file, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_linkedin_post(
    topic,
    language,
    company_file_path
):

    company_name = load_company_name(company_file_path)
    company_rules = load_company_rules(company_file_path)
    global_rules = load_global_rules()

    context = retrieve_semantic_context(
        topic,
        company_file_path
    )

    company_rules_text = json.dumps(
        company_rules or {},
        ensure_ascii=False,
        indent=2
    )

    global_rules_text = json.dumps(
        global_rules,
        ensure_ascii=False,
        indent=2
    )

    instructions = f"""
You are a LinkedIn content agent for {company_name}.

Create a LinkedIn post about the requested topic.

Use only the provided company context for company-specific facts.

Follow all global rules and company-specific rules provided below.

Global rules:
{global_rules_text}

Company-specific rules:
{company_rules_text}

Task-specific rules:
- Focus clearly on the requested topic.
- Provide useful or interesting value to the reader.
- Connect the topic to the company or its products only when relevant.
- Do not force a company connection when it does not naturally fit.
- Do not invent company facts, capabilities, customers, products, statistics, or partnerships.

Return valid JSON with exactly these fields:

{{
  "hook": "The opening hook",
  "post": "The main LinkedIn post content",
  "cta": "The call to action",
  "hashtags": ["#Example1", "#Example2"]
}}

Return only JSON.
"""

    user_input = f"""
Topic:
{topic}

Language:
{language}

Relevant company context:
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
        raise ValueError(
            "The AI returned an invalid JSON response."
        )

    required_fields = [
        "hook",
        "post",
        "cta",
        "hashtags"
    ]

    for field in required_fields:
        if field not in post_data:
            raise ValueError(
                f"Missing field in AI response: {field}"
            )

    return post_data


def revise_linkedin_post(
    current_post,
    feedback,
    company_file_path
):
    
    company_name = load_company_name(company_file_path)
    company_rules = load_company_rules(company_file_path)
    global_rules = load_global_rules()

    company_rules_text = json.dumps(
    company_rules,
    ensure_ascii=False,
    indent=2
    )

    global_rules_text = json.dumps(
        global_rules,
        ensure_ascii=False,
        indent=2
    )


    instructions = f"""
    You are a LinkedIn content editor for {company_name}.

    Revise the existing LinkedIn post according to the user's feedback.

    Follow all global rules and company-specific rules provided in the prompt.

    Revision rules:
    - Follow the user's feedback carefully.
    - Keep parts of the original post that do not need changing.
    - Preserve the original meaning unless the user asks to change it.

    Return the revised post as valid JSON with exactly these fields:

    {{
    "hook": "The revised opening hook",
    "post": "The revised LinkedIn post content",
    "cta": "The revised call to action",
    "hashtags": ["#Example1", "#Example2"]
    }}

    Return only JSON.
    """

    prompt = f"""
    CURRENT POST:

    {json.dumps(current_post, ensure_ascii=False)}

    USER FEEDBACK:

    {feedback}

    Global rules:
    {global_rules_text}

    Company-specific rules:
    {company_rules_text}
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=instructions,
        input=prompt
    )

   
    output_text = response.output_text

    if not output_text or not output_text.strip():
        raise ValueError(
            "The AI returned an empty response. Please try revising the post again."
        )

    try:
        revised_post = json.loads(output_text)

    except json.JSONDecodeError:
        raise ValueError(
            f"The AI returned invalid JSON:\n{output_text}"
        )

    return revised_post