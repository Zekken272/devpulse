"""Git diff extraction utilities."""

import git
from git.exc import InvalidGitRepositoryError, GitCommandError


# Files that are never useful to review
IGNORED_EXTENTIONS = {
    ".lock", ".min.js", ".min.css", ".map",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".exe", ".bin",
}

IGNORED_FILENAMES = {
    "package-lock.json", "yarn.lock", "poetry.lock",
    "Pipfile.lock", "pnpm-lock.yaml",
}


def get_repo(path: str = ".") -> git.Repo:
    """Open the Git repository at the given path, searching parent directories."""
    try:
        return git.Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError(
            f"No Git repository found at '{path}' or any parent directory.\n"
            "Make sure you run DevPulse inside a Git project."
        )
    
def should_ignore_file(filename: str) -> bool:
    """Return True if a file should be skipped during review."""
    from pathlib import Path
    p = Path(filename)
    if p.suffix.lower() in IGNORED_EXTENTIONS:
        return True
    if p.name in IGNORED_FILENAMES:
        return True
    return False


def filter_diff(raw_diff: str, max_lines: int = 500) -> str:
    """
    Remove ignored files from a raw diff string and enforce a line limit.
    Returns a cleaned diff string.
    """
    if not raw_diff.strip():
        return ""
    
    sections = []
    current_section = list[str] = []
    current_file = None
    skip_current = False

    for line in raw_diff.splitlines():
        # Detect start of a new file section
        if line.startswith("diff --git"):
            # Save the previous section if it wasn't skipped
            if current_section and not skip_current:
                sections.append("\n".join(current_section))
            
            current_section = [line]
            current_file = line.split(" b/")[-1] if " b/" in line else None
            skip_current = should_ignore_file(current_file) if current_file else False
        else:
            current_section.append(line)
    
    # Don't forget the last section
    if current_section and not skip_current:
        sections.append("\n".join(current_section))
    
    full_diff = "\n".join(sections)

    # Enforce line limit to avoid overwhelming the model
    lines = full_diff.splitlines()
    if len(lines) > max_lines:
        truncated = lines[:max_lines]
        truncated.append(
            f"\n... [Diff truncated at {max_lines} lines. "
            "Use --max-lines to increase the limit.] ..."
        )
        return "\n".join(truncated)
    
    return full_diff


def get_diff(staged: bool = False, repo_path: str = ".", max_lines: int = 500) -> str:
    """
    Extract the current git diff from the repository.
    
    Args:
        staged: If True, return only staged (cached) changes.
        repo_path: Path to the repository root.
        max_lines: Maximum number of diff lines to return.
        
    Returns:
        A filtered, cleaned diff string ready for AI review.
    
    Raises:
        RuntimeError: If no Git repository is found or diff fails.
    """
    repo = get_repo(repo_path)

    try:
        if staged:
            raw = repo.git.diff("--cached")
        else:
            raw = repo.git.diff()
    except GitCommandError as e:
        raise RuntimeError(f"Git command failed: {e}")
    
    return filter_diff(raw, max_lines=max_lines)