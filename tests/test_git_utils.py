"""Tests for git_utils module."""

import pytest
from devpulse.git_utils import should_ignore_file, filter_diff


class TestShouldIgnoreFile:
    def test_ignores_lock_files(self):
        assert should_ignore_file("package-lock.json") is True
        assert should_ignore_file("yarn.lock") is True
        assert should_ignore_file("poetry.lock") is True

    def test_ignores_binary_extensions(self):
        assert should_ignore_file("image.png") is True
        assert should_ignore_file("font.woff2") is True
        assert should_ignore_file("archive.zip") is True

    def test_ignores_minified_files(self):
        assert should_ignore_file("app.min.js") is True
        assert should_ignore_file("style.min.css") is True

    def test_allows_source_files(self):
        assert should_ignore_file("main.py") is False
        assert should_ignore_file("index.ts") is False
        assert should_ignore_file("App.jsx") is False
        assert should_ignore_file("README.md") is False

    def test_allows_config_files(self):
        assert should_ignore_file("pyproject.toml") is False
        assert should_ignore_file(".devpulse.toml") is False


class TestFilterDiff:
    def test_returns_empty_for_empty_input(self):
        assert filter_diff("") == ""
        assert filter_diff("   ") == ""

    def test_passes_through_clean_diff(self):
        sample = (
            "diff --git a/main.py b/main.py\n"
            "--- a/main.py\n"
            "+++ b/main.py\n"
            "@@ -1,3 +1,4 @@\n"
            "+import os\n"
            " def hello():\n"
            "     pass\n"
        )
        result = filter_diff(sample)
        assert "main.py" in result
        assert "+import os" in result

    def test_removes_ignored_files(self):
        sample = (
            "diff --git a/package-lock.json b/package-lock.json\n"
            "--- a/package-lock.json\n"
            "+++ b/package-lock.json\n"
            "@@ -1 +1 @@\n"
            '+{"version": 2}\n'
            "diff --git a/main.py b/main.py\n"
            "--- a/main.py\n"
            "+++ b/main.py\n"
            "@@ -1 +1 @@\n"
            "+print('hello')\n"
        )
        result = filter_diff(sample)
        assert "package-lock.json" not in result
        assert "main.py" in result

    def test_truncates_at_max_lines(self):
        long_diff = "diff --git a/big.py b/big.py\n"
        long_diff += "\n".join([f"+line {i}" for i in range(600)])
        result = filter_diff(long_diff, max_lines=100)
        assert "truncated" in result.lower()
        assert len(result.splitlines()) < 200

    def test_respects_custom_max_lines(self):
        diff = "diff --git a/f.py b/f.py\n"
        diff += "\n".join([f"+x = {i}" for i in range(50)])
        result = filter_diff(diff, max_lines=200)
        assert "truncated" not in result