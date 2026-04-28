"""Configuration loader for DevPulse."""

from pathlib import Path
from dataclasses import dataclass, field

try:
    import tomllib  # Python 3.11+ built-in
except ImportError:
    import tomli as tomllib  # fallback for older versions


DEFAULT_CONFIG_FILENAME = ".devpulse.toml"


@dataclass
class DevPulseConfig:
    """Holds all DevPulse configuration values."""
    model: str = "mistral"
    max_lines: int = 500
    review_language: str = "English"
    fail_on: list[str] = field(default_factory=list)
    ignore_files: list[str] = field(default_factory=list)


def find_config_file(start_path: str = ".") -> Path | None:
    """Walk up directory tree to find a .devpulse.toml file."""
    current = Path(start_path).resolve()
    for directory in [current, *current.parents]:
        candidate = directory / DEFAULT_CONFIG_FILENAME
        if candidate.exists():
            return candidate
    return None


def load_config(config_path: str | None = None) -> DevPulseConfig:
    """
    Load DevPulse configuration from a TOML file.
    Falls back to defaults if no config file is found.
    
    Args:
        config_path: Explicit path to a config file. If None, auto-discovers.
        
    Returns:
        A DevPulseConfig instance with merged values.
    """
    config = DevPulseConfig()

    path = Path(config_path) if config_path else find_config_file()

    if path is None or not path.exists():
        return config  # Return defaults silently
    
    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    # Merge file values into config, ignoring unknown keys
    if "model" in data:
        config.model = str(data["model"])
    if "max_lines" in data:
        config.max_lines = int(data["max_lines"])
    if "review_language" in data:
        config.review_language = str(data["review_language"])
    if "fail_on" in data:
        config.fail_on = list(data["fail_on"])
    if "ignore_files" in data:
        config.ignore_files = list(data["ignore_files"])

    return config