# Prompt Refiner

A web-based prompt engineering assistant that helps you iteratively test and refine your LLM prompts. Enter a system prompt, user prompt, and intended goal, then test against a variety of models. Provide feedback on the LLM’s response to generate improved system prompts—repeat until you’re satisfied.

---

## Table of Contents

- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- Test any system + user prompt against multiple LLM backends (OpenAI, Anthropic).
- Instant in-browser results with syntax-highlighted response.
- Iteration history with timestamps.
- One-click “Refine System Prompt” to generate improved prompts based on your feedback.
- Memory of all iterations during your session.

---

## Prerequisites

- Python >= 3.13  
- [uv CLI](https://docs.astral.sh/uv/getting-started/installation/) (for dependency management & server)  
- Valid LLM API key(s):
  - `OPENAI_API_KEY` for OpenAI models
  - `ANTHROPIC_API_KEY` for Anthropic Claude models (if you wish to use Claude)

---

## Installation

```bash
git clone https://github.com/ohnotnow/prompt-refiner.git
cd prompt-refiner
uv sync
```

---

## Configuration

Create a `.env` file in the project root (or export env vars in your shell):

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=ak-...
```

The project uses [litellm](https://github.com/astral-sh/litellm) under the hood; it will automatically pick up these environment variables.

---

## Usage

```bash
# Start the development server
uv run main.py
```

By default, the app listens on `http://localhost:8000/`.  
Open that URL in your browser to begin testing and refining prompts.

---

## Contributing

1. Fork the repository  
2. Create a feature branch  
   ```bash
   git checkout -b feature/my-cool-feature
   ```
3. Make your changes & add tests  
4. Run `uv run main.py` to verify everything works  
5. Commit, push, and open a Pull Request  

Please follow PEP 8 style guidelines and include docstrings for new functions.

---

## License

This project is licensed under the MIT License.  
See [LICENSE](LICENSE) for details.

