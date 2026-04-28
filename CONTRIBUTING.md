# Contributing to DevPulse

Thank you for considering contributing! Here's how to get started.

---

## 🛠️ Local Setup

1. **Fork** this repository on GitHub
2. **Clone** your fork:
```bash
   git clone https://github.com/YOUR-USERNAME/devpulse.git
   cd devpulse
```
3. **Create a virtual environment and install dependencies:**
```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
```
4. **Verify everything works:**
```bash
   pytest tests/ -v
   devpulse --help
```

---

## 🌿 Branching

- Never commit directly to `main`
- Create a branch for every change:
```bash
  git checkout -b feature/your-feature-name
```

Branch naming conventions:

| Prefix | When to use |
|--------|-------------|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation only |
| `chore/` | Tooling, CI, config |
| `test/` | Adding or fixing tests |

---

## 💬 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):
Examples:
    feat(reviewer): add support for llama3 model
    fix(git_utils): handle repos with no commits
    docs(readme): add VS Code extension roadmap item
    test(reviewer): add test for timeout handling

---

## ✅ Before Opening a Pull Request

- [ ] All tests pass: `pytest tests/ -v`
- [ ] No lint errors: `ruff check .`
- [ ] New features have matching tests
- [ ] Public functions have docstrings
- [ ] `README.md` updated if user-facing behavior changed

---

## 🔀 Opening a Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Open a PR on GitHub against `main`
3. Fill in the PR description — what does it change and why?
4. Wait for CI to pass before requesting review