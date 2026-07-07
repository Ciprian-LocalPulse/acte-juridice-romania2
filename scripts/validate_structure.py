from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "scripts" / "catalog.json").read_text(encoding="utf-8"))
DIACRITICS = "\u0103\u00e2\u00ee\u0219\u021b\u0102\u00c2\u00ce\u0218\u021a\u015f\u0163\u015e\u0162"
REQUIRED = ["## Cand se foloseste", "## Temei legal", "## Model", "## Checklist inainte de semnare"]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    expected = []
    for category in CATALOG:
        category_dir = ROOT / "templates" / category["category"]
        if not category_dir.is_dir():
            fail(f"Missing category directory: {category_dir}", errors)
        for item in category["files"]:
            expected.append(category_dir / item["file"])

    model_files = [path for path in (ROOT / "templates").glob("**/*.md") if path.name != "INDEX.md"]
    if len(model_files) != 480:
        fail(f"Expected 480 model files, found {len(model_files)}", errors)

    missing = [path for path in expected if not path.exists()]
    for path in missing:
        fail(f"Missing model file: {path.relative_to(ROOT)}", errors)

    extra = sorted(set(model_files) - set(expected))
    for path in extra:
        fail(f"Unexpected model file: {path.relative_to(ROOT)}", errors)

    for path in expected:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED:
            if section not in text:
                fail(f"{path.relative_to(ROOT)} missing section {section}", errors)
        if any(char in text for char in DIACRITICS):
            fail(f"{path.relative_to(ROOT)} contains Romanian diacritics", errors)
        fields = re.findall(r"\[[^\]\n]+\]", text)
        for field in fields:
            body = field[1:-1]
            if body != body.upper() or not re.fullmatch(r"[A-Z0-9_ ./,-]+", body):
                fail(f"{path.relative_to(ROOT)} has invalid field {field}", errors)
        checklist = text.split("## Checklist inainte de semnare", 1)[-1]
        checks = re.findall(r"^- \[ \] ", checklist, flags=re.M)
        if not (5 <= len(checks) <= 12):
            fail(f"{path.relative_to(ROOT)} has {len(checks)} checklist items", errors)

    if errors:
        print("\n".join(errors))
        return 1
    print("OK: 480 models, 51 categories, required sections, fields and checklists validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
