# AI Chatbot with Pydantic AI
# A web-based chatbot supporting multiple LLMs and MCP servers

import logging
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from config import load_config, save_config
from llm_service import create_agent
import api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config
config = load_config()

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Yield control back to FastAPI
    yield

# Initialize FastAPI app
app = FastAPI(
    title="TigerGPT",
    description="Web-based AI chatbot with Pydantic AI and MCP support",
    lifespan=lifespan
)

# Initialize directories
Path("static").mkdir(exist_ok=True)

# Initialize agent with default configuration and MCP servers
agent = create_agent(config["llm_config"], config.get("mcp_servers", []))

# Initialize API
api.initialize(config, agent)

# Register API routes
app.include_router(api.router, prefix="/api")

# Health check route at root level
@app.get("/")
async def root():
    """Root endpoint redirecting to Streamlit UI or documentation"""
    return {"message": "API is running. Use /docs for API documentation or visit the Streamlit UI."}


if __name__ == "__main__":
    # Save config to file
    save_config(config)

    # Use reload only in development mode
    debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=debug_mode)
