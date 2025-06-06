# 🐯 TigerGPT

TigerGPT is a web-based AI chatbot application that supports multiple LLMs (Language Learning Models) and MCP (Model Control Protocol) servers. It provides a user-friendly interface for interacting with AI models and configuring various aspects of the system.

## Features

- Chat with AI language models (OpenAI or Azure OpenAI)
- Support for MCP servers for extending AI capabilities
- Streamlit-based UI for easy interaction
- FastAPI backend for robust API support
- Configurable LLM settings
- Conversation management

## Requirements

- Python 3.12 or later
- Required Python libraries (listed in [requirements.txt](requirements.txt))
- Access to OpenAI or Azure OpenAI services

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tigergpt.git
   cd tigergpt
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables (optional):
   ```bash
   # For Azure OpenAI
   set AZURE_OPENAI_API_KEY=your_api_key
   set AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
   set AZURE_OPENAI_API_VERSION=2024-09-01-preview
   set AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

## Running the Application

### Backend API Server

Run the FastAPI backend server:

```bash
python main.py
```

The backend will start on http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

### Streamlit UI

In a separate terminal, run the Streamlit UI:

```bash
cd ui
streamlit run streamlit_app.py
```

The UI will be available at http://localhost:8501.

## Using TigerGPT

### Chat Interface

1. Navigate to the Streamlit UI at http://localhost:8501
2. Use the "Chat" tab to interact with the AI
3. Type your message in the input box and press Enter
4. View the AI's response in the chat window

### Configuring LLM Settings

1. Go to the "LLM Config" tab in the UI
2. Select the provider (OpenAI or Azure)