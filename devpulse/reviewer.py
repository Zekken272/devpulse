"""Ollama AI review engine for DevPulse."""

import requests
import json
from dataclasses import dataclass, field


OLLAMA_BASE_URL = "http://localhost:11434"


SYSTEM_PROMPT = """You are a senior software engineer performing a thorough code review.
You will be given a git diff. Analyze it and respond ONLY in the following format,
with no extra text before or after:

ISSUES
------
List any bugs, logic errors, or broken code. If none, write "None found."

SUGGESTIONS
-----------
List improvements for readability, performance, or best practices. If none, write "None found."

SECURITY
--------
List any security vulnerabilities, exposed secrets, or unsafe patterns. If none, write "None found."

SUMMARY
-------
One sentence describing the overall quality of the changes.

Be concise. Reference specific line numbers when possible.
Respond in: {language}"""


@dataclass
class ReviewResult:
    """Structured result returned from the AI review."""
    issues: str = ""
    suggestions: str = ""
    security: str = ""
    summary: str = ""
    model: str = ""
    error: str = ""

    @property
    def has_error(self) -> bool:
        return bool(self.error)

    @property
    def issue_count(self) -> int:
        if not self.issues or self.issues.strip() == "None found.":
            return 0
        return len([l for l in self.issues.strip().splitlines() if l.strip()])

    @property
    def suggestion_count(self) -> int:
        if not self.suggestions or self.suggestions.strip() == "None found.":
            return 0
        return len([l for l in self.suggestions.strip().splitlines() if l.strip()])

    @property
    def security_count(self) -> int:
        if not self.security or self.security.strip() == "None found.":
            return 0
        return len([l for l in self.security.strip().splitlines() if l.strip()])


def check_ollama_running() -> bool:
    """Return True if the Ollama server is reachable."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except requests.ConnectionError:
        return False


def list_available_models() -> list[str]:
    """Return a list of model names currently pulled in Ollama."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        response.raise_for_status()
        data = response.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def parse_review_response(raw_text: str) -> dict[str, str]:
    """
    Parse the structured AI response into a dictionary of sections.
    Gracefully handles partially malformed responses.
    """
    sections = {
        "issues": "",
        "suggestions": "",
        "security": "",
        "summary": "",
    }

    section_markers = {
        "ISSUES": "issues",
        "SUGGESTIONS": "suggestions",
        "SECURITY": "security",
        "SUMMARY": "summary",
    }

    current_key = None
    buffer: list[str] = []

    for line in raw_text.splitlines():
        stripped = line.strip()

        # Check if this line is a section header
        matched_header = None
        for marker, key in section_markers.items():
            if stripped.upper().startswith(marker):
                matched_header = key
                break

        if matched_header:
            # Save previous buffer into the previous section
            if current_key and buffer:
                # Strip dashes and blank lines from content
                content = "\n".join(
                    l for l in buffer if not set(l.strip()) <= {"-"}
                ).strip()
                sections[current_key] = content
            current_key = matched_header
            buffer = []
        else:
            if current_key is not None:
                buffer.append(line)

    # Save the last section
    if current_key and buffer:
        content = "\n".join(
            l for l in buffer if not set(l.strip()) <= {"-"}
        ).strip()
        sections[current_key] = content

    return sections


def review_diff(
    diff: str,
    model: str = "mistral",
    language: str = "English",
) -> ReviewResult:
    """
    Send a git diff to Ollama for AI-powered code review.

    Args:
        diff: The raw git diff string to review.
        model: The Ollama model name to use.
        language: Language for the review response.

    Returns:
        A ReviewResult with structured feedback.
    """
    if not check_ollama_running():
        return ReviewResult(
            error=(
                "Ollama is not running.\n"
                "Start it with: ollama serve\n"
                "Then make sure you have a model pulled: ollama pull mistral"
            )
        )

    available = list_available_models()
    # Match partial names e.g. "mistral" matches "mistral:latest"
    matched_model = next(
        (m for m in available if m.startswith(model)), None
    )

    if not matched_model:
        available_str = ", ".join(available) if available else "none"
        return ReviewResult(
            error=(
                f"Model '{model}' not found in Ollama.\n"
                f"Available models: {available_str}\n"
                f"Pull it with: ollama pull {model}"
            )
        )

    system = SYSTEM_PROMPT.format(language=language)
    prompt = f"Here is the git diff to review:\n\n{diff}"

    payload = {
        "model": matched_model,
        "system": system,
        "prompt": prompt,
        "stream": True,
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            stream=True,
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return ReviewResult(
            error="Ollama request timed out. The model may be too slow — try a smaller one."
        )
    except requests.exceptions.RequestException as e:
        return ReviewResult(error=f"Request to Ollama failed: {e}")

    # Collect streamed response chunks
    full_text = []
    try:
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_text.append(chunk["response"])
                if chunk.get("done"):
                    break
    except Exception as e:
        return ReviewResult(error=f"Failed to read Ollama stream: {e}")

    raw_output = "".join(full_text)
    parsed = parse_review_response(raw_output)

    return ReviewResult(
        issues=parsed["issues"],
        suggestions=parsed["suggestions"],
        security=parsed["security"],
        summary=parsed["summary"],
        model=matched_model,
    )