# ADK RAG API - Complete Guide

A Retrieval-Augmented Generation (RAG) API built with Google's Agent Development Kit (ADK) that combines large language models with your own data for intelligent question answering.

## What Is This?

This project creates an intelligent chatbot API that can answer questions about your specific data. Instead of just relying on what an AI model already knows, it searches through your documents and data to provide accurate, up-to-date answers.

### Simple Explanation
- **Regular AI**: "I know what I was trained on"
- **This RAG System**: "Let me search your data and then answer based on what I find"

## Architecture Overview

```
User Question → FastAPI → ADK Agent → Gemini Model ↗
                                                   ↘
Your Documents ← Vertex AI Search ← Search Tool ←
```

**Flow:**
1. User asks a question via API
2. ADK Agent analyzes the question
3. Agent automatically searches your data using Vertex AI Search
4. Agent combines search results with Gemini's knowledge
5. Returns intelligent, data-grounded response

## Key Technologies

### Google Agent Development Kit (ADK)
- **What**: Open-source framework for building AI agents
- **Why**: Handles complex agent orchestration, tool usage, and session management
- **Role**: Coordinates between the language model and search tools

### Vertex AI Search
- **What**: Google Cloud's enterprise search service
- **Why**: Provides powerful search capabilities over your documents
- **Role**: Finds relevant information from your data store

### Gemini 2.0 Flash
- **What**: Google's large language model
- **Why**: Provides natural language understanding and generation
- **Role**: Processes questions and generates human-like responses

### FastAPI
- **What**: Modern Python web framework
- **Why**: Easy to use, fast, and automatic API documentation
- **Role**: Provides REST API interface

## Project Structure

```
rag-agent-cloud-run/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── deploy.ps1             # PowerShell deployment script
├── .env                   # Environment variables (optional)
└── README.md              # This file
```

## Prerequisites

### 1. Google Cloud Account
- Active Google Cloud Project (`ai-adk-rag-faq`)
- Billing enabled
- Owner or Editor permissions

### 2. Required APIs Enabled
```bash
# Enable necessary APIs
gcloud services enable aiplatform.googleapis.com --project=ai-adk-rag-faq
gcloud services enable run.googleapis.com --project=ai-adk-rag-faq
gcloud services enable cloudbuild.googleapis.com --project=ai-adk-rag-faq
gcloud services enable discoveryengine.googleapis.com --project=ai-adk-rag-faq
```

### 3. Data Store Setup
- Vertex AI Search data store created
- Documents indexed and searchable
- Data store ID: `clothing-site_1755361501141` (in EU region)

### 4. Local Development Environment
- Python 3.9+ installed
- Google Cloud CLI installed and authenticated
- Git (optional, for version control)

## Installation & Setup

### Step 1: Clone and Setup
```bash
# Create project directory
mkdir rag-agent-cloud-run
cd rag-agent-cloud-run

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install fastapi>=0.115.0 uvicorn[standard] google-adk google-cloud-aiplatform python-dotenv
```

### Step 3: Authentication Setup
```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set default project
gcloud config set project ai-adk-rag-faq
```

### Step 4: Set Permissions
```bash
# Grant necessary permissions to Cloud Run service account
gcloud projects add-iam-policy-binding ai-adk-rag-faq \
  --member="serviceAccount:851160410617-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ai-adk-rag-faq \
  --member="serviceAccount:851160410617-compute@developer.gserviceaccount.com" \
  --role="roles/ml.developer"
```

## Configuration

### Environment Variables
The application uses these key environment variables:

```bash
GOOGLE_GENAI_USE_VERTEXAI=True              # Use Vertex AI (not Google AI Studio)
GOOGLE_CLOUD_PROJECT=ai-adk-rag-faq         # Your Google Cloud project ID
GOOGLE_CLOUD_LOCATION=us-central1           # Region for Gemini model
```

### Data Store Configuration
```python
DATA_STORE_ID = "projects/ai-adk-rag-faq/locations/eu/collections/default_collection/dataStores/clothing-site_1755361501141"
```

**Important**: The data store is in EU region, but the Gemini model runs in us-central1. This mixed-region setup works perfectly.

## Code Explanation

### Core Components

#### 1. ADK Agent Setup
```python
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# Create search tool
vertex_search_tool = VertexAiSearchTool(data_store_id=DATA_STORE_ID)

# Create intelligent agent
root_agent = Agent(
    name="rag_agent",
    model="gemini-2.0-flash",
    description="Agent that answers questions via Vertex AI Search",
    instruction="When users ask questions, use the Vertex AI Search tool to find relevant information from our datastore before answering.",
    tools=[vertex_search_tool]
)
```

#### 2. Runner Setup
```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Create runner to execute agent
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="rag_app",
    session_service=session_service
)
```

#### 3. Query Processing
```python
# Process user question
async for event in runner.run_async(
    user_id="api_user",
    session_id=session.id,
    new_message=content
):
    if event.is_final_response():
        response_text = event.content.parts[0].text
        break
```

### How the Magic Works

1. **User asks question**: "Tell me about product A"
2. **ADK analyzes**: Determines if search is needed
3. **Automatic search**: VertexAiSearchTool searches your data
4. **LLM processes**: Gemini combines search results with its knowledge
5. **Response**: Returns answer based on your actual data

## Deployment

### Deploy to Google Cloud Run

#### Using PowerShell (Windows):
```powershell
gcloud run deploy adk-working-rag `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --timeout 600 `
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=ai-adk-rag-faq,GOOGLE_CLOUD_LOCATION=us-central1" `
  --project=ai-adk-rag-faq
```

#### Using Bash (macOS/Linux):
```bash
gcloud run deploy adk-working-rag \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 600 \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=ai-adk-rag-faq,GOOGLE_CLOUD_LOCATION=us-central1" \
  --project=ai-adk-rag-faq
```

### Deployment Process
1. **Source Upload**: Your code is uploaded to Google Cloud Build
2. **Container Build**: Google automatically builds a Docker container
3. **Service Creation**: Cloud Run creates a scalable web service
4. **URL Generation**: You get a public HTTPS URL

## API Usage

### Base URL
```
https://adk-working-rag-851160410617.us-central1.run.app
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "Working ADK RAG API (Based on Your Local Code)",
  "status": "ready",
  "agent_ready": true,
  "runner_ready": true,
  "model": "gemini-2.0-flash",
  "data_store": "clothing-site (EU region)"
}
```

#### 2. Ask Questions
```http
POST /query
Content-Type: application/json

{
  "question": "Tell me about product A"
}
```

**Response:**
```json
{
  "response": "Based on the information in our database, Product A is...",
  "status": "success",
  "sources": []
}
```

#### 3. Health Status
```http
GET /health
```

### Testing Examples

#### PowerShell:
```powershell
# Check if service is running
Invoke-RestMethod -Uri "https://adk-working-rag-851160410617.us-central1.run.app/" -Method GET

# Ask a question
$body = @{ question = "What products do you have?" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://adk-working-rag-851160410617.us-central1.run.app/query" -Method POST -Body $body -ContentType "application/json"
```

#### Curl:
```bash
# Check status
curl https://adk-working-rag-851160410617.us-central1.run.app/

# Ask a question
curl -X POST https://adk-working-rag-851160410617.us-central1.run.app/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about your clothing collection"}'
```

## Troubleshooting

### Common Issues

#### 1. "Service not ready" Error
**Cause**: Agent initialization failed
**Solution**: Check Cloud Run logs
```bash
gcloud logs read --service=adk-working-rag --region=us-central1 --limit=50
```

#### 2. "Model not found" Error
**Cause**: Gemini model access issues
**Solution**: 
- Check if Vertex AI APIs are enabled
- Verify model access in Model Garden console
- Ensure service account has `aiplatform.user` role

#### 3. "Search resource not found" Error
**Cause**: Data store access issues
**Solution**:
- Verify data store ID is correct
- Check data store exists in EU region
- Ensure service account has `discoveryengine.editor` role

#### 4. Authentication Errors
**Cause**: Missing or invalid credentials
**Solution**:
```bash
gcloud auth application-default login
gcloud auth list  # Verify correct account is active
```

### Debugging Steps

1. **Check Service Status**:
   ```bash
   gcloud run services describe adk-working-rag --region=us-central1
   ```

2. **View Logs**:
   ```bash
   gcloud logs read --service=adk-working-rag --region=us-central1 --limit=50
   ```

3. **Test Locally First**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## Costs & Limits

### Google Cloud Run
- **Free Tier**: 2 million requests/month
- **Pricing**: $0.40 per million requests after free tier
- **Memory**: 2GB allocated (can be adjusted)

### Vertex AI (Gemini)
- **Input**: ~$3.50 per million tokens
- **Output**: ~$10.50 per million tokens
- **Typical Query**: ~$0.01-0.05 per question

### Vertex AI Search
- **Queries**: $3.00 per 1,000 queries
- **Storage**: $0.15 per GB per month

### Estimated Monthly Costs (1000 queries)
- Cloud Run: Free (within limits)
- Gemini: ~$10-50
- Search: ~$3
- **Total**: ~$15-55/month

## Security

### Current Setup
- **Authentication**: Google Cloud service account
- **Network**: HTTPS only
- **Access**: Public API (unauthenticated)
- **Data**: Remains in your Google Cloud project

### Production Recommendations
1. **Add API Authentication**: 
   - API keys
   - OAuth 2.0
   - JWT tokens

2. **Rate Limiting**:
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

3. **Input Validation**:
   - Sanitize user input
   - Limit query length
   - Filter harmful content

## Scaling

### Automatic Scaling
Cloud Run automatically scales based on:
- **Requests**: 0 to 1000 concurrent instances
- **CPU/Memory**: Scales up under load
- **Cold Starts**: ~1-3 seconds for new instances

### Performance Optimization
1. **Increase Memory**: More memory = faster processing
2. **Concurrency**: Adjust max concurrent requests per instance
3. **Caching**: Add Redis for frequently asked questions
4. **Connection Pooling**: Reuse database connections

## Advanced Features

### Session Management
```python
# Maintain conversation history
session = await runner.session_service.create_session(
    app_name="rag_app",
    user_id="unique_user_id"  # Track individual users
)
```

### Custom Instructions
```python
Agent(
    instruction="You are a fashion expert. Always mention style trends when discussing clothing. Be enthusiastic but professional."
)
```

### Multiple Data Sources
```python
# Add multiple search tools
tools=[
    VertexAiSearchTool(data_store_id=CLOTHING_STORE),
    VertexAiSearchTool(data_store_id=ACCESSORIES_STORE),
    custom_database_tool
]
```

## Next Steps

### Immediate Improvements
1. **Add authentication** for production use
2. **Implement caching** for common questions
3. **Add logging** for query analytics
4. **Create monitoring** dashboards

### Advanced Features
1. **Multi-turn conversations** with context
2. **Image search** capabilities
3. **Multiple data sources** integration
4. **Custom embedding models**

### Integration Options
1. **Web Frontend**: React, Vue, or plain HTML
2. **Mobile Apps**: REST API integration
3. **Slack Bot**: Slack integration
4. **WhatsApp**: WhatsApp Business API

## Support & Resources

### Documentation
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Vertex AI Search Guide](https://cloud.google.com/vertex-ai/docs/search-conversation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Monitoring
- **Google Cloud Console**: Monitor logs, metrics, errors
- **Cloud Run Dashboard**: View request patterns
- **Error Reporting**: Automatic error tracking

### Community
- [ADK GitHub Repository](https://github.com/google/adk-python)
- [Google Cloud Community](https://cloud.google.com/community)

---

**Congratulations!** You now have a fully functional RAG system that can answer questions about your specific data using cutting-edge AI technology. The system is production-ready, scalable, and built on Google Cloud's enterprise infrastructure.
