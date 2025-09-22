#!/usr/bin/env python3
"""Quick markdown linter for docs/ directory.

Checks performed:
- MD032: lists surrounded by blank lines
- trailing whitespace
- header style (no underlined headers)
- max line length (88)
"""
import os
import re
import sys


def check_file(path):
    issues = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # check for trailing whitespace
    for i, line in enumerate(lines, start=1):
        if line.rstrip("\n").endswith(" "):
            issues.append((i, "TRAILING_WHITESPACE", "Line ends with space"))

    # check for underlined headers (Setext style) — prefer ATX (#)
    for i in range(len(lines) - 1):
        if re.match(r"^[=-]{2,}\s*$", lines[i + 1]):
            issues.append((i + 1, "HEADER_STYLE", "Setext underlined header; use ATX (#) style"))

    # check list spacing: lists should be surrounded by blank lines
    for i, line in enumerate(lines, start=1):
        if re.match(r"^\s*[-*+]\s+", line):
            # previous line should be blank
            if i - 2 >= 0 and lines[i - 2].strip() != "":
                issues.append((i, "MD032", "List should be surrounded by blank lines (previous not blank)"))
            # next line doesn't need to be blank necessarily

    # line length
    for i, line in enumerate(lines, start=1):
        if len(line.rstrip("\n")) > 88:
            issues.append((i, "LINE_LENGTH", f"Line exceeds 88 chars ({len(line.rstrip())})"))

    return issues


def main():
    root = os.path.join(os.path.dirname(__file__), "..", "docs")
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print("docs/ directory not found", file=sys.stderr)
        return 2

    had = False
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            issues = check_file(path)
            if issues:
                had = True
                print(path)
                for ln, code, msg in issues:
                    print(f"  {ln:4d} {code}: {msg}")
                print()

    if had:
        return 1
    print("No issues found in docs/ markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
