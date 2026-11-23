#!/usr/bin/env python3
"""Copy this repository's licence and provenance notice into the carried content.

The `.smod` is what players download, and the licence requires its notice to
travel with copies of the work, so the notice rides as data the game ignores:
`data/cloudglass/license/license.txt` and `data/cloudglass/license/notice.txt`, written from
the repository's `LICENSE` and `LICENSE-NOTICE.md`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "cloudglass" / "license"

OUT.mkdir(parents=True, exist_ok=True)
for source, name in (("LICENSE", "license.txt"), ("LICENSE-NOTICE.md", "notice.txt")):
    text = (ROOT / source).read_text()
    (OUT / name).write_text(text)
    print(f"wrote {OUT / name}")
