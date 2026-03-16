# TI Student Agent Pack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Portable, self-contained workspace for Tinbergen Institute workshop exercises (AI Agents in Economics and Business Research).

## Quick Start

### Option 1: One-line Install (Linux/macOS)

```bash
curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh | bash
```

### Option 2: Download and Install

1. Download the latest release zip file
2. Extract it to a folder of your choice
3. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Option 3: Use in Your Project

1. Download this repository as a zip file
2. Extract it
3. Open the `student-agent-pack` folder in your coding agent (VS Code, Cursor, etc.)
4. Follow the instructions in `AGENTS.md` for coaching

## What's Included

- **Exercise files** (E1-E8) - Pre-created templates for all workshop exercises
- **Submission tools** - Python scripts for submitting exercises to Google Forms
- **Coaching agent** (`AGENTS.md`) - Personalized tutor that guides you through exercises
- **Progress dashboard** - ASCII dashboard showing your progress
- **Course Q&A tool** - Ask questions about course materials
- **Startup checker** - Verifies your environment is ready

## For Students

1. Unzip this folder
2. Open it in your coding agent
3. Follow the coaching instructions in `AGENTS.md`
4. Write exercises in the `work/` directory
5. Submit with: `python tools/submit_exercise.py --from-markdown work/E1.md`

## For Instructors

To customize the pack with your Google Form configuration:

1. Edit `config/form_config.json` with your Google Form URL and field IDs
2. Share the zip file with students

Or use the automated setup script:

```bash
./scripts/google/bootstrap_workshop.sh --write-env-file website/.env.local
python scripts/course_pack/sync_student_pack_form_config.py --env-file website/.env.local
```

## Documentation

- **Full instructions**: See `README.md` in the `student-agent-pack` folder after extraction
- **Coaching guide**: See `AGENTS.md` in the `student-agent-pack` folder
- **Workshop materials**: Visit [Tinbergen Institute Workshop Site](https://finnoh.github.io/ws_genai_eb/)

## System Requirements

- Python 3.8 or higher
- Internet connection (for course material indexing and submission)
- Optional: `uv` for faster Python environment management

## License

MIT License - See LICENSE file for details

## Contributing

This pack is maintained as part of the Tinbergen Institute AI Agents workshop. For issues or suggestions, please open an issue on the main workshop repository.
