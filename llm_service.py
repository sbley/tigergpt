from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
import logging
from config import LLMConfig, MCPServerConfig

logger = logging.getLogger(__name__)

def get_llm_model(config: LLMConfig):
    """Get the configured LLM model"""
    if config.provider == "openai":
        return OpenAIModel(
            model_name=config.model_name,
            api_key=config.api_key
        )
    elif config.provider == "azure":
        client = AsyncAzureOpenAI(
            azure_endpoint=config.base_url,
            api_version=config.api_version,
            azure_deployment=config.deployment,
            api_key=config.api_key
        )
        return OpenAIModel(
            model_name=config.model_name,
            provider=OpenAIProvider(openai_client=client)
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")


def create_mcp_servers(mcp_configs: list[MCPServerConfig]):
    """Create MCP server objects from configurations"""
    mcp_servers = []

    for config in mcp_configs:
        if not config.enabled:
            continue

        # Create an MCPServerStdio object for each enabled server
        server = MCPServerStdio(
            command=config.command,
            args=config.args,
            env=config.env,
            tool_prefix=config.name  # Use the server name as a tool prefix to avoid name conflicts
        )
        mcp_servers.append(server)
        logger.info(f"Added MCP server: {config.name}")

    return mcp_servers


def create_agent(config: LLMConfig, mcp_configs: list[MCPServerConfig] = None):
    """Create a new AI agent with given configuration and MCP servers"""
    try:
        model = get_llm_model(config)

        # Create MCP servers if provided
        mcp_servers = []
        if mcp_configs:
            mcp_servers = create_mcp_servers(mcp_configs)
            logger.info(f"Created {len(mcp_servers)} MCP servers")

        return Agent(
            model=model,
            system_prompt="You are a helpful AI assistant. Respond in a clear and concise manner.",
            mcp_servers=mcp_servers
        )
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return None
