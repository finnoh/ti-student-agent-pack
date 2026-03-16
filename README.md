# TI Student Agent Pack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Portable, self-contained workspace for Tinbergen Institute workshop exercises (AI Agents in Economics and Business Research).

## Quick Start

### Option 1: Download and Install (Recommended for Students)

1. Download the latest release zip file from [GitHub releases](https://github.com/finnoh/ti-student-agent-pack/releases)
2. Extract it to a new folder (e.g., `student-agent-pack`)
3. Open a terminal in that folder
4. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Option 2: One-line Install (Linux/macOS)

**Note:** This method downloads the install script only. You'll still need to download the full zip file.

```bash
curl -sL https://raw.githubusercontent.com/finnoh/ti-student-agent-pack/main/install.sh -o install.sh
chmod +x install.sh
# Then download the zip file from GitHub releases and extract it
# Finally run: ./install.sh
```

### Option 3: Use the GitHub Repository

Visit [github.com/finnoh/ti-student-agent-pack](https://github.com/finnoh/ti-student-agent-pack) for the latest release and instructions.

## What's Included

- **Exercise files** (E1-E8) - Pre-created templates for all workshop exercises
- **Submission tools** - Python scripts for submitting exercises to Google Forms
- **Coaching agent** (`AGENTS.md`) - Personalized tutor that guides you through exercises
- **Progress dashboard** - ASCII dashboard showing your progress
- **Course Q&A tool** - Ask questions about course materials
- **Startup checker** - Verifies your environment is ready

## For Students

1. Download and extract the zip file
2. Open the folder in your coding agent (VS Code, Cursor, etc.)
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

- **Full instructions**: See `README.md` in the extracted folder
- **Coaching guide**: See `AGENTS.md`
- **Workshop materials**: Visit [Tinbergen Institute Workshop Site](https://finnoh.github.io/ws_genai_eb/)

## System Requirements

- Python 3.8 or higher
- Internet connection (for course material indexing and submission)
- Optional: `uv` for faster Python environment management

## License

MIT License - See LICENSE file for details

## Contributing

This pack is maintained as part of the Tinbergen Institute AI Agents workshop. For issues or suggestions, please open an issue on the main workshop repository.
