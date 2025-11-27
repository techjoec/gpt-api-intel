"""Scan HAR/text captures for wham/codex/chatgpt/openai related functions.

The script searches two sources:
  1. HAR files – `_initiator.stack.callFrames[*].functionName` and script URLs.
  2. Plain text files – lines containing the target keywords near function
     declarations/usages.

Usage:

    python tools/service_function_scanner.py --output hits.json

By default, it walks `docs/`. Use `--paths` to override.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

KEYWORDS = ["wham", "codex", "chatgpt", "openai", "sidetron", "sidekick"]
DEFAULT_PATHS = [Path("docs")]

TEXT_EXTENSIONS = {".js", ".ts", ".tsx", ".json", ".txt", ".md", ".html", ".log", ".py"}
TEXT_PATTERN = re.compile(r"(.{0,60})(wham|codex|chatgpt|openai|sidetron|sidekick)(.{0,60})", re.IGNORECASE)


def iter_paths(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in path.rglob("*"):
            if child.is_file():
                yield child


def keyword_hit(*values: str) -> bool:
    for value in values:
        if not value:
            continue
        lower = value.lower()
        if any(keyword in lower for keyword in KEYWORDS):
            return True
    return False


def scan_har(path: Path) -> List[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []

    entries: List[Dict[str, Any]] = []
    for entry in data.get("log", {}).get("entries", []):
        request = entry.get("request", {})
        url = request.get("url", "")

        initiator = entry.get("_initiator") or entry.get("initiator")
        if isinstance(initiator, dict):
            stack = initiator.get("stack") or {}
            call_frames = stack.get("callFrames") or []
            for frame in call_frames:
                func_name = frame.get("functionName", "")
                script_url = frame.get("url", "")
                if keyword_hit(func_name, script_url):
                    entries.append(
                        {
                            "path": str(path),
                            "type": "har_callframe",
                            "function": func_name,
                            "script": script_url,
                            "request_url": url,
                        }
                    )
        if keyword_hit(url):
            entries.append(
                {
                    "path": str(path),
                    "type": "har_request_url",
                    "request_url": url,
                }
            )

    return entries


def scan_text(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    matches: List[Dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        if not keyword_hit(line):
            continue
        match = TEXT_PATTERN.search(line)
        if not match:
            continue
        snippet = "".join(match.groups())
        matches.append(
            {
                "path": str(path),
                "type": "text_snippet",
                "line": idx,
                "context": snippet.strip(),
            }
        )
    return matches


def scan(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for file_path in iter_paths(paths):
        if file_path.suffix.lower() == ".har":
            hits = scan_har(file_path)
        else:
            hits = scan_text(file_path)
        if hits:
            results.extend(hits)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", nargs="*", type=Path, default=DEFAULT_PATHS, help="Files or directories to scan")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    results = scan(args.paths or DEFAULT_PATHS)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
        print()


if __name__ == "__main__":
    main()
