#!/usr/bin/env bash
# TI Student Agent Pack Installer
# Usage: curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
# Installer version: 2026-03-16-tty-prompt

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "=== TI Student Agent Pack Installer ==="

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "git is not installed. Please install git first."
    exit 1
fi

# Clone the repository
REPO_URL="https://github.com/finnoh/ti-student-agent-pack.git"
TARGET_DIR="student-agent-pack"

if [ -d "$TARGET_DIR" ]; then
    print_error "Directory '$TARGET_DIR' already exists."
    print_error "Please remove it or run from a different directory."
    exit 1
fi

print_info "Cloning repository from GitHub..."
if git clone "$REPO_URL" "$TARGET_DIR"; then
    print_success "Repository cloned successfully"
else
    print_error "Failed to clone repository"
    exit 1
fi

# Change to the directory
cd "$TARGET_DIR" || exit 1

# Check for Python
print_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 -V 2>&1 | cut -d' ' -f2)
    print_info "Found Python $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python -V 2>&1 | cut -d' ' -f2)
    print_info "Found Python $PYTHON_VERSION"
else
    print_error "Python not found. Please install Python 3.8+"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Initialize exercises
if [ -f "tools/init_exercises.py" ]; then
    print_info "Initializing exercise files..."
    $PYTHON_CMD tools/init_exercises.py
fi

print_success ""
print_success "=== Installation Complete ==="
print_success ""
print_success "Your student agent pack is ready in: $(pwd)"
print_success ""

# Offer to install OpenCode
print_info "=== Coding Agent Setup ==="
print_info ""
CODING_AGENT=""
CODING_AGENT_LOWER=""
response="n"
OPENCODE_INSTALLED="false"

if [ -r /dev/tty ]; then
    printf "[INFO] What is your coding agent (opencode, codex, claude, cursor-agent, ...)? " > /dev/tty
    if ! IFS= read -r CODING_AGENT < /dev/tty; then
        CODING_AGENT=""
    fi
    CODING_AGENT_LOWER=$(printf '%s' "$CODING_AGENT" | tr '[:upper:]' '[:lower:]')

    if [ "$CODING_AGENT_LOWER" = "opencode" ]; then
        print_info "Coding agent is opencode; skipping install prompt and proceeding with OpenCode install check."
        response="y"
    else
        printf "[INFO] Would you like to install OpenCode now? (y/N) " > /dev/tty
        if ! IFS= read -r response < /dev/tty; then
            response="n"
        fi
    fi
else
    print_info "No interactive terminal detected; skipping coding-agent and OpenCode prompts."
fi

if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Installing OpenCode..."
    if curl -fsSL https://opencode.ai/install | bash; then
        print_success "OpenCode installed successfully!"
        OPENCODE_INSTALLED="true"
    else
        print_warning "OpenCode installation failed."
        print_warning "Install manually: curl -fsSL https://opencode.ai/install | bash"
    fi
else
    print_info "You can install OpenCode later with:"
    print_info "  curl -fsSL https://opencode.ai/install | bash"
fi

print_success ""
print_success "=== Ready to Start ==="
print_success ""
LAUNCH_CMD=""
if [ "$OPENCODE_INSTALLED" = "true" ]; then
    LAUNCH_CMD="cd ${TARGET_DIR} && opencode"
elif [ -n "$CODING_AGENT" ]; then
    LAUNCH_CMD="cd ${TARGET_DIR} && ${CODING_AGENT}"
fi

print_success "START YOUR CODING AGENT!"
if [ -n "$LAUNCH_CMD" ]; then
    print_success "Copy and run: $LAUNCH_CMD"
else
    print_success "Copy and run: cd ${TARGET_DIR} && <your-coding-agent>"
fi
print_success ""
