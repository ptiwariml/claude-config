#!/usr/bin/env python3
"""RLMClaudeSkill CLI — Option C hybrid: HTTP-first with direct import fallback.

Usage:
    python3 rlm_query.py "your prompt here"
    python3 rlm_query.py --route rlm "complex analysis question"
    python3 rlm_query.py --json "get structured output"
    python3 rlm_query.py --server http://localhost:9000 "custom server"
    python3 rlm_query.py --dry-run "test without calling"
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

# Default RLM-Claude server
DEFAULT_SERVER = "http://localhost:8000"
DEFAULT_TIMEOUT = 300  # 5 minutes — RLM route can take 2+ minutes
RLM_PROJECT_PATH = os.path.expanduser("~/work/projects/rlm-claude")


def check_server_health(server_url: str) -> bool:
    """Check if the RLM-Claude server is running."""
    try:
        url = f"{server_url.rstrip('/')}/health"
        with urllib.request.urlopen(url, timeout=3) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False


def complete_via_http(
    server_url: str,
    prompt: str,
    route: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Send completion request to the RLM-Claude HTTP API."""
    url = f"{server_url.rstrip('/')}/api/completion"
    body = {"prompt": prompt}
    if route:
        body["force_route"] = route

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    result["via"] = "http"
    return result


def import_and_run_direct(prompt: str, api_key: str, route: str | None = None):
    """Import RLMClaude directly and run a completion. Returns CompletionResult."""
    # Add project paths for imports
    if RLM_PROJECT_PATH not in sys.path:
        sys.path.insert(0, RLM_PROJECT_PATH)
    vendor_path = os.path.join(RLM_PROJECT_PATH, "vendor", "rlm")
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)

    from src.rlm_claude import RLMClaude, RLMClaudeConfig

    config = RLMClaudeConfig(
        anthropic_api_key=api_key,
        db_path=os.path.join(RLM_PROJECT_PATH, "data", "strategies.db"),
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
    )
    rlm = RLMClaude(config)
    try:
        return rlm.completion(prompt, force_route=route)
    finally:
        rlm.close()


def complete_via_direct(
    prompt: str,
    api_key: str | None = None,
    route: str | None = None,
) -> dict:
    """Run completion via direct Python import (no server needed)."""
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is required for direct mode. "
            "Set it in your environment or pass --api-key."
        )

    result = import_and_run_direct(prompt, api_key, route)

    return {
        "response": result.response,
        "route_used": result.route_used,
        "iterations": result.iterations,
        "tokens_used": result.tokens_used,
        "execution_time": result.execution_time,
        "strategy_hint": result.strategy_hint,
        "termination_reason": result.termination_reason,
        "via": "direct",
    }


DEFAULT_ROUTE = "rlm"


def run_completion(
    prompt: str,
    server_url: str = DEFAULT_SERVER,
    route: str | None = DEFAULT_ROUTE,
    timeout: int = DEFAULT_TIMEOUT,
    api_key: str | None = None,
) -> dict:
    """Option C hybrid: try HTTP first, fall back to direct import. Always RLM by default."""
    # Try HTTP if server is up
    if check_server_health(server_url):
        try:
            return complete_via_http(server_url, prompt, route=route, timeout=timeout)
        except Exception:
            pass  # Fall through to direct

    # Fallback: direct import
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    return complete_via_direct(prompt, api_key=api_key, route=route)


def format_output(result: dict, json_mode: bool = False) -> str:
    """Format the completion result for stdout."""
    if json_mode:
        return json.dumps(result, indent=2)

    lines = [
        f"=== RLM-Claude Response (via {result.get('via', 'unknown')}) ===",
        f"Route: {result.get('route_used', 'unknown')}",
        f"Iterations: {result.get('iterations', 'N/A')}",
        f"Tokens: {result.get('tokens_used', 'N/A')}",
        f"Time: {result.get('execution_time', 'N/A')}s",
        "",
        result.get("response", ""),
    ]
    if result.get("strategy_hint"):
        lines.insert(5, f"Strategy hint: {result['strategy_hint']}")
    if result.get("termination_reason"):
        lines.insert(5, f"Termination: {result['termination_reason']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="RLMClaudeSkill — Recursive Language Model powered by Claude"
    )
    parser.add_argument("prompt", help="The prompt to send to RLM-Claude")
    parser.add_argument(
        "--route",
        choices=["direct", "structured", "rlm"],
        default=DEFAULT_ROUTE,
        help=f"Route to use (default: {DEFAULT_ROUTE})",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER,
        help=f"RLM-Claude server URL (default: {DEFAULT_SERVER})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_mode",
        help="Output as JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Anthropic API key (default: from ANTHROPIC_API_KEY env var)",
    )

    args = parser.parse_args()

    if args.dry_run:
        info = {
            "dry_run": True,
            "prompt": args.prompt,
            "route": args.route,
            "server": args.server,
            "timeout": args.timeout,
            "json_mode": args.json_mode,
        }
        if args.json_mode:
            print(json.dumps(info, indent=2))
        else:
            print(f"Dry-run: would send to {args.server}")
            print(f"  Prompt: {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
            print(f"  Route: {args.route or 'auto'}")
            print(f"  Timeout: {args.timeout}s")
        return

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    try:
        result = run_completion(
            prompt=args.prompt,
            server_url=args.server,
            route=args.route,
            timeout=args.timeout,
            api_key=api_key,
        )
        print(format_output(result, json_mode=args.json_mode))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
