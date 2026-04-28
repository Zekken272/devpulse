"""Tests for the reviewer module."""

import pytest
from unittest.mock import patch, MagicMock
from devpulse.reviewer import (
    parse_review_response,
    ReviewResult,
    check_ollama_running,
)


class TestParseReviewResponse:
    def test_parses_all_sections(self):
        raw = """ISSUES
------
- Line 5: division by zero risk

SUGGESTIONS
-----------
- Use context manager for file handling

SECURITY
--------
- Hardcoded API key on line 3

SUMMARY
-------
The diff has critical security issues that must be addressed."""

        result = parse_review_response(raw)
        assert "division by zero" in result["issues"]
        assert "context manager" in result["suggestions"]
        assert "API key" in result["security"]
        assert "critical security" in result["summary"]

    def test_handles_none_found_sections(self):
        raw = """ISSUES
------
None found.

SUGGESTIONS
-----------
None found.

SECURITY
--------
None found.

SUMMARY
-------
Clean and well-written changes."""

        result = parse_review_response(raw)
        assert result["issues"] == "None found."
        assert result["security"] == "None found."

    def test_handles_missing_sections_gracefully(self):
        raw = """ISSUES
------
Some issue here."""

        result = parse_review_response(raw)
        assert "Some issue" in result["issues"]
        assert result["suggestions"] == ""
        assert result["security"] == ""

    def test_returns_empty_strings_for_blank_input(self):
        result = parse_review_response("")
        assert result["issues"] == ""
        assert result["suggestions"] == ""
        assert result["security"] == ""
        assert result["summary"] == ""


class TestReviewResult:
    def test_has_error_is_true_when_error_set(self):
        r = ReviewResult(error="something went wrong")
        assert r.has_error is True

    def test_has_error_is_false_when_no_error(self):
        r = ReviewResult()
        assert r.has_error is False

    def test_issue_count_is_zero_for_none_found(self):
        r = ReviewResult(issues="None found.")
        assert r.issue_count == 0

    def test_issue_count_counts_lines(self):
        r = ReviewResult(issues="- Bug on line 3\n- Another bug\n- Third bug")
        assert r.issue_count == 3

    def test_security_count_is_zero_for_empty(self):
        r = ReviewResult(security="")
        assert r.security_count == 0


class TestCheckOllamaRunning:
    def test_returns_true_when_server_responds(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        with patch("devpulse.reviewer.requests.get", return_value=mock_response):
            assert check_ollama_running() is True

    def test_returns_false_when_connection_refused(self):
        import requests
        with patch(
            "devpulse.reviewer.requests.get",
            side_effect=requests.ConnectionError,
        ):
            assert check_ollama_running() is False