from __future__ import annotations
import json


def parse_key_val_lines(content: str) -> dict[str, any]:
    out = dict()
    for line in content.strip().splitlines():
        k: str
        v: str
        try:
            k, v = line.strip().split(":", 1)
        except ValueError:
            raise ValueError(f"Line '{line}' does not contain a colon")
        k = k.rstrip()
        v = v.lstrip()
        out[k] = json.loads(v)

    return out
