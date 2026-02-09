# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SRMP AutoSign is an automated sign-in/task completion system that uses a pipeline-based architecture. It supports multiple platforms (QQ, 163 Mail, TapTap, etc.) and provides both CLI and web interface options.

## Architecture

### Pipeline System

The core architecture is built around a pipeline system defined in `src/manager/pipeline.py`:

- **Pipeline Definition**: Each platform/task has a JSON configuration in `assets/resource/pipeline/` defining the workflow steps
- **Pipeline Stages**: Each pipeline consists of stages that execute sequentially (fetch -> parse -> checkin -> notification)
- **Stage Types**:
  - `request`: HTTP requests to external APIs
  - `action`: Custom Python functions for complex logic
  - `check`: Validate response data before proceeding
  - `notification`: Send alerts (Telegram, Bark, ServerChan, etc.)

### Key Components

- **`src/manager/pipeline.py`**: Pipeline engine that loads configs and executes stages
- **`src/manager/bot.py`**: Manages user credentials and runs pipelines
- **`src/web/`**: Web interface (Flask-based) for user management and manual execution
- **`src/interface/`**: Legacy interface definitions (being migrated to pipeline system)
- **`assets/`**:
  - `interface.json`: Schema definitions and API endpoint configurations
  - `resource/pipeline/`: Pipeline JSON configs for each platform
  - `resource/interface/`: Legacy interface configs

### Notification System

Notifications are sent through multiple channels configured in `assets/interface.json`:
- Telegram
- Bark (iOS)
- ServerChan
- Wecom
- SMTP Email
- PushPlus
- Lark
- DingTalk

## Development Commands

### Python Environment
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py                    # CLI mode
python main.py --mode web         # Web interface mode
```

### Running Tests
```bash
pytest                            # Run all tests
pytest tests/                     # Run tests in directory
pytest tests/test_file.py         # Run specific test file
pytest -k "test_name"             # Run tests matching pattern
```

### Code Quality
```bash
ruff check src/                   # Lint code
ruff format src/                  # Format code
```

## Pipeline Configuration Format

Pipelines are JSON files in `assets/resource/pipeline/` with this structure:

```json
{
  "pipeline": [
    {
      "type": "request|action|check|notification",
      "name": "stage_name",
      "url": "...",
      "method": "GET|POST",
      "headers": {...},
      "params": {...},
      "data": {...},
      "conditions": {...},
      "notification": {...}
    }
  ]
}
```

## Adding a New Platform

1. Create a pipeline JSON in `assets/resource/pipeline/{platform}.json`
2. Add the platform to `assets/interface.json` if needed
3. Implement any custom actions in `src/manager/pipeline.py` under the action functions
4. Test locally with CLI: `python main.py --single {username} --pipelines {platform}`

## Important Notes

- The project is migrating from the legacy interface system to the new pipeline-based system
- Old interface configs in `assets/resource/interface/` are being removed
- Pipeline configs support Jinja2 templating for dynamic values
- User credentials are stored in `assets/user.json` (never commit this file)
- The web interface runs on port 5000 by default
