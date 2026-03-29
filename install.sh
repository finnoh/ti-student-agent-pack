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
TI_NONINTERACTIVE="${TI_NONINTERACTIVE:-}"
TI_OPENROUTER_API_KEY="${TI_OPENROUTER_API_KEY:-}"
TI_CODING_AGENT="${TI_CODING_AGENT:-}"
TI_INSTALL_OPENCODE="${TI_INSTALL_OPENCODE:-}"

to_lower() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

is_noninteractive() {
    case "$(to_lower "$TI_NONINTERACTIVE")" in
        1|true|yes|y) return 0 ;;
        *) return 1 ;;
    esac
}

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
    local api_key="${TI_OPENROUTER_API_KEY}"

    print_info "=== OpenRouter Setup ==="
    print_info "Open this URL in your browser: ${OPENROUTER_URL}"
    print_info "Sign up/login, create an API key, then paste it below."

    if [ -n "$api_key" ]; then
        print_info "Using TI_OPENROUTER_API_KEY from environment."
    elif is_noninteractive; then
        print_warning "Non-interactive mode enabled and no TI_OPENROUTER_API_KEY provided."
        print_warning "Skipping API key prompt. Add OPENROUTER_API_KEY manually to .env"
    elif [ -r /dev/tty ]; then
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

ensure_uv() {
    if command -v uv &> /dev/null; then
        print_success "uv detected"
        return 0
    fi

    print_info "uv not found; installing in user space..."
    if ! command -v curl &> /dev/null; then
        print_error "curl is required to install uv automatically."
        print_error "Install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        return 1
    fi

    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        export PATH="$HOME/.local/bin:$PATH"
        if command -v uv &> /dev/null; then
            print_success "uv installed successfully"
            return 0
        fi
    fi

    print_error "Failed to install uv automatically."
    print_error "Install uv manually, then rerun installer."
    return 1
}

clone_or_download_repo() {
    local repo_url="$1"
    local target_dir="$2"

    if command -v git &> /dev/null; then
        print_info "Cloning repository from GitHub..."
        if git clone "$repo_url" "$target_dir"; then
            print_success "Repository cloned successfully"
            return 0
        fi
        print_warning "git clone failed; trying ZIP fallback..."
    else
        print_warning "git not found; using ZIP download fallback."
    fi

    if ! command -v curl &> /dev/null; then
        print_error "curl is required for ZIP fallback download."
        return 1
    fi

    local zip_url="https://github.com/finnoh/ti-student-agent-pack/archive/refs/heads/main.zip"
    local zip_file="ti-student-agent-pack-main.zip"
    local extracted_dir="ti-student-agent-pack-main"

    print_info "Downloading repository ZIP..."
    if ! curl -fsSL "$zip_url" -o "$zip_file"; then
        print_error "Failed to download repository ZIP."
        return 1
    fi

    if command -v unzip &> /dev/null; then
        if ! unzip -q "$zip_file"; then
            print_error "Failed to extract repository ZIP with unzip."
            return 1
        fi
    elif command -v tar &> /dev/null; then
        if ! tar -xf "$zip_file"; then
            print_error "Failed to extract repository ZIP with tar."
            return 1
        fi
    else
        print_error "Need either unzip or tar to extract ZIP fallback download."
        return 1
    fi

    rm -f "$zip_file"

    if [ ! -d "$extracted_dir" ]; then
        print_error "Expected extracted directory '$extracted_dir' not found."
        return 1
    fi

    if ! mv "$extracted_dir" "$target_dir"; then
        print_error "Failed to move extracted folder to '$target_dir'."
        return 1
    fi

    print_success "Repository downloaded and extracted successfully"
    return 0
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

# Clone the repository
REPO_URL="https://github.com/finnoh/ti-student-agent-pack.git"
TARGET_DIR="student-agent-pack"

if [ -d "$TARGET_DIR" ]; then
    print_error "Directory '$TARGET_DIR' already exists."
    print_error "Please remove it or run from a different directory."
    exit 1
fi

if ! clone_or_download_repo "$REPO_URL" "$TARGET_DIR"; then
    print_error "Failed to acquire repository contents."
    exit 1
fi

# Change to the directory
cd "$TARGET_DIR" || exit 1

# Check for Python (optional if uv-managed Python is used)
print_info "Checking system Python installation..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -n "$PYTHON_CMD" ]; then
    PYTHON_VERSION=$($PYTHON_CMD -V 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_warning "Found Python $PYTHON_VERSION (<3.10). Will use uv-managed Python instead."
        PYTHON_CMD=""
    else
        print_info "Found Python $PYTHON_VERSION"
    fi
else
    print_warning "No system Python found. Will use uv-managed Python."
fi

# Ensure uv exists (bootstrap in user space when needed)
if ! ensure_uv; then
    exit 1
fi

# Create uv environment
USE_UV="false"
print_info "Installing uv-managed Python 3.11 (if needed)..."
if ! uv python install 3.11 >/dev/null 2>&1; then
    print_warning "Could not preinstall uv Python 3.11. uv sync may still succeed with available Python."
fi

print_info "Setting up project virtual environment with uv..."
if [ -f "pyproject.toml" ]; then
    if uv sync; then
        USE_UV="true"
        print_success "uv environment ready (.venv/)"
        if [ -x ".venv/bin/python" ]; then
            PYTHON_CMD=".venv/bin/python"
        fi
    else
        if [ -n "$PYTHON_CMD" ]; then
            print_warning "uv sync failed; continuing with system Python ($PYTHON_CMD)."
        else
            print_error "uv sync failed and no usable system Python was found."
            exit 1
        fi
    fi
else
    print_warning "No pyproject.toml found after repository download."
    print_warning "Skipping uv sync and using system Python when available."
fi

if [ -z "$PYTHON_CMD" ]; then
    print_error "No usable Python interpreter found after setup."
    exit 1
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

if [ -n "$TI_CODING_AGENT" ]; then
    CODING_AGENT="$TI_CODING_AGENT"
    CODING_AGENT_LOWER=$(printf '%s' "$CODING_AGENT" | tr '[:upper:]' '[:lower:]')
fi

if [ -n "$TI_INSTALL_OPENCODE" ]; then
    response="$TI_INSTALL_OPENCODE"
fi

if is_noninteractive; then
    print_info "Non-interactive mode: skipping coding-agent prompt."
elif [ -r /dev/tty ]; then
    printf "[INFO] What is your coding agent (opencode, codex, claude, cursor-agent, ...)? " > /dev/tty
    if ! IFS= read -r CODING_AGENT < /dev/tty; then
        CODING_AGENT=""
    fi
    CODING_AGENT_LOWER=$(printf '%s' "$CODING_AGENT" | tr '[:upper:]' '[:lower:]')

    if [ "$CODING_AGENT_LOWER" = "opencode" ] && [ -z "$TI_INSTALL_OPENCODE" ]; then
        print_info "Coding agent is opencode; skipping install prompt and proceeding with OpenCode install check."
        response="y"
    elif [ -z "$TI_INSTALL_OPENCODE" ]; then
        printf "[INFO] Would you like to install OpenCode now? (y/N) " > /dev/tty
        if ! IFS= read -r response < /dev/tty; then
            response="n"
        fi
    fi
else
    print_info "No interactive terminal detected; skipping coding-agent and OpenCode prompts."
fi

if [[ "$response" =~ ^[Yy]$|^[Tt][Rr][Uu][Ee]$|^1$ ]]; then
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
