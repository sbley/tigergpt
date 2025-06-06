from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
import yaml
import json
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
    "mcp_servers": []  # Empty list as we'll load from separate file
}

CONFIG_FILE = Path("config.yaml")
MCP_CONFIG_FILE = Path("mcp_servers_config.json")


def load_mcp_servers() -> List[MCPServerConfig]:
    """Load MCP server configurations from the JSON file"""
    servers = []
    if MCP_CONFIG_FILE.exists():
        try:
            with open(MCP_CONFIG_FILE, "r") as f:
                mcp_config = json.load(f)

                if "mcpServers" in mcp_config:
                    for name, server_config in mcp_config["mcpServers"].items():
                        # Update environment variables with latest values from env
                        if "env" in server_config:
                            if "AZURE_OPENAI_API_KEY" in server_config["env"] and os.getenv("AZURE_OPENAI_API_KEY"):
                                server_config["env"]["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")

                        # Add the name to the config
                        config = {
                            "name": name,
                            "command": server_config["command"],
                            "args": server_config.get("args", []),
                            "env": server_config.get("env", {}),
                            "enabled": server_config.get("enabled", True)
                        }
                        servers.append(MCPServerConfig(**config))
        except Exception as e:
            print(f"Error loading MCP server configurations: {e}")
    return servers


def save_mcp_servers(servers: List[MCPServerConfig]) -> bool:
    """Save MCP server configurations to the JSON file"""
    try:
        # Convert to the format needed for the JSON file
        mcp_config = {"mcpServers": {}}

        for server in servers:
            mcp_config["mcpServers"][server.name] = {
                "command": server.command,
                "args": server.args,
                "env": server.env,
                "enabled": server.enabled
            }

        with open(MCP_CONFIG_FILE, "w") as f:
            json.dump(mcp_config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving MCP server configurations: {e}")
        return False


def load_config() -> dict:
    """Load configuration from file if it exists"""
    # Load MCP servers first
    mcp_servers = load_mcp_servers()
    default_config["mcp_servers"] = mcp_servers

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

            return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_config


def save_config(config: dict) -> bool:
    """Save configuration to file"""
    try:
        # Save MCP servers to separate file
        if "mcp_servers" in config:
            print(f"Saving {len(config['mcp_servers'])} MCP servers to {MCP_CONFIG_FILE}")
            save_mcp_servers(config["mcp_servers"])
        else:
            print("No MCP servers to save")

        # Save main config without MCP servers
        config_dict = {
            "llm_config": config["llm_config"].model_dump()
        }

        print(f"Saving main config to {CONFIG_FILE} (keys: {list(config_dict.keys())})")
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config_dict, f)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


# Load config at module import time
config = load_config()
