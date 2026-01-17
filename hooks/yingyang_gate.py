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


def read_stdin() -> dict:
    """Read and parse JSON from stdin."""
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            return {}
        return json.loads(raw_input)
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


def check_verification(entries: list[dict]) -> bool:
    """Check if YingYang verification pattern exists AFTER the last user message."""
    # Find index of last user message
    last_user_idx = -1
    for i, entry in enumerate(entries):
        if entry.get("type") == "user":
            last_user_idx = i

    # Only check assistant messages AFTER the last user message
    for entry in entries[last_user_idx + 1:]:
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
        input_data = read_stdin()

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

        # Check for verification pattern
        if check_verification(entries):
            response = continue_response()
        else:
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
