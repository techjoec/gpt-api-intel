"""Scan repository files for quoted numeric literals that may represent hashed IDs.

The script detects double-quoted decimal strings (default length ≥ 9) while
excluding occurrences that already map to known Statsig gates/configs or are
embedded in call sites such as `Wt("…")` / `We("…")`.

Usage:

    python tools/hash_scanner.py --paths . --output hashes.json

Outputs a JSON payload: `{hash_value: [{"path": str, "line": int, "context": str}, …]}`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_PATHS = [Path("docs")]
DEFAULT_INVENTORY = Path("data/statsig_inventory.json")
CONTEXT_WINDOW = 60
CALL_GUARDS = ("Wt(", "We(", "logEventWithStatsig", "logValueEventWithStatsig")


def load_known_ids(inventory_path: Path) -> set[str]:
    if not inventory_path.exists():
        return set()
    data = json.loads(inventory_path.read_text(encoding="utf-8", errors="ignore"))
    known = set(data.get("feature_gates", {}).keys())
    known.update(data.get("dynamic_configs", {}).keys())
    # Secondary exposures / nested references may include additional hashes.
    for config in data.get("dynamic_configs", {}).values():
        for key in config.get("value_types", {}).keys():
            if key.isdigit():
                known.add(key)
    return known


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


def scan_file(path: Path, min_length: int, known: set[str]) -> Dict[str, List[Dict[str, str]]]:
    results: Dict[str, List[Dict[str, str]]] = {}
    pattern = re.compile(r'"(\d{%d,})"' % min_length)

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return results

    for lineno, line in enumerate(lines, start=1):
        for match in pattern.finditer(line):
            value = match.group(1)
            if value in known:
                continue
            start = max(0, match.start() - CONTEXT_WINDOW)
            end = match.end() + CONTEXT_WINDOW
            context = line[start:end]
            if any(token in context for token in CALL_GUARDS):
                continue
            results.setdefault(value, []).append(
                {
                    "path": str(path),
                    "line": lineno,
                    "context": context.strip(),
                }
            )
    return results


def merge_results(dest: Dict[str, List[Dict[str, str]]], src: Dict[str, List[Dict[str, str]]]) -> None:
    for key, entries in src.items():
        dest.setdefault(key, []).extend(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", nargs="*", type=Path, default=DEFAULT_PATHS, help="Files or directories to scan")
    parser.add_argument("--min-length", type=int, default=9, help="Minimum digits for a literal to be considered")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY, help="Known IDs inventory JSON")
    parser.add_argument("--output", type=Path, help="Optional output JSON file")
    args = parser.parse_args()

    known_ids = load_known_ids(args.inventory)
    aggregate: Dict[str, List[Dict[str, str]]] = {}

    for file_path in iter_files(args.paths or DEFAULT_PATHS):
        file_results = scan_file(file_path, args.min_length, known_ids)
        if file_results:
            merge_results(aggregate, file_results)

    if not aggregate:
        print("No unmatched numeric literals found.")
        return

    output = {key: entries for key, entries in sorted(aggregate.items(), key=lambda item: item[0])}
    text = json.dumps(output, indent=2)

    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
