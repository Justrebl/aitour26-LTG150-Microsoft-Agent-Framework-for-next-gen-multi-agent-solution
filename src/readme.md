# Zava Clothing Concept Analyzer

> **Intelligent Fashion Concept Evaluation System**

A comprehensive AI-powered system for Zava clothing company to evaluate new fashion concept submissions through automated analysis and human-in-the-loop approval workflows.

## Overview

The Zava Clothing Concept Analyzer is a production-ready demonstration of the Microsoft Agent Framework, showcasing how AI agents can collaborate to analyze complex business scenarios.

- **Market Analysis**: Fashion trend alignment and consumer demand assessment
- **Design Evaluation**: Aesthetic appeal, brand fit, and creative merit analysis
- **Production Assessment**: Manufacturing feasibility and cost considerations
- **Human Approval**: Zava team decision-making with comprehensive reporting

### **Workflow Process**

1. **Concept Upload**: Upload PowerPoint pitch deck containing clothing concept
2. **Content Parsing**: Extract text and design elements from slides
3. **Research Preparation**: Analyze content for fashion-relevant information
4. **Concurrent Analysis**: Run market, design, and production agents in parallel
5. **Report Compilation**: Synthesize agent outputs into comprehensive analysis
6. **Human Approval**: Present findings to Zava team for final decision
7. **Result Processing**: Generate detailed reports or rejection emails

## Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Azure AI Foundry project with a deployed model (e.g. gpt-4o)
- Azure CLI for authentication (`az login`)

### Installation

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AI Project details
   ```

2. **Authenticate with Azure**
   ```bash
   az login
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

## Running the Application

The project offers **two UIs** — a custom FastAPI interface and the Agent Framework DevUI. Both can run simultaneously on different ports.

### Option 1: Custom FastAPI UI (port 8000)

The full-featured custom interface with WebSocket real-time updates, progress tracking, and styled approval dialog.

```bash
uv run python main.py
```

Open **http://localhost:8000** — upload a `.pptx` file, watch the analysis progress in real time, and approve/reject concepts.

### Option 2: Agent Framework DevUI (port 8080)

[DevUI](https://learn.microsoft.com/en-us/agent-framework/devui/?pivots=programming-language-python) is the official Agent Framework sample app. It provides a web interface with built-in tracing and workflow graph visualization.

```bash
uv run python main.py --devui
```

Open **http://localhost:8080** — DevUI shows the workflow graph and a **Configure Workflow Inputs** panel.

**How to run a workflow in DevUI:**

1. The input type is **String** (the file path to a `.pptx` pitch deck)
2. Paste the full path to your PowerPoint file in the input field, for example:
   ```
   C:\Github\aitour26-LTG150-Microsoft-Agent-Framework-for-next-gen-multi-agent-solution\src\sample_ppt\bad_winter_pitch.pptx
   ```
3. Click **Run Workflow**
4. Watch the **Events** panel on the right for real-time execution updates
5. Switch to the **Traces** tab to inspect OpenTelemetry spans and the execution graph

> **Auto-approve mode**: DevUI does not natively support `RequestInfoExecutor` (human-in-the-loop) for workflows. In DevUI mode, the human approval step is automatically approved so the workflow runs end-to-end. Use the custom FastAPI UI (`python main.py`) for interactive approval/rejection.

> **File input**: DevUI's drag-and-drop file upload only works for Agents. For Workflows, it renders the input widget based on the first executor's expected type — here a string file path.

### Running Both UIs Simultaneously

You can run both UIs side-by-side in separate terminals. Each runs its own independent workflow instance:

**Terminal 1 — Custom UI (port 8000):**
```bash
cd src
uv run python main.py
```

**Terminal 2 — DevUI with tracing (port 8080):**
```bash
cd src
uv run python main.py --devui
```

> **Note**: Each UI runs its own workflow instance. They share the same Azure AI Foundry models and Application Insights telemetry, but workflow executions are independent. You can use DevUI's built-in tracing view to visualize the Agent Framework execution graph and inspect OpenTelemetry spans.

## Telemetry & Observability

Traces are sent to **Azure Application Insights** via the `APPLICATIONINSIGHTS_CONNECTION_STRING` env var. Both UIs emit OpenTelemetry spans to the same Application Insights instance (`appi-aitourparis-2026` in `rg-aitourparis-2026`, swedencentral).

- **DevUI**: Has built-in tracing visualization — requires `ENABLE_OTEL=true` in `.env` (already set). Open the **Traces** tab in DevUI to see spans.
- **FastAPI UI**: Configures OpenTelemetry + Azure Monitor exporter automatically
- **Azure Portal**: View traces in Application Insights > Transaction search / Performance

## Sample Data

Use `sample_data/bad_winter_pitch.pptx` to test the system.

## Project Structure

```
src/
├── main.py                 # Entry point (--devui flag for DevUI)
├── backend.py              # FastAPI server + WebSocket (custom UI)
├── start_ui.py             # Alternative launcher for custom UI
├── core/
│   ├── build.py            # Standalone workflow builder (used by DevUI)
│   ├── workflow_manager.py # Workflow orchestration with callbacks (used by FastAPI UI)
│   ├── agents.py           # Agent creation (market, design, production, report)
│   ├── executors.py        # Workflow step functions
│   └── approval.py         # Human-in-the-loop approval logic
├── services/
│   ├── pitch_parser.py     # PowerPoint content extraction
│   └── report_generator.py # Markdown report generation
└── static/                 # Custom UI frontend (HTML/CSS/JS)
```

## Contributing

This demo is designed as a learning tool and reference implementation. For the main Agent Framework:

- [GitHub Issues](https://github.com/microsoft/agent-framework/issues)
- [Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)

## License + Disclaimers

- This demo follows the Microsoft Agent Framework license terms. See the main repository for detailed license information.
- This is not intended to be used in production and is for demo purposes only.

---

**Built with Microsoft Agent Framework in San Francisco** 🌉