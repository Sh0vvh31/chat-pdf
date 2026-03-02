# ChatPDF - RAG with Explainable AI (XAI)

ChatPDF is a responsive, local-first multimodal AI web application that allows users to upload PDF documents and converse with an AI assistant initialized with Retrieval-Augmented Generation (RAG). The system features an Explainable AI (XAI) UI, providing full transparency on which text chunks and AI model were utilized to generate each response.

This project was built following **Hexagonal Architecture (Ports and Adapters)** and **Test-Driven Development (TDD)** to ensure maintainability and robustness.

## Features

- **Local LLM Inference**: Fully private document analysis powered by Ollama running locally.
- **RAG via `pgvector`**: Text embeddings and semantic search are handled directly inside PostgreSQL.
- **Explainable AI (XAI) UI**: Users can view the exact source chunks and distance metrics the AI used to reason its answer.
- **Containerized Stack**: Streamlit, FastAPI, and PostgreSQL run seamlessly inside Docker Compose.
- **Dynamic Routing**: LangGraph orchestrates routing fallback models (e.g., `minicpm-v`) based on multimodal inputs.

## Prerequisites

Before running the application, ensure you have the following installed on your host machine:

1. [Docker & Docker Compose](https://docs.docker.com/get-docker/)
2. [Ollama](https://ollama.com/) (Must be installed and running on your host machine/gaming PC)

## Initial Setup: Downloading AI Models

The backend relies on Ollama running on your host machine. Before starting the containers, you **must download** the required models using your host's terminal (PowerShell or Command Prompt):

```bash
# 1. Embedding Model (Required for converting PDF text to vectors)
ollama pull nomic-embed-text

# 2. Standard Chat Model (Default RAG model)
ollama pull gemma:2b

# 3. Multimodal/Image Model (Fallback routing model for images inside PDFs)
ollama pull minicpm-v
```

## Running the Application

Once the models are pulled to your host machine, you can launch the container stack.

```bash
# Build and start the containers in detached mode
docker-compose up -d --build
```

The following services will be available:
- **Frontend (Streamlit)**: [http://localhost:8501](http://localhost:8501)
- **Backend API (FastAPI)**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
- **Database**: PostgreSQL on `localhost:5432`

> **LAN Access**: The frontend is explicitly bound to `0.0.0.0` with CORS/XSRF protection disabled to allow seamless testing from smartphones or other laptops on the same Wi-Fi network. Simply access `http://<YOUR_PC_LOCAL_IP>:8501`.

## Architecture

The backend strictly adheres to **Hexagonal Architecture**:

- `src/domain`: Core business logic and data structures.
- `src/application`: Use Cases (`ChatUseCase`, `DocumentExtractionUseCase`), Ports, and LangGraph workflow orchestrations.
- `src/infrastructure`: Database Adapters (Alembic SQL models, Repositories), LLM Adapters (Ollama API clients), extraction tools (PyMuPDF).
- `src/api`: FastAPI REST endpoints and dependency injection (DI).

### Test-Driven Development (TDD)
Unit and Integration tests cover Port specifications and Adapters. To run the tests inside the backend container:

```bash
docker-compose exec backend python -m pytest tests/
```
