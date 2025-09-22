#!/usr/bin/env python3
"""Aggressive fixer: ensure a blank line before list blocks outside fenced code.

This script is more assertive: for each markdown file, it scans outside fenced
code blocks and inserts a blank line before any line that begins a list block
(`- `, `* `, `+ `) when the previous line is not blank.

Use with care; changes are minimal and reversible via git.
"""
from pathlib import Path
import re
import sys


def fix_text(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    out = []
    in_fence = False
    changes = 0
    for i, line in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        if re.match(r"^\s*[-*+]\s+", line):
            # previous line exists and is not blank
            if len(out) > 0 and out[-1].strip() != "":
                out.append("")
                changes += 1
        out.append(line)

    new_text = "\n".join(out) + ("\n" if text.endswith("\n") else "")
    return new_text, changes


def main():
    root = Path(__file__).resolve().parents[1] / "docs"
    if not root.exists():
        print("docs/ not found", file=sys.stderr)
        return 2
    total = 0
    for p in sorted(root.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        new_text, changed = fix_text(text)
        if changed:
            p.write_text(new_text, encoding="utf-8")
            print(f"Patched {p} (+{changed})")
            total += changed
    if total == 0:
        print("No changes made")
    else:
        print(f"Applied {total} insertions across docs/")


if __name__ == "__main__":
    main()
