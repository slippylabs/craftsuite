"""Shared helper for the noai/<app>.py and delink/<app>.py patch scripts.

Every edit names the exact text it replaces and must match exactly once, so
an upstream release that moves the code makes the patch FAIL rather than
quietly leave an AI feature or a promo link in. sync.sh then refuses that
release.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()


def sub(rel, old, new, count=1):
    p = ROOT / rel
    s = p.read_text()
    n = s.count(old)
    if n != count:
        sys.exit(f"{pathlib.Path(sys.argv[0]).parent.name}/{pathlib.Path(sys.argv[0]).name}: {rel}: expected {count} match(es), found {n}:\n{old[:200]}")
    p.write_text(s.replace(old, new))




# The ArtCraft community and project links: the Discord invite, getartcraft.com
# (and its /apps/<app> pages), and the storytold GitHub repos and their issue
# trackers. The craft-fonts repo is only ever named in font attribution, which
# stays.
PROMO = re.compile(
    r"(?:https?://)?(?:"
    r"discord\.(?:gg|com)/(?:invite/)?artcraft"
    r"|(?:www\.)?getartcraft\.com(?:/apps)?(?:/[A-Za-z_{}]+)?/?"
    r"|github\.com/storytold/(?!craft-fonts)[A-Za-z0-9_.{}-]*(?:/[A-Za-z0-9_.#/?=&{}-]*)?"
    r")",
    re.I)
# A TOML line naming a project link: Cargo's repository/homepage/documentation.
META_KEY = re.compile(r'^\s*(?:repository|homepage|documentation)\s*=.*$', re.M)


def scrub():
    """Blank every promo URL in the source that reaches the build.

    The patch's sub() edits take the buttons and menu items out; this clears
    the URLs those leave behind -- in link tables, tooltips and every
    language's translation of them -- so that nothing in the app can open one
    and sync.sh's PROMO check passes. Keys and their translations change the
    same way, so lookups still match. Cargo's repository/homepage keys are
    left empty rather than removed (env!("CARGO_PKG_REPOSITORY") reaches the
    binary, and members inherit them with `repository.workspace = true`).
    """
    hits = 0
    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or "target" in p.parts:
            continue
        if p.suffix not in (".rs", ".tsv", ".ftl", ".json", ".toml", ".html", ".js", ".txt", ".css"):
            continue
        if p.suffix in (".json", ".txt") and "i18n" not in p.parts and "locales" not in p.parts:
            continue
        s = p.read_text(errors="surrogateescape")
        if p.suffix == ".toml":
            # Only the package's own links: git dependencies on other storytold
            # repos (EffectCraft builds FilmCraft's codecs) must keep their URLs.
            t = META_KEY.sub(lambda m: PROMO.sub("", m.group(0)), s)
        else:
            t = PROMO.sub("", s)
        if t != s:
            hits += 1
            p.write_text(t, errors="surrogateescape")
    if not hits:
        sys.exit(f"{pathlib.Path(sys.argv[0]).name}: scrub() found no promo links -- has upstream changed?")


def plain_credits(rel="crates/ui-egui/src/credits.rs"):
    """About > Contributors: keep every name, drop the link to their GitHub."""
    sub(rel, 'ui.hyperlink_to(c.name(v.names), format!("https://github.com/{}", c.login))',
        "ui.label(c.name(v.names))", count=2)


def cut(rel, start, end, keep=""):
    """Remove the text from `start` up to (not including) `end`, putting `keep` in its place.

    For blocks too long to quote whole. Both ends must occur exactly once in the file, and
    `end` after `start`.
    """
    p = ROOT / rel
    s = p.read_text()
    for a in (start, end):
        if s.count(a) != 1:
            sys.exit(f"{pathlib.Path(sys.argv[0]).name}: {rel}: expected 1 match, found {s.count(a)}:\n{a[:200]}")
    i, j = s.index(start), s.index(end)
    if j < i:
        sys.exit(f"{pathlib.Path(sys.argv[0]).name}: {rel}: end comes before start:\n{end[:200]}")
    p.write_text(s[:i] + keep + s[j:])
