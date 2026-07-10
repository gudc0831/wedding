#!/usr/bin/env python3
"""Verify the checked-in Swiss and Prague guidebook PDF artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPECS = [
    (ROOT / "output" / "swiss_interlaken_lucerne_guidebook_2026.pdf", 50),
    (ROOT / "output" / "pdf" / "prague_city_field_guide_2026_ko.pdf", 50),
]
A5_WIDTH = 419.528
A5_HEIGHT = 595.276


def verify_pdf(path: Path, minimum_pages: int) -> dict[str, object]:
    reader = PdfReader(str(path))
    blank_pages = []
    bad_a5_pages = []
    for index, page in enumerate(reader.pages, start=1):
        if len((page.extract_text() or "").strip()) < 5:
            blank_pages.append(index)
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - A5_WIDTH) > 1 or abs(height - A5_HEIGHT) > 1:
            bad_a5_pages.append(index)

    valid = (
        path.read_bytes()[:4] == b"%PDF"
        and len(reader.pages) >= minimum_pages
        and not blank_pages
        and not bad_a5_pages
    )
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "pages": len(reader.pages),
        "blankPages": blank_pages,
        "badA5Pages": bad_a5_pages,
        "valid": valid,
    }


def main() -> None:
    results = [verify_pdf(path, minimum_pages) for path, minimum_pages in SPECS]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not all(result["valid"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
