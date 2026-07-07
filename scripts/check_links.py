from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urldefrag

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    errors: list[str] = []
    for path in list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md")) + [ROOT / "templates" / "INDEX.md"]:
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            clean, _fragment = urldefrag(target)
            if not clean:
                continue
            candidate = (path.parent / clean).resolve()
            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)} links outside repo: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{path.relative_to(ROOT)} broken link: {target}")
    if errors:
        print("\n".join(errors))
        return 1
    print("OK: markdown links validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
