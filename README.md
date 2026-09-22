# AI LinkedIn Content Agent

An AI-powered, multi-company LinkedIn content agent built with Python, Streamlit, the OpenAI API, semantic retrieval, structured outputs, tool calling, and automated content evaluation.

The project explores how an LLM can move beyond simple text generation and operate as part of a controlled **agentic workflow** with company-specific knowledge, tools, evaluation, memory, and human approval.

## What the Agent Does

The agent generates LinkedIn content using company-specific knowledge and rules rather than relying only on a generic prompt.

Current workflow:

```text
User Request
    ↓
AI Agent
    ↓
Retrieve Relevant Company Knowledge
    ↓
Check Topic Similarity
    ↓
Generate Structured LinkedIn Post
    ↓
Evaluate
 ┌───────┼────────┐
Similarity  Rules  Grounding
 └───────┼────────┘
    ↓
Human Review
   ↙     ↘
Revise   Approve
           ↓
     Save to History
```

## Key Features

### Multi-Company Architecture

Each company can have its own:

* structured company knowledge
* content rules
* semantic embeddings
* approved post history

This allows the same agent architecture to support different companies without hardcoding the workflow for one organization.

### AI-Assisted Company Onboarding

Users can provide raw company information.

The application converts it into structured company knowledge using the OpenAI API and Pydantic schemas.

The knowledge is then stored in a company-specific directory and embeddings are generated for semantic retrieval.

### Structured Outputs

Pydantic schemas are used for predictable and validated AI outputs, including:

* company knowledge
* topic suggestions
* LinkedIn posts

This reduces dependence on manually parsing free-form model responses.

### Semantic Retrieval

The application uses embeddings and cosine similarity to retrieve the company information most relevant to the requested topic.

Instead of providing all available company information to the model, the system selects relevant context before content generation.

### Tool Calling

The agent can call application tools such as:

* retrieving relevant company context
* checking topic and angle similarity
* generating a structured LinkedIn post

Python executes the requested tools and returns the results to the model.

### Agent Loop

The agent can perform multiple tool-calling iterations before completing a task.

A typical sequence may be:

```text
Retrieve company context
        ↓
Check topic similarity
        ↓
Generate LinkedIn post
        ↓
Return result for human review
```

A maximum iteration limit is used as a safety guard.

### Semantic Duplicate Detection

New topics, angles, and generated drafts are compared with previously approved content using embeddings and cosine similarity.

This helps reduce repetitive LinkedIn content.

### Rule Compliance Evaluation

Generated posts are evaluated against company-specific content rules.

The evaluator reports whether the post passes the rules and identifies potential violations.

### Grounding Evaluation

Company-specific claims are checked against retrieved company knowledge.

Unsupported claims are flagged before approval, helping reduce hallucinated company information.

### Feedback and Revision

Users can provide feedback on a generated post and request a revision.

The revised post is evaluated again before approval.

### Human-in-the-Loop

The system does not automatically approve generated content.

The user remains responsible for reviewing, revising, and approving posts before they are saved or used.

### Post History

Approved posts are stored in company-specific history.

Their embeddings can later be used for semantic similarity checks against future topics and drafts.

### Agent Workflow Trace

The Streamlit interface displays the tools used during the agent workflow, making the agent's actions easier to inspect.

Example:

```text
✓ Retrieved relevant company knowledge
✓ Checked topic similarity
✓ Generated structured LinkedIn post
⏸ Waiting for human review
```

## Architecture

```text
                    ┌─────────────────────┐
                    │    Streamlit UI     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      AI Agent       │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      Semantic Retrieval   Similarity Check   Post Generation
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                         Evaluations
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
             Rules         Grounding      Similarity
                └──────────────┼──────────────┘
                               ▼
                         Human Review
                               │
                        Revise / Approve
                               │
                               ▼
                         Post History
```

## Technology Stack

* Python
* Streamlit
* OpenAI API
* OpenAI Responses API
* Pydantic
* Structured Outputs
* Function / Tool Calling
* OpenAI Embeddings
* Cosine Similarity
* JSON-based company knowledge and rules
* Git / GitHub

## Project Structure

```text
linkedin-content-agent/
│
├── app.py
├── content_agent.py
├── company_knowledge.py
├── semantic_retrieval.py
├── post_history.py
├── evaluation.py
│
├── config/
│   └── global_rules.json
│
└── data/
    └── <company_name>/
        ├── knowledge.json
        ├── rules.json
        ├── embeddings.json
        └── post_history.json
```

Generated embedding and post-history files can remain local/runtime data rather than being committed to the repository.

## Running the Project

Install the required Python packages and configure the OpenAI API key as an environment variable.

Example with PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
```

Run the Streamlit application:

```powershell
py -3.10 -m streamlit run app.py
```

The API key should never be committed to GitHub.

## Reliability and Safety

The current architecture includes several safeguards:

* company-specific rules
* structured and validated outputs
* semantic duplicate detection
* grounding evaluation
* rule compliance evaluation
* human approval before content is accepted
* maximum agent iteration limit
* separation of company knowledge and behavioral rules

## Roadmap

Planned development includes:

* automatic self-correction when evaluations fail
* stronger content-quality evaluation
* learning from approved content and performance
* AI image generation
* brand-aware visual generation
* publishing and scheduling integrations
* analytics feedback
* MCP integrations
* Docker containerization
* cloud deployment
* CI/CD
* logging and observability
* systematic LLM and agent evaluation

More advanced orchestration or multi-agent architectures may be explored if the workflow complexity justifies them.

## Project Status

**Active development**

The current version demonstrates an end-to-end human-in-the-loop agentic workflow:

**Company Knowledge → Retrieval → Tool Calling → Generation → Evaluation → Revision → Human Approval → History**

The project is being developed as a practical AI engineering portfolio project and as a foundation for a more production-ready content automation system.
