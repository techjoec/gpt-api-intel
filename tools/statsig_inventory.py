"""Aggregate Statsig gate/config metadata across captures.

The script walks one or more paths (HAR archives or text-based dumps) and
produces a consolidated summary of hashed gate/config identifiers observed in
Statsig payloads.

Example:

    python tools/statsig_inventory.py --output data/statsig_inventory.json
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

if __package__ is None or __package__ == "":
    # Allow running as a script without packaging the repo as a module.
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from tools.statsig_resolver import _process_har, _process_text  # type: ignore
else:  # pragma: no cover
    from .statsig_resolver import _process_har, _process_text


TEXT_EXTS = {
    ".html",
    ".htm",
    ".js",
    ".json",
    ".txt",
    ".xml",
    ".log",
    ".resp",
    ".response",
    ".data",
}


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTS:
        return True
    # treat files without suffix as text candidates if reasonably small
    return path.suffix == "" and path.stat().st_size <= 5 * 1024 * 1024


def _read_configs(path: Path) -> Dict[str, Dict[str, Any]]:
    if path.suffix.lower() == ".har":
        try:
            return _process_har(path)
        except json.JSONDecodeError:
            return {}

    if not _is_text_file(path):
        return {}

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return {}

    if "feature_gates" not in text:
        return {}

    return _process_text(text)


def _merge_configs(aggregate: Dict[str, Dict[str, Any]], configs: Dict[str, Dict[str, Any]]) -> None:
    for name, data in configs.items():
        aggregate.setdefault(name, {}).setdefault("instances", []).append(data)


def _summarise(aggregate: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    feature_map = defaultdict(set)
    dynamic_map: Dict[str, Dict[str, Any]] = {}

    def classify_value(val: Any) -> str:
        if isinstance(val, bool):
            return "bool"
        if isinstance(val, (int, float)):
            return "number"
        if isinstance(val, str):
            return "string"
        if val is None:
            return "null"
        if isinstance(val, list):
            return "list"
        if isinstance(val, dict):
            return "dict"
        return type(val).__name__

    for name, payload in aggregate.items():
        for data in payload.get("instances", []):
            value = data.get("value")
            if isinstance(value, bool):
                feature_map[name].add(value)
                continue

            if not isinstance(value, dict):
                continue

            entry = dynamic_map.setdefault(
                name,
                {
                    "keys": set(),
                    "groups": set(),
                    "rule_ids": set(),
                    "value_types": defaultdict(set),
                },
            )

            for key, val in value.items():
                if isinstance(key, str):
                    entry["keys"].add(key)
                    entry["value_types"][key].add(classify_value(val))

            group = data.get("group")
            if isinstance(group, str):
                entry["groups"].add(group)

            rule_id = data.get("rule_id")
            if isinstance(rule_id, str):
                entry["rule_ids"].add(rule_id)

    dynamic_serialised = {
        name: {
            "keys": sorted(data["keys"]),
            "groups": sorted(data["groups"]),
            "rule_ids": sorted(data["rule_ids"]),
            "value_types": {k: sorted(v) for k, v in data["value_types"].items()},
        }
        for name, data in dynamic_map.items()
    }

    return {
        "feature_gates": {name: sorted(values) for name, values in feature_map.items()},
        "dynamic_configs": dynamic_serialised,
    }


def _walk_paths(paths: Iterable[Path]) -> Dict[str, Dict[str, Any]]:
    aggregate: Dict[str, Dict[str, Any]] = {}

    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if not child.is_file():
                    continue
                configs = _read_configs(child)
                if configs:
                    _merge_configs(aggregate, configs)
        elif path.is_file():
            configs = _read_configs(path)
            if configs:
                _merge_configs(aggregate, configs)

    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, default=[Path("raw"), Path("hars")], help="Files or directories to scan")
    parser.add_argument("--output", type=Path, help="Optional output JSON file")
    args = parser.parse_args()

    aggregate = _walk_paths(args.paths)
    if not aggregate:
        raise SystemExit("No Statsig payloads found in provided paths")

    summary = _summarise(aggregate)
    output_text = json.dumps(summary, indent=2)

    if args.output:
        args.output.write_text(output_text + "\n", encoding="utf-8")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
