#!/usr/bin/env bash
# TI Student Agent Pack Installer
# Usage: curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
# Or: curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash -s -- --help

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show usage
if [[ "${1:-}" == "--help" ]]; then
    echo "TI Student Agent Pack Installer"
    echo ""
    echo "Usage:"
    echo "  curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash"
    echo ""
    echo "This will:"
    echo "  1. Clone the repository to the current directory"
    echo "  2. Set up the environment"
    echo "  3. Optionally install OpenCode"
    exit 0
fi

print_info "=== TI Student Agent Pack Installer ==="
print_info "Cloning repository from GitHub..."

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

# Clone the repository
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

# Initialize exercises
if [ -f "tools/init_exercises.py" ]; then
    print_info "Initializing exercise files..."
    $PYTHON_CMD tools/init_exercises.py
fi

print_success ""
print_success "=== Installation Complete ==="
print_success ""
print_success "Your student agent pack is ready!"
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
print_info "To work on exercises, you'll need a coding agent."
print_info ""
print_info "Would you like to install OpenCode now? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Installing OpenCode..."
    if curl -fsSL https://opencode.ai/install | bash; then
        print_success "OpenCode installed successfully!"
        print_info "You can now run: opencode"
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
print_success "Open the student-agent-pack folder in your coding agent"
print_success "and start working on exercises!"
print_success ""
