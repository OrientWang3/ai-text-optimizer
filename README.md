<p align="center">
<h1 align="center">AI Text Optimizer</h1>
</p>
<p align="center">
  <a href="https://img.shields.io/badge/version-v1.0.1-blue">
    <img alt="version" src="https://img.shields.io/badge/version-v1.0.1-blue?color=009922" />
  </a>
  <a>
    <img alt="platform" src="https://img.shields.io/badge/platform-Windows-blue?color=0078D6" />
  </a>
  <a>
    <img alt="license" src="https://img.shields.io/badge/license-MIT-red" />
  </a>
  <a>
    <img alt="PRs-Welcome" src="https://img.shields.io/badge/PRs-Welcome-green" />
  </a>
  <br />
</p>

<div align="center">
<p align="center">
  <a href="#motivation">Motivation</a>/
  <a href="#design">Design</a>/
  <a href="#quick-start">Quick Start</a>/
  <a href="#structure">Structure</a>/
  <a href="#faq">FAQ</a>
</p>
</div>

> [中文文档](README_zh.md)

## Motivation

In daily work, we constantly face: a cryptic error in the terminal, an email that needs polishing, docs in a foreign language. The usual workflow is: select text → switch to browser → open ChatGPT → paste → wait → copy response → switch back → paste. That's six context switches for one fix.

What if you could just: select text, press one key, done?

That's this tool. It's not "yet another AI wrapper" — it's a **system-level productivity utility**: tray-resident, globally hotkeyed, works in any application.

## Design

### Workflow

```
Select text → Ctrl+Shift+Q → AI analyzes → result window → one-click copy
```

You never leave the current application.

### Context Awareness

Before sending text to AI, the analyzer extracts:

| Dimension | What it detects | Used for |
|-----------|----------------|----------|
| Source app | Foreground window (VS Code, Chrome, Terminal, etc.) | Tailored prompt generation |
| Content type | Error, code, log, config, or plain text | Automatic template selection |
| Language | Python, JS, Java, Go, Rust, SQL, and more | Informing AI of language context |

This means you don't need to manually pick a template — the tool figures out what kind of text you selected.

### Multi-Provider Support

| Provider | Models | Notes |
|----------|--------|-------|
| OpenAI | GPT-4, GPT-4-turbo, GPT-3.5-turbo | OpenAI API compatible |
| DeepSeek | deepseek-chat, deepseek-coder | Cost-effective |
| Zhipu AI | GLM-4, GLM-4-flash | Chinese LLM |
| Moonshot | moonshot-v1-8k/32k/128k | Ultra-long context |
| Qwen | qwen-turbo, qwen-plus, qwen-max | Alibaba Cloud |
| Claude | claude-3-opus/sonnet | Anthropic |
| Ollama | llama3, codellama, mistral | Local, free |

Any service compatible with OpenAI's `/v1/chat/completions` endpoint works.

### Built-in Templates

10 preset templates covering common dev tasks:

| Template | Category | Use case |
|----------|----------|----------|
| Code Fix | Code | Analyze errors, provide fix |
| Code Optimize | Code | Improve performance & readability |
| Code Explain | Code | Explain what code does |
| Code Review | Code | Review quality, suggest improvements |
| Bug Debug | Debug | Systematic issue tracing |
| Stack Trace | Debug | Parse stack traces, find root cause |
| Config Fix | Config | Diagnose & fix configuration |
| Log Analyze | Log | Extract insights from logs |
| Translate | General | Translate selected text |
| Summarize | General | Extract key points |

Custom templates can be added/edited/deleted via the UI, with `{text}`, `{source}`, `{language}` variables.

## Quick Start

### Requirements

- Windows 10/11
- Python 3.10+

### Install

```bash
git clone https://github.com/yourusername/ai-text-optimizer.git
cd ai-text-optimizer
pip install -r requirements.txt
```

### Configure

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "ai_service": {
    "provider": "openai_compatible",
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4"
  },
  "hotkey": {
    "trigger": "ctrl+shift+q"
  }
}
```

Or right-click the tray icon → Settings after launch.

### Run

```bash
python main.py
```

A tray icon appears. Press `Ctrl+Shift+Q` to start using.

### Build EXE

```bash
pip install pyinstaller
python build.py
```

Output: `dist/AI文本优化器.exe`

## Structure

```
ai-text-optimizer/
├── main.py                   # Entry point, lifecycle management
├── config.py                 # JSON config with dot-path access
├── ai_service.py             # AI adapter (OpenAI + Claude protocols)
├── prompt_templates.py       # Template manager (built-in + custom)
├── context_analyzer.py       # Window detection + text classification
├── clipboard.py              # Clipboard ops (Ctrl+C simulation)
├── hotkey.py                 # Global hotkey listener (dynamic keys)
├── text_cleaner.py           # Markdown → plain text
├── language.py               # zh/en bilingual support
├── logger.py                 # Structured logging (console + file)
├── icons.py                  # Programmatic icon generation (Pillow)
├── build.py                  # PyInstaller build script
├── tests/                    # Unit tests (pytest, 29 cases)
└── ui/
    ├── floating_window.py    # AI result popup
    ├── settings_window.py    # Settings panel
    ├── hotkey_window.py      # "Press to set" hotkey recorder
    ├── template_window.py    # Template browser & editor
    └── tray.py               # System tray icon & menu
```

## FAQ

**Q: Hotkey not working?**

Another app may be using the same combo (e.g., screenshot tools). Right-click tray → Hotkey settings → record a new combo.

**Q: AI returns Markdown formatting?**

The built-in cleaner strips bold markers, code fences, headings, and link syntax. If artifacts remain, file an issue.

**Q: Which AI services are supported?**

Any OpenAI-compatible API (`/v1/chat/completions`) and Anthropic Claude API. Local Ollama works too.

**Q: How to switch between Chinese and English?**

Right-click tray icon → Language → select. Auto-detects system language on first run.

## License

MIT License

## Disclaimer

You need your own API key for AI services. Keep it safe — `config.json` is gitignored. Never commit API keys to public repositories.

---

If this tool helps you, give it a star ⭐
