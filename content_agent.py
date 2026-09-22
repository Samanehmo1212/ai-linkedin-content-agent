# This module contains the main AI content generation and agent logic.
# It generates and revises LinkedIn posts and coordinates AI tools.
import os
import json
from openai import OpenAI
from semantic_retrieval import retrieve_semantic_context
from post_history import load_post_history, check_topic_similarity
from pydantic import BaseModel

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class LinkedInPost(BaseModel):
    hook: str
    post: str
    cta: str
    hashtags: list[str]
#defining schema for suggest topics
class TopicSuggestion(BaseModel):
    topic: str
    angle: str

class TopicSuggestions(BaseModel):
    topics: list[TopicSuggestion]

retrieve_context_tool = {
    "type": "function",
    "name": "retrieve_company_context",
    "description": "Find relevant company information for a LinkedIn post topic.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The LinkedIn post topic to find relevant company information for."
            }
        },
        "required": ["topic"],
        "additionalProperties": False
    }
}    

check_topic_similarity_tool = {
    "type": "function",
    "name": "check_topic_similarity",
    "description": "Check whether a proposed LinkedIn topic is too similar to previously approved topics.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The proposed LinkedIn post topic."
            },
            "angle": {
                "type": "string",
                "description": "The proposed angle or perspective for the topic."
            }
        },
        "required": ["topic", "angle"],
        "additionalProperties": False
    }
}

generate_post_tool = {
    "type": "function",
    "name": "generate_linkedin_post",
    "description": "Generate a LinkedIn post for an approved topic and angle.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The main topic of the LinkedIn post."
            },
            "angle": {
                "type": "string",
                "description": "The specific perspective or angle for the post."
            },
            "language": {
                "type": "string",
                "description": "The language in which the LinkedIn post should be written."
            }
        },
        "required": ["topic", "angle", "language"],
        "additionalProperties": False
    }
}



def run_agent(
    user_request,
    company_file_path,
    max_iterations=5
):

    generated_post = None
    tool_trace = []
    response = client.responses.create(
        model="gpt-5.6",
        input=user_request,
        #tools=[retrieve_context_tool]
        tools=[
            retrieve_context_tool,
            check_topic_similarity_tool,
            generate_post_tool
        ]              
    )

    iteration = 0
    while True:

        iteration += 1

        if iteration > max_iterations:
            raise RuntimeError(
                "Agent stopped because it reached the maximum number of iterations."
            )

        print("Agent iteration:", iteration)
    
        tool_calls = []

        for item in response.output:
            if item.type == "function_call":
                tool_calls.append(item)


        
        if not tool_calls:

            if generated_post is not None:
                return {
                    "status": "awaiting_approval",
                    "post": generated_post,
                    "agent_message": response.output_text,
                    "tool_trace": tool_trace
                }

            return {
                "status": "completed",
                "agent_message": response.output_text,
                "tool_trace": tool_trace

            }        

        tool_outputs = []

        for tool_call in tool_calls:

            print("Selected tool:", tool_call.name)
            # for knowing how many tools agent uses
            tool_trace.append(tool_call.name)

            arguments = json.loads(tool_call.arguments)        
                   
            if tool_call.name == "retrieve_company_context":

                topic = arguments["topic"]

                tool_result = retrieve_semantic_context(
                    topic,
                    company_file_path
                )  

            elif tool_call.name == "check_topic_similarity":

                topic = arguments["topic"]
                angle = arguments["angle"]

                similarity_result = check_topic_similarity(
                    company_file_path,
                    topic,
                    angle
                )

                tool_result = json.dumps(
                    similarity_result,
                    ensure_ascii=False
                )

            elif tool_call.name == "generate_linkedin_post":

                topic = arguments["topic"]
                angle = arguments["angle"]
                language = arguments["language"]

                full_topic = f"{topic}\nAngle: {angle}"

                post_result = generate_linkedin_post(
                    full_topic,
                    language,
                    company_file_path
                )

                generated_post = post_result

                tool_result = json.dumps(
                    post_result,
                    ensure_ascii=False
                )  
            else:
                raise ValueError(
                    f"Unknown tool: {tool_call.name}"
                )                                          

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": tool_result
            })  

            
        response = client.responses.create(
            model="gpt-5.6",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=[
                retrieve_context_tool,
                check_topic_similarity_tool,
                generate_post_tool
            ]           
        ) 

                

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
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=instructions,
        text_format=TopicSuggestions
    )

    topic_suggestions = response.output_parsed

    return topic_suggestions.model_dump()

    

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
    response = client.responses.parse(
        model="gpt-5.6",
        instructions=instructions,
        input=user_input,
        text_format=LinkedInPost  #for adding schema
    )

    post_data = response.output_parsed
    
    return post_data.model_dump()
   


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

    
    response = client.responses.parse(
    model="gpt-4.1-mini",
    instructions=instructions,
    input=prompt,
    text_format=LinkedInPost
    )

    revised_post = response.output_parsed

    return revised_post.model_dump()


