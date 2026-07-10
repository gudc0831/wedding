#!/usr/bin/env python3
"""Fetch reusable Wikimedia Commons photos for the Swiss PDF guidebook."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "guidebook" / "swiss" / "photos"
API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "WeddingGuidePDF/1.0 (personal travel guide asset fetcher)"

PHOTOS = [
    {
        "commons_file": "Kapell Brucke Bridge in Lucerne..jpg",
        "filename": "lucerne-kapellbrucke.jpg",
        "caption_ko": "카펠교와 로이스강: 수탑, 목조 교량, 강변 구시가지를 한 프레임에서 읽는 대표 장면",
    },
    {
        "commons_file": "Lion Monument.jpg",
        "filename": "lucerne-lion-monument.jpg",
        "caption_ko": "빈사의 사자상: 1792년 튈르리 궁전에서 전사한 스위스 근위대를 기억하는 기념 조각",
    },
    {
        "commons_file": "Luzern asv2022-10 Jesuitenkirche img2.jpg",
        "filename": "lucerne-jesuit-church.jpg",
        "caption_ko": "예수회 교회 내부: 반종교개혁 시대의 바로크 공간과 빛·장식의 효과를 읽는 장면",
    },
    {
        "commons_file": "Panorama of Swiss Alps from Rigi Kulm.jpg",
        "filename": "rigi-kulm-panorama.jpg",
        "caption_ko": "리기 쿨름 남쪽 파노라마: 정상부에서 알프스 능선의 겹을 확인하는 장면",
    },
    {
        "commons_file": "PanoramaRigiKulmKeller.png",
        "filename": "rigi-kulm-historic-panorama.png",
        "caption_ko": "1913년 이전 리기 쿨름 파노라마 도판: 철도 관광 초창기의 산악 조망 안내 방식",
    },
    {
        "commons_file": "Höhematte Interlaken 2022-10-02 01.jpg",
        "filename": "interlaken-hohematte.jpg",
        "caption_ko": "회에마테 공원: 인터라켄 도심에서 남쪽 산군을 바라보는 열린 시야",
    },
    {
        "commons_file": "Switzerland-03221 - Town Hall Square (23704506431).jpg",
        "filename": "unterseen-stadthausplatz.jpg",
        "caption_ko": "운터젠 시청 광장: 인터라켄 관광축과 구분되는 1279년 기원 역사도시의 중심",
    },
    {
        "commons_file": "Paragliding Interlaken - Switzerland (Unsplash).jpg",
        "filename": "interlaken-paragliding.jpg",
        "caption_ko": "인터라켄 패러글라이딩: 회에마테 착륙과 두 호수 사이 지형을 이해하는 일정 사진",
    },
    {
        "commons_file": "Top of Interlaken - Panorama.jpg",
        "filename": "harder-kulm-panorama.jpg",
        "caption_ko": "하더쿨름 파노라마: 인터라켄과 브리엔츠호·툰호의 위치 관계를 읽는 조망",
    },
    {
        "commons_file": "Eiger seen from Grindelwald village 2022-10-02 01.jpg",
        "filename": "grindelwald-eiger.jpg",
        "caption_ko": "그린델발트 마을에서 본 아이거: 마을과 산벽의 고도 차이를 체감하는 장면",
    },
    {
        "commons_file": "Bachalpsee reflection.jpg",
        "filename": "bachalpsee-reflection.jpg",
        "caption_ko": "바흐알프호 반영: 바람이 약할 때 나타나는 산악 호수의 대표적인 반사 장면",
    },
]


def clean_metadata(value: dict | None) -> str:
    if not value:
        return ""
    raw = str(value.get("value", ""))
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"\s+", " ", html.unescape(raw)).strip()
    return raw


def query_file(file_name: str) -> dict:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": "1800",
        "titles": f"File:{file_name}",
    }
    request = urllib.request.Request(
        f"{API_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": USER_AGENT},
    )
    payload = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            break
        except HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            retry_after = int(error.headers.get("Retry-After", "0") or 0)
            time.sleep(max(retry_after, 8 * (attempt + 1)))
    if payload is None:
        raise RuntimeError(f"Commons metadata request failed: {file_name}")
    page = payload["query"]["pages"][0]
    if page.get("missing"):
        raise RuntimeError(f"Commons file not found: {file_name}")
    return page["imageinfo"][0]


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                target.write_bytes(response.read())
            return
        except HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            retry_after = int(error.headers.get("Retry-After", "0") or 0)
            time.sleep(max(retry_after, 4 * (attempt + 1)))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []

    for photo in PHOTOS:
        info = query_file(photo["commons_file"])
        metadata = info.get("extmetadata", {})
        target = OUTPUT_DIR / photo["filename"]
        download(info.get("thumburl") or info["url"], target)
        item = {
            **photo,
            "commons_page": info["descriptionurl"],
            "download_url": info.get("thumburl") or info["url"],
            "author": clean_metadata(metadata.get("Artist")),
            "license": clean_metadata(metadata.get("LicenseShortName")),
            "license_url": clean_metadata(metadata.get("LicenseUrl")),
            "credit": clean_metadata(metadata.get("Credit")),
            "bytes": str(target.stat().st_size),
        }
        manifest.append(item)
        print(f"Fetched {target.name}: {target.stat().st_size:,} bytes")
        time.sleep(2)

    manifest_path = OUTPUT_DIR / "photo-credits.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
