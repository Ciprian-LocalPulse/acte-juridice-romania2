from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "scripts" / "catalog.json").read_text(encoding="utf-8"))


def main() -> None:
    parts = ["# Indexul complet al modelelor", ""]
    for category in CATALOG:
        parts.extend([f"## {category['title']}", ""])
        for item in category["files"]:
            path = ROOT / "templates" / category["category"] / item["file"]
            if not path.exists():
                raise SystemExit(f"Missing file: {path.relative_to(ROOT)}")
            parts.append(f"- [{item['title']}](./{category['category']}/{item['file']}) - Model pentru {item['title'].lower()}.")
        parts.append("")
    (ROOT / "templates" / "INDEX.md").write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8", newline="\n")
    print("Generated templates/INDEX.md")


if __name__ == "__main__":
    main()
