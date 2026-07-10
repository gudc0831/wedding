#!/usr/bin/env python3
"""Validate and render proof pages from the Milan city study guidebook PDF."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader
import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "output" / "milan_city_study_guidebook_2026.pdf"
PROOF_DIR = ROOT / "output" / "browser-check" / "20260710-milan-city-study-guidebook-pdf"


REQUIRED_PHRASES = [
    "UNA HOTELS",
    "Via Fabio Filzi 25 B",
    "증빙확인",
    "예약필요",
    "Ceresio 7",
    "Risotto alla milanese",
    "Panettone",
    "Tax Free",
    "112",
]


def page_for(pages: list[str], phrase: str, start: int = 2) -> int | None:
    for index, text in enumerate(pages[start:], start=start):
        if phrase in text:
            return index
    return None


def main() -> None:
    if not PDF_PATH.is_file():
        raise SystemExit(f"Missing PDF: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))
    page_texts = [(page.extract_text() or "").strip() for page in reader.pages]
    full_text = "\n".join(page_texts)
    normalized_text = re.sub(r"\s+", " ", full_text)
    missing = [
        phrase
        for phrase in REQUIRED_PHRASES
        if re.sub(r"\s+", " ", phrase) not in normalized_text
    ]
    if "Risotto alla milanese" in missing and "Risotto" in full_text and "milanese" in full_text:
        missing.remove("Risotto alla milanese")
    blank_pages = [index + 1 for index, text in enumerate(page_texts) if len(text) < 5]

    a5_width = 419.528
    a5_height = 595.276
    bad_sizes: list[dict[str, float | int]] = []
    link_annotations = 0
    for index, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - a5_width) > 1.0 or abs(height - a5_height) > 1.0:
            bad_sizes.append({"page": index, "width": width, "height": height})
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            if annotation.get("/Subtype") == "/Link":
                link_annotations += 1

    chapter_pages: dict[str, int | None] = {}
    for chapter in range(1, 17):
        marker = f"{chapter}장."
        chapter_pages[str(chapter)] = page_for(page_texts, marker, start=3)

    chapter_sequence = [page for page in chapter_pages.values() if page is not None]
    chapter_order_ok = len(chapter_sequence) == 16 and chapter_sequence == sorted(chapter_sequence)

    target_phrases = [
        "목차",
        "이 여행의 확정 조건",
        "Duomo di Milano",
        "Brera가 특별한 이유",
        "밀라노 음식",
        "패션·디자인·식품 선물",
        "공식 출처",
        "최종 운영 카드",
    ]
    selected: list[int] = [0]
    for phrase in target_phrases:
        page_index = page_for(page_texts, phrase, start=0 if phrase == "목차" else 3)
        if page_index is not None and page_index not in selected:
            selected.append(page_index)
    last_index = len(page_texts) - 1
    if last_index not in selected:
        selected.append(last_index)

    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(PDF_PATH))
    proof_paths: list[str] = []
    for page_index in selected:
        bitmap = document[page_index].render(scale=1.7)
        image = bitmap.to_pil()
        output = PROOF_DIR / f"page-{page_index + 1:03d}.png"
        image.save(output)
        proof_paths.append(str(output))

    summary = {
        "pdf": str(PDF_PATH),
        "bytes": PDF_PATH.stat().st_size,
        "pages": len(reader.pages),
        "blank_pages": blank_pages,
        "bad_page_sizes": bad_sizes,
        "missing_required_phrases": missing,
        "replacement_character_count": full_text.count("�"),
        "link_annotations": link_annotations,
        "chapter_pages_zero_based": chapter_pages,
        "chapter_order_ok": chapter_order_ok,
        "proof_pages_zero_based": selected,
        "proof_images": proof_paths,
    }
    summary_path = PROOF_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if missing or blank_pages or bad_sizes or not chapter_order_ok or full_text.count("�"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
