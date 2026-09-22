# This module evaluates AI-generated LinkedIn posts.
# It checks whether generated content follows company rules
# and will contain additional quality and safety evaluations.

import json
from pydantic import BaseModel
from openai import OpenAI
from content_agent import load_company_rules


client = OpenAI()

class RuleEvaluation(BaseModel):
    passed: bool
    issues: list[str]

class GroundingEvaluation(BaseModel):
    grounded: bool
    unsupported_claims: list[str]    

# Evaluates whether a generated LinkedIn post follows the company's content rules
def evaluate_post_rules(post, company_rules):

    post_text = json.dumps(
        post,
        ensure_ascii=False,
        indent=2
    )

    rules_text = json.dumps(
        company_rules,
        ensure_ascii=False,
        indent=2
    )

    instructions = f"""
You are evaluating a generated LinkedIn post.

Check whether the post follows the provided company content rules.

Company rules:
{rules_text}

Generated post:
{post_text}

Evaluate only based on the provided rules.
If all rules are followed, passed should be true and issues should be empty.
If any rule is violated, passed should be false and describe each violation in issues.
"""
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=instructions,
        text_format=RuleEvaluation
    )

    evaluation = response.output_parsed

    return evaluation.model_dump()     

# Checks whether company-specific claims in a generated post are supported by company knowledge
def evaluate_company_grounding(post, company_context):

    post_text = json.dumps(
        post,
        ensure_ascii=False,
        indent=2
    )

    instructions = f"""
You are evaluating whether company-specific claims in a generated LinkedIn post
are supported by the provided company context.

Company context:
{company_context}

Generated post:
{post_text}

Check only claims about the company, its experience, services, customers,
partnerships, capabilities, achievements, statistics, or other company-specific facts.

Do not flag general industry statements.

If every company-specific claim is supported by the provided context,
grounded should be true and unsupported_claims should be empty.

If a company-specific claim is not supported by the provided context,
grounded should be false and include that claim in unsupported_claims.
"""

    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=instructions,
        text_format=GroundingEvaluation
    )

    evaluation = response.output_parsed

    return evaluation.model_dump()       