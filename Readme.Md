<div align="center">

# FastAPI Learning & AI Backend

**A hands-on Python repository that progresses from FastAPI fundamentals to authentication, databases, and an AI-ready chatbot backend.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-learning%20projects-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Md--Emon--Hasan-181717?logo=github)](https://github.com/Md-Emon-Hasan)

<img width="1420" height="947" alt="Image" src="https://github.com/user-attachments/assets/643db94b-a51f-425d-9b2d-9a3ef16d1f1e" />

</div>

---

## Overview

This repository contains independent, numbered examples for learning FastAPI and building backend features used in AI applications. The lessons begin with basic routes and request validation, then move through dependency injection, configuration, error handling, SQLAlchemy, JWT authentication, and role-based authorization.

The repository also includes a chatbot backend project structure with API routes and service modules for chat, document upload and retrieval, agent tasks, authentication, embeddings, and vector search. Its integrations require local configuration and credentials; see the project-specific notes before running it.

> **Learning repository:** examples are organized by topic and may have different levels of completeness. Install the dependencies and follow the README in the specific lesson when one is provided.

## Contents

### FastAPI fundamentals — `tutorials/fastapi-basics/`

| Lesson | Topic |
| --- | --- |
| `01-first-api` | Your first FastAPI application |
| `02-path-parameters` | Path parameters |
| `03-query-parameters` | Query parameters |
| `04-request-body` | Request bodies and Pydantic schemas |
| `05-response-model` | Response models |
| `06-dependency-injection` | Dependencies and service structure |
| `07-config-environment-management` | Configuration and environment variables |
| `08-global-exception-handling` | Error handling |
| `09-postgresql-sqlalchemy` | PostgreSQL and SQLAlchemy |
| `10-put-vs-patch` | Update methods |
| `11-jwt-authentication` | Signup, login, and JWT-protected routes |
| `12-role-based-authorization` | Role-based access control |
| `13-chatbot-backend` | AI chatbot backend architecture and integrations |

### Chatbot API progression — `tutorials/chatbot-backend/`

| Lesson | Topic |
| --- | --- |
| `01-foundation` | FastAPI application foundation |
| `02-pydantic-validation` | Data validation |
| `03-post-endpoint-validation` | Validated POST endpoint |
| `04-post-endpoint-with-runtime-validation` | Runtime validation |
| `05-combined-endpoint` | Combined endpoint patterns |
| `06-error-handling` | Error handling and response schemas |
| `07-crud-operations` | CRUD operations |
| `08-database-sqlalchemy-dependency-injection-crud` | Database-backed CRUD |
| `09-jwt-authentication` | JWT authentication |
| `10-current-user-dependency-and-protected-routes` | Current-user dependency and protected routes |
| `11-role-based-access-control-and-jwt` | Role-based authorization with JWT |

### Other files

- `data/sample-names.csv` — sample CSV data.
- `archive/legacy/` — older examples retained for reference.
- `requirements.txt` — shared dependencies for basic examples. Advanced lessons may include their own dependency files.

## Technology

- **Python** and **FastAPI** for API development
- **Pydantic** for request and response validation
- **SQLAlchemy** and PostgreSQL for database examples
- **JWT** and password hashing for authentication examples
- In the AI backend example: **Groq**, **LangChain**, **Sentence Transformers**, **FAISS**, and PDF processing libraries

The AI backend's dependencies and external services are specific to that project. Its `requirements.txt` is at [`tutorials/fastapi-basics/13-chatbot-backend/requirements.txt`](tutorials/fastapi-basics/13-chatbot-backend/requirements.txt).

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/Md-Emon-Hasan/FastAPI.git
cd FastAPI
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

For basic examples:

```bash
pip install -r requirements.txt
```

For a lesson with its own `requirements.txt`, move into that lesson directory and install its dependencies instead. For example:

```bash
cd tutorials/fastapi-basics/13-chatbot-backend
pip install -r requirements.txt
```

### 4. Run an example

For a simple lesson with `main.py` at its root:

```bash
cd tutorials/fastapi-basics/01-first-api
uvicorn main:app --reload
```

For a lesson whose application is under `app/main.py`:

```bash
cd tutorials/fastapi-basics/09-postgresql-sqlalchemy
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI or [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) for ReDoc.

## AI chatbot backend configuration

The advanced chatbot backend uses external services and environment-based settings. Before launching it, configure the required values (including `GROQ_API_KEY`, `SECRET_KEY`, and `DATABASE_URL`) in a local `.env` file inside the project directory. Never commit real credentials. Check the implementation and local service requirements for PostgreSQL, model downloads, and vector store setup.

Run it from the project directory after installing its dependencies and configuring the environment:

```bash
cd tutorials/fastapi-basics/13-chatbot-backend
uvicorn app.main:app --reload
```

## Learning path

1. Start with lessons 01–05 to learn routes, parameters, request bodies, and responses.
2. Continue with lessons 06–10 for application structure, configuration, databases, and update patterns.
3. Study lessons 11–12 for authentication and authorization.
4. Explore lesson 13 for a larger AI backend architecture, then compare it with the smaller chatbot API progression.

## Contributing

Suggestions, fixes, and improvements are welcome. Please keep examples focused, make lesson-specific setup clear, and avoid committing secrets, local databases, or generated model files.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Connect With Me

- 🌐 **Portfolio:** [emonlabs-ai.hitechparks.com](https://emonlabs-ai.hitechparks.com)
- 💻 **GitHub:** [Md-Emon-Hasan](https://github.com/Md-Emon-Hasan)
- 💼 **LinkedIn:** [Md Emon Hasan](https://www.linkedin.com/in/md-emon-hasan-695483237/)
- 🤗 **Hugging Face:** [emonHasan01](https://huggingface.co/emonHasan01)
- 📧 **Email:** [emon.mlengineer@gmail.com](mailto:emon.mlengineer@gmail.com)
- 📱 **WhatsApp:** [+8801834363533](https://wa.me/8801834363533)
