"""
Main entry point for Zava Clothing Concept Analysis System.

Usage:
    python main.py          Launch the custom FastAPI UI on port 8000
    python main.py --devui  Launch DevUI (Agent Framework sample app) on port 8080
"""

import asyncio
import sys

from dotenv import load_dotenv


def start_web_ui(port: int = 8000):
    """Start the existing FastAPI-based web interface."""
    import uvicorn
    from backend import app

    print("Starting Zava Clothing Concept Analysis Web Interface...")
    print(f"Access the interface at: http://localhost:{port}")
    print("Real-time updates available via WebSocket")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(app, host="0.0.0.0", port=port)


def start_devui(port: int = 8080):
    """Start DevUI — the Agent Framework sample app."""
    try:
        from agent_framework.devui import serve
    except ImportError:
        print("ERROR: agent-framework-devui is not installed.")
        print("   Install with: uv sync")
        sys.exit(1)

    from core.build import build_workflow, create_chat_clients

    print("Starting Zava Clothing Concept Analysis System (DevUI)")
    print("Initializing Azure AI chat clients...")
    chat_clients = create_chat_clients()

    print("Building Zava concept evaluation workflow (auto-approve enabled)...")
    workflow = asyncio.run(build_workflow(chat_clients, auto_approve=True))

    print(f"Launching DevUI at http://localhost:{port} ...")
    serve(entities=[workflow], auto_open=True, port=port, tracing_enabled=True)


def main():
    load_dotenv()

    if "--devui" in sys.argv:
        start_devui()
    else:
        start_web_ui()


if __name__ == "__main__":
    main()