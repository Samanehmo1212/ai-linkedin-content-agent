# AI LinkedIn Content Agent

A multi-company AI content platform for generating, revising, and approving LinkedIn posts using structured company knowledge, semantic retrieval, configurable content rules, and human-in-the-loop review.

The project started as a simple LinkedIn content generation prototype and has evolved into a more structured AI workflow that separates company knowledge, content rules, semantic retrieval, post history, and AI generation logic.

## Features

### Multi-Company Architecture

* Support multiple companies with separate knowledge and content rules
* Store company-specific data independently
* Switch between companies from the Streamlit interface
* Keep the core AI logic independent from individual brands

### Company Knowledge Management

* Add company information through the interface
* Convert raw company information into structured JSON using AI
* Review and update existing company knowledge
* Automatically rebuild semantic embeddings when needed

### AI Topic Suggestions

* Generate topic and angle suggestions based on company knowledge and content strategy
* Compare suggested topics against previously approved content
* Filter highly similar topic suggestions
* Allow users to enter their own topic and optional angle

### Semantic Retrieval

* Convert company knowledge into embeddings
* Retrieve context based on semantic similarity instead of keyword matching
* Provide only relevant company information to the language model
* Cache embeddings locally to avoid unnecessary regeneration

### LinkedIn Post Generation

Generate structured LinkedIn content containing:

* Hook
* Main post
* Call to action
* Hashtags

Content generation uses:

* Selected topic
* Selected language
* Relevant company context
* Global content rules
* Company-specific rules

### Feedback-Based Revision

* Review generated posts before approval
* Provide natural-language feedback
* Ask the AI to revise the existing draft
* Preserve parts of the original post that do not require changes
* Re-check similarity after revision

### Duplicate Content Detection

The application uses embeddings to compare:

* New topic + angle combinations against previous approved topics
* Generated drafts against previous approved posts

This helps reduce repetitive LinkedIn content.

### Human-in-the-Loop Approval

Content is not automatically treated as final.

The workflow allows the user to:

1. Generate content
2. Review the draft
3. Provide feedback
4. Revise the draft
5. Approve the final version

Only approved posts are added to post history.

### Languages

Current interface supports:

* English
* Finnish

## Technologies

* Python
* OpenAI API
* Streamlit
* JSON
* Embeddings
* Semantic Search
* Cosine Similarity
* Retrieval-Augmented Generation concepts
* Prompt Engineering
* Git / GitHub

## Architecture

The application separates AI logic, company knowledge, company-specific rules, global rules, semantic retrieval, and post history.

```text
linkedin-content-agent/
│
├── app.py
├── content_agent.py
├── company_knowledge.py
├── semantic_retrieval.py
├── post_history.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/
│   └── global_rules.json
│
└── data/
    ├── vahvero_symbiosis_oy/
    │   ├── knowledge.json
    │   └── rules.json
    │
    └── nordic_data_labs_oy/
        ├── knowledge.json
        └── rules.json
```

Runtime-generated files such as `embeddings.json` and `post_history.json` are excluded from Git using `.gitignore`.

## How It Works

The current workflow is:

```text
Select Company
      ↓
Select Language
      ↓
AI Suggests Topics + Angles
      ↓
Topic Similarity Check
      ↓
Select Suggested Topic
or Enter Custom Topic
      ↓
Semantic Retrieval
      ↓
Relevant Company Context
      ↓
Global Rules + Company Rules
      ↓
AI Generates LinkedIn Draft
      ↓
Draft Similarity Check
      ↓
Human Review
      ↓
Feedback-Based AI Revision
      ↓
Human Approval
      ↓
Approved Post History
```

## Knowledge and Rules Separation

One of the architectural changes introduced in V2 is the separation between company knowledge and content rules.

### `knowledge.json`

Contains factual information about the company, such as:

* Company information
* Products
* Services
* Technologies and expertise
* Target audiences
* Product capabilities

### `rules.json`

Contains company-specific content guidance, such as:

* Content strategy
* Tone
* Content rules
* CTA preferences
* Formatting rules
* Language rules
* Compliance constraints

### `global_rules.json`

Contains general rules shared across companies, including:

* Avoid unsupported claims
* Use verified company information
* Write clearly and naturally
* Return structured output

This separation allows the same AI content engine to work with different companies without hardcoding brand-specific behavior into the Python logic.

## Semantic Retrieval

V1 used keyword matching to find relevant company information.

V2 replaces this with embedding-based semantic retrieval.

Company knowledge is divided into chunks and converted into embeddings using the OpenAI API.

When a topic is provided:

1. The topic is converted into an embedding.
2. Its similarity to company knowledge chunks is calculated.
3. The most relevant chunks are selected.
4. These chunks are provided to the language model as company context.

Cosine similarity is used to compare embedding vectors.

## Output Structure

Generated and revised content uses a structured JSON format:

```json
{
  "hook": "Opening hook",
  "post": "Main LinkedIn post content",
  "cta": "Call to action",
  "hashtags": [
    "#Example",
    "#LinkedIn"
  ]
}
```

This makes individual parts of the generated content easier to validate, display, revise, and process.

## Project Evolution

### V1 — Initial MVP

The first version focused on proving the basic concept:

* Single-company architecture
* Structured JSON company information
* Keyword-based retrieval and scoring
* Basic LinkedIn post generation
* User-selected post type, tone, and length
* Streamlit interface
* Structured AI output

### V2 — Current Version

The current version expands the prototype into a multi-company AI content workflow:

* Multi-company architecture
* Separate company knowledge and rules
* Global content rules
* Semantic retrieval with embeddings
* Cached company embeddings
* AI topic and angle suggestions
* Topic similarity detection
* Custom topic support
* Draft similarity detection
* Feedback-based AI revision
* Human approval workflow
* Approved post history
* Automatic embedding rebuilding

This evolution moves the project from a basic content generator toward a reusable AI content agent architecture.

## Installation

Clone the repository:

```bash
git clone https://github.com/Samanehmo1212/ai-linkedin-content-agent.git
cd ai-linkedin-content-agent
```

Install the required packages:

```bash
py -m pip install -r requirements.txt
```

## OpenAI API Key

The application requires an OpenAI API key.

Set the key as an environment variable before running the application.

### PowerShell

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Do not store a real API key directly in the source code or commit it to the repository.

The `.env.example` file can be used to document the required environment variable without exposing a real credential.

## Run the Application

Start the Streamlit application:

```bash
py -m streamlit run app.py
```

The application will open in the browser.

## Security

Sensitive credentials such as API keys should never be committed to the repository.

The project uses `.gitignore` to exclude secrets and runtime-generated files such as:

* `.env`
* API key files
* Python cache files
* Generated embeddings
* Post history

## Current Status

**V2 is the current working version.**

The application currently supports the complete workflow from company knowledge management and topic suggestion through semantic retrieval, post generation, revision, similarity checking, and human approval.

The project is currently intended as a practical AI agent prototype rather than a production social-media automation platform.

## Roadmap

### V3 — Planned

Potential next steps include:

* AI image generation for LinkedIn posts
* LinkedIn or social-media platform integration
* Draft publishing
* Post scheduling
* Content performance analytics
* Engagement-based feedback loops
* Improved content quality evaluation
* Persistent database storage
* Authentication and user management
* Deployment as an online application

## Project Goals

This project is being developed as a practical exploration of:

* AI agent architecture
* Retrieval-Augmented Generation
* Semantic search
* Embeddings
* Structured knowledge management
* Prompt engineering
* Human-in-the-loop AI workflows
* Multi-company AI systems
* Content automation
* Building production-oriented AI applications with Python
