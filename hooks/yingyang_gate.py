#!/usr/bin/env python3
"""
YingYang Gate Hook for Claude Code

This hook enforces YingYang verification by checking the conversation
transcript for verification evidence before allowing completion.

Usage:
    This script is called by Claude Code as a stop hook.
    It receives JSON via stdin with a `transcript_path` field.

Exit codes:
    0: Success (decision returned via stdout)
    1: Error (error message returned via stdout)
"""

import json
import sys
from pathlib import Path


VERIFICATION_PATTERN = "=== YINGYANG VERIFICATION COMPLETE ==="


def read_stdin() -> tuple[dict, str]:
    """Read and parse JSON from stdin. Returns (parsed_dict, raw_string)."""
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return {}, ""
        return json.loads(raw_input), raw_input
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")


def read_transcript(transcript_path: str) -> list[dict]:
    """Read JSONL transcript file and return list of entries."""
    path = Path(transcript_path)

    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")

    if not path.is_file():
        raise ValueError(f"Transcript path is not a file: {transcript_path}")

    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as e:
                # Log but continue - some lines might be malformed
                sys.stderr.write(f"Warning: Malformed JSON on line {line_num}: {e}\n")

    return entries


def extract_message_content(message: dict) -> str:
    """Extract text content from a message object."""
    content = message.get("message", {}).get("content", "")

    # Content might be a string or a list of content blocks
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text from content blocks
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif "text" in block:
                    text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "\n".join(text_parts)

    return ""


def detect_code_modifications(entries: list[dict]) -> bool:
    """Check if any code files were modified using Write/Edit tools."""
    code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.java', '.rs',
                       '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
                       '.kt', '.scala', '.r', '.m', '.mm'}

    for entry in entries:
        if entry.get("type") == "assistant":
            message = entry.get("message", {})
            content = message.get("content", [])

            # Content might be a list of blocks
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_name = block.get("name", "")
                        tool_input = block.get("input", {})

                        # Check for Write or Edit tools
                        if tool_name in ["Write", "Edit"]:
                            file_path = tool_input.get("file_path", "")
                            if file_path:
                                # Check if file has a code extension
                                for ext in code_extensions:
                                    if file_path.endswith(ext):
                                        return True

    return False


def detect_simple_qa(entries: list[dict]) -> bool:
    """Detect if this is a simple Q&A session without code changes."""
    tool_invocation_count = 0
    has_write_edit_bash = False

    for entry in entries:
        if entry.get("type") == "assistant":
            message = entry.get("message", {})
            content = message.get("content", [])

            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_invocation_count += 1
                        tool_name = block.get("name", "")

                        if tool_name in ["Write", "Edit", "Bash"]:
                            has_write_edit_bash = True

    # Simple Q&A: few tool invocations or no code-modifying tools
    if tool_invocation_count < 3 or not has_write_edit_bash:
        return True

    return False


def detect_planning_context(entries: list[dict]) -> bool:
    """Detect if this is a planning or research context."""
    planning_indicators = [
        "PLANNING MINION",
        "writing-plans",
        "brainstorm",
        "creating a plan",
        "implementation plan",
        "research",
        "investigation"
    ]

    for entry in entries:
        if entry.get("type") in ["user", "assistant"]:
            content = extract_message_content(entry)
            content_lower = content.lower()

            for indicator in planning_indicators:
                if indicator.lower() in content_lower:
                    return True

    return False


def should_require_verification(entries: list[dict]) -> bool:
    """
    Determine if YingYang verification should be required.

    Returns True ONLY when:
    - Code files were modified (Write/Edit on .py, .js, etc.)
    - NOT in planning/research context
    - NOT a simple Q&A session
    """
    # Skip verification for planning contexts
    if detect_planning_context(entries):
        return False

    # Check if code was modified
    code_modified = detect_code_modifications(entries)

    # If code was modified, verification is required regardless of other factors
    if code_modified:
        return True

    # If no code was modified, skip verification for simple Q&A
    if detect_simple_qa(entries):
        return False

    # Default: don't require verification
    return False


def check_verification(entries: list[dict], raw_stdin: str = "") -> bool:
    """Check if YingYang verification pattern exists.

    Checks two sources:
    1. The raw stdin input (which may contain the current response not yet
       flushed to the transcript file — fixes the stop hook timing issue)
    2. Assistant messages in the transcript AFTER the last user message
    """
    # Check 1: Raw stdin may contain the current response content
    if raw_stdin and VERIFICATION_PATTERN in raw_stdin:
        return True

    # Check 2: Search transcript entries after last user message
    last_user_idx = -1
    for i, entry in enumerate(entries):
        if entry.get("type") == "user":
            last_user_idx = i

    for entry in entries[last_user_idx + 1:]:
        if entry.get("type") == "assistant":
            content = extract_message_content(entry)
            if VERIFICATION_PATTERN in content:
                return True

    # Check 3: Search ALL assistant entries (not just after last user)
    # because the hook feedback itself creates new "user" entries that
    # push the boundary forward, hiding earlier verification blocks
    for entry in entries:
        if entry.get("type") == "assistant":
            content = extract_message_content(entry)
            if VERIFICATION_PATTERN in content:
                return True

    return False


def block_response(reason: str, system_message: str) -> dict:
    """Generate a block decision response."""
    return {
        "decision": "block",
        "reason": reason,
        "systemMessage": system_message
    }


def continue_response() -> dict:
    """Generate a continue decision response.

    For Stop hooks, omitting 'decision' or returning empty object allows stopping.
    Only 'decision': 'block' prevents stopping.
    """
    return {}


def main():
    """Main entry point for the hook."""
    try:
        # Read input from stdin
        input_data, raw_stdin = read_stdin()

        # Check for transcript_path
        transcript_path = input_data.get("transcript_path")
        if not transcript_path:
            # No transcript path provided - this might be a dry run or error
            response = block_response(
                reason="No transcript_path provided in hook input",
                system_message="YingYang Gate: Unable to verify - no transcript path available. Please ensure the hook is properly configured."
            )
            print(json.dumps(response))
            return

        # Read and parse transcript
        try:
            entries = read_transcript(transcript_path)
        except FileNotFoundError as e:
            response = block_response(
                reason=str(e),
                system_message=f"YingYang Gate: Cannot read transcript file. {e}"
            )
            print(json.dumps(response))
            return
        except ValueError as e:
            response = block_response(
                reason=str(e),
                system_message=f"YingYang Gate: Invalid transcript format. {e}"
            )
            print(json.dumps(response))
            return

        # Check if verification is required for this context
        if not should_require_verification(entries):
            # Context doesn't require verification (planning, Q&A, no code changes)
            response = continue_response()
        elif check_verification(entries, raw_stdin):
            # Verification required and found
            response = continue_response()
        else:
            # Verification required but not found
            response = block_response(
                reason="YingYang verification not found in conversation",
                system_message=(
                    "YingYang Gate: BLOCKED - No verification evidence found.\n\n"
                    "Before completing, you MUST run YingYang verification:\n"
                    "1. Write comprehensive tests for your implementation\n"
                    "2. Run the tests and ensure they pass\n"
                    "3. Output: === YINGYANG VERIFICATION COMPLETE ===\n\n"
                    "This ensures all implementations are properly tested."
                )
            )

        print(json.dumps(response))

    except ValueError as e:
        # JSON parsing error from stdin
        response = block_response(
            reason=f"Hook input error: {e}",
            system_message=f"YingYang Gate: Hook configuration error. {e}"
        )
        print(json.dumps(response))
        sys.exit(1)
    except Exception as e:
        # Unexpected error - fail safe by blocking
        response = block_response(
            reason=f"Unexpected error: {e}",
            system_message=f"YingYang Gate: Internal error occurred. {e}"
        )
        print(json.dumps(response))
        sys.exit(1)


if __name__ == "__main__":
    main()
