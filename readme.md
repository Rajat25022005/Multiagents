# Multi-Agent Orchestration System

This project is a sophisticated **FastAPI-based** multi-agent system with a **modern React frontend** designed to execute complex tasks by leveraging the power of local Large Language Models (LLMs) via Ollama. It intelligently breaks down tasks, assigns them to specialized AI agents, and generates the necessary files and reports.

## 🎨 New: React Frontend

The system now features a **premium, modern React UI** for easy task management!

- 🚀 **Task Executor**: Intuitive interface for submitting and tracking tasks
- 📜 **History**: View and manage previously executed tasks
- 💚 **System Health**: Real-time monitoring of backend status
- 🌙 **Dark Theme**: Beautiful glassmorphism design with smooth animations

### Quick Start

1. **Start the Backend:**
   ```bash
   ./run.sh
   ```
   API runs on `http://localhost:8000`

2. **Start the Frontend:**
   ```bash
   cd frontend
   npm install  # First time only
   npm run dev
   ```
   UI runs on `http://localhost:5173`

3. **Open your browser** to `http://localhost:5173` and start orchestrating! 🎉

## Key Features

- **Full Stack Project Generation:** Capable of generating complex directory structures (e.g., MERN stack with `client/` and `server/`) using a robust file protocol.
- **Vision-to-Code:** Can analyze UI screenshots and generate matching code (React, HTML/CSS).
- **Self-Healing Dependency Management:** Automatically runs `npm install` or `pip install`. If installation fails, the system **self-corrects** by asking the AI to fix the configuration files (e.g., `package.json`) and retries.
- **Intelligent Task Decomposition:** The system takes a high-level task and breaks it down into actionable subtasks.
- **Dynamic Agent Spawning:** Automatically spawns specialized agents (Planner, Executor, Finalizer) based on the task needs.
- **Security Validation:** Commands are validated against security levels before execution to prevent unsafe operations.
- **Local Privacy:** Built on top of [Ollama](https://ollama.ai/), ensuring all model inference happens locally.
- **REST API:** Fully functional FastAPI backend for easy integration.
- **Modern UI:** Premium React frontend with real-time updates and task history.

## System Architecture

The system is built on a modular architecture:

- **`OrchestratorEngine`**: The core brain (no UI/API) that coordinates the entire lifecycle.
- **`EnvironmentManager`**: Handles automated dependency installation and environment setup.
- **`AgentSpawner`**: Dynamically configures and spawns the appropriate LLM contexts.
- **`PlannerAgent`**: Breaks down the initial prompt into a structured plan.
- **`ExecutorAgent`**: Executes individual subtasks using the selected LLM with support for deep file structures.
- **`SecurityValidator`**: Enforces security policies (e.g., blocking dangerous shell commands).
- **`ResultProcessor`**: Parses agent output and handles file creation (including recursive directories).
- **`FinalizerAgent`**: Reviews the work and generates a final report.
- **`FileManager`**: Handles workspace file operations.

## Frontend Technology Stack

- **React 18** with modern hooks
- **Vite** for lightning-fast development
- **React Router** for navigation
- **Axios** for API calls
- **Custom CSS** with premium design tokens
- **Responsive Design** for all devices

## Capabilities

### Complex Project Structures
Unlike simple code generators, this system supports creating deep directory trees.
- **Example**: "Create a MERN stack app"
- **Result**:
  - `workspace/server/package.json`
  - `workspace/server/routes/auth.js`
  - `workspace/client/src/App.js`

### Auto-Install & Repair
The system attempts to make the generated code **runnable out of the box**.
1.  It detects `package.json` or `requirements.txt`.
2.  Run the install command (`npm install`, etc).
3.  **Self-Correction**: If the install fails (e.g. invalid version), it feeds the error back to the AI, patches the file, and retries automatically.

### Vision Agent 👁️➡️💻
The system includes a dedicated `VisionAgent` that can:
- **Analyze UI Designs:** Breaks down screenshots into structural components (Header, Sidebar, Grid).
- **Generate Code:** Converts visual inputs directly into frontend code (e.g., "Build this dashboard").
- **Multi-Provider Support:** Works with LLaVA (Ollama), GPT-4o, and Gemini Pro Vision.

## Getting Started

### Prerequisites

- **Mac/Linux** (Recommended)
- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Ollama** installed and running

### Installation

The project includes an automated setup script to install dependencies and pull the required Ollama models.

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/multi-agent-system.git
    cd multi-agent-system
    ```

2.  Run the setup script:
    ```bash
    ./setup.sh
    ```
    This will:
    - Check for Python and Ollama.
    - Install Python dependencies from `requirements.txt`.
    - Pull the default models (e.g., `deepseek-v3.1`).
    - Create the necessary workspace directories.

3.  Install Frontend Dependencies:
    ```bash
    cd frontend
    npm install
    ```

### Usage

#### Option 1: Use the Web UI (Recommended)

1.  **Start the Backend:**
    ```bash
    ./run.sh
    ```
    The server will start at `http://127.0.0.1:8000`.

2.  **Start the Frontend:**
    ```bash
    cd frontend
    npm run dev
    ```
    The UI will start at `http://localhost:5173`.

3.  **Access the Application:**
    Open `http://localhost:5173` in your browser and use the intuitive interface to:
    - Submit tasks
    - View task history
    - Monitor system health

#### Option 2: Use the API Directly

1.  **Start the Server:**
    ```bash
    ./run.sh
    ```

2.  **Access the API:**
    - **Swagger UI:** Navigate to `http://127.0.0.1:8000/docs` to interact with the API visually.
    - **ReDoc:** Navigate to `http://127.0.0.1:8000/redoc`.

3.  **Execute a Task:**
    Send a POST request to `/tasks/execute`:

    ```bash
    curl -X POST "http://127.0.0.1:8000/tasks/execute" \
         -H "Content-Type: application/json" \
         -d '{
               "task": "Create a MERN stack application for a car dealership",
               "context": {}
             }'
    ```

## Docker Support 🐳

You can run the entire system in a Docker container.

1.  **Build and Run:**
    ```bash
    docker-compose up --build
    ```

2.  **Access:**
    The API will be available at `http://localhost:8000`.

3.  **Note on Ollama:**
    The container is configured to talk to your *host machine's* Ollama instance via `host.docker.internal`. Ensure Ollama is running on your machine (`ollama serve`).

## Development

- **`backend/`**: Contains all backend code organized into modules
  - **`api/`**: FastAPI application, routes, and schemas
  - **`core/`**: Core logic (OrchestratorEngine, LLM Router)
  - **`agents/`**: AI agents (Planner, Vision, GraphMemory)
  - **`actions/`**: Execution tools (FileManager, EnvironmentManager, Finalizer)
  - **`admin/`**: Admin utilities (Spawner, Security, Manager)
  - **`processing/`**: Result processing
  - **`config/`**: Configuration settings
- **`frontend/`**: Contains the React application
- **`workspace/`**: The default location where generated files are saved
- **`tests/`**: Test files

## Frontend Features

### Task Executor
- Submit tasks with optional JSON context
- Real-time loading indicators
- Result display with syntax highlighting
- Error handling with user-friendly messages

### Task History
- View all previously executed tasks
- Detailed task inspection
- Delete individual or all tasks
- Persistent localStorage storage

### System Health
- Real-time backend monitoring
- API endpoint status checks
- Auto-refresh every 30 seconds
- System statistics display

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
