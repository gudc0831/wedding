#!/usr/bin/env python3
"""Keep the latest revision of each chapter in the Milan guidebook source."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "info" / "milan_city_study_guidebook_2026.md"


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^# (\d+)장\.[^\n]*$", raw))
    if not matches:
        raise RuntimeError("No numbered chapters found")

    prefix = raw[: matches[0].start()].strip()
    chapters: dict[int, str] = {}
    revisions: dict[int, int] = {}
    for index, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        chapters[number] = raw[match.start() : end].strip()
        revisions[number] = revisions.get(number, 0) + 1

    expected = set(range(1, 17))
    if set(chapters) != expected:
        raise RuntimeError(f"Expected chapters 1-16, found {sorted(chapters)}")

    blocks = [chapters[number] for number in sorted(chapters)]
    normalized = "\n\n".join(([prefix] if prefix else []) + blocks) + "\n"
    SOURCE.write_text(normalized, encoding="utf-8", newline="\n")
    duplicates = {number: count for number, count in revisions.items() if count > 1}
    print(f"Normalized: {SOURCE}")
    print(f"Chapters: {sorted(chapters)}")
    print(f"Removed older revisions: {duplicates}")


if __name__ == "__main__":
    main()
