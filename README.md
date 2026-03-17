# TI Student Agent Pack

Portable, self-contained workspace for Tinbergen Institute workshop exercises.

## Quick Start

### Option 1: One-line Install (Recommended)

```bash
curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
```

This will:
1. Clone the repository to `student-agent-pack/` directory
2. Set up your environment
3. Optionally install OpenCode (coding agent)

**Requirements:**
- Git (for cloning)
- Python 3.8+

### Option 2: Manual Installation

1. Download the zip file from [GitHub releases](https://github.com/finnoh/ti-student-agent-pack/releases)
2. Extract it to a new folder
3. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## What's Included

- **Exercise files (E1-E8)** - Pre-created templates for all workshop exercises
- **Submission tools** - Python scripts for submitting exercises
- **Jan coaching agent** (`AGENTS.md`) - Your AI tutor
- **Progress dashboard** - Track your exercise completion
- **Course Q&A tool** - Ask questions about course materials

## Next Steps

1. Open the `student-agent-pack/` folder in your coding agent (VS Code, Cursor, OpenCode, etc.)
2. Edit `config/form_config.json` with your Google Form details
3. Complete `BOOTSTRAP.md` with your information
4. Start working on exercises in the `work/` directory

## Jan - Your AI Tutor

Jan is your AI tutor for the Tinbergen Institute workshop.
When you open Jan, it guides you through exercises with concise step-by-step coaching.

## More Information

- Full documentation: See `AGENTS.md`
- Workshop materials: Visit [Tinbergen Institute Workshop Site](https://finnoh.github.io/ws_genai_eb/)
