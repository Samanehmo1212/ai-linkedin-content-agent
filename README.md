# AI LinkedIn Content Agent

A Python-based AI application that generates company-specific LinkedIn content using structured company knowledge, retrieval logic, and the OpenAI API.

The project was built as a practical AI agent prototype for creating LinkedIn content based on a company's products, expertise, target audience, and communication needs.

## Features

- Generate LinkedIn posts based on a user-provided topic
- Support multiple post types:
  - Product post
  - Educational post
  - Industry insight
  - Technical post
- Retrieve relevant information from a structured JSON knowledge base
- Rank relevant information using keyword matching and scoring
- Use retrieved company context when generating content
- Generate structured output:
  - Hook
  - Main post
  - CTA (Call to Action)
  - Hashtags
- Customize content by:
  - Language
  - Tone
  - Post length
- Streamlit web interface
- Basic error handling and AI response validation
- API key management through environment variables

## Technologies

- Python
- OpenAI API
- Streamlit
- JSON
- Information Retrieval
- Prompt Engineering

## Project Structure

```text
linkedin-content-agent/
│
├── app.py
├── content_agent.py
├── retrieval.py
├── company_info.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## How It Works

The application combines information retrieval with a large language model to generate company-specific LinkedIn content.

```text
User Input
   ↓
Topic + Post Type + Language + Tone + Length
   ↓
Information Retrieval
   ↓
Structured Company Knowledge (JSON)
   ↓
Relevant Context
   ↓
OpenAI Language Model
   ↓
Structured LinkedIn Content
   ↓
Streamlit Interface
```

The retrieval layer searches the company knowledge base and scores relevant information before creating the context used by the language model.

For product-specific queries, the application can also retrieve a complete relevant section of the knowledge base to provide richer context.

The language model then uses the retrieved context together with the selected post type, language, tone, and length to generate the final content.

## Output Structure

The generated content is returned in a structured format containing:

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

This structured output makes it easier to display and process individual parts of the generated content.

## Installation

Clone the repository:

```bash
git clone https://github.com/Samanehmo1212/ai-linkedin-content-agent.git
cd linkedin-content-agent
```

Install the required Python packages:

```bash
py -m pip install -r requirements.txt
```

## OpenAI API Key

The application requires an OpenAI API key.

Set the API key as an environment variable before running the application.

### PowerShell

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Do not store your real API key directly in the source code or commit it to the repository.

The `.env.example` file shows the required environment variable without containing a real API key.

## Run the Application

Start the Streamlit application:

```bash
py -m streamlit run app.py
```

The application will open in your browser.

## Example

A user can select:

```text
Topic:
Raiqu and healthcare data

Post type:
Educational post

Language:
English

Tone:
Clear and educational

Post length:
Short
```

The application retrieves relevant information from the knowledge base and generates a structured LinkedIn post containing a hook, main content, CTA, and hashtags.

## Project Goals

The main goals of this project are to explore:

- AI-assisted content generation
- Retrieval-based grounding
- Structured knowledge bases
- Prompt design
- Structured LLM output
- Building a practical AI application with Python
- Creating a simple interactive interface for an AI workflow

## Current Status

This project is currently an MVP (Minimum Viable Product).

The current version uses a lightweight keyword-based retrieval and scoring approach together with section-based retrieval for selected company information.

## Future Improvements

Possible next steps include:

- Semantic search using embeddings
- Vector-based RAG
- Improved relevance ranking
- Content quality evaluation
- Generated post history
- Additional content formats
- More advanced company knowledge management
- Direct social media integrations
- FastAPI backend
- React frontend
- Deployment as an online application

## Security

Sensitive credentials such as the OpenAI API key are excluded from the repository using `.gitignore`.

Never commit API keys, passwords, or other secrets to a public repository.
