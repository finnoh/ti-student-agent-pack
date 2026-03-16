#!/usr/bin/env bash
# TI Student Agent Pack Installer
# Quick install: curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
# Or download the zip and run: chmod +x install.sh && ./install.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "=== TI Student Agent Pack Installer ==="

# Detect OS
OS=$(uname -s)
case "$OS" in
    Linux*)     OS="linux" ;;
    Darwin*)    OS="macos" ;;
    CYGWIN*|MINGW*|MSYS*) OS="windows" ;;
    *)          OS="unknown" ;;
esac

print_info "Detected OS: $OS"

# Check if we're already in an extracted directory (has tools/ and work/ folders)
if [ -d "tools" ] && [ -d "work" ]; then
    print_info "Already in extracted directory, skipping extraction..."
else
    # Find and extract the zip file
    ZIP_FILE=""
    if [ -f "student-agent-pack.zip" ]; then
        ZIP_FILE="student-agent-pack.zip"
    elif [ -f "ti-student-agent-pack.zip" ]; then
        ZIP_FILE="ti-student-agent-pack.zip"
    elif [ -f "ti-student-agent-pack-latest.zip" ]; then
        ZIP_FILE="ti-student-agent-pack-latest.zip"
    else
        # Look for any .zip file in the current directory
        for f in *.zip; do
            if [ -f "$f" ]; then
                ZIP_FILE="$f"
                break
            fi
        done
    fi

    if [ -n "$ZIP_FILE" ]; then
        print_info "Extracting $ZIP_FILE..."
        if command -v unzip &> /dev/null; then
            unzip -q "$ZIP_FILE"
        else
            print_error "unzip command not found. Please install unzip and rerun."
            exit 1
        fi
    else
        print_error "Could not find student-agent-pack directory or zip file"
        print_error ""
        print_error "This script must be run from the student-agent-pack directory"
        print_error "or in a directory containing a zip file."
        print_error ""
        print_error "To install:"
        print_error "1. Download the zip file from:"
        print_error "   https://github.com/finnoh/ti-student-agent-pack/releases"
        print_error "2. Extract it to a new folder"
        print_error "3. Run: chmod +x install.sh && ./install.sh"
        exit 1
    fi
fi

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
    print_error "Python not found. Please install Python 3.8+ and rerun this script."
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "tools/submit_exercise.py" ]; then
    print_error "Could not find tools/submit_exercise.py"
    print_error "Please ensure you're in the correct directory"
    exit 1
fi

# Run startup check
print_info "Running startup check..."
if [ -f "tools/startup_check.py" ]; then
    if $PYTHON_CMD tools/startup_check.py; then
        print_success "Startup check passed"
    else
        print_warning "Some startup checks failed"
    fi
else
    print_warning "startup_check.py not found, skipping"
fi

# Initialize exercises if needed
if [ -f "tools/init_exercises.py" ]; then
    print_info "Initializing exercise files..."
    $PYTHON_CMD tools/init_exercises.py
fi

print_success ""
print_success "=== Installation Complete ==="
print_success ""
print_success "Next steps:"
print_success "1. Edit config/form_config.json with your Google Form details"
print_success "2. Complete BOOTSTRAP.md with your information"
print_success "3. Start working on exercises in the work/ directory"
print_success ""
print_success "Available commands:"
print_success "  python tools/submit_exercise.py --from-markdown work/E1.md"
print_success "  python tools/progress_dashboard.py"
print_success "  python tools/ask_course.py --q \"Your question here\""
print_success ""

# Offer to install OpenCode
print_info "=== Coding Agent Setup ==="
print_info ""
print_info "To work on exercises, you'll need a coding agent. Options include:"
print_info ""
print_info "1. OpenCode (recommended for this workshop):"
print_info "   curl -fsSL https://opencode.ai/install | bash"
print_info ""
print_info "2. VS Code with GitHub Copilot"
print_info ""
print_info "3. Cursor (VS Code-based AI editor)"
print_info ""
print_info "4. Claude Code / Codex (CLI tools)"
print_info ""
print_info "Would you like to install OpenCode now? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Installing OpenCode..."
    if curl -fsSL https://opencode.ai/install | bash; then
        print_success "OpenCode installed successfully!"
        print_info "You can now run: opencode"
    else
        print_warning "OpenCode installation failed. You can install it later using:"
        print_warning "  curl -fsSL https://opencode.ai/install | bash"
    fi
else
    print_info "You can install OpenCode later using:"
    print_info "  curl -fsSL https://opencode.ai/install | bash"
fi

print_success ""
print_success "=== Ready to Start ==="
print_success ""
print_success "Your student agent pack is ready!"
print_success "Open this folder in your coding agent and start working on exercises."
print_success ""
