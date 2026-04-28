# DevPulse 🔍

> Local AI-powered code review in your terminal — no cloud, no leaks.

![CI](https://github.com/Zekken272/devpulse/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

DevPulse reviews your git diffs using a locally running AI model via [Ollama](https://ollama.com).
Your code never leaves your machine.

---

## ✨ Features

- 🔍 Reviews staged or unstaged git changes instantly
- 🐛 Catches bugs, logic errors, and bad practices
- 🔒 Flags security vulnerabilities and exposed secrets
- 💡 Suggests readability and performance improvements
- ⚙️ Fully configurable via `.devpulse.toml`
- 🖥️ Beautiful terminal output powered by Rich

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Git
- [Ollama](https://ollama.com) with at least one model pulled:

```bash
ollama pull mistral
```

### Install DevPulse

```bash
git clone https://github.com/Zekken272/devpulse.git
cd devpulse
pip install -e .
```

---

## ⚙️ Configuration

Drop a `.devpulse.toml` file in your project root:

```toml
model = "mistral"
max_lines = 500
review_language = "English"
fail_on = []
ignore_files = ["*.lock", "*.min.js", "dist/"]
```

All fields are optional — DevPulse uses sensible defaults if no config is found.

---

## 🧪 Usage

### Review all unstaged changes
```bash
devpulse review
```

### Review staged changes only
```bash
devpulse review --staged
```

### Use a specific model
```bash
devpulse review --model codellama
```

### Plain text output (for piping or CI)
```bash
devpulse review --plain
```

### See what will be sent to the AI
```bash
devpulse diff --staged
```

### List available Ollama models
```bash
devpulse models
```

### Exit with code 1 if security issues are found
```bash
devpulse review --fail-on-security
```

---

## 🔗 Pre-commit Hook Integration

Install pre-commit:
```bash
pip install pre-commit
```

Add to `.pre-commit-config.yaml` in your project:
```yaml
repos:
  - repo: local
    hooks:
      - id: devpulse-review
        name: DevPulse AI Review
        entry: devpulse review --staged
        language: system
        always_run: true
```

Then enable it:
```bash
pre-commit install
```

---

## 🗺️ Roadmap

- [x] Git diff extraction with smart file filtering
- [x] Ollama AI integration with streaming
- [x] Rich terminal UI with color-coded panels
- [x] TOML config file support
- [x] Pre-commit hook integration
- [ ] HTML report export
- [ ] Multi-repo batch review
- [ ] VS Code extension

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.