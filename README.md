# Pico (I have a vision with ts)

A lightweight, cross‑platform AI assistant for your terminal with TUI, workflows, web search, and file operations. Works on Linux, macOS, and Windows.

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Features

- **TUI Mode** — Interactive terminal UI with markdown rendering, syntax highlighting, scrollback, and animations
- **One‑Shot Mode** — Pipe questions or run from scripts: `echo "question" | pico`
- **Workflow System** — Create and execute multi‑step plans (saved as JSON)
- **Web Search** — Built‑in DuckDuckGo search (no API key needed), with per‑result title/URL/snippet parsing and a lite‑endpoint fallback
- **File Operations** — Read, write, edit, and search files anywhere on disk (`C:\`, `D:\`, `/mnt/...`)
- **Shell Commands** — Run commands safely with sandboxing
- **Cross‑Platform** — Works on Linux, macOS, and Windows
- **Dual API Support** — OpenRouter **and** NVIDIA NIM API, switchable live from the web UI (no restart needed)

## Desktop Pet (Windows)

A new optional feature adds a whimsical "desktop pet" that lives on your Windows desktop.

### Installation

```bash
# Install Pico with the optional GUI dependencies
pip install "pico[gui]"
```

### Usage

```bash
# Run the pet (adds a system‑tray icon for control)
 pico pet
```

The pet animates using the PNG sprites found in `pico/desktop/sprites/`.

#### Controls
- **Drag** — Click and drag the pet to reposition it.
- **Double‑click** — Toggles between idle and sleep animation.
- **System tray menu** — Show/Hide, toggle *click‑through* (allow mouse events to pass to windows beneath), and Quit.

#### Configuration (edit `~/.config/pico/config.json` or modify defaults in `pico/config.py`)
- `PET_DEFAULT_POS` — Starting screen coordinates, e.g. `[200, 100]`.
- `PET_SCALE` — Sprite scaling factor (default `1.0`).
- `PET_CLICK_THROUGH_DEFAULT` — Start with click‑through enabled (`true`/`false`).
- `PET_AUTO_START` — Create a shortcut in the Windows Startup folder so the pet launches on login (`true`/`false`).
- `PET_IDLE_TIMEOUT` — Seconds of inactivity before automatically switching to the sleep animation.

### Building a Windows executable

A PyInstaller spec (`pico/desktop/pyinstaller_pet.spec`) is provided to bundle the pet into a single‑file `pico-pet.exe` that includes the required Qt libraries and sprite resources.

```bash
pip install pyinstaller
pyinstaller pico/desktop/pyinstaller_pet.spec
```

The generated executable can be distributed without requiring a Python interpreter on the target machine.

### Testing

Run the unit tests with:

```bash
pytest -m pet
```
The tests use `pytest-qt` to verify the window flags, animation timers, and tray‑menu behavior.

---

## Installation

```bash
# From PyPI (when published)
pip install pico

# From source
git clone https://github.com/Abhinav-Sharmaaaa/Pico.git
cd Pico
pip install -e .
```

## Quick Start

### OpenRouter (Default)

```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Run TUI (interactive) — launches automatically when stdin is a real terminal and no args are given
pico

# Force TUI explicitly (e.g. from a wrapper script)
pico --tui

# One‑shot mode
pico "what is the latest Python version?"

# Pipe input
echo "explain asyncio" | pico

# System status
pico --status

# Help
pico --help

# Web UI for configuration and logs
pico-web
```

### NVIDIA NIM API

```bash
# Set NVIDIA API key (get from https://build.nvidia.com)
export NVIDIA_API_KEY="nvapi-..."
export LINAI_API_PROVIDER="nvidia_nim"

# Optional: custom NIM endpoint (default: https://integrate.api.nvidia.com/v1)
export NVIDIA_NIM_API_URL="https://your-nim-endpoint/v1"

# Optional: model override
export LINAI_NVIDIA_NIM_MODEL="nvidia/nemotron-3-ultra"

pico
```

## Web UI

```bash
# Start web UI for configuration and logs
pico-web

# Custom port
pico-web 8080
```

The web UI runs at `http://127.0.0.1:8765` and provides:
- **Configuration Panel** — Set API keys, choose provider (OpenRouter/NVIDIA NIM) via a toggle, select models. Switching providers here takes effect immediately — no restart needed.
- **Logs Viewer** — Real‑time log streaming with filtering
- **Workflow Manager** — Create, list, execute workflows visually
- **System Dashboard** — Disk, memory, CPU, uptime
- **API Connection Tester** — Tests against whatever's currently in the form (not just the last‑saved config)
- **Model Browser** — Browse available models with pricing

## Usage

### TUI Hotkeys

> **Note:** only `pico` (bare, in a real terminal) or `pico --tui` actually launch the TUI. A `pico tui` subcommand isn't currently implemented in `cli.py` despite being mentioned in `--help`'s usage text — that's a known doc/behavior mismatch, not something you're doing wrong.

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Ctrl+C` | Cancel streaming |
| `Ctrl+D` / `Esc` | Quit |
| `Ctrl+L` | Clear screen |
| `Ctrl+M` | Model picker |
| `Ctrl+H` | Help overlay |
| `Ctrl+Y` | Copy output to clipboard |
| `↑/↓` | Input history |
| `PgUp/PgDn` | Scroll output |

### TUI Commands

Type these at the prompt:

| Command | Alias | Action |
|---------|-------|--------|
| `/model` | `/m` | Model picker |
| `/status` | `/s` | System snapshot |
| `/context` | `/c` | Token budget |
| `/clear` |  | Reset conversation |
| `/help` |  | Help screen |
| `/workflows` | `/w` | List saved workflows |

### Workflow Tools (available to the model)

The AI can create and execute multi‑step workflows:

```json
// create_workflow
{
  "name": "Python Version Check",
  "description": "Find latest Python version and save summary",
  "steps": [
    {"name": "search", "tool": "web_search", "args": {"query": "latest Python version 2024"}, "description": "Search for latest version"},
    {"name": "write", "tool": "write_file", "args": {"path": "python_version.md", "content": "# Python Version\n\n..."}, "description": "Write markdown file"}
  ]
}
```

### One‑Shot Examples

```bash
# Quick questions
pico "how to create a virtualenv in Python?"
pico "what's new in Python 3.13?"

# File operations
pico "read my ~/.bashrc and suggest improvements"
pico "create a Python script that fetches Bitcoin price"
pico "search for pokemon files in D drive"

# System tasks
pico "check disk space and clean caches"
pico "run: git status && git diff --stat"

# Web search
pico "latest Rust release notes"
pico "compare React vs Vue 2024"
```

## Configuration

Config file: `~/.config/pico/config.json`

```json
{
  "provider": "openrouter",
  "openrouter_key": "sk-or-v1-...",
  "nvidia_key": "",
  "nvidia_url": "https://integrate.api.nvidia.com/v1",
  "model": "google/gemma-4-26b-a4b-it:free",
  "nvidia_model": "nvidia/nemotron-3-ultra",
  "temperature": 0.2,
  "max_tokens": 1000
}
```

`provider` is the active toggle (`openrouter` or `nvidia_nim` — `nvidia` is also accepted as an alias). Whichever provider is active determines which key/model field is actually used (`openrouter_key`/`model` vs `nvidia_key`/`nvidia_model`). `config.json` is read fresh on every request and takes priority over environment variables — editing it (directly or via the web UI) takes effect immediately, no restart required.

### Environment Variables

Environment variables are used as a **fallback** for any field left empty in `config.json` (e.g. if you've never opened the web UI, or deliberately keep secrets out of the config file).

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key (used if `openrouter_key` is empty in config.json) |
| `NVIDIA_API_KEY` / `NVIDIA_NIM_API_KEY` | NVIDIA NIM API key (used if `nvidia_key` is empty in config.json) |
| `LINAI_API_PROVIDER` | `openrouter` (default) or `nvidia_nim` — only used if `provider` is unset in config.json |
| `LINAI_MODEL` | Default model override |
| `LINAI_OPENROUTER_MODEL` | OpenRouter default model |
| `LINAI_NVIDIA_NIM_MODEL` | NVIDIA NIM default model |
| `NVIDIA_NIM_API_URL` / `NVIDIA_API_URL` | Custom NIM endpoint |
| `NO_COLOR` | Disable colors |

## Switching Providers

The easiest way is the web UI toggle (`pico‑web`) — it writes straight to `config.json` and applies on your very next message.

You can also switch via environment variables, but note these are only used as a fallback for whatever `config.json` doesn't already specify:

```bash
# Use OpenRouter (default)
export LINAI_API_PROVIDER="openrouter"
export OPENROUTER_API_KEY="sk-or-v1-..."

# Use NVIDIA NIM
export LINAI_API_PROVIDER="nvidia_nim"
export NVIDIA_API_KEY="nvapi-..."
```

## Architecture

```
pico/
├── agent.py      # API calls (streaming + non‑streaming, dual provider)
├── cli.py        # CLI entry point, one‑shot + TUI routing
├── config.py     # Config, constants, API key management
├── tools.py      # Tool definitions + implementations
├── utils.py      # Colors, wrapping, system status, model cache
└── tui/
    ├── app.py    # TUI rendering, input, markdown rendering
    └── keys.py   # Raw key input handling
```

## Free Models (OpenRouter)

| Model | Context | Best For |
|-------|---------|----------|
| `meta-llama/llama-3.1-8b-instruct:free` | 128k | General chat, coding |
| `google/gemma-2-9b-it:free` | 8k | Fast responses |
| `microsoft/phi-3-mini-128k-instruct:free` | 128k | Long context |
| `nousresearch/hermes-3-llama-3.1-8b:free` | 128k | Reasoning |

Set default: `export LINAI_MODEL="meta-llama/llama-3.1-8b-instruct:free"`

## NVIDIA NIM Models

Popular NIM models (require NVIDIA API key):

- `nvidia/nemotron-3-ultra` — Best reasoning
- `nvidia/nemotron-3-super` — Strong performance
- `nvidia/nemotron-3-nano` — Fast, efficient
- `meta/llama-3.1-8b-instruct` — Meta's model on NIM
- `google/gemma-2-9b` — Google's model on NIM

See [NVIDIA NGC Catalog](https://build.nvidia.com) for full list.

## Windows Support

- Uses `Path.home()` for cross‑platform paths
- File tools accept any absolute path, including bare drive letters (`D:`, `D:\`) which are normalized to that drive's root
- Windows‑specific system status (disk, memory, uptime via WMI/PowerShell)
- Windows cache locations in `clean_cache`
- Color support via ANSI (Windows 10+)
- TUI works in Windows Terminal, ConEmu, etc.

## License

MIT — see [LICENSE](LICENSE)

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes with tests
4. Submit PR

---

**Pico** — Your terminal AI companion. 🤖