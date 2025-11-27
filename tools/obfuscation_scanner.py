r"""Detect common substitution/obfuscation patterns in capture files.

Heuristics covered:
  - Long sequences of ``\xNN`` hex escapes.
  - Frequent use of `String.fromCharCode`, `.charCodeAt`, `eval(`, `Function(`,
    `atob(`, `btoa(`, `Intl.v8BreakIterator`, etc.
  - Inline base64 blobs embedded inside strings (delegates to regex only,
    decoder is handled elsewhere).

Outputs a JSON list of matches with path, line number, and short context.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_PATHS = [Path("raw"), Path("hars")]

HEX_ESCAPE_PATTERN = re.compile(r"(\\x[0-9a-fA-F]{2}){8,}")  # ≥ 8 escapes in a row
BASE64_INLINE_PATTERN = re.compile(r'"[A-Za-z0-9+/]{24,}={0,2}"')
API_PATTERN = re.compile(
    r"(String\.fromCharCode|charCodeAt|eval\(|Function\(|atob\(|btoa\(|Intl\.v8BreakIterator|navigator\.languages|CryptoJS)",
    re.IGNORECASE,
)


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in path.rglob("*"):
            if child.is_file():
                yield child


def scan_file(path: Path) -> List[Dict[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []

    findings: List[Dict[str, str]] = []
    for idx, line in enumerate(lines, start=1):
        match = HEX_ESCAPE_PATTERN.search(line)
        if match:
            findings.append(
                {
                    "path": str(path),
                    "type": "hex_escape",
                    "line": idx,
                    "context": line.strip(),
                }
            )
            continue  # Avoid flooding with multiple categories on the same line

        api_match = API_PATTERN.search(line)
        if api_match:
            findings.append(
                {
                    "path": str(path),
                    "type": "suspicious_api",
                    "line": idx,
                    "context": line.strip(),
                }
            )
            continue

        base64_match = BASE64_INLINE_PATTERN.search(line)
        if base64_match:
            findings.append(
                {
                    "path": str(path),
                    "type": "inline_base64",
                    "line": idx,
                    "context": line.strip()[:200],
                }
            )
    return findings


def scan(paths: Iterable[Path]) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for file_path in iter_files(paths):
        hits = scan_file(file_path)
        if hits:
            results.extend(hits)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", nargs="*", type=Path, default=DEFAULT_PATHS)
    parser.add_argument("--output", type=Path, help="Optional JSON output file")
    args = parser.parse_args()

    results = scan(args.paths or DEFAULT_PATHS)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
        print()


if __name__ == "__main__":
    main()
