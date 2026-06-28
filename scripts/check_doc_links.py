#!/usr/bin/env python3
"""Offline relative-link checker for the monorepo's Markdown docs.

Scans tracked Markdown files for inline links `[text](target)` and verifies that
every *relative* link resolves to a file (or directory) that exists. External
links (http/https/mailto), in-page anchors (`#...`), and protocol-relative URLs
are skipped — this checker only guards intra-repo relative links so the
consolidation's "single front door, all intra-repo links" invariant cannot rot
(consolidation-design §2/§8).

Usage:
    python scripts/check_doc_links.py            # scan the whole repo
    python scripts/check_doc_links.py docs learn # scan specific roots

Exit code 0 when every relative link resolves; 1 (with a report) otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Inline-link target capture: the `(...)` of `[text](...)`. Stops at the first
# whitespace (so `(path "title")` keeps only the path) or closing paren.
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# Directories that are not part of the documentation surface.
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".sdd"}

# Subtrees excluded from link-checking by repo-relative prefix. reference/specs
# is the SDD engineering history (PDCA logs, gap analyses): frozen records that
# intentionally reference local-only artifacts (.sdd/, .venv/) and pinned source
# line numbers, not part of the learning front door this checker guards.
SKIP_REL_PREFIXES = ("reference/specs",)


def is_external(target: str) -> bool:
    """Return True for links this checker deliberately does not resolve."""
    return (
        target.startswith(("http://", "https://", "mailto:", "//", "#"))
        or target.startswith("tel:")
    )


def iter_markdown(roots: list[Path]):
    for root in roots:
        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts):
                continue
            if rel.startswith(SKIP_REL_PREFIXES):
                continue
            yield path


def check(roots: list[Path]) -> list[tuple[Path, int, str]]:
    broken: list[tuple[Path, int, str]] = []
    for md in iter_markdown(roots):
        lines = md.read_text(encoding="utf-8").splitlines()
        in_fence = False
        for lineno, line in enumerate(lines, start=1):
            # Skip fenced code blocks: ``` or ~~~ toggles. Avoids matching
            # Python like `class Judge[T](Protocol):` as a Markdown link.
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in LINK.finditer(line):
                target = m.group(1)
                if is_external(target):
                    continue
                # Strip any in-page anchor: link to a file plus heading.
                file_part = target.split("#", 1)[0]
                if not file_part:  # pure anchor like (#section)
                    continue
                resolved = (md.parent / file_part).resolve()
                if not resolved.exists():
                    broken.append((md, lineno, target))
    return broken


def main(argv: list[str]) -> int:
    roots = [REPO_ROOT / a for a in argv] if argv else [REPO_ROOT]
    broken = check(roots)
    if not broken:
        print("doc-links: OK — every relative Markdown link resolves.")
        return 0
    print(f"doc-links: {len(broken)} broken relative link(s):\n")
    for md, lineno, target in broken:
        print(f"  {md.relative_to(REPO_ROOT)}:{lineno}  ->  {target}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
