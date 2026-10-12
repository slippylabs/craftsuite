"""Shared helper for the noai/<app>.py patch scripts.

Every edit names the exact text it replaces and must match exactly once, so
an upstream release that moves the code makes the patch FAIL rather than
quietly leave an AI feature in. sync.sh then refuses that release.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()


def sub(rel, old, new, count=1):
    p = ROOT / rel
    s = p.read_text()
    n = s.count(old)
    if n != count:
        sys.exit(f"noai: {rel}: expected {count} match(es), found {n}:\n{old[:200]}")
    p.write_text(s.replace(old, new))


