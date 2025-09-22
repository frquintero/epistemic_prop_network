#!/usr/bin/env python3
"""Safe fixes for docs/ markdown files.

Performs two non-destructive, review-friendly fixes:
- Remove trailing whitespace from every line.
- Ensure there is a blank line before any list start (`- `, `* `, `+ `) when the
  previous non-empty line is not itself a list (avoids breaking list groups).

This script avoids reflowing paragraphs or changing long lines.
"""
import os
import re
from pathlib import Path


def fix_file(path: Path) -> int:
    changed = 0
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    in_fence = False
    for i, line in enumerate(lines):
        # detect start/end of fenced code block (``` or ~~~)
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            new_lines.append(line.rstrip())
            continue

        # remove trailing whitespace
        fixed = line.rstrip()

        if in_fence:
            new_lines.append(fixed)
            continue

        # detect list item
        if re.match(r"^\s*[-*+]\s+", fixed):
            # look back for previous non-empty line
            prev_idx = len(new_lines) - 1
            prev_line = new_lines[prev_idx] if prev_idx >= 0 else ""
            if prev_line.strip() != "" and not re.match(r"^\s*[-*+]\s+", prev_line):
                new_lines.append("")
                changed += 1

        new_lines.append(fixed)

    new_text = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        changed += 1
    return changed


def main():
    root = Path(__file__).resolve().parents[1] / "docs"
    if not root.exists():
        print("docs/ not found")
        return 2
    total = 0
    for p in sorted(root.rglob("*.md")):
        c = fix_file(p)
        if c:
            print(f"Fixed {p} ({c} changes)")
            total += c
    if total == 0:
        print("No changes made")
    else:
        print(f"Applied {total} changes across docs/")


if __name__ == "__main__":
    main()
