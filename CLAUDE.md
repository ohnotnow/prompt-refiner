# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web-based prompt engineering assistant built with FastHTML and litellm. It allows iterative testing and refinement of LLM prompts across multiple model providers (OpenAI, Anthropic). The application provides a web interface for testing system prompts, evaluating responses, and generating improved prompts based on user feedback.

## Development Commands

**Start the development server:**
```bash
uv run main.py
```
The application will be available at `http://localhost:8000/`

**Install dependencies:**
```bash
uv sync
```

**Add new dependencies:**
```bash
uv add <package-name>
```

## Environment Configuration

Create a `.env` file in the project root with the required API keys:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=ak-...
```

Both keys are optional - you only need the keys for the models you intend to use. The application uses litellm which automatically detects and uses these environment variables.

## Architecture

**Single-file application:** The entire application logic is contained in `main.py` - this is a FastHTML application with HTMX for dynamic interactions.

**Key components:**
- **FastHTML app** with CSS styling and HTMX endpoints
- **LLM integration** via litellm supporting multiple providers
- **In-memory session storage** in the `iterations` list (not persistent across server restarts)
- **Three main endpoints:** `/` (main form), `/test` (prompt testing), `/refine` (prompt improvement)

**Supported models** are defined in the `MODELS` constant:
- OpenAI: gpt-5-mini, gpt-5, gpt-4.1-mini, gpt-4.1  
- Anthropic: claude-sonnet-4-20250514

**Session data:** All iteration history is stored in the global `iterations` list and will be lost when the server restarts.

## Core Functions

- `test_prompt()`: Sends prompts to selected LLM model via litellm
- `refine_prompt()`: Uses gpt-5-mini to generate improved system prompts based on user feedback
- HTMX endpoints handle the web interface interactions

## Development Notes

- No test suite is configured
- No linting or code quality tools are set up
- The application uses in-memory storage only - consider adding persistent storage for production use
- Model list is hardcoded - update the `MODELS` constant to add new models
- Uses fasthtml.common import which includes most needed components