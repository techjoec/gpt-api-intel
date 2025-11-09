"""Statsig payload resolver for ChatGPT HAR captures.

Given either a HAR file or a raw HTML dump that embeds the React Server
Component bootstrap (`enqueue("…");`), this script rematerialises the
`feature_gates` / `dynamic_configs` payloads and reports a sanitised
inventory.  It is designed for local analysis of captured traffic where the
standard JSON summary is inconveniently encoded with positional indices.

Usage:

    python tools/statsig_resolver.py path/to/file.har

Outputs JSON with two dictionaries:
  - `feature_gates`: `{hashed_gate_id: [observed boolean values...]}`
  - `dynamic_configs`: `{hashed_config_id: {keys: [...], groups: [...],
      rule_ids: [...], value_types: {key: type_name}}}`

The script purposefully reports only metadata about each config to avoid
leaking full payload contents (tokens, identifiers, etc.).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


PATTERN = re.compile(r'enqueue\("(.*?)"\);')


def _parse_root(text: str) -> Optional[List[Any]]:
    match_iter = PATTERN.findall(text)
    if not match_iter:
        return None
    try:
        return json.loads(match_iter[0].encode("utf-8").decode("unicode_escape"))
    except json.JSONDecodeError:
        return None


def _resolve_configs(root: List[Any]) -> Dict[str, Dict[str, Any]]:
    root_len = len(root)
    cache: Dict[int, Any] = {}

    def resolve_index(idx: Any, stack: Set[int]) -> Any:
        if isinstance(idx, bool) or isinstance(idx, str) or idx is None:
            return idx
        if not isinstance(idx, int):
            return idx
        if idx in stack:
            return "CYCLE"
        if idx == -5:
            return None
        if idx == -7:
            return "UNSET"
        if idx < 0 or idx >= root_len:
            return idx
        if idx in cache:
            return cache[idx]

        value = root[idx]
        stack = set(stack)
        stack.add(idx)

        if isinstance(value, bool) or isinstance(value, str) or value is None:
            cache[idx] = value
            return value
        if isinstance(value, int):
            result = resolve_index(value, stack)
            cache[idx] = result
            return result
        if isinstance(value, list):
            if len(value) == 2 and value[0] == "P" and isinstance(value[1], int):
                result = {"resource_ref": value[1]}
            else:
                result = [resolve_any(v, stack) for v in value]
            cache[idx] = result
            return result
        if isinstance(value, dict):
            resolved: Dict[str, Any] = {}
            for key, val in value.items():
                new_key = key
                if isinstance(key, str) and key.startswith("_"):
                    key_idx = int(key[1:])
                    candidate = resolve_index(key_idx, stack)
                    if isinstance(candidate, str):
                        new_key = candidate
                resolved[new_key] = resolve_any(val, stack)
            cache[idx] = resolved
            return resolved

        cache[idx] = value
        return value

    def resolve_any(val: Any, stack: Set[int]) -> Any:
        if isinstance(val, bool) or isinstance(val, str) or val is None:
            return val
        if isinstance(val, int):
            return resolve_index(val, stack)
        if isinstance(val, list):
            if len(val) == 2 and val[0] == "P" and isinstance(val[1], int):
                return {"resource_ref": val[1]}
            return [resolve_any(v, stack) for v in val]
        if isinstance(val, dict):
            return {(
                resolve_index(int(k[1:]), stack) if isinstance(k, str) and k.startswith("_") else k
            ): resolve_any(v, stack) for k, v in val.items()}
        return val

    configs: Dict[str, Dict[str, Any]] = {}
    for idx, item in enumerate(root):
        if not isinstance(item, dict):
            continue
        resolved = resolve_index(idx, set())
        if not (isinstance(resolved, dict) and "name" in resolved and "value" in resolved):
            continue
        name = resolved["name"]
        if isinstance(name, str) and name.isdigit():
            configs[name] = resolved

    return configs


def _process_text(text: str) -> Dict[str, Dict[str, Any]]:
    root = _parse_root(text)
    if root is None:
        return {}
    return _resolve_configs(root)


def _process_har(path: Path) -> Dict[str, Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    for entry in data.get("log", {}).get("entries", []):
        content = entry.get("response", {}).get("content", {})
        text = content.get("text")
        if text is None:
            continue
        if content.get("encoding") == "base64":
            try:
                text = base64.b64decode(text).decode("utf-8", "ignore")
            except (ValueError, UnicodeDecodeError):
                continue
        if "feature_gates" not in text:
            continue
        configs = _process_text(text)
        if configs:
            return configs
    return {}


def _summarise_configs(configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    features: Dict[str, List[bool]] = defaultdict(list)
    dynamic: Dict[str, Dict[str, Any]] = {}

    for name, data in configs.items():
        value = data.get("value")
        if isinstance(value, bool):
            if value not in features[name]:
                features[name].append(value)
        elif isinstance(value, dict):
            entry = dynamic.setdefault(name, {
                "keys": set(),
                "groups": set(),
                "rule_ids": set(),
                "value_types": {}
            })
            entry["keys"].update(k for k in value.keys() if isinstance(k, str))
            group = data.get("group")
            if isinstance(group, str):
                entry["groups"].add(group)
            rule_id = data.get("rule_id")
            if isinstance(rule_id, str):
                entry["rule_ids"].add(rule_id)
            for key, val in value.items():
                if not isinstance(key, str):
                    continue
                if isinstance(val, bool):
                    summary = "bool"
                elif isinstance(val, (int, float)):
                    summary = "number"
                elif isinstance(val, str):
                    summary = "string"
                elif val is None:
                    summary = "null"
                elif isinstance(val, list):
                    summary = "list"
                elif isinstance(val, dict):
                    summary = "dict"
                else:
                    summary = type(val).__name__
                entry["value_types"].setdefault(key, set()).add(summary)

    # Normalise sets to sorted lists for JSON output
    dynamic_serialised = {
        name: {
            "keys": sorted(data["keys"]),
            "groups": sorted(data["groups"]),
            "rule_ids": sorted(data["rule_ids"]),
            "value_types": {k: sorted(v) for k, v in data["value_types"].items()},
        }
        for name, data in dynamic.items()
    }

    return {
        "feature_gates": {name: sorted(values) for name, values in features.items()},
        "dynamic_configs": dynamic_serialised,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="HAR file or HTML containing the bootstrap payload")
    args = parser.parse_args()

    if args.path.suffix.lower() == ".har":
        configs = _process_har(args.path)
    else:
        configs = _process_text(args.path.read_text(encoding="utf-8", errors="ignore"))

    if not configs:
        raise SystemExit("No Statsig payload found in the provided file.")

    summary = _summarise_configs(configs)
    json.dump(summary, fp=sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
