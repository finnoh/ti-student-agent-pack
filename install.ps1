Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info($Message) { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success($Message) { Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warn($Message) { Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-ErrorAndExit($Message) { Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

$RepoUrl = "https://github.com/finnoh/ti-student-agent-pack.git"
$RepoZipUrl = "https://github.com/finnoh/ti-student-agent-pack/archive/refs/heads/main.zip"
$TargetDir = "student-agent-pack"
$LangChainMcpUrl = "https://docs.langchain.com/mcp"
$OpenRouterUrl = "https://openrouter.ai/"
$OpenRouterBaseUrl = "https://openrouter.ai/api/v1"
$OpenRouterFreeModels = @(
  "nvidia/nemotron-3-super-120b-a12b:free",
  "minimax/minimax-m2.5:free",
  "stepfun/step-3.5-flash:free",
  "arcee-ai/trinity-large-preview:free",
  "openai/gpt-oss-120b:free",
  "z-ai/glm-4.5-air:free"
)
$DefaultChatModel = $OpenRouterFreeModels[0]
$EnvNonInteractive = $env:TI_NONINTERACTIVE
$EnvOpenRouterKey = $env:TI_OPENROUTER_API_KEY

function Is-NonInteractive {
  $Value = "" + $EnvNonInteractive
  if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
  $Normalized = $Value.Trim().ToLowerInvariant()
  return @("1", "true", "yes", "y") -contains $Normalized
}

function Add-ToPathIfMissing($PathEntry) {
  if ([string]::IsNullOrWhiteSpace($PathEntry)) { return }
  $parts = ($env:PATH -split ";")
  if ($parts -notcontains $PathEntry) {
    $env:PATH = "$PathEntry;$env:PATH"
  }
}

function Ensure-Uv {
  if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Success "uv detected"
    return
  }

  Write-Info "uv not found, installing in user space..."
  try {
    & powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
  } catch {
    Write-ErrorAndExit "Failed to install uv automatically. Install manually: https://docs.astral.sh/uv/getting-started/installation/"
  }

  Add-ToPathIfMissing "$HOME\.local\bin"
  Add-ToPathIfMissing "$HOME\.cargo\bin"

  if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-ErrorAndExit "uv install completed but uv is still not on PATH. Restart terminal and retry."
  }

  Write-Success "uv installed"
}

function Clone-OrDownloadRepo {
  if (Test-Path $TargetDir) {
    Write-ErrorAndExit "Directory '$TargetDir' already exists. Remove it or run from another folder."
  }

  if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Info "Cloning repository with git..."
    git clone $RepoUrl $TargetDir | Out-Null
    Write-Success "Repository cloned"
    return
  }

  Write-Warn "git not found. Using ZIP download fallback..."
  $ZipPath = Join-Path (Get-Location) "ti-student-agent-pack-main.zip"
  $ExtractPath = Join-Path (Get-Location) "ti-student-agent-pack-main"

  Invoke-WebRequest -Uri $RepoZipUrl -OutFile $ZipPath
  Expand-Archive -Path $ZipPath -DestinationPath (Get-Location)
  Rename-Item -Path $ExtractPath -NewName $TargetDir
  Remove-Item -Force $ZipPath
  Write-Success "Repository downloaded via ZIP"
}

function Upsert-EnvKey($EnvPath, $Key, $Value) {
  if (-not (Test-Path $EnvPath)) {
    New-Item -ItemType File -Path $EnvPath | Out-Null
  }

  $Lines = Get-Content -Path $EnvPath -ErrorAction SilentlyContinue
  if ($null -eq $Lines) { $Lines = @() }

  $Updated = $false
  $Pattern = "^\s*" + [Regex]::Escape($Key) + "\s*="
  $Out = @()

  foreach ($Line in $Lines) {
    if ($Line -match $Pattern) {
      $Out += "$Key=$Value"
      $Updated = $true
    } else {
      $Out += $Line
    }
  }

  if (-not $Updated) {
    $Out += "$Key=$Value"
  }

  Set-Content -Path $EnvPath -Value $Out -Encoding UTF8
}

function Configure-OpenRouterEnv {
  $EnvPath = ".env"
  Write-Info "=== OpenRouter Setup ==="
  Write-Info "Open this URL: $OpenRouterUrl"
  Write-Info "Create an API key, then paste it below."

  $ApiKey = $EnvOpenRouterKey
  if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    if (Is-NonInteractive) {
      Write-Warn "Non-interactive mode enabled and no TI_OPENROUTER_API_KEY provided."
      $ApiKey = ""
    } else {
      $ApiKey = Read-Host "Paste your OpenRouter API key (or press Enter to skip)"
    }
  } else {
    Write-Info "Using TI_OPENROUTER_API_KEY from environment."
  }

  if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {
    Upsert-EnvKey $EnvPath "OPENROUTER_API_KEY" $ApiKey
    Upsert-EnvKey $EnvPath "OPENAI_API_KEY" $ApiKey
    Write-Success "Saved OPENROUTER_API_KEY in .env"
  } else {
    Write-Warn "OPENROUTER_API_KEY not set by installer. Add it manually to .env"
  }

  Upsert-EnvKey $EnvPath "OPENAI_BASE_URL" $OpenRouterBaseUrl
  Upsert-EnvKey $EnvPath "OPENROUTER_DEFAULT_MODEL" $DefaultChatModel
  Upsert-EnvKey $EnvPath "OPENAI_CHAT_MODEL" $DefaultChatModel
  Upsert-EnvKey $EnvPath "OPENROUTER_FREE_MODELS" ($OpenRouterFreeModels -join ",")
}

function Configure-McpJson($Path, $ContainerKey) {
  $Parent = Split-Path -Parent $Path
  if (-not (Test-Path $Parent)) {
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
  }

  $Data = @{}
  if (Test-Path $Path) {
    $Raw = Get-Content -Raw -Path $Path
    if (-not [string]::IsNullOrWhiteSpace($Raw)) {
      $Data = ConvertFrom-Json $Raw -AsHashtable
    }
  }

  if (-not $Data.ContainsKey($ContainerKey)) {
    $Data[$ContainerKey] = @{}
  }

  $Data[$ContainerKey]["docs-langchain"] = @{ url = $LangChainMcpUrl }
  ($Data | ConvertTo-Json -Depth 10) + "`n" | Set-Content -Path $Path -Encoding UTF8
}

function Configure-OpenCodeProject {
  $Path = "opencode.json"
  $Config = @{}

  if (Test-Path $Path) {
    $Raw = Get-Content -Raw -Path $Path
    if (-not [string]::IsNullOrWhiteSpace($Raw)) {
      $Config = ConvertFrom-Json $Raw -AsHashtable
    }
  }

  $Config["`$schema"] = "https://opencode.ai/config.json"

  if (-not $Config.ContainsKey("mcp")) {
    $Config["mcp"] = @{}
  }

  $Config["mcp"]["docs-langchain"] = @{
    type = "remote"
    url = $LangChainMcpUrl
    enabled = $true
  }

  $RequiredInstructions = @("AGENTS.md", "STARTUP.md", "BOOTSTRAP.md", "INSIGHTS.md")
  if (-not $Config.ContainsKey("instructions")) {
    $Config["instructions"] = @()
  }

  foreach ($Item in $RequiredInstructions) {
    if ($Config["instructions"] -notcontains $Item) {
      $Config["instructions"] += $Item
    }
  }

  ($Config | ConvertTo-Json -Depth 12) + "`n" | Set-Content -Path $Path -Encoding UTF8
  Write-Success "Configured opencode.json"
}

function Install-LocalGitHook {
  if (-not (Test-Path ".git")) {
    Write-Info "No .git directory found; skipped pre-push hook installation."
    return
  }

  if (-not (Test-Path ".githooks/pre-push")) {
    Write-Warn "Hook template .githooks/pre-push not found."
    return
  }

  $HookDir = ".git/hooks"
  New-Item -ItemType Directory -Path $HookDir -Force | Out-Null
  Copy-Item ".githooks/pre-push" ".git/hooks/pre-push" -Force
  Write-Success "Installed pre-push hook"
}

Write-Info "=== TI Student Agent Pack Installer (Windows) ==="

Clone-OrDownloadRepo
Set-Location $TargetDir

Ensure-Uv

Write-Info "Installing Python 3.11 in uv (user space)..."
uv python install 3.11

Write-Info "Creating project environment with uv..."
uv sync

if (Test-Path "tools/init_exercises.py") {
  Write-Info "Initializing exercise files..."
  uv run python tools/init_exercises.py
}

Configure-OpenCodeProject
Configure-McpJson ".cursor/mcp.json" "mcpServers"
Configure-McpJson ".vscode/mcp.json" "servers"
Configure-OpenRouterEnv
Install-LocalGitHook

Write-Success ""
Write-Success "=== Ready to Start ==="
Write-Success "Open this folder in VS Code/Cursor/OpenCode and run:"
Write-Success "  uv run python tools/startup_check.py"
Write-Success ""
Write-Info "If OpenCode is not installed, continue with your existing coding agent."
