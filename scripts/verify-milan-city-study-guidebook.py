#!/usr/bin/env python3
"""Verify and render the Milan city-study guidebook PDF."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "output" / "milan_city_study_guidebook_2026.html"
PDF = ROOT / "output" / "milan_city_study_guidebook_2026.pdf"
RENDER_DIR = ROOT / "output" / "browser-check" / "20260710-milan-city-study-guidebook"


def html_checks() -> None:
    raw = HTML.read_text(encoding="utf-8")
    headings = re.findall(r"<h1\b[^>]*>(.*?)</h1>", raw, flags=re.DOTALL)
    clean_headings = [re.sub(r"<[^>]+>", "", heading).strip() for heading in headings]
    chapter_numbers = [int(match) for match in re.findall(r"<h1\b[^>]*>\s*(\d+)장\.", raw)]
    expected = list(range(1, 17))

    local_images: list[Path] = []
    for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', raw):
        parsed = urlparse(src)
        if parsed.scheme or src.startswith("data:"):
            continue
        local_images.append((HTML.parent / unquote(parsed.path)).resolve())
    missing_images = [str(path) for path in local_images if not path.exists()]
    hrefs = re.findall(r'<a\b[^>]*\bhref="([^"]+)"', raw)
    external_hrefs = [href for href in hrefs if href.startswith(("http://", "https://"))]
    broken_hrefs = [href for href in hrefs if href.startswith("<") or "%3Chttp" in href]

    print(f"HTML headings: {len(clean_headings)}")
    print(f"Chapter order: {chapter_numbers}")
    print(f"Chapter order valid: {chapter_numbers == expected}")
    print(f"Local images: {len(local_images)}")
    print(f"Missing local images: {missing_images}")
    print(f"HTML external links: {len(external_hrefs)}")
    print(f"Broken HTML hrefs: {broken_hrefs}")


def pdf_checks() -> tuple[int, str]:
    reader = PdfReader(str(PDF))
    page_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(page_text)
    required = [
        "UNA HOTELS",
        "증빙확인",
        "예약필요",
        "Ceresio 7",
        "Navigli",
        "Ossobuco",
        "Tax Free",
        "최종 운영 카드",
    ]
    print(f"PDF pages: {len(reader.pages)}")
    print(f"PDF bytes: {PDF.stat().st_size}")
    print(f"Extracted text chars: {len(text)}")
    near_empty = [index + 1 for index, value in enumerate(page_text) if len(value.strip()) < 40]
    print(f"Near-empty pages: {near_empty}")
    pdf_uris: list[str] = []
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                pdf_uris.append(str(action.get("/URI")))
    invalid_pdf_uris = [uri for uri in pdf_uris if not uri.startswith(("https://", "http://", "mailto:"))]
    print(f"PDF link annotations: {len(pdf_uris)}")
    print(f"Invalid PDF URIs: {invalid_pdf_uris}")
    for phrase in required:
        print(f"Contains {phrase!r}: {phrase in text}")
    return len(reader.pages), text


def render_contact_sheets(page_count: int) -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(PDF)
    thumb_size = (210, 297)
    label_height = 24
    cols, rows = 4, 4
    cell_size = (thumb_size[0], thumb_size[1] + label_height)

    pages: list[Image.Image] = []
    for index in range(page_count):
        page = document[index]
        bitmap = page.render(scale=0.75)
        image = bitmap.to_pil().convert("RGB")
        image.thumbnail(thumb_size, Image.Resampling.LANCZOS)
        cell = Image.new("RGB", cell_size, "white")
        x = (thumb_size[0] - image.width) // 2
        cell.paste(image, (x, label_height))
        ImageDraw.Draw(cell).text((7, 5), f"PAGE {index + 1}", fill="#273a36")
        pages.append(cell)

    per_sheet = cols * rows
    for start in range(0, len(pages), per_sheet):
        sheet = Image.new("RGB", (cell_size[0] * cols, cell_size[1] * rows), "#d8dedb")
        for offset, page in enumerate(pages[start : start + per_sheet]):
            x = (offset % cols) * cell_size[0]
            y = (offset // cols) * cell_size[1]
            sheet.paste(page, (x, y))
        sheet_number = start // per_sheet + 1
        sheet.save(RENDER_DIR / f"contact-sheet-{sheet_number:02d}.png", optimize=True)

    selected = sorted(
        index
        for index in {
            0,
            1,
            15,
            17,
            21,
            41,
            51,
            53,
            page_count // 2,
            page_count - 2,
            page_count - 1,
        }
        if 0 <= index < page_count
    )
    for index in selected:
        page = document[index]
        bitmap = page.render(scale=1.8)
        bitmap.to_pil().convert("RGB").save(
            RENDER_DIR / f"page-{index + 1:03d}.png", optimize=True
        )
    print(f"Rendered pages: {RENDER_DIR}")


def main() -> None:
    html_checks()
    page_count, _ = pdf_checks()
    render_contact_sheets(page_count)


if __name__ == "__main__":
    main()
