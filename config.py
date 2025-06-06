from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
import yaml
from pathlib import Path

# Pydantic models for configuration
class LLMConfig(BaseModel):
    provider: str = Field(..., description="LLM provider (openai, azure)")
    model_name: str = Field(..., description="Model name")
    api_key: str = Field(..., description="API key")
    base_url: Optional[str] = Field(None, description="Base URL for API (for Azure)")
    api_version: Optional[str] = Field(None, description="API version (for Azure)")
    deployment: Optional[str] = Field(None, description="Deployment (for Azure)")


class MCPServerConfig(BaseModel):
    name: str = Field(..., description="MCP server name")
    command: str = Field(..., description="Command to start MCP server")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    enabled: bool = Field(True, description="Whether the server is enabled")


class ConfigUpdate(BaseModel):
    llm_config: Optional[LLMConfig] = None
    mcp_servers: Optional[List[MCPServerConfig]] = None


# Default configuration
default_config = {
    "llm_config": LLMConfig(
        provider="azure",
        model_name="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
        deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    ),
    "mcp_servers": [
        MCPServerConfig(
            name="zeiss-mcp-foss",
            command="C:\\Data\\Coding\\AI\\MCP\\foss\\.venv\\Scripts\\python",
            args=[
                "C:\\Data\\Coding\\AI\\MCP\\foss\\mcp_server.py"
            ],
            env={
                "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
            }
        )
    ]
}

CONFIG_FILE = Path("config.yaml")

def load_config() -> dict:
    """Load configuration from file if it exists"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config_dict = yaml.safe_load(f)

                # Validate and construct proper objects
                if "llm_config" in config_dict:
                    # Override with environment variables if they exist
                    llm_config = config_dict["llm_config"]
                    if os.getenv("AZURE_OPENAI_ENDPOINT"):
                        llm_config["base_url"] = os.getenv("AZURE_OPENAI_ENDPOINT")
                    if os.getenv("AZURE_OPENAI_API_VERSION"):
                        llm_config["api_version"] = os.getenv("AZURE_OPENAI_API_VERSION")
                    if os.getenv("AZURE_OPENAI_DEPLOYMENT"):
                        llm_config["deployment"] = os.getenv("AZURE_OPENAI_DEPLOYMENT")
                    if os.getenv("AZURE_OPENAI_API_KEY"):
                        llm_config["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")

                    default_config["llm_config"] = LLMConfig(**llm_config)

                if "mcp_servers" in config_dict:
                    servers = []
                    for server in config_dict["mcp_servers"]:
                        # Update environment variables with latest values
                        if "env" in server:
                            if "AZURE_OPENAI_API_KEY" in server["env"] and os.getenv("AZURE_OPENAI_API_KEY"):
                                server["env"]["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")

                        servers.append(MCPServerConfig(**server))

                    default_config["mcp_servers"] = servers

            return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config

def save_config(config: dict) -> bool:
    """Save configuration to file"""
    try:
        # Convert objects to dictionaries
        config_dict = {
            "llm_config": config["llm_config"].model_dump(),
            "mcp_servers": [server.model_dump() for server in config["mcp_servers"]]
        }

        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config_dict, f)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Load config at module import time
config = load_config()
