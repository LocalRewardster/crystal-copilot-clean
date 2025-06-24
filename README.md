# Crystal Copilot MVP

Crystal Reports modernization tool with drag-and-drop upload, natural language queries, and simple edits.

## Features

- ✅ **Week 1**: File upload & XML parsing
- ✅ **Week 2**: AI-powered Q&A with GPT-4o
- 🔄 **Week 3**: Natural language report editing

## Architecture

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Streamlit with tabbed interface
- **Parser**: RptToXml CLI + Python wrapper
- **LLM**: OpenAI GPT-4o for natural language queries
- **Container**: Windows Server Core with Crystal Runtime

## Local Development (macOS)

### Prerequisites

- Python 3.12+
- Poetry
- Docker Desktop with Windows containers enabled
- OpenAI API key (for Q&A functionality)
- Git

### Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repo-url>
   cd crystal-copilot
   poetry install
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Setup pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

4. **Run backend (FastAPI)**:
   ```bash
   poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run frontend (Streamlit)**:
   ```bash
   poetry run streamlit run frontend/app.py
   ```

6. **Build Windows container** (Week 0):
   ```bash
   docker build -f Dockerfile.windows -t crystal-copilot:latest .
   ```

## Week 0-2 Milestones

### ✅ Week 1: Core Upload & Parsing
- ✅ Project structure with Poetry
- ✅ FastAPI upload endpoint (≤25MB)
- ✅ Mock XML parsing pipeline
- ✅ Streamlit drag-and-drop interface
- ✅ Field lineage analysis
- ✅ Unit tests with pytest

### ✅ Week 2: AI Q&A Integration
- ✅ OpenAI GPT-4o integration
- ✅ Natural language query processing
- ✅ Contextual question suggestions
- ✅ Confidence scoring & source attribution
- ✅ Enhanced Streamlit UI with tabs
- ✅ Q&A service unit tests

### 🔄 Week 3: Report Editing (Planned)
- 🔄 Natural language edit commands
- 🔄 Hide/rename field operations
- 🔄 Visual preview of changes
- 🔄 Edit validation & rollback

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `POST /upload` - Upload .rpt file for parsing
- `GET /reports/{id}/metadata` - Get report metadata

### Week 2: Q&A Endpoints
- `POST /reports/{id}/ask` - Ask natural language questions
- `GET /reports/{id}/suggested-questions` - Get contextual suggestions
- `GET /health/openai` - Check OpenAI API status

## Q&A Examples

Once you upload a report, you can ask questions like:

- *"What data sources does this report use?"*
- *"Which fields use formulas instead of direct database fields?"*
- *"Show me all the calculated fields and their formulas"*
- *"What tables are connected to this report?"*
- *"Which section contains the company logo?"*

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=backend --cov=frontend

# Run specific test files
poetry run pytest backend/tests/test_parser.py
poetry run pytest backend/tests/test_qa_service.py

# Skip tests requiring OpenAI API
poetry run pytest -m "not integration"
```

## Sample Files

The `sample_reports/` directory contains test files:

- `Simple_Customer_List.rpt` - Basic customer directory
- `Sales_Report.rpt` - Complex sales analysis with formulas
- `Inventory_Summary.rpt` - Multi-section inventory management

Each generates different metadata for testing the Q&A functionality.

## Deployment

The application is designed to run in Azure App Service with Windows containers.

```bash
# Build for production
docker build -f Dockerfile.windows -t crystal-copilot:prod .

# Push to Azure Container Registry
az acr build --registry myregistry --image crystal-copilot:latest .
```

## Environment Variables

- `OPENAI_API_KEY` - Required for Q&A functionality
- `RPTTOXML_PATH` - Path to RptToXml.exe (Windows container)
- `DATABASE_URL` - Optional: Database for persistent storage
