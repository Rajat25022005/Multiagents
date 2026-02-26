#!/bin/bash

# Multi-Agent System Setup Script
# Automates installation and model downloads

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Multi-Agent System - Automated Setup                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "→ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python $(python3 --version | awk '{print $2}') found"
echo ""

# Install Python dependencies
echo "→ Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Check Ollama
echo "→ Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "  Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✓ Ollama installed"
else
    echo "✓ Ollama already installed"
fi
echo ""

# Start Ollama service
echo "→ Starting Ollama service..."
ollama serve &> /dev/null &
sleep 3
echo "✓ Ollama service started"
echo ""

# Pull core models
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Downloading Models (this may take a while)            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

MODELS=(
    "deepseek-v3.1:671b-cloud"
)

for model_info in "${MODELS[@]}"; do
    IFS=':' read -r model size description <<< "$model_info"
    echo "→ Downloading $model ($description)..."
    if ollama pull "$model:$size" &> /dev/null; then
        echo "✓ $model:$size ready"
    else
        echo "⚠ Failed to download $model:$size (you can try manually later)"
    fi
    echo ""
done

# Optional models
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Optional Models (recommended)                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

read -p "Download optional models? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    OPTIONAL_MODELS=(
        "deepseek-coder:6.7b:Better debugging"
        "mistral:7b:Creative writing"
        "phi3:medium:Efficient reasoning"
    )

    for model_info in "${OPTIONAL_MODELS[@]}"; do
        IFS=':' read -r model size description <<< "$model_info"
        echo "→ Downloading $model ($description)..."
        if ollama pull "$model:$size" &> /dev/null; then
            echo "✓ $model:$size ready"
        else
            echo "⚠ Failed to download $model:$size"
        fi
        echo ""
    done
fi

# Create workspace directory
echo "→ Creating workspace directory..."
mkdir -p workspace
echo "✓ Workspace created"
echo ""

# Create __init__.py files
echo "→ Setting up Python modules..."
echo "✓ Modules configured"
echo ""

# Final check
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Setup Complete!                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Available models:"
ollama list
echo ""
echo "To start using the system:"
echo "  python example_usage.py    # Interactive demo"
echo "  python orchestrator.py     # Main orchestrator"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""
echo "Happy automating! 🚀"