import os
import json
from openai import OpenAI
import re
from pydantic import BaseModel

class CompanyInfo(BaseModel):
    name: str
    website: str
    industry: str
    description: str


class ContactInformation(BaseModel):
    email: str
    phone: str
    address: str


class CompanyKnowledge(BaseModel):
    company: CompanyInfo
    products: list[str]
    services: list[str]
    technologies: list[str]
    target_audience: list[str]
    key_messages: list[str]
    contact_information: ContactInformation

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


# Converts raw company information into structured company knowledge
def structure_company_information(company_name, raw_text):    

    instructions = """
You are a company knowledge extraction assistant.

Analyze the company information provided by the user and convert it into
structured company knowledge.

The company name is provided separately by the user.
Use exactly that company name and do not infer or change it.

Important rules:
- Use only information provided by the user.
- Do not invent missing facts.
- Do not guess customers, products, statistics, technologies, or partnerships.
- If information is not available, use an empty list or empty string.
- Preserve important details from the source text.


"""

    
    # response = client.responses.create(
    # model="gpt-4.1-mini",
    # instructions=instructions,
    # # input=raw_text
    # input=f"""
    # Company name: {company_name}

    # Company information:
    # {raw_text}
    # """    
    # )

    # cleaned_output = response.output_text.strip()

    # if cleaned_output.startswith("```json"):
    #     cleaned_output = cleaned_output[7:]

    # if cleaned_output.endswith("```"):
    #     cleaned_output = cleaned_output[:-3]

    # cleaned_output = cleaned_output.strip()

    # structured_data = json.loads(cleaned_output)

    # return structured_data
    response = client.responses.parse(
        model="gpt-4.1-mini",
        instructions=instructions,
        input=f"""
    Company name: {company_name}

    Company information:
    {raw_text}
    """,
        text_format=CompanyKnowledge
    )

    structured_data = response.output_parsed

    return structured_data.model_dump()    

def save_company_knowledge(company_data):

    company_name = company_data["company"]["name"]

    folder_name = company_name.lower()
    folder_name = re.sub(r"[^a-z0-9]+", "_", folder_name)
    folder_name = folder_name.strip("_")

    company_folder = os.path.join("data", folder_name)

    os.makedirs(company_folder, exist_ok=True)

    file_path = os.path.join(
        company_folder,
        "knowledge.json"
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            company_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return file_path

def load_company_knowledge(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def update_company_knowledge(existing_data, new_information):

    instructions = """
You are a company knowledge update assistant.

You will receive:
1. Existing structured company knowledge
2. New company information

Update the existing knowledge using only the new information provided.

Rules:
- Preserve existing information unless the new information clearly updates or replaces it.
- Add genuinely new information to the appropriate section.
- Do not invent facts.
- Do not remove existing facts without a clear reason.
- Avoid duplicate items.
- Keep the same JSON structure as the existing company knowledge.

Return only valid JSON.
"""

    prompt = f"""
EXISTING COMPANY KNOWLEDGE:

{json.dumps(existing_data, ensure_ascii=False)}

NEW COMPANY INFORMATION:

{new_information}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=instructions,
        input=prompt
    )

    cleaned_output = response.output_text.strip()

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output[7:]

    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output[:-3]

    cleaned_output = cleaned_output.strip()

    updated_data = json.loads(cleaned_output)

    return updated_data

def get_available_companies():

    data_folder = "data"

    if not os.path.exists(data_folder):
        return []

    companies = []

    for folder_name in os.listdir(data_folder):

        company_folder = os.path.join(data_folder, folder_name)
        knowledge_file = os.path.join(
            company_folder,
            "knowledge.json"
        )

        if os.path.isdir(company_folder) and os.path.exists(knowledge_file):

            company_data = load_company_knowledge(
                knowledge_file
            )

            company_name = company_data["company"]["name"]

            companies.append({
                "name": company_name,
                "folder": folder_name,
                "file_path": knowledge_file
            })

    return companies