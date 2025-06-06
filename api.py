from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import logging
import asyncio
import uuid
from typing import List, Dict, Optional, Any

from models import ChatRequest, MCPServerRequest
from conversation_manager import ConversationManager
from config import ConfigUpdate, MCPServerConfig, save_config
from llm_service import create_agent, create_mcp_servers
from pydantic_ai.mcp import MCPServerStdio

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
conversation_manager = None
app_config = None
agent = None


def initialize(config, agent_instance):
    global conversation_manager, app_config, agent
    conversation_manager = ConversationManager()
    app_config = config
    agent = agent_instance


@router.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests"""
    if not agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")

    try:
        # Get or create conversation
        conv_id = request.conversation_id or f"conv-{str(uuid.uuid4())}"

        # Add user message to conversation
        user_message = conversation_manager.create_message("user", request.message)
        conversation_manager.add_message(conv_id, user_message)

        # Process with agent that has MCP servers configured
        async with agent.run_mcp_servers():  # This automatically manages MCP server connections
            response = await agent.run(request.message)

        # Add AI response to conversation
        ai_message = conversation_manager.create_message("assistant", response.data)
        conversation_manager.add_message(conv_id, ai_message)

        return {
            "response": response.data,
            "conversation_id": conv_id
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Handle streaming chat requests"""
    if not agent:
        raise HTTPException(status_code=500, detail="AI agent not initialized")

    async def generate():
        try:
            # Get or create conversation
            conv_id = request.conversation_id or f"conv-{str(uuid.uuid4())}"

            # Add user message to conversation
            user_message = conversation_manager.create_message("user", request.message)
            conversation_manager.add_message(conv_id, user_message)

            # Stream AI response using MCP servers
            full_response = ""
            async with agent.run_mcp_servers():  # This automatically manages MCP server connections
                async for chunk in agent.run_stream(request.message):
                    if hasattr(chunk, 'data'):
                        content = chunk.data
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"

            # Add complete AI response to conversation
            ai_message = conversation_manager.create_message("assistant", full_response)
            conversation_manager.add_message(conv_id, ai_message)

            yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# MCP Server endpoints
# Update only the MCP server-related endpoints

@router.get("/mcp/servers", response_model=List[dict])
async def get_mcp_servers():
    """Get all MCP server configurations"""
    return [
        {
            "name": server.name,
            "command": server.command,
            "args": server.args,
            "env": server.env,
            "enabled": server.enabled
        }
        for server in app_config.get("mcp_servers", [])
    ]


@router.post("/mcp/servers")
async def add_mcp_server(request: MCPServerRequest):
    """Add or update an MCP server configuration"""
    global agent

    # Create the server config
    server_config = MCPServerConfig(
        name=request.name,
        command=request.command,
        args=request.args,
        env=request.env,
        enabled=request.enabled
    )

    # Update the config
    mcp_servers = app_config.get("mcp_servers", [])

    # Check if server with same name exists
    for i, server in enumerate(mcp_servers):
        if server.name == request.name:
            mcp_servers[i] = server_config
            break
    else:
        mcp_servers.append(server_config)

    app_config["mcp_servers"] = mcp_servers

    # Save the config (this will save MCP servers to the JSON file)
    save_config(app_config)

    # Recreate agent with updated MCP servers
    agent = create_agent(app_config["llm_config"], app_config["mcp_servers"])

    return {"success": True}


@router.delete("/mcp/servers/{server_name}")
async def delete_mcp_server(server_name: str):
    """Remove an MCP server configuration"""
    global agent

    # Update the config
    mcp_servers = app_config.get("mcp_servers", [])
    mcp_servers = [server for server in mcp_servers if server.name != server_name]
    app_config["mcp_servers"] = mcp_servers

    # Save the config (this will save MCP servers to the JSON file)
    save_config(app_config)

    # Recreate agent with updated MCP servers
    agent = create_agent(app_config["llm_config"], app_config["mcp_servers"])

    return {"success": True}


# Other API endpoints
@router.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "llm_config": (
            app_config["llm_config"].model_dump() if hasattr(app_config["llm_config"], "model_dump") else app_config[
                "llm_config"]),
        "mcp_servers": [
            {
                "name": s.name,
                "command": s.command,
                "args": s.args,
                "env": {k: "***" if k.lower().endswith("key") else v for k, v in s.env.items()},
                "enabled": s.enabled
            }
            for s in app_config.get("mcp_servers", [])
        ]
    }


@router.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration"""
    global agent

    try:
        # Update LLM config
        if config_update.llm_config:
            app_config["llm_config"] = config_update.llm_config

        # Update MCP servers
        if config_update.mcp_servers is not None:
            app_config["mcp_servers"] = config_update.mcp_servers

        # Save config
        save_config(app_config)

        # Recreate agent with updated config
        agent = create_agent(app_config["llm_config"], app_config.get("mcp_servers", []))

        return {"success": True}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
