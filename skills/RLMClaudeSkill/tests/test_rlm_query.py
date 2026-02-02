"""Tests for rlm_query.py — RLMClaudeSkill CLI tool.

Tests the Option C hybrid approach:
1. Try HTTP to running RLM-Claude server
2. Fall back to direct Python import if server is down
"""
import json
import subprocess
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add scripts dir to path so we can import rlm_query
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, SCRIPTS_DIR)


# ---------------------------------------------------------------------------
# Health check logic
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """Test the server health check function."""

    def test_returns_true_when_server_is_up(self):
        from rlm_query import check_server_health
        with patch('rlm_query.urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"status":"ok","model":"claude-sonnet-4-20250514"}'
            mock_response.status = 200
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response
            assert check_server_health("http://localhost:8000") is True

    def test_returns_false_when_server_is_down(self):
        from rlm_query import check_server_health
        with patch('rlm_query.urllib.request.urlopen', side_effect=Exception("Connection refused")):
            assert check_server_health("http://localhost:8000") is False

    def test_returns_false_on_timeout(self):
        from rlm_query import check_server_health
        with patch('rlm_query.urllib.request.urlopen', side_effect=TimeoutError("timed out")):
            assert check_server_health("http://localhost:8000") is False


# ---------------------------------------------------------------------------
# HTTP completion (server up path)
# ---------------------------------------------------------------------------

class TestHTTPCompletion:
    """Test the HTTP-based completion when server is running."""

    def test_sends_correct_request(self):
        from rlm_query import complete_via_http
        with patch('rlm_query.urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "response": "The answer is 42",
                "route_used": "direct",
                "iterations": 1,
                "tokens_used": 500,
                "execution_time": 1.2,
                "strategy_hint": None,
                "termination_reason": None,
            }).encode()
            mock_response.status = 200
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = complete_via_http("http://localhost:8000", "What is 6*7?")

            assert result["response"] == "The answer is 42"
            assert result["route_used"] == "direct"

            # Verify the request was constructed correctly
            call_args = mock_urlopen.call_args
            request = call_args[0][0]
            body = json.loads(request.data.decode())
            assert body["prompt"] == "What is 6*7?"

    def test_passes_force_route(self):
        from rlm_query import complete_via_http
        with patch('rlm_query.urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "response": "Deep analysis",
                "route_used": "rlm",
                "iterations": 8,
                "tokens_used": 95000,
                "execution_time": 67.3,
                "strategy_hint": None,
                "termination_reason": None,
            }).encode()
            mock_response.status = 200
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = complete_via_http("http://localhost:8000", "Analyze X", route="rlm")

            call_args = mock_urlopen.call_args
            request = call_args[0][0]
            body = json.loads(request.data.decode())
            assert body["force_route"] == "rlm"

    def test_passes_timeout(self):
        from rlm_query import complete_via_http
        with patch('rlm_query.urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({
                "response": "ok",
                "route_used": "direct",
                "iterations": 1,
                "tokens_used": 100,
                "execution_time": 0.5,
                "strategy_hint": None,
                "termination_reason": None,
            }).encode()
            mock_response.status = 200
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            complete_via_http("http://localhost:8000", "quick", timeout=60)

            call_args = mock_urlopen.call_args
            # timeout should be passed to urlopen
            assert call_args[1].get("timeout") == 60 or call_args[0][1] == 60

    def test_raises_on_http_error(self):
        from rlm_query import complete_via_http
        with patch('rlm_query.urllib.request.urlopen', side_effect=Exception("500 Server Error")):
            with pytest.raises(Exception, match="500"):
                complete_via_http("http://localhost:8000", "fail")


# ---------------------------------------------------------------------------
# Direct import completion (fallback path)
# ---------------------------------------------------------------------------

class TestDirectCompletion:
    """Test the direct Python import fallback when server is down."""

    def test_calls_rlm_claude_directly(self):
        from rlm_query import complete_via_direct

        mock_result = MagicMock()
        mock_result.response = "Direct answer"
        mock_result.route_used = "direct"
        mock_result.iterations = 1
        mock_result.tokens_used = 300
        mock_result.execution_time = 1.5
        mock_result.strategy_hint = None
        mock_result.verification = None
        mock_result.termination_reason = None

        with patch('rlm_query.import_and_run_direct') as mock_run:
            mock_run.return_value = mock_result
            result = complete_via_direct("What is 1+1?", api_key="sk-test")
            assert result["response"] == "Direct answer"
            mock_run.assert_called_once()

    def test_requires_api_key(self):
        from rlm_query import complete_via_direct
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            complete_via_direct("test", api_key=None)


# ---------------------------------------------------------------------------
# Hybrid orchestration
# ---------------------------------------------------------------------------

class TestHybridOrchestration:
    """Test the Option C hybrid: HTTP first, direct fallback."""

    def test_uses_http_when_server_is_up(self):
        from rlm_query import run_completion
        with patch('rlm_query.check_server_health', return_value=True), \
             patch('rlm_query.complete_via_http') as mock_http:
            mock_http.return_value = {
                "response": "HTTP answer",
                "route_used": "rlm",
                "iterations": 5,
                "tokens_used": 20000,
                "execution_time": 35.0,
                "via": "http",
            }
            result = run_completion("test prompt")
            assert result["via"] == "http"
            mock_http.assert_called_once()
            # Verify RLM is the default route
            call_args = mock_http.call_args
            assert call_args[1].get("route") == "rlm" or call_args[0][2] == "rlm"

    def test_default_route_is_rlm(self):
        from rlm_query import DEFAULT_ROUTE
        assert DEFAULT_ROUTE == "rlm"

    def test_falls_back_to_direct_when_server_down(self):
        from rlm_query import run_completion
        with patch('rlm_query.check_server_health', return_value=False), \
             patch('rlm_query.complete_via_direct') as mock_direct:
            mock_direct.return_value = {
                "response": "Direct answer",
                "route_used": "direct",
                "iterations": 1,
                "tokens_used": 200,
                "execution_time": 1.0,
                "via": "direct",
            }
            result = run_completion("test prompt", api_key="sk-test")
            assert result["via"] == "direct"
            mock_direct.assert_called_once()

    def test_falls_back_to_direct_on_http_failure(self):
        from rlm_query import run_completion
        with patch('rlm_query.check_server_health', return_value=True), \
             patch('rlm_query.complete_via_http', side_effect=Exception("HTTP failed")), \
             patch('rlm_query.complete_via_direct') as mock_direct:
            mock_direct.return_value = {
                "response": "Fallback answer",
                "route_used": "direct",
                "iterations": 1,
                "tokens_used": 200,
                "execution_time": 1.0,
                "via": "direct",
            }
            result = run_completion("test prompt", api_key="sk-test")
            assert result["via"] == "direct"


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

class TestOutputFormatting:
    """Test the structured output format."""

    def test_formats_result_as_structured_text(self):
        from rlm_query import format_output
        result = {
            "response": "The answer is 42",
            "route_used": "rlm",
            "iterations": 12,
            "tokens_used": 145000,
            "execution_time": 87.3,
            "via": "http",
        }
        output = format_output(result)
        assert "The answer is 42" in output
        assert "rlm" in output
        assert "http" in output

    def test_formats_result_as_json(self):
        from rlm_query import format_output
        result = {
            "response": "The answer is 42",
            "route_used": "direct",
            "iterations": 1,
            "tokens_used": 500,
            "execution_time": 1.2,
            "via": "http",
        }
        output = format_output(result, json_mode=True)
        parsed = json.loads(output)
        assert parsed["response"] == "The answer is 42"


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

class TestCLI:
    """Test the command-line interface."""

    def test_requires_prompt_argument(self):
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, 'rlm_query.py')],
            capture_output=True, text=True
        )
        assert result.returncode != 0

    def test_accepts_prompt_as_positional_arg(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS_DIR, 'rlm_query.py'),
                 '--dry-run', 'What is 1+1?'],
                capture_output=True, text=True
            )
            assert result.returncode == 0
            assert "dry-run" in result.stdout.lower() or "What is 1+1?" in result.stdout

    def test_route_flag(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS_DIR, 'rlm_query.py'),
                 '--dry-run', '--route', 'rlm', 'Analyze deeply'],
                capture_output=True, text=True
            )
            assert result.returncode == 0

    def test_json_flag(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS_DIR, 'rlm_query.py'),
                 '--dry-run', '--json', 'test'],
                capture_output=True, text=True
            )
            assert result.returncode == 0

    def test_server_url_flag(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            result = subprocess.run(
                [sys.executable, os.path.join(SCRIPTS_DIR, 'rlm_query.py'),
                 '--dry-run', '--server', 'http://localhost:9000', 'test'],
                capture_output=True, text=True
            )
            assert result.returncode == 0
