#!/usr/bin/env python3
"""Build the Milan city study guidebook as a print-ready A5 PDF."""

from __future__ import annotations

import argparse
import importlib.util
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "info" / "milan_city_study_guidebook_2026.md"
DEFAULT_HTML = ROOT / "output" / "milan_city_study_guidebook_2026.html"
DEFAULT_PDF = ROOT / "output" / "milan_city_study_guidebook_2026.pdf"


def load_base_builder():
    source = ROOT / "scripts" / "build-swiss-guidebook-pdf.py"
    spec = importlib.util.spec_from_file_location("guidebook_base", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load base builder: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base_builder()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--html-only", action="store_true")
    return parser.parse_args()


def cover_html() -> str:
    return """
<section class="cover milan-cover">
  <div class="cover-rail" aria-hidden="true"></div>
  <div class="milan-mark" aria-hidden="true">MI</div>
  <div class="cover-edition">CITY STUDY · HONEYMOON FIELD EDITION · 2026</div>
  <div class="cover-main">
    <p class="cover-eyebrow">MILANO</p>
    <h1>밀라노<br>도시 여행가이드북</h1>
    <p class="cover-subtitle">숙소에서 시작해 예술·건축·미식·디자인으로 읽는 도시</p>
    <p class="cover-deck">UNA HOTELS Century Milano를 베이스로<br>유명한 이유와 현장에서 볼 디테일까지 연결한 학습형 가이드</p>
  </div>
  <div class="cover-route" aria-label="도시 읽기 축">
    <span>CENTRALE</span><i></i><span>DUOMO</span><i></i><span>BRERA</span><i></i><span>NAVIGLI</span>
  </div>
  <div class="cover-meta">
    <div><b>TRAVEL DATES</b><span>2026.07.21 - 07.26</span></div>
    <div><b>BASE</b><span>UNA HOTELS CENTURY MILANO</span></div>
  </div>
  <div class="milan-grid" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>
</section>
"""


BASE_CSS = (
    BASE.CSS.replace("SWITZERLAND FIELD GUIDE", "MILANO CITY STUDY GUIDE")
    .replace("2026.07.16 - 07.21", "2026.07.21 - 07.26")
    .replace("INTERLAKEN · LUZERN", "MILANO · LOMBARDIA")
    .replace("--red: #d52b1e;", "--red: #a53b2f;")
    .replace("--pine: #176b5b;", "--pine: #1f584d;")
    .replace("--lake: #2d7694;", "--lake: #2d6671;")
    .replace('content: "FIELD CHAPTER";', 'content: "CITY STUDY CHAPTER";')
    .replace('content: "DAY OPERATIONS";', 'content: "FIELD ROUTE";')
)


EXTRA_CSS = r"""
.milan-cover { background: #f4efe5; }
.milan-cover .cover-rail { width: 9mm; background: #a53b2f; }
.milan-cover .cover-main { top: 46mm; left: 21mm; right: 12mm; }
.milan-cover .cover-main h1 { font-size: 29pt; line-height: 1.17; }
.milan-cover .cover-subtitle { max-width: 102mm; color: #9b6a2f; font-size: 12.5pt; line-height: 1.52; }
.milan-cover .cover-deck { margin-top: 10mm; }
.milan-cover .cover-route { left: 21mm; bottom: 55mm; }
.milan-cover .cover-meta { left: 21mm; }

.milan-mark {
  position: absolute;
  top: 14mm;
  right: 13mm;
  display: grid;
  width: 15mm;
  height: 15mm;
  place-items: center;
  border: 0.55mm solid #a53b2f;
  color: #a53b2f;
  font-size: 8pt;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.milan-grid { position: absolute; right: -7mm; bottom: 74mm; width: 43mm; height: 43mm; transform: rotate(-10deg); }
.milan-grid i { position: absolute; display: block; background: #c6bba9; opacity: 0.78; }
.milan-grid i:nth-child(1), .milan-grid i:nth-child(2), .milan-grid i:nth-child(3) { top: 0; bottom: 0; width: 0.28mm; }
.milan-grid i:nth-child(1) { left: 8mm; }
.milan-grid i:nth-child(2) { left: 21mm; }
.milan-grid i:nth-child(3) { left: 34mm; }
.milan-grid i:nth-child(4), .milan-grid i:nth-child(5), .milan-grid i:nth-child(6) { left: 0; right: 0; height: 0.28mm; }
.milan-grid i:nth-child(4) { top: 8mm; }
.milan-grid i:nth-child(5) { top: 21mm; }
.milan-grid i:nth-child(6) { top: 34mm; }

.chapter-title { border-top-color: #a53b2f; }
.chapter-title::before, .toc-kicker { color: #a53b2f; }
h2.day-title { border-bottom-color: #9b6a2f; color: #714922; }
h2.day-title::before { color: #9b6a2f; }

.lead {
  margin: 0 0 6mm;
  padding: 4.5mm 5mm;
  border: 0.3mm solid #d9cdb9;
  border-radius: 2mm;
  background: #f8f3ea;
  color: #394a45;
  font-size: 9.4pt;
  line-height: 1.7;
}

.guide-map {
  margin: 5mm 0 6mm;
  break-inside: avoid-page;
}
.guide-map img {
  display: block;
  width: 100%;
  max-height: 100mm;
  border: 0.3mm solid #cfd7d3;
  border-radius: 2mm;
  object-fit: contain;
  background: white;
}
.guide-map figcaption {
  margin-top: 2mm;
  color: #6b7572;
  font-size: 6.8pt;
  line-height: 1.45;
}

.lens-grid,
.method-grid,
.decision-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 3mm;
  margin: 4mm 0 5mm;
}
.lens-card,
.method-card,
.decision-card {
  padding: 3.6mm 3.8mm;
  border: 0.28mm solid #d1d9d5;
  border-radius: 1.8mm;
  background: #f7f8f5;
  break-inside: avoid-page;
}
.lens-card h3,
.method-card h3,
.decision-card h3 { margin: 0 0 1.6mm; font-size: 9.2pt; }
.lens-card p,
.method-card p,
.decision-card p { margin: 0; color: #52605c; font-size: 7.7pt; line-height: 1.55; }

.fact-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 2.4mm;
  margin: 4mm 0 5mm;
}
.fact-strip div {
  padding: 3mm;
  border-top: 1.2mm solid #2d6671;
  background: #eef4f3;
  break-inside: avoid-page;
}
.fact-strip b { display: block; margin-bottom: 1mm; color: #173b34; font-size: 6.4pt; text-transform: uppercase; }
.fact-strip span { display: block; color: #243532; font-size: 8pt; font-weight: 800; line-height: 1.35; }

.status-confirmed,
.status-required,
.status-option,
.status-closed {
  display: inline-block;
  margin-right: 1mm;
  padding: 0.55mm 1.4mm;
  border-radius: 99mm;
  color: white;
  font-size: 6.2pt;
  font-weight: 900;
  line-height: 1.25;
  vertical-align: 0.2mm;
}
.status-confirmed { background: #1f584d; }
.status-required { background: #b26034; }
.status-option { background: #64727f; }
.status-closed { background: #9a3540; }

.look-list li strong:first-child { color: #9b6a2f; }
.source-list { font-size: 7.2pt; line-height: 1.5; }
.source-list li { margin-bottom: 1.4mm; }
.source-list a { overflow-wrap: anywhere; }
.small { color: #68736f; font-size: 7.1pt; line-height: 1.52; }
.page-break { break-before: page; }

@media print {
  .lens-card, .method-card, .decision-card, .fact-strip div, .guide-map { break-inside: avoid; }
}
"""


def build_html(markdown_source: str) -> str:
    chapter_matches = list(re.finditer(r"(?m)^# (\d+)장\.[^\n]*$", markdown_source))
    if chapter_matches:
        prefix = markdown_source[: chapter_matches[0].start()]
        # Keep the latest revision of each chapter.  The working manuscript may
        # still contain an older chapter block while a rewritten block is added
        # later in the file; rendering both would duplicate entire chapters.
        chapters: dict[int, str] = {}
        for index, match in enumerate(chapter_matches):
            end = chapter_matches[index + 1].start() if index + 1 < len(chapter_matches) else len(markdown_source)
            chapters[int(match.group(1))] = markdown_source[match.start() : end]
        markdown_source = prefix + "\n".join(chapters[number] for number in sorted(chapters))

    prepared, headings = BASE.preprocess_markdown(markdown_source)
    manuscript = BASE.render_markdown(prepared)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Honeymoon City Study Guide">
  <meta name="description" content="UNA HOTELS Century Milano 기반 밀라노 도시 학습형 여행가이드북">
  <title>밀라노 도시 여행가이드북 2026</title>
  <style>{BASE_CSS}{EXTRA_CSS}</style>
</head>
<body>
{cover_html()}
{BASE.build_toc(headings)}
<main class="manuscript">
{manuscript}
</main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    source_path = args.source.resolve()
    html_path = args.html.resolve()
    pdf_path = args.pdf.resolve()
    markdown_source = source_path.read_text(encoding="utf-8")
    html_output = build_html(markdown_source)

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html_output, encoding="utf-8", newline="\n")
    print(f"HTML: {html_path}")

    if not args.html_only:
        browser = BASE.find_browser()
        temp_root = ROOT / "output" / ".milan-guidebook-tmp"
        temp_root.mkdir(parents=True, exist_ok=True)
        tempfile.tempdir = str(temp_root)
        BASE.print_pdf(browser, html_path, pdf_path)
        try:
            temp_root.rmdir()
        except OSError:
            pass
        print(f"PDF: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
