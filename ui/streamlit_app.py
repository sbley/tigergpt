import streamlit as st
import requests
import json
from datetime import datetime
import os
import sys
from typing import Dict, List, Optional, Any

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import ChatRequest, MCPServerRequest

# API endpoint
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="TigerGPT",
    page_icon="🐯",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "config" not in st.session_state:
    st.session_state.config = None

if "mcp_servers" not in st.session_state:
    st.session_state.mcp_servers = []

if "active_server" not in st.session_state:
    st.session_state.active_server = None

def load_config():
    """Load configuration from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/config")
        if response.status_code == 200:
            st.session_state.config = response.json()
            return True
        else:
            st.error(f"Error loading configuration: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def load_mcp_servers():
    """Load MCP servers from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/mcp/servers")
        if response.status_code == 200:
            st.session_state.mcp_servers = response.json()
            return True
        else:
            st.error(f"Error loading MCP servers: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def save_config(config_data):
    """Save configuration to API"""
    try:
        response = requests.post(f"{API_BASE_URL}/config", json=config_data)
        if response.status_code == 200:
            st.success("Configuration saved successfully!")
            return True
        else:
            st.error(f"Error saving configuration: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def add_mcp_server(server_data):
    """Add MCP server to API"""
    try:
        response = requests.post(f"{API_BASE_URL}/mcp/servers", json=server_data)
        if response.status_code == 200:
            st.success(f"MCP server '{server_data['name']}' added successfully!")
            load_mcp_servers()  # Reload server list
            return True
        else:
            st.error(f"Error adding MCP server: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def delete_mcp_server(server_name):
    """Delete MCP server from API"""
    try:
        response = requests.delete(f"{API_BASE_URL}/mcp/servers/{server_name}")
        if response.status_code == 200:
            st.success(f"MCP server '{server_name}' deleted successfully!")
            load_mcp_servers()  # Reload server list
            return True
        else:
            st.error(f"Error deleting MCP server: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def connect_to_mcp_server(server_name):
    """Connect to MCP server through API"""
    try:
        response = requests.post(f"{API_BASE_URL}/mcp/servers/{server_name}/connect")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                st.success(f"Connected to MCP server '{server_name}'!")
                st.session_state.active_server = server_name
                return True
            else:
                st.error(f"Failed to connect to MCP server '{server_name}'")
                return False
        else:
            st.error(f"Error connecting to MCP server: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def disconnect_from_mcp_server(server_name):
    """Disconnect from MCP server through API"""
    try:
        response = requests.post(f"{API_BASE_URL}/mcp/servers/{server_name}/disconnect")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                st.success(f"Disconnected from MCP server '{server_name}'!")
                if st.session_state.active_server == server_name:
                    st.session_state.active_server = None
                return True
            else:
                st.error(f"Failed to disconnect from MCP server '{server_name}'")
                return False
        else:
            st.error(f"Error disconnecting from MCP server: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def get_mcp_server_tools(server_name):
    """Get tools from MCP server through API"""
    try:
        response = requests.get(f"{API_BASE_URL}/mcp/servers/{server_name}/tools")
        if response.status_code == 200:
            return response.json().get("tools", [])
        else:
            st.error(f"Error getting MCP server tools: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def get_mcp_server_resources(server_name):
    """Get resources from MCP server through API"""
    try:
        response = requests.get(f"{API_BASE_URL}/mcp/servers/{server_name}/resources")
        if response.status_code == 200:
            return response.json().get("resources", [])
        else:
            st.error(f"Error getting MCP server resources: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def call_mcp_tool(server_name, tool_name, arguments):
    """Call tool on MCP server through API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/mcp/servers/{server_name}/tools/{tool_name}",
            json=arguments
        )
        if response.status_code == 200:
            return response.json().get("result")
        else:
            st.error(f"Error calling MCP tool: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def send_message(message):
    """Send a message to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=ChatRequest(
                message=message,
                conversation_id=st.session_state.conversation_id
            ).model_dump()
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.conversation_id = data.get("conversation_id")
            return data.get("response")
        else:
            st.error(f"Error from API: {response.status_code}")
            return f"Error: Failed to get response (Status code: {response.status_code})"
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return f"Error: {str(e)}"

def render_chat_tab():
    """Render the chat interface tab"""
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
                st.markdown(response)

        # Add AI message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def render_llm_config_tab():
    """Render the LLM configuration tab"""
    st.subheader("LLM Configuration")

    if st.session_state.config:
        config = st.session_state.config

        provider = st.selectbox(
            "Provider",
            options=["openai", "azure"],
            index=["openai", "azure"].index(config["llm_config"]["provider"])
        )

        model_name = st.text_input("Model Name", value=config["llm_config"]["model_name"])
        api_key = st.text_input("API Key", type="password", value="")

        # Azure-specific options
        base_url = None
        api_version = None
        deployment = None

        if provider == "azure":
            base_url = st.text_input("Base URL", value=config["llm_config"].get("base_url", ""))
            api_version = st.text_input("API Version", value=config["llm_config"].get("api_version", ""))
            deployment = st.text_input("Deployment", value=config["llm_config"].get("deployment", ""))

        if st.button("Save LLM Configuration"):
            config_update = {
                "llm_config": {
                    "provider": provider,
                    "model_name": model_name,
                    "api_key": api_key if api_key else config["llm_config"].get("api_key", ""),
                    "base_url": base_url,
                    "api_version": api_version,
                    "deployment": deployment
                }
            }
            save_config(config_update)
    else:
        st.info("Click 'Reload Configuration' to load current settings")
# Modify the render_mcp_servers_tab function

def render_mcp_servers_tab():
    """Render the MCP servers configuration tab"""
    st.subheader("MCP Servers")

    # Reload button
    if st.button("Reload MCP Servers"):
        load_config()  # This will reload all configuration including MCP servers

    # Display existing servers
    if st.session_state.config and "mcp_servers" in st.session_state.config:
        mcp_servers = st.session_state.config["mcp_servers"]
        st.markdown("### Configured MCP Servers")

        for idx, server in enumerate(mcp_servers):
            with st.expander(f"{server['name']} ({server['command']})", expanded=False):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(f"**Command:** {server['command']}")
                    st.write(f"**Arguments:** {', '.join(server['args']) if server['args'] else 'None'}")
                    st.write(f"**Enabled:** {'Yes' if server['enabled'] else 'No'}")
                    st.write(f"**Environment Variables:** {len(server['env'])} variables")

                with col2:
                    if st.button("Delete", key=f"delete_{idx}"):
                        delete_mcp_server(server['name'])
                        st.rerun()

    # Add new MCP server
    st.markdown("### Add New MCP Server")

    with st.form("add_mcp_server_form"):
        name = st.text_input("Server Name")
        command = st.text_input("Command (path to Python or executable)")
        args_str = st.text_input("Arguments (comma-separated)")
        args = [arg.strip() for arg in args_str.split(",")] if args_str else []

        # Environment variables as key=value pairs
        env_str = st.text_area("Environment Variables (key=value, one per line)")
        env = {}
        if env_str:
            for line in env_str.strip().split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()

        enabled = st.checkbox("Enabled", value=True)

        submitted = st.form_submit_button("Add Server")

        if submitted:
            if not name or not command:
                st.error("Server name and command are required")
            else:
                server_config = MCPServerRequest(
                    name=name,
                    command=command,
                    args=args,
                    env=env,
                    enabled=enabled
                )

                if add_mcp_server(server_config.model_dump()):
                    st.success(f"MCP server '{name}' added successfully!")
                    st.rerun()

# Main app layout
st.title("🐯 TigerGPT")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["Chat", "LLM Config", "MCP Servers"])

with tab1:
    render_chat_tab()

with tab2:
    render_llm_config_tab()

with tab3:
    render_mcp_servers_tab()

# Sidebar for conversation management
with st.sidebar:
    st.header("Conversation")

    if st.button("New Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()

    if st.button("Reload Configuration"):
        load_config()

# Load config and MCP servers on startup
if not st.session_state.config:
    load_config()

if not st.session_state.mcp_servers:
    load_mcp_servers()

# Run Streamlit app
if __name__ == "__main__":
    st.info("Use the sidebar to manage conversations, and the MCP Servers tab to configure MCP servers.")
