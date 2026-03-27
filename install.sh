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

LANGCHAIN_MCP_URL="https://docs.langchain.com/mcp"
OPENROUTER_URL="https://openrouter.ai/"
OPENROUTER_API_BASE_URL="https://openrouter.ai/api/v1"
OPENROUTER_FREE_MODELS=(
    "nvidia/nemotron-3-super-120b-a12b:free"
    "minimax/minimax-m2.5:free"
    "stepfun/step-3.5-flash:free"
    "arcee-ai/trinity-large-preview:free"
    "openai/gpt-oss-120b:free"
    "z-ai/glm-4.5-air:free"
)
DEFAULT_CHAT_MODEL="${OPENROUTER_FREE_MODELS[0]}"

upsert_env_key() {
    local python_cmd="$1"
    local env_path="$2"
    local key="$3"
    local value="$4"

    "$python_cmd" - "$env_path" "$key" "$value" <<'PY'
import re
import sys
from pathlib import Path

env_path, key, value = sys.argv[1], sys.argv[2], sys.argv[3]
path = Path(env_path)

if path.exists():
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
else:
    lines = []

pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
replacement = f"{key}={value}"
updated = False
out = []

for line in lines:
    if pattern.match(line):
        out.append(replacement)
        updated = True
    else:
        out.append(line)

if not updated:
    out.append(replacement)

path.write_text("\n".join(out).rstrip("\n") + "\n", encoding="utf-8")
PY
}

configure_openrouter_env() {
    local python_cmd="$1"
    local env_path=".env"
    local api_key=""

    print_info "=== OpenRouter Setup ==="
    print_info "Open this URL in your browser: ${OPENROUTER_URL}"
    print_info "Sign up/login, create an API key, then paste it below."

    if [ -r /dev/tty ]; then
        while true; do
            printf "[INFO] Paste your OpenRouter API key: " > /dev/tty
            if ! IFS= read -r -s api_key < /dev/tty; then
                api_key=""
            fi
            printf "\n" > /dev/tty
            api_key=$(printf '%s' "$api_key" | tr -d '\r')

            if [ -n "$api_key" ]; then
                break
            fi

            printf "[WARNING] API key cannot be empty. Try again? (Y/n) " > /dev/tty
            local retry="y"
            if ! IFS= read -r retry < /dev/tty; then
                retry="y"
            fi
            if [[ "$retry" =~ ^[Nn]$ ]]; then
                break
            fi
        done
    else
        print_warning "No interactive terminal detected."
        print_warning "Skipping API key prompt. Add OPENROUTER_API_KEY manually to .env"
    fi

    if [ ! -f "$env_path" ]; then
        touch "$env_path"
    fi
    chmod 600 "$env_path" 2>/dev/null || true

    if [ -n "$api_key" ]; then
        upsert_env_key "$python_cmd" "$env_path" "OPENROUTER_API_KEY" "$api_key"
        upsert_env_key "$python_cmd" "$env_path" "OPENAI_API_KEY" "$api_key"
        print_success "Saved OPENROUTER_API_KEY in ${env_path}"
    else
        print_warning "OPENROUTER_API_KEY not set by installer."
    fi

    upsert_env_key "$python_cmd" "$env_path" "OPENAI_BASE_URL" "$OPENROUTER_API_BASE_URL"
    upsert_env_key "$python_cmd" "$env_path" "OPENROUTER_DEFAULT_MODEL" "$DEFAULT_CHAT_MODEL"
    upsert_env_key "$python_cmd" "$env_path" "OPENAI_CHAT_MODEL" "$DEFAULT_CHAT_MODEL"
    upsert_env_key "$python_cmd" "$env_path" "OPENROUTER_FREE_MODELS" "$(IFS=,; printf '%s' "${OPENROUTER_FREE_MODELS[*]}")"

    print_info "Default free model priority:"
    for model in "${OPENROUTER_FREE_MODELS[@]}"; do
        print_info "  - ${model}"
    done
}

configure_opencode_project() {
    local python_cmd="$1"

    print_info "Configuring OpenCode project MCP + instructions..."
    if "$python_cmd" - <<'PY'
import json
from pathlib import Path

path = Path("opencode.json")

if path.exists():
    raw = path.read_text(encoding="utf-8")
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Existing opencode.json is invalid JSON: {exc}")
else:
    config = {}

if not isinstance(config, dict):
    raise SystemExit("opencode.json root must be an object")

config.setdefault("$schema", "https://opencode.ai/config.json")

mcp = config.get("mcp")
if not isinstance(mcp, dict):
    mcp = {}

mcp["docs-langchain"] = {
    "type": "remote",
    "url": "https://docs.langchain.com/mcp",
    "enabled": True,
}
config["mcp"] = mcp

required_instructions = [
    "AGENTS.md",
    "STARTUP.md",
    "BOOTSTRAP.md",
    "INSIGHTS.md",
]

instructions = config.get("instructions")
if instructions is None:
    config["instructions"] = required_instructions
elif isinstance(instructions, str):
    merged = [instructions]
    for item in required_instructions:
        if item not in merged:
            merged.append(item)
    config["instructions"] = merged
elif isinstance(instructions, list):
    for item in required_instructions:
        if item not in instructions:
            instructions.append(item)
else:
    config["instructions"] = required_instructions

path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
print("Configured opencode.json")
PY
    then
        print_success "OpenCode project config ready (opencode.json)"
    else
        print_warning "Could not update opencode.json automatically."
        print_warning "Please add docs-langchain MCP manually: ${LANGCHAIN_MCP_URL}"
    fi
}

configure_json_mcp_file() {
    local python_cmd="$1"
    local target_path="$2"
    local container_key="$3"

    if "$python_cmd" - "$target_path" "$container_key" "$LANGCHAIN_MCP_URL" <<'PY'
import json
import sys
from pathlib import Path

target_path, container_key, url = sys.argv[1], sys.argv[2], sys.argv[3]
path = Path(target_path)

if path.exists():
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {target_path}: {exc}")
else:
    data = {}

if not isinstance(data, dict):
    raise SystemExit(f"{target_path} root must be an object")

container = data.get(container_key)
if not isinstance(container, dict):
    container = {}

container["docs-langchain"] = {"url": url}
data[container_key] = container

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"Configured {target_path}")
PY
    then
        print_success "Updated ${target_path}"
    else
        print_warning "Could not update ${target_path} automatically."
    fi
}

configure_additional_agent_mcp() {
    local python_cmd="$1"
    local coding_agent="$2"

    print_info "Configuring MCP for additional coding agents..."
    configure_json_mcp_file "$python_cmd" ".cursor/mcp.json" "mcpServers"
    configure_json_mcp_file "$python_cmd" ".vscode/mcp.json" "servers"

    case "$coding_agent" in
        codex|codex-cli)
            if command -v codex &> /dev/null; then
                if codex mcp add langchain-docs --url "$LANGCHAIN_MCP_URL" >/dev/null 2>&1; then
                    print_success "Registered LangChain MCP in Codex CLI"
                else
                    print_warning "Codex CLI MCP registration failed; using project config files instead."
                fi
            else
                print_info "Codex CLI not found; skipped codex mcp add."
            fi
            ;;
        claude|claude-code)
            if command -v claude &> /dev/null; then
                if claude mcp add --transport http docs-langchain "$LANGCHAIN_MCP_URL" >/dev/null 2>&1; then
                    print_success "Registered LangChain MCP in Claude Code"
                else
                    print_warning "Claude MCP registration failed; using project config files instead."
                fi
            else
                print_info "Claude CLI not found; skipped claude mcp add."
            fi
            ;;
        *)
            ;;
    esac
}

install_local_git_hook() {
    print_info "Installing local pre-push hook for STARTUP.md and exercise-script hygiene..."

    if [ ! -d ".git" ]; then
        print_info "No .git directory found; skipped hook installation."
        return
    fi

    local source_hook=".githooks/pre-push"
    local target_hook=".git/hooks/pre-push"

    if [ ! -f "$source_hook" ]; then
        print_warning "Hook template not found at $source_hook"
        return
    fi

    if cp "$source_hook" "$target_hook"; then
        chmod +x "$target_hook"
        print_success "Installed git pre-push hook (.git/hooks/pre-push)"
    else
        print_warning "Could not install pre-push hook automatically."
        print_warning "Manual: cp .githooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push"
    fi
}

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
    print_error "Python not found. Please install Python 3.10+"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Create uv environment when available
USE_UV="false"
if command -v uv &> /dev/null; then
    print_info "Setting up project virtual environment with uv..."
    if uv sync; then
        USE_UV="true"
        print_success "uv environment ready (.venv/)"
    else
        print_warning "uv sync failed; continuing with system Python"
    fi
else
    print_warning "uv not found; using system Python. Install uv for reproducible envs."
fi

# Initialize exercises
if [ -f "tools/init_exercises.py" ]; then
    print_info "Initializing exercise files..."
    if [ "$USE_UV" = "true" ]; then
        uv run python tools/init_exercises.py
    else
        $PYTHON_CMD tools/init_exercises.py
    fi
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

configure_opencode_project "$PYTHON_CMD"
configure_additional_agent_mcp "$PYTHON_CMD" "$CODING_AGENT_LOWER"
configure_openrouter_env "$PYTHON_CMD"
install_local_git_hook

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
