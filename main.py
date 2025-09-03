# main.py - FastAPI version based on your working local code
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Working ADK RAG API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    response: str
    status: str = "success"
    sources: list = []

# Global variables
root_agent = None
runner = None
init_status = "not_started"

@app.on_event("startup")
async def startup_event():
    """Initialize using the exact same pattern as your working code"""
    global root_agent, runner, init_status
    
    try:
        init_status = "initializing"
        logger.info("Initializing ADK RAG agent using working pattern...")
        
        # Set up Google Cloud environment - keep it simple
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "ai-adk-rag-faq"
        os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"  # Use us-central1 for Gemini
        
        # Import exactly as in your working code
        from google.adk.agents import Agent
        from google.adk.tools import VertexAiSearchTool
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        # Use the exact same data store ID and configuration
        DATA_STORE_ID = "projects/ai-adk-rag-faq/locations/eu/collections/default_collection/dataStores/clothing-site_1755361501141"
        vertex_search_tool = VertexAiSearchTool(data_store_id=DATA_STORE_ID)
        
        # Create agent using your exact working configuration
        root_agent = Agent(
            name="rag_agent",
            model="gemini-2.0-flash",  # Your working model
            description="Agent that answers questions via Vertex AI Search",
            instruction="You are a helpful assistant. "
                "When users ask questions, use the Vertex AI Search tool "
                "to find relevant information from our datastore before answering.",
            tools=[vertex_search_tool]
        )
        
        logger.info("Agent created successfully")
        
        # Add runner for FastAPI usage
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="rag_app", 
            session_service=session_service
        )
        
        logger.info("Runner created successfully")
        
        # Quick test to ensure everything works
        from google.genai import types
        
        session = await runner.session_service.create_session(
            app_name="rag_app",
            user_id="test_user"
        )
        
        logger.info("Test session created - ADK RAG agent ready")
        init_status = "ready"
        
    except Exception as e:
        init_status = f"failed: {str(e)}"
        logger.error(f"Startup failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")

@app.get("/")
def root():
    return {
        "message": "Working ADK RAG API (Based on Your Local Code)",
        "status": init_status,
        "agent_ready": root_agent is not None,
        "runner_ready": runner is not None,
        "model": "gemini-2.0-flash",
        "data_store": "clothing-site (EU region)",
        "note": "This uses the exact same configuration as your working local code"
    }

@app.post("/query")
async def query(request: QueryRequest):
    """Query using the working ADK pattern"""
    
    if init_status != "ready" or not root_agent or not runner:
        raise HTTPException(
            status_code=503, 
            detail=f"Service not ready: {init_status}"
        )
    
    try:
        logger.info(f"Processing query: '{request.question}'")
        
        # Create session for this request
        from google.genai import types
        
        session = await runner.session_service.create_session(
            app_name="rag_app",
            user_id="api_user"
        )
        
        # Prepare user message
        content = types.Content(role='user', parts=[types.Part(text=request.question)])
        
        # Execute the agent using runner - same as your working code
        response_text = ""
        sources = []
        
        async for event in runner.run_async(
            user_id="api_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                break
        
        if not response_text:
            response_text = "Agent completed but produced no response."
        
        return QueryResponse(
            response=response_text,
            status="success",
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        error_msg = str(e)
        
        # Better error handling based on common issues
        if "404" in error_msg or "not found" in error_msg.lower():
            return QueryResponse(
                response=f"Search resource not found: {error_msg[:150]}",
                status="not_found"
            )
        elif "enterprise edition" in error_msg.lower():
            return QueryResponse(
                response="Your data store configuration requires enterprise features.",
                status="config_error"
            )
        else:
            return QueryResponse(
                response=f"Query processing failed: {error_msg[:200]}",
                status="error"
            )

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if (init_status == "ready") else "unhealthy",
        "init_status": init_status,
        "components": {
            "agent": root_agent is not None,
            "runner": runner is not None,
        }
    }

@app.get("/test-local-pattern")
async def test_local_pattern():
    """Test that mimics your local working code exactly"""
    if not root_agent or not runner:
        return {"error": "Agent not initialized"}
    
    try:
        from google.genai import types
        
        session = await runner.session_service.create_session(
            app_name="rag_app",
            user_id="local_test_user"
        )
        
        # Test with the same kind of query you'd use locally
        content = types.Content(role='user', parts=[types.Part(text="Hello, can you help me with clothing questions?")])
        
        response_text = ""
        async for event in runner.run_async(
            user_id="local_test_user",
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                break
        
        return {
            "status": "success",
            "message": "Local pattern test successful",
            "response": response_text[:200] + "..." if len(response_text) > 200 else response_text
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Local pattern test failed: {str(e)[:200]}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)