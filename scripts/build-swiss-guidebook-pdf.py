#!/usr/bin/env python3
"""Build the Swiss honeymoon field guide as a print-ready A5 PDF."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "info" / "swiss_interlaken_lucerne_guidebook_2026.md"
DEFAULT_HTML = ROOT / "output" / "swiss_interlaken_lucerne_guidebook_2026.html"
DEFAULT_PDF = ROOT / "output" / "swiss_interlaken_lucerne_guidebook_2026.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--html-only", action="store_true")
    return parser.parse_args()


def find_browser() -> Path:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for command in ("chrome", "msedge"):
        resolved = shutil.which(command)
        if resolved:
            candidates.insert(0, Path(resolved))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError("Chrome or Microsoft Edge is required to build the PDF.")


def slugify(value: str, seen: dict[str, int]) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip().lower()
    normalized = re.sub(r"[`*_]", "", normalized)
    normalized = re.sub(r"[^0-9a-z가-힣]+", "-", normalized).strip("-")
    base = normalized or "section"
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}-{seen[base]}"


def extract_body(source: str) -> str:
    first_chapter = re.search(r"(?m)^# 1장\. 이 여행의 확정 조건\s*$", source)
    if not first_chapter:
        raise ValueError("Could not find the first chapter in the manuscript.")
    return source[first_chapter.start() :]


def preprocess_markdown(source: str) -> tuple[str, list[dict[str, str | int]]]:
    source = extract_body(source)
    source = re.sub(r"(?m)^\\newpage\s*$", "", source)
    source = re.sub(
        r"(?m)^(\s*)- \[ \] (.+)$",
        r'\1- <span class="checkbox" aria-hidden="true"></span> \2',
        source,
    )
    source = re.sub(
        r"(?m)^(\s*)- \[[xX]\] (.+)$",
        r'\1- <span class="checkbox checked" aria-hidden="true"></span> \2',
        source,
    )
    source = re.sub(
        r"(?<![<(=\"'])https://[^\s|>]+",
        lambda match: f"<{match.group(0).rstrip('.,;')}>" + match.group(0)[len(match.group(0).rstrip('.,;')) :],
        source,
    )

    seen: dict[str, int] = {}
    headings: list[dict[str, str | int]] = []

    def replace_heading(match: re.Match[str]) -> str:
        level = len(match.group(1))
        title = match.group(2).strip()
        anchor = slugify(title, seen)
        classes: list[str] = []
        if level == 1:
            classes.append("chapter-title")
        if level == 2 and re.match(r"9\.[1-6]\s", title):
            classes.append("day-title")
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        headings.append({"level": level, "title": title, "anchor": anchor})
        return f'<h{level} id="{anchor}"{class_attr}>{html.escape(title)}</h{level}>'

    source = re.sub(r"(?m)^(#{1,6})[ \t]+(.+?)[ \t]*$", replace_heading, source)
    return source, headings


def build_toc(headings: list[dict[str, str | int]]) -> str:
    excluded = {
        "이 장에서 알 수 있는 것",
        "핵심 체크포인트",
        "최종 핵심 체크포인트",
    }
    entries: list[str] = []
    for heading in headings:
        level = int(heading["level"])
        title = str(heading["title"])
        if title in excluded:
            continue
        if level == 1 or (level == 2 and re.match(r"\d+\.\d+\s", title)):
            entries.append(
                f'<li class="toc-level-{level}"><a href="#{heading["anchor"]}">'
                f'<span>{html.escape(title)}</span><span class="toc-dot" aria-hidden="true"></span>'
                "</a></li>"
            )
    return (
        '<section class="toc" aria-labelledby="toc-title">'
        '<div class="toc-kicker">FIELD INDEX</div>'
        '<h1 id="toc-title">목차</h1>'
        '<p class="toc-lead">장과 절 제목을 누르면 해당 페이지로 이동합니다.</p>'
        f'<ol class="toc-list">{"".join(entries)}</ol>'
        "</section>"
    )


def classify_callouts(rendered: str) -> str:
    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        plain = re.sub(r"<[^>]+>", " ", inner)
        if "방문 전" in plain or "공식 사이트" in plain:
            callout_class = "verify"
        elif "주의" in plain or "절대" in plain:
            callout_class = "warning"
        elif "운영 원칙" in plain or "핵심" in plain:
            callout_class = "rule"
        else:
            callout_class = "note"
        return f'<blockquote class="callout {callout_class}">{inner}</blockquote>'

    return re.sub(r"<blockquote>\s*(.*?)\s*</blockquote>", replace, rendered, flags=re.S)


def classify_tables(rendered: str) -> str:
    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        column_count = len(re.findall(r"<th(?:\s[^>]*)?>", inner))
        table_class = "data-table compact-table" if column_count >= 5 else "data-table"
        return f'<div class="table-wrap"><table class="{table_class}">{inner}</table></div>'

    return re.sub(r"<table>\s*(.*?)\s*</table>", replace, rendered, flags=re.S)


def classify_media(rendered: str) -> str:
    pattern = re.compile(
        r'<p><img src="([^"]+)" alt="([^"]*)"(?: title="([^"]*)")?\s*/?></p>',
        flags=re.S,
    )

    def replace(match: re.Match[str]) -> str:
        source, alt_text, title = match.groups()
        source_key = html.unescape(source).lower()
        classes = ["media-figure"]
        if "/maps/" in source_key or source_key.endswith(".svg"):
            classes.append("map-figure")
        else:
            classes.append("photo-figure")
        if "panorama" in source_key or "hohematte" in source_key:
            classes.append("panorama-figure")
        if "historic" in source_key:
            classes.append("historic-figure")
        caption = title or alt_text
        caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
        return (
            f'<figure class="{" ".join(classes)}">'
            f'<img src="{source}" alt="{alt_text}">{caption_html}</figure>'
        )

    return pattern.sub(replace, rendered)


def render_markdown(source: str) -> str:
    parser = MarkdownIt(
        "commonmark",
        {"html": True, "breaks": False, "linkify": False, "typographer": False},
    ).enable("table")
    rendered = parser.render(source)
    rendered = classify_callouts(rendered)
    rendered = classify_tables(rendered)
    rendered = classify_media(rendered)
    return rendered


def cover_html() -> str:
    return """
<section class="cover">
  <div class="cover-rail" aria-hidden="true"></div>
  <div class="swiss-mark" aria-hidden="true"><span></span></div>
  <div class="cover-edition">HONEYMOON FIELD EDITION · 2026</div>
  <div class="cover-main">
    <p class="cover-eyebrow">SWITZERLAND</p>
    <h1>인터라켄<br>· 루체른</h1>
    <p class="cover-subtitle">실전 여행가이드북</p>
    <p class="cover-deck">확정된 예약과 이동 순서를 지키면서<br>현장에서 바로 꺼내 보는 여행 운영 매뉴얼</p>
  </div>
  <div class="cover-route" aria-label="여행 구간">
    <span>LUZERN</span><i></i><span>RIGI</span><i></i><span>INTERLAKEN</span><i></i><span>GRINDELWALD</span>
  </div>
  <div class="cover-meta">
    <div><b>TRAVEL DATES</b><span>2026.07.16 - 07.21</span></div>
    <div><b>FORMAT</b><span>A5 · OFFLINE FIELD GUIDE</span></div>
  </div>
  <div class="cover-lines" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
</section>
"""


CSS = r"""
@page {
  size: A5 portrait;
  margin: 14mm 12mm 16mm;
  @top-left {
    content: "SWITZERLAND FIELD GUIDE";
    color: #6e7976;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.5pt;
    font-weight: 700;
    letter-spacing: 0;
  }
  @top-right {
    content: "2026.07.16 - 07.21";
    color: #8a9390;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.5pt;
  }
  @bottom-left {
    content: "INTERLAKEN · LUZERN";
    color: #8a9390;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.5pt;
  }
  @bottom-right {
    content: counter(page) " / " counter(pages);
    color: #33403d;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 7pt;
    font-weight: 700;
  }
}

@page cover {
  size: A5 portrait;
  margin: 0;
  @top-left { content: none; }
  @top-right { content: none; }
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}

@page toc {
  size: A5 portrait;
  margin: 14mm 12mm 15mm;
  @top-left { content: "CONTENTS"; }
}

:root {
  --ink: #1d2926;
  --muted: #65716e;
  --paper: #fbfbf8;
  --line: #d9dfdc;
  --red: #d52b1e;
  --pine: #176b5b;
  --lake: #2d7694;
  --soft-red: #fff0ed;
  --soft-green: #edf6f2;
  --soft-blue: #edf5f8;
  --soft-gray: #f1f3f1;
}

* { box-sizing: border-box; }

html {
  color: var(--ink);
  background: var(--paper);
  font-family: "Pretendard", "Noto Sans KR", "Malgun Gothic", sans-serif;
  font-size: 9.1pt;
  line-height: 1.67;
  word-break: keep-all;
  overflow-wrap: anywhere;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}

body { margin: 0; background: var(--paper); }

a { color: #155e75; text-decoration: none; }
a[href^="http"] { overflow-wrap: anywhere; }

p { margin: 0 0 3.1mm; }
strong { color: #15201e; font-weight: 800; }
code {
  padding: 0.15em 0.35em;
  border: 0.25mm solid #d8dfdc;
  border-radius: 1mm;
  background: #f2f5f3;
  color: #315249;
  font-family: Consolas, "Malgun Gothic", monospace;
  font-size: 0.88em;
  white-space: normal;
}

hr {
  height: 0;
  margin: 7mm 0;
  border: 0;
  border-top: 0.35mm solid var(--line);
}

h1, h2, h3, h4, h5, h6 {
  margin: 0;
  color: var(--ink);
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.34;
  break-after: avoid-page;
}

.chapter-title {
  margin: 0 0 8mm;
  padding: 17mm 0 5mm;
  border-top: 2.3mm solid var(--red);
  color: #15211e;
  font-size: 20pt;
  break-before: page;
}

.chapter-title::before {
  display: block;
  margin-bottom: 3mm;
  color: var(--red);
  content: "FIELD CHAPTER";
  font-size: 7pt;
  font-weight: 800;
}

h2 {
  margin: 7mm 0 3.2mm;
  padding-bottom: 1.5mm;
  border-bottom: 0.45mm solid #b7c1bd;
  color: #173b34;
  font-size: 13.5pt;
}

h2.day-title {
  margin-top: 0;
  padding-top: 12mm;
  border-bottom: 1.2mm solid var(--lake);
  color: #174b5f;
  font-size: 16pt;
  break-before: page;
}

h2.day-title::before {
  display: block;
  margin-bottom: 2.5mm;
  color: var(--lake);
  content: "DAY OPERATIONS";
  font-size: 7pt;
  font-weight: 800;
}

h3 { margin: 5mm 0 2.2mm; color: #245d52; font-size: 10.8pt; }
h4 { margin: 4mm 0 2mm; color: #315f58; font-size: 9.8pt; }

ul, ol { margin: 0 0 3.5mm; padding-left: 5.7mm; }
li { margin: 1.1mm 0; padding-left: 0.6mm; }
li::marker { color: var(--pine); font-weight: 700; }
li:has(> .checkbox) { margin-left: -5.5mm; padding-left: 0; list-style: none; }

.checkbox {
  display: inline-block;
  width: 3.1mm;
  height: 3.1mm;
  margin: 0 1.8mm -0.45mm 0;
  border: 0.4mm solid #70807b;
  border-radius: 0.6mm;
  background: white;
}

.checkbox.checked { background: var(--pine); box-shadow: inset 0 0 0 0.65mm white; }

.callout {
  position: relative;
  margin: 5mm 0;
  padding: 4mm 4.5mm 4mm 5.2mm;
  border: 0;
  border-left: 1.2mm solid var(--lake);
  border-radius: 0 1.5mm 1.5mm 0;
  background: var(--soft-blue);
  color: #263835;
  break-inside: avoid-page;
}

.callout p:last-child { margin-bottom: 0; }
.callout.verify { border-color: var(--pine); background: var(--soft-green); }
.callout.warning { border-color: var(--red); background: var(--soft-red); }
.callout.rule { border-color: #3e6259; background: var(--soft-gray); }

.table-wrap {
  width: 100%;
  margin: 4.5mm 0 5mm;
  break-inside: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  table-layout: fixed;
  font-size: 7.65pt;
  line-height: 1.48;
}

.data-table thead { display: table-header-group; }
.data-table tr { break-inside: avoid-page; }
.data-table th,
.data-table td {
  padding: 2.2mm 2.1mm;
  border: 0.25mm solid #cfd7d3;
  vertical-align: top;
  overflow-wrap: anywhere;
  word-break: normal;
}

.data-table th {
  background: #244b43;
  color: white;
  font-weight: 800;
  text-align: left;
}

.data-table tbody tr:nth-child(even) td { background: #f3f6f4; }
.data-table.compact-table { font-size: 6.35pt; line-height: 1.38; }
.data-table.compact-table th,
.data-table.compact-table td { padding: 1.55mm 1.25mm; }

.media-figure {
  width: 100%;
  margin: 5mm 0 6mm;
  break-inside: avoid-page;
}

.media-figure img {
  display: block;
  width: 100%;
  max-height: 82mm;
  border-radius: 1.2mm;
  background: #eef1ef;
  object-fit: cover;
}

.media-figure.panorama-figure img { max-height: 65mm; }
.media-figure.historic-figure img { max-height: 76mm; object-fit: contain; }

.media-figure.map-figure img {
  max-height: none;
  padding: 1.2mm;
  border: 0.3mm solid #cfd7d3;
  border-radius: 1.2mm;
  background: white;
  object-fit: contain;
}

.media-figure figcaption {
  margin-top: 1.6mm;
  padding-left: 2.2mm;
  border-left: 0.8mm solid var(--lake);
  color: #5f6e69;
  font-size: 6.8pt;
  line-height: 1.48;
}

.media-figure.map-figure figcaption { border-left-color: var(--red); }

.cover {
  position: relative;
  width: 148mm;
  height: 210mm;
  overflow: hidden;
  page: cover;
  break-after: page;
  background: #f4f5f0;
  color: #16221f;
}

.cover-rail {
  position: absolute;
  inset: 0 auto 0 0;
  width: 11mm;
  background: var(--red);
}

.swiss-mark {
  position: absolute;
  top: 16mm;
  right: 13mm;
  width: 13mm;
  height: 13mm;
  background: var(--red);
}

.swiss-mark::before,
.swiss-mark::after {
  position: absolute;
  display: block;
  background: white;
  content: "";
}

.swiss-mark::before { top: 5mm; left: 2.4mm; width: 8.2mm; height: 3mm; }
.swiss-mark::after { top: 2.4mm; left: 5mm; width: 3mm; height: 8.2mm; }

.cover-edition {
  position: absolute;
  top: 18mm;
  left: 22mm;
  color: #596561;
  font-size: 6.6pt;
  font-weight: 800;
}

.cover-main { position: absolute; top: 49mm; left: 22mm; right: 13mm; }
.cover-eyebrow { margin: 0 0 4mm; color: var(--red); font-size: 8pt; font-weight: 800; }
.cover-main h1 { margin: 0; color: #17231f; font-size: 34pt; line-height: 1.15; }
.cover-subtitle { margin: 5mm 0 0; color: var(--lake); font-size: 16pt; font-weight: 800; }
.cover-deck { margin: 12mm 0 0; color: #44534f; font-size: 9.4pt; line-height: 1.72; }

.cover-route {
  position: absolute;
  left: 22mm;
  right: 13mm;
  bottom: 54mm;
  display: flex;
  align-items: center;
  color: #30453f;
  font-size: 6.3pt;
  font-weight: 800;
}

.cover-route i { flex: 1; height: 0.35mm; margin: 0 2mm; background: #9ca8a4; }

.cover-meta {
  position: absolute;
  left: 22mm;
  right: 13mm;
  bottom: 20mm;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9mm;
  padding-top: 4mm;
  border-top: 0.45mm solid #aeb8b4;
}

.cover-meta div { display: flex; flex-direction: column; gap: 1.5mm; }
.cover-meta b { color: #697570; font-size: 5.8pt; }
.cover-meta span { color: #23332f; font-size: 7.1pt; font-weight: 800; }

.cover-lines { position: absolute; right: -7mm; bottom: 77mm; width: 34mm; height: 34mm; transform: rotate(45deg); }
.cover-lines i { position: absolute; inset: auto 0; height: 0.3mm; background: #b8c2be; }
.cover-lines i:nth-child(1) { top: 2mm; }
.cover-lines i:nth-child(2) { top: 10mm; }
.cover-lines i:nth-child(3) { top: 18mm; }
.cover-lines i:nth-child(4) { top: 26mm; }

.toc {
  page: toc;
  min-height: 176mm;
  break-after: page;
}

.toc-kicker { margin-top: 4mm; color: var(--red); font-size: 7pt; font-weight: 800; }
.toc h1 { margin: 2mm 0 2mm; font-size: 24pt; }
.toc-lead { margin-bottom: 6mm; color: var(--muted); font-size: 8pt; }
.toc-list { columns: 2; column-gap: 8mm; margin: 0; padding: 0; list-style: none; }
.toc-list li { break-inside: avoid; margin: 0 0 2.1mm; padding: 0; }
.toc-list a { display: flex; gap: 1.5mm; align-items: baseline; color: #31413d; }
.toc-list a span:first-child { flex: 0 1 auto; }
.toc-dot { flex: 1; min-width: 3mm; border-bottom: 0.25mm dotted #b5bfbb; }
.toc-level-1 { margin-top: 3.5mm !important; color: #173b34; font-size: 8.2pt; font-weight: 800; }
.toc-level-2 { padding-left: 3mm !important; font-size: 6.8pt; line-height: 1.35; }

.manuscript > .chapter-title:first-child { margin-top: 0; }
.manuscript > p:first-of-type { font-size: 9.6pt; }

@media screen {
  body { padding: 18px; background: #dfe4e1; }
  .cover, .toc, .manuscript { max-width: 148mm; margin: 0 auto 18px; background: var(--paper); }
  .toc, .manuscript { padding: 14mm 12mm 16mm; }
  .manuscript { box-shadow: 0 3px 20px rgb(0 0 0 / 0.12); }
}
"""


def build_html(markdown_source: str) -> str:
    prepared, headings = preprocess_markdown(markdown_source)
    manuscript = render_markdown(prepared)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Honeymoon Field Guide">
  <meta name="description" content="2026 스위스 인터라켄·루체른 실전 여행가이드북">
  <title>스위스 인터라켄·루체른 실전 여행가이드북 2026</title>
  <style>{CSS}</style>
</head>
<body>
{cover_html()}
{build_toc(headings)}
<main class="manuscript">
{manuscript}
</main>
</body>
</html>
"""


def print_pdf(browser: Path, html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="swiss-guidebook-chrome-") as profile:
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-default-apps",
            "--no-first-run",
            "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=3000",
            "--no-pdf-header-footer",
            "--generate-pdf-document-outline",
            f"--user-data-dir={profile}",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            details = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(f"Browser PDF generation failed: {details}")
    if not pdf_path.is_file() or pdf_path.stat().st_size < 100_000:
        raise RuntimeError("PDF generation did not produce a valid-sized output file.")
    if pdf_path.read_bytes()[:4] != b"%PDF":
        raise RuntimeError("Generated output does not have a PDF signature.")


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
        browser = find_browser()
        print_pdf(browser, html_path, pdf_path)
        print(f"PDF: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
