#!/usr/bin/env python3
"""Build the Korean Prague city field guide as a print-ready A5 PDF."""

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
DEFAULT_SOURCE = ROOT / "info" / "prague_city_guidebook_2026.md"
DEFAULT_HTML = ROOT / "tmp" / "pdfs" / "prague_city_guidebook_2026.html"
DEFAULT_PDF = ROOT / "output" / "pdf" / "prague_city_field_guide_2026_ko.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--html-only", action="store_true")
    parser.add_argument("--min-pages", type=int, default=50)
    return parser.parse_args()


def find_browser() -> Path:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
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


def preprocess_markdown(source: str) -> tuple[str, list[dict[str, str | int]]]:
    forbidden = ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014"]
    present = [f"U+{ord(char):04X}" for char in forbidden if char in source]
    if present:
        raise ValueError(f"Replace Unicode dash characters with ASCII hyphen: {', '.join(present)}")

    # Chapter headings already start on a fresh page. Ignoring manuscript-level
    # page hints lets profiles flow naturally and prevents short tail pages.
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

    seen: dict[str, int] = {}
    headings: list[dict[str, str | int]] = []

    def replace_heading(match: re.Match[str]) -> str:
        level = len(match.group(1))
        title = match.group(2).strip()
        # Short destinations avoid overlong PDF name tokens when Chrome emits
        # internal anchors for long Korean section titles.
        anchor = f"sec-{len(headings) + 1:03d}"
        classes: list[str] = []
        if level == 1:
            classes.append("chapter-title")
        if level == 2 and re.match(r"(?:명소|미식|제품|부록)\s*\d+", title):
            classes.append("profile-title")
        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        headings.append({"level": level, "title": title, "anchor": anchor})
        return f'<h{level} id="{anchor}"{class_attr}>{html.escape(title)}</h{level}>'

    source = re.sub(r"(?m)^(#{1,6})[ \t]+(.+?)[ \t]*$", replace_heading, source)
    return source, headings


def render_markdown(source: str) -> str:
    parser = MarkdownIt(
        "commonmark",
        {"html": True, "breaks": False, "linkify": False, "typographer": False},
    ).enable("table")
    rendered = parser.render(source)

    def callout(match: re.Match[str]) -> str:
        inner = match.group(1)
        plain = re.sub(r"<[^>]+>", " ", inner)
        if any(token in plain for token in ("주의", "폐쇄", "금지", "경고")):
            kind = "warning"
        elif any(token in plain for token in ("공식", "방문 직전", "확인")):
            kind = "verify"
        elif any(token in plain for token in ("핵심", "원칙", "고정")):
            kind = "rule"
        else:
            kind = "note"
        return f'<blockquote class="callout {kind}">{inner}</blockquote>'

    rendered = re.sub(r"<blockquote>\s*(.*?)\s*</blockquote>", callout, rendered, flags=re.S)

    def table_wrap(match: re.Match[str]) -> str:
        inner = match.group(1)
        columns = len(re.findall(r"<th(?:\s[^>]*)?>", inner))
        kind = "data-table compact-table" if columns >= 5 else "data-table"
        return f'<div class="table-wrap"><table class="{kind}">{inner}</table></div>'

    rendered = re.sub(r"<table>\s*(.*?)\s*</table>", table_wrap, rendered, flags=re.S)

    def media_figure(match: re.Match[str]) -> str:
        source, alt_text, title = match.groups()
        source_key = html.unescape(source).lower()
        classes = ["media-figure"]
        if "/maps/" in source_key or source_key.endswith(".svg"):
            classes.append("map-figure")
        else:
            classes.append("photo-figure")
        if any(token in source_key for token in ("panorama", "skyline", "old-town-square", "charles-bridge")):
            classes.append("panorama-figure")
        if any(
            token in source_key
            for token in (
                "hotel-paris",
                "charles-bridge-palace",
                "powder-tower",
                "st-vitus",
                "mala-strana-st",
                "wallenstein-garden",
                "vysehrad-panorama",
                "st-martin-rotunda",
                "pilsner-urquell",
            )
        ):
            classes.append("portrait-figure")
        caption = title or alt_text
        caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
        return (
            f'<figure class="{" ".join(classes)}">'
            f'<img src="{source}" alt="{alt_text}">{caption_html}</figure>'
        )

    return re.sub(
        r'<p><img src="([^"]+)" alt="([^"]*)"(?: title="([^"]*)")?\s*/?></p>',
        media_figure,
        rendered,
        flags=re.S,
    )


def resolve_local_media(rendered: str, source_dir: Path) -> str:
    """Resolve manuscript-relative image paths for the generated temp HTML."""

    def replace(match: re.Match[str]) -> str:
        raw = html.unescape(match.group(1))
        if re.match(r"^(?:https?:|data:|file:)", raw, flags=re.I):
            return match.group(0)
        asset = (source_dir / raw).resolve()
        if not asset.is_file():
            raise FileNotFoundError(f"Guidebook media not found: {asset}")
        return f'src="{asset.as_uri()}"'

    return re.sub(r'src="([^"]+)"', replace, rendered)


def build_toc(headings: list[dict[str, str | int]]) -> str:
    entries: list[str] = []
    for heading in headings:
        level = int(heading["level"])
        title = str(heading["title"])
        if level not in (1, 2):
            continue
        if level == 2 and not (
            re.match(r"(?:명소|미식|제품|부록)\s*\d+", title)
            or title.startswith(("베이스캠프", "날짜별", "도시 읽기", "여행 전"))
        ):
            continue
        entries.append(
            f'<li class="toc-level-{level}"><a href="#{heading["anchor"]}">'
            f'<span>{html.escape(title)}</span><i aria-hidden="true"></i></a></li>'
        )
    return (
        '<section class="toc" aria-labelledby="toc-title">'
        '<div class="toc-kicker">FIELD INDEX</div>'
        '<h1 id="toc-title">목차</h1>'
        '<p class="toc-lead">큰 장과 핵심 프로필을 누르면 해당 페이지로 이동합니다.</p>'
        f'<ol class="toc-list">{"".join(entries)}</ol>'
        '</section>'
    )


def cover_html() -> str:
    return r"""
<section class="cover">
  <div class="cover-wash" aria-hidden="true"></div>
  <div class="cover-edition">HONEYMOON FIELD EDITION · JULY 2026</div>
  <div class="cover-main">
    <p class="cover-eyebrow">PRAHA · PRAGUE</p>
    <h1>프라하를<br>읽는 여행</h1>
    <p class="cover-subtitle">숙소에서 시작하는 도시 가이드북</p>
    <p class="cover-deck">왕의 길, 고딕과 바로크, 시민의 기억,<br>체코의 식탁과 공예를 한 권에 담다</p>
  </div>
  <svg class="cover-skyline" viewBox="0 0 720 250" role="img" aria-label="프라하 성과 카를교를 추상화한 선 그림">
    <path d="M0 205 H720" />
    <path d="M18 205 V155 H74 V205 M35 155 V115 H57 V155 M46 115 V80" />
    <path d="M96 205 V135 H146 V205 M108 135 L121 108 L134 135" />
    <path d="M165 205 V160 H222 V205 M176 160 V125 H211 V160 M193 125 V72" />
    <path d="M235 205 C275 170 315 170 355 205 C395 170 435 170 475 205" />
    <path d="M245 205 V160 M465 205 V160" />
    <path d="M500 205 V128 H545 V205 M511 128 V94 H534 V128 M522 94 V48" />
    <path d="M557 205 V145 H615 V205 M570 145 L586 111 L602 145" />
    <path d="M632 205 V120 H701 V205 M648 120 V82 H685 V120 M666 82 V32" />
    <circle cx="666" cy="22" r="7" />
  </svg>
  <div class="cover-route" aria-label="두 숙소 거점">
    <span>HOTEL PARIS</span><i></i><span>OLD TOWN</span><i></i><span>CHARLES BRIDGE PALACE</span>
  </div>
  <div class="cover-meta">
    <div><b>TRAVEL DATES</b><span>2026.07.11 - 07.16 · 07.26 - 07.27</span></div>
    <div><b>FORMAT</b><span>A5 · 2026-07-10 VERIFIED EDITION</span></div>
  </div>
</section>
"""


CSS = r"""
@page {
  size: A5 portrait;
  margin: 15mm 12mm 17mm;
  @top-left {
    content: "PRAHA FIELD GUIDE";
    color: #7a746c;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.5pt;
    font-weight: 700;
  }
  @top-right {
    content: "2026 · VERIFIED 07.10";
    color: #918a82;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.5pt;
  }
  @bottom-left {
    content: "HOTEL PARIS · CHARLES BRIDGE PALACE";
    color: #918a82;
    font-family: "Malgun Gothic", sans-serif;
    font-size: 6.2pt;
  }
  @bottom-right {
    content: counter(page) " / " counter(pages);
    color: #3e302d;
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
  margin: 14mm 12mm 16mm;
  @top-left { content: "CONTENTS"; }
  @bottom-left { content: "PRAHA · PRAGUE"; }
}

:root {
  --ink: #2b2724;
  --muted: #6f6963;
  --paper: #fbf8f2;
  --line: #ded4c6;
  --garnet: #7b2231;
  --gold: #bd914c;
  --river: #2f6870;
  --midnight: #1b2731;
  --soft-garnet: #f7eaed;
  --soft-gold: #f7f0e3;
  --soft-river: #e9f1f1;
  --soft-gray: #f0ede8;
}

* { box-sizing: border-box; }

html {
  color: var(--ink);
  background: var(--paper);
  font-family: "Malgun Gothic", "Noto Sans KR", sans-serif;
  font-size: 9.25pt;
  line-height: 1.72;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
  text-rendering: optimizeLegibility;
}

body { margin: 0; background: var(--paper); }

a { color: #245d66; text-decoration: none; overflow-wrap: anywhere; }
a:hover { text-decoration: underline; }

p { margin: 0 0 3.2mm; orphans: 3; widows: 3; }
strong { color: #34211f; }
em { color: var(--muted); }

h1, h2, h3, h4 {
  color: var(--midnight);
  line-height: 1.25;
  page-break-after: avoid;
  break-after: avoid-page;
}

h1.chapter-title {
  break-before: page;
  margin: 0 0 7mm;
  padding: 18mm 0 7mm;
  border-bottom: 1.5pt solid var(--garnet);
  font-family: "Batang", "Malgun Gothic", serif;
  font-size: 23pt;
  letter-spacing: -0.6pt;
}

h1.chapter-title::before {
  content: "PRAHA DOSSIER";
  display: block;
  margin-bottom: 3mm;
  color: var(--garnet);
  font-family: "Malgun Gothic", sans-serif;
  font-size: 7pt;
  font-weight: 700;
  letter-spacing: 1.6pt;
}

h2 {
  margin: 7mm 0 3.2mm;
  padding-left: 3mm;
  border-left: 3pt solid var(--gold);
  font-size: 15pt;
  letter-spacing: -0.25pt;
}

h2.profile-title {
  margin-top: 0;
  padding-top: 2mm;
}

h3 {
  margin: 5mm 0 2.3mm;
  color: var(--garnet);
  font-size: 11.2pt;
}

h4 { margin: 3.6mm 0 1.8mm; font-size: 9.8pt; }

ul, ol { margin: 0 0 4mm; padding-left: 5.3mm; }
li { margin: 0 0 1.5mm; }
li::marker { color: var(--garnet); }

hr { border: 0; border-top: 1px solid var(--line); margin: 6mm 0; }

.page-break { break-before: page; page-break-before: always; }

.cover {
  page: cover;
  position: relative;
  width: 148mm;
  height: 210mm;
  overflow: hidden;
  padding: 17mm 15mm 14mm;
  color: #fffdf8;
  background:
    radial-gradient(circle at 80% 14%, rgba(189,145,76,.33), transparent 26%),
    linear-gradient(153deg, #13232c 0%, #23343a 48%, #6e2330 100%);
}

.cover-wash {
  position: absolute;
  inset: 0;
  opacity: .16;
  background-image:
    linear-gradient(30deg, transparent 47%, #fff 48%, transparent 49%),
    linear-gradient(150deg, transparent 47%, #fff 48%, transparent 49%);
  background-size: 24mm 24mm;
}

.cover-edition {
  position: relative;
  z-index: 2;
  color: #e7cf9f;
  font-size: 6.8pt;
  font-weight: 700;
  letter-spacing: 1.5pt;
}

.cover-main { position: relative; z-index: 2; margin-top: 25mm; }
.cover-eyebrow { margin: 0 0 5mm; color: #e7cf9f; font-size: 10pt; font-weight: 800; letter-spacing: 3.3pt; }
.cover h1 { margin: 0; color: #fffdf8; font-family: "Batang", serif; font-size: 37pt; line-height: 1.08; letter-spacing: -2pt; }
.cover-subtitle { margin: 6mm 0 0; color: #fff; font-size: 14pt; font-weight: 700; }
.cover-deck { margin: 4mm 0 0; color: #e8e1d7; font-size: 9pt; line-height: 1.65; }

.cover-skyline {
  position: absolute;
  z-index: 1;
  left: 5mm;
  right: 5mm;
  bottom: 38mm;
  width: 138mm;
  height: auto;
  fill: none;
  stroke: rgba(255,245,222,.72);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.cover-route {
  position: absolute;
  z-index: 2;
  left: 15mm;
  right: 15mm;
  bottom: 24mm;
  display: flex;
  align-items: center;
  gap: 2.2mm;
  color: #f3e7d2;
  font-size: 6.2pt;
  font-weight: 700;
  letter-spacing: .5pt;
}
.cover-route i { flex: 1; height: 1px; background: rgba(255,255,255,.5); }

.cover-meta {
  position: absolute;
  z-index: 2;
  left: 15mm;
  right: 15mm;
  bottom: 9mm;
  display: flex;
  justify-content: space-between;
  gap: 8mm;
  font-size: 6.1pt;
}
.cover-meta div { display: flex; flex-direction: column; gap: .8mm; }
.cover-meta b { color: #e7cf9f; font-size: 5.8pt; letter-spacing: 1pt; }
.cover-meta span { color: #fff; }

.toc { page: toc; }
.toc-kicker { color: var(--garnet); font-size: 7pt; font-weight: 800; letter-spacing: 1.7pt; }
.toc h1 { margin: 2mm 0 2mm; font-family: "Batang", serif; font-size: 26pt; }
.toc-lead { color: var(--muted); font-size: 8pt; }
.toc-list { list-style: none; margin: 7mm 0 0; padding: 0; columns: 2; column-gap: 6mm; }
.toc-list li { break-inside: avoid; margin: 0 0 2.3mm; }
.toc-list a { display: flex; align-items: baseline; gap: 1.5mm; color: var(--ink); }
.toc-list i { flex: 1; border-bottom: 1px dotted #b8aea1; }
.toc-level-1 { font-size: 8.2pt; font-weight: 800; }
.toc-level-2 { padding-left: 2mm; color: var(--muted); font-size: 7.2pt; }

.callout {
  margin: 4.5mm 0;
  padding: 3.4mm 4mm;
  border: 0;
  border-left: 3pt solid var(--river);
  border-radius: 1.5mm;
  background: var(--soft-river);
  color: #263c40;
  break-inside: avoid;
}
.callout p:last-child { margin-bottom: 0; }
.callout.warning { border-color: var(--garnet); background: var(--soft-garnet); color: #55232b; }
.callout.verify { border-color: var(--gold); background: var(--soft-gold); color: #51412a; }
.callout.rule { border-color: var(--midnight); background: var(--soft-gray); color: var(--midnight); }

.table-wrap { width: 100%; margin: 4.5mm 0; break-inside: avoid; }
.data-table { width: 100%; border-collapse: collapse; font-size: 7.4pt; line-height: 1.45; }
.data-table th { padding: 2.2mm; color: #fff; background: var(--midnight); text-align: left; font-weight: 700; }
.data-table td { padding: 2mm 2.2mm; border-bottom: 1px solid var(--line); vertical-align: top; }
.data-table tr:nth-child(even) td { background: #f5f1ea; }
.compact-table { font-size: 6.7pt; }
.compact-table th, .compact-table td { padding: 1.5mm; }

.checkbox {
  display: inline-block;
  width: 3mm;
  height: 3mm;
  margin-right: 1.2mm;
  border: 1px solid #7d756d;
  vertical-align: -0.4mm;
}
.checkbox.checked { background: var(--garnet); box-shadow: inset 0 0 0 1px #fff; }

.route-card, .study-card, .fact-grid, .food-grid, .product-grid {
  display: grid;
  gap: 3mm;
  margin: 4mm 0;
  break-inside: avoid;
}
.route-card { grid-template-columns: repeat(5, 1fr); align-items: stretch; }
.route-card .stop {
  position: relative;
  min-height: 26mm;
  padding: 3mm 2.2mm;
  border: 1px solid var(--line);
  border-top: 3pt solid var(--garnet);
  background: #fffdf9;
  text-align: center;
  font-size: 7pt;
  line-height: 1.35;
}
.route-card .stop b { display: block; margin-bottom: 1.5mm; color: var(--midnight); font-size: 7.4pt; }
.route-card .stop span { color: var(--muted); }
.study-card { grid-template-columns: repeat(3, 1fr); }
.study-card > div, .fact-grid > div, .food-grid > div, .product-grid > div {
  padding: 3.2mm;
  border: 1px solid var(--line);
  border-radius: 1.5mm;
  background: #fffdf9;
}
.study-card b, .fact-grid b, .food-grid b, .product-grid b { display: block; margin-bottom: 1.5mm; color: var(--garnet); }
.study-card p, .fact-grid p, .food-grid p, .product-grid p { margin: 0; color: var(--muted); font-size: 7.3pt; line-height: 1.55; }
.fact-grid { grid-template-columns: repeat(2, 1fr); }
.food-grid { grid-template-columns: repeat(2, 1fr); }
.product-grid { grid-template-columns: repeat(2, 1fr); }

.timeline {
  position: relative;
  margin: 5mm 0 6mm 3mm;
  padding-left: 8mm;
  border-left: 2pt solid var(--gold);
}
.timeline div { position: relative; margin: 0 0 4mm; break-inside: avoid; }
.timeline div::before {
  content: "";
  position: absolute;
  left: -10.2mm;
  top: 1mm;
  width: 4mm;
  height: 4mm;
  border: 1.5pt solid var(--garnet);
  border-radius: 50%;
  background: var(--paper);
}
.timeline b { display: block; color: var(--garnet); font-size: 8pt; }
.timeline span { color: var(--muted); font-size: 7.5pt; }

.mini-source { color: var(--muted); font-size: 6.7pt; line-height: 1.45; }
.source-list { font-size: 7.2pt; line-height: 1.45; }
.source-list li { margin-bottom: 2mm; }

.media-figure {
  width: 100%;
  margin: 5mm 0 6mm;
  break-inside: avoid-page;
}
.media-figure img {
  display: block;
  width: 100%;
  height: 70mm;
  border: 1px solid var(--line);
  border-radius: 1.5mm;
  background: #ede9e2;
  object-fit: cover;
}
.media-figure.panorama-figure img { height: 55mm; }
.media-figure.portrait-figure img {
  height: 84mm;
  background: #fffdf9;
  object-fit: contain;
}
.media-figure.map-figure img {
  height: auto;
  max-height: 104mm;
  padding: 1mm;
  border-color: #c9d5d5;
  background: #ffffff;
  object-fit: contain;
}
.media-figure figcaption {
  margin-top: 1.6mm;
  padding-left: 2.2mm;
  border-left: 3pt solid var(--river);
  color: var(--muted);
  font-size: 6.45pt;
  line-height: 1.48;
}
.media-figure.map-figure figcaption { border-left-color: var(--garnet); }

code { font-family: Consolas, monospace; font-size: 8pt; color: #4a2c2d; background: #f2ece5; padding: .3mm .8mm; border-radius: .8mm; }

@media print {
  .cover { break-after: page; page-break-after: always; }
  .toc { break-after: page; page-break-after: always; }
}
"""


def build_html(markdown_source: str, source_dir: Path = DEFAULT_SOURCE.parent) -> str:
    preprocessed, headings = preprocess_markdown(markdown_source)
    body = render_markdown(preprocessed)
    body = resolve_local_media(body, source_dir)
    toc = build_toc(headings)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>프라하를 읽는 여행 - 숙소에서 시작하는 도시 가이드북</title>
  <style>{CSS}</style>
</head>
<body>
{cover_html()}
{toc}
<main>{body}</main>
</body>
</html>
"""


def print_pdf(browser: Path, html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="prague-guide-chrome-") as profile:
        command = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        if completed.returncode != 0 or not pdf_path.is_file():
            raise RuntimeError(
                "Browser PDF generation failed.\n"
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            )


def count_pdf_pages(pdf_path: Path) -> int:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf_path)).pages)
    except ModuleNotFoundError:
        candidates = [
            shutil.which("pdfinfo"),
            Path.home()
            / ".cache"
            / "codex-runtimes"
            / "codex-primary-runtime"
            / "dependencies"
            / "native"
            / "poppler"
            / "Library"
            / "bin"
            / "pdfinfo.exe",
        ]
        for candidate in candidates:
            if not candidate:
                continue
            executable = Path(candidate)
            if not executable.is_file():
                continue
            completed = subprocess.run(
                [str(executable), str(pdf_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            if completed.returncode == 0:
                match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", completed.stdout)
                if match:
                    return int(match.group(1))
        raise RuntimeError("Neither pypdf nor pdfinfo is available to count PDF pages.")


def main() -> None:
    args = parse_args()
    source_path = args.source.resolve()
    html_path = args.html.resolve()
    pdf_path = args.pdf.resolve()

    markdown_source = source_path.read_text(encoding="utf-8")
    output_html = build_html(markdown_source, source_path.parent)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(output_html, encoding="utf-8")
    print(f"HTML: {html_path}")

    if args.html_only:
        return

    browser = find_browser()
    print_pdf(browser, html_path, pdf_path)
    page_count = count_pdf_pages(pdf_path)
    if page_count < args.min_pages:
        raise RuntimeError(f"Guidebook is only {page_count} pages; expected at least {args.min_pages}.")
    print(f"PDF: {pdf_path}")
    print(f"Pages: {page_count}")


if __name__ == "__main__":
    main()
