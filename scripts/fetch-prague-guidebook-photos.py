#!/usr/bin/env python3
"""Fetch reusable Wikimedia Commons photos for the Prague field guide."""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.error import HTTPError


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "guidebook" / "prague" / "photos"
API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "WeddingPragueGuidePDF/1.0 (personal travel guide asset fetcher)"


PHOTOS = [
    {
        "commons_file": "Hotel Paris Prag 01.jpg",
        "filename": "hotel-paris-prague.jpg",
        "caption_ko": "Hotel Paris Prague - 네오고딕의 수직선과 초기 아르누보 장식을 함께 읽는 첫 번째 숙소",
    },
    {
        "commons_file": "Municipal House, Prague.jpg",
        "filename": "municipal-house.jpg",
        "caption_ko": "시민회관 - 돔, 중앙 모자이크, 장식예술이 결합한 체코 아르누보의 대표 정면",
    },
    {
        "commons_file": "Charles Bridge Palace.jpg",
        "filename": "charles-bridge-palace.jpg",
        "caption_ko": "Charles Bridge Palace - 아넨스케 광장에서 강과 구시가를 연결하는 두 번째 숙소",
    },
    {
        "commons_file": "Powder Tower, Prague.jpg",
        "filename": "powder-tower.jpg",
        "caption_ko": "화약탑 - 후기 고딕 관문과 대관 행렬의 출발점을 보여 주는 왕의 길 기준점",
    },
    {
        "commons_file": "House of the Black Madonna 2010 4.jpg",
        "filename": "house-black-madonna.jpg",
        "caption_ko": "검은 성모의 집 - 꺾인 입면과 모서리 성모상으로 체코 큐비즘을 식별하는 건물",
    },
    {
        "commons_file": "Church of Our Lady Before Tyn in Old Town Square Prague (34349652964).jpg",
        "filename": "old-town-square-tyn.jpg",
        "caption_ko": "구시가 광장과 틴 성당 - 시장, 시민 자치, 종교 갈등이 겹친 도시의 중심",
    },
    {
        "commons_file": "The Prague Astronomical Clock in Old Town - 8549.jpg",
        "filename": "astronomical-clock.jpg",
        "caption_ko": "프라하 천문시계 - 천문 다이얼, 황도대, 시간 표기를 중세 우주관으로 읽는 세부",
    },
    {
        "commons_file": "Charles Bridge - panorama.jpg",
        "filename": "charles-bridge-panorama.jpg",
        "caption_ko": "카를교 - 고딕 교량, 바로크 조각열, 생활 보행축을 한 프레임에서 읽는 파노라마",
    },
    {
        "commons_file": "Prague Castle from Charles Bridge panorama.JPG",
        "filename": "prague-castle-panorama.jpg",
        "caption_ko": "카를교에서 본 프라하성 - 왕의 길이 도달하는 언덕과 성 비투스의 스카이라인",
    },
    {
        "commons_file": "Facade of St. Vitus Cathedral, Prague.jpg",
        "filename": "st-vitus-facade.jpg",
        "caption_ko": "성 비투스 대성당 서쪽 정면 - 쌍탑, 장미창, 수직선으로 고딕의 상승감을 확인",
    },
    {
        "commons_file": "Callejón del oro, Praga, República Checa, 2022-07-02, DD 139.jpg",
        "filename": "golden-lane.jpg",
        "caption_ko": "황금소로 - 낮은 장인 주택과 좁은 골목이 성 안의 일상 규모를 보여 준다",
    },
    {
        "commons_file": "Strahov Theological Hall, Prague - 7565.jpg",
        "filename": "strahov-theological-hall.jpg",
        "caption_ko": "스트라호프 신학 홀 - 책장, 지구본, 천장 장식으로 지식의 분류 체계를 읽는 공간",
    },
    {
        "commons_file": "Prague Mala Strana St. Nicholas-01.jpg",
        "filename": "mala-strana-st-nicholas.jpg",
        "caption_ko": "말라스트라나 성 니콜라스 성당 - 녹색 돔과 종탑으로 하이 바로크의 존재감을 식별",
    },
    {
        "commons_file": "Gardens of Wallenstein Palace.jpg",
        "filename": "wallenstein-garden.jpg",
        "caption_ko": "발트슈타인 정원 - 살라 테레나, 분수, 정형 축선으로 귀족 권력의 연출을 읽는다",
    },
    {
        "commons_file": "Čertovka, vodní kolo.jpg",
        "filename": "certovka-waterwheel.jpg",
        "caption_ko": "체르토프카 수로와 물레방아 - 캄파가 관광 섬 이전에 생활·생산 공간이었음을 보여 준다",
    },
    {
        "commons_file": "Spanish Synagogue in Prague inside.jpg",
        "filename": "spanish-synagogue-interior.jpg",
        "caption_ko": "스페인 회당 내부 - 무어 리바이벌의 금빛 기하 문양과 19세기 공동체의 자신감",
    },
    {
        "commons_file": "Praha Old Jewish Cemetery 20170501 04.jpg",
        "filename": "old-jewish-cemetery.jpg",
        "caption_ko": "구유대인묘지 - 겹겹이 놓인 묘비가 제한된 공간과 축적된 공동체 기억을 드러낸다",
    },
    {
        "commons_file": "Panorama of Prague from Vysehrad.jpg",
        "filename": "vysehrad-panorama.jpg",
        "caption_ko": "비셰흐라드에서 본 프라하 - 블타바와 성곽 언덕이 도시의 남북 구조를 설명한다",
    },
    {
        "commons_file": "Rotunda sv. Martina - Vyšehrad 1.jpg",
        "filename": "vysehrad-st-martin-rotunda.jpg",
        "caption_ko": "성 마르틴 원형교회 - 둥근 몸체와 두꺼운 벽으로 로마네스크 건축을 판별한다",
    },
    {
        "commons_file": "Svíčková na smetaně s brusinkovým terčem.jpg",
        "filename": "svickova.jpg",
        "caption_ko": "스비치코바 - 쇠고기, 크림 채소 소스, 빵 크네들리키, 크랜베리의 대비",
    },
    {
        "commons_file": "Chlebicek.2.jpg",
        "filename": "chlebicek.jpg",
        "caption_ko": "흘레비체크 - 햄, 달걀, 샐러드, 채소를 층층이 올린 체코식 오픈 샌드위치",
    },
    {
        "commons_file": "Vetrnik.jpg",
        "filename": "vetrnik.jpg",
        "caption_ko": "베트르니크 - 캐러멜 글레이즈와 두 종류의 크림이 층을 이루는 체코식 슈 디저트",
    },
    {
        "commons_file": "Pilsener Urquell hohes Glas.jpg",
        "filename": "pilsner-urquell-glass.jpg",
        "caption_ko": "필스너 라거 - 황금빛 맥주와 젖은 거품층의 균형을 관찰하는 기준 잔",
    },
    {
        "commons_file": "The Republic exhibition - NM Prague 52.JPG",
        "filename": "bohemian-garnet-bracelet.jpg",
        "caption_ko": "19세기 보헤미안 가넷 팔찌 - 작은 짙은 적색 석류석을 군집시키는 전통 세팅",
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
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": "1800",
        "titles": f"File:{file_name}",
    }
    request = urllib.request.Request(
        f"{API_URL}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": USER_AGENT},
    )
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
            break
        except HTTPError as error:
            if error.code != 429 or attempt == 5:
                raise
            retry_after = int(error.headers.get("Retry-After", "0") or 0)
            time.sleep(max(retry_after, 12 * (attempt + 1)))
    page = payload["query"]["pages"][0]
    if page.get("missing"):
        raise RuntimeError(f"Commons file not found: {file_name}")
    return page["imageinfo"][0]


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                target.write_bytes(response.read())
            return
        except HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            retry_after = int(error.headers.get("Retry-After", "0") or 0)
            time.sleep(max(retry_after, 5 * (attempt + 1)))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str | int]] = []

    for photo in PHOTOS:
        info = query_file(photo["commons_file"])
        metadata = info.get("extmetadata", {})
        target = OUTPUT_DIR / photo["filename"]
        if not target.is_file() or target.stat().st_size < 50_000:
            download(info.get("thumburl") or info["url"], target)
        item = {
            **photo,
            "commons_page": info["descriptionurl"],
            "download_url": info.get("thumburl") or info["url"],
            "author": clean_metadata(metadata.get("Artist")),
            "license": clean_metadata(metadata.get("LicenseShortName")),
            "license_url": clean_metadata(metadata.get("LicenseUrl")),
            "credit": clean_metadata(metadata.get("Credit")),
            "width": info.get("thumbwidth") or info.get("width") or 0,
            "height": info.get("thumbheight") or info.get("height") or 0,
            "bytes": target.stat().st_size,
        }
        manifest.append(item)
        print(
            f"Fetched {target.name}: {target.stat().st_size:,} bytes "
            f"({item['license']}, {item['width']}x{item['height']})"
        )
        time.sleep(2.0)

    manifest_path = OUTPUT_DIR / "photo-credits.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
