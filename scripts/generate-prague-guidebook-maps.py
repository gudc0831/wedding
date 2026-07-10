#!/usr/bin/env python3
"""Generate privacy-preserving schematic SVG maps for the Prague PDF guide."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "guidebook" / "prague" / "maps"
WIDTH = 1400
HEIGHT = 900

COLORS = {
    "ink": "#1b2731",
    "muted": "#68645f",
    "paper": "#fbf8f2",
    "line": "#d8d0c5",
    "garnet": "#7b2231",
    "gold": "#bd914c",
    "river": "#2f6870",
    "walk": "#176b5b",
    "tram": "#a04435",
    "metro": "#315f9b",
    "option": "#77716a",
    "hotel_a": "#c76b22",
    "hotel_b": "#2f6870",
}


@dataclass(frozen=True)
class Place:
    lat: float
    lon: float
    label: str


P = {
    "hotel_a": Place(50.088219, 14.427489, "Hotel Paris Prague"),
    "hotel_b": Place(50.085207, 14.414501, "Charles Bridge Palace"),
    "old_town": Place(50.085000, 14.420000, "구시가"),
    "new_town": Place(50.076944, 14.426111, "신시가"),
    "josefov": Place(50.090281, 14.419439, "요세포프"),
    "mala_strana": Place(50.088056, 14.403889, "말라스트라나"),
    "hradcany": Place(50.089444, 14.397222, "흐라드차니"),
    "vysehrad": Place(50.063889, 14.420000, "비셰흐라드"),
    "letna": Place(50.093736, 14.412533, "레트나"),
    "holesovice": Place(50.099694, 14.438111, "홀레쇼비체"),
    "municipal_house": Place(50.087619, 14.428239, "시민회관"),
    "powder_tower": Place(50.087222, 14.427778, "화약탑"),
    "black_madonna": Place(50.087000, 14.425450, "검은 성모의 집"),
    "estates_theatre": Place(50.086111, 14.423889, "에스테이트 극장"),
    "old_town_square": Place(50.087500, 14.421389, "구시가 광장"),
    "astronomical_clock": Place(50.086980, 14.420714, "천문시계"),
    "spanish_synagogue": Place(50.090359, 14.420847, "스페인 회당"),
    "clementinum": Place(50.086655, 14.416119, "클레멘티눔"),
    "smetana_museum": Place(50.085419, 14.412969, "스메타나 박물관"),
    "old_town_bridge_tower": Place(50.086292, 14.413656, "구시가 교탑"),
    "charles_bridge": Place(50.086389, 14.411944, "카를교"),
    "cafe_slavia": Place(50.081819, 14.413258, "Café Slavia"),
    "national_theatre": Place(50.080556, 14.413889, "국립극장"),
    "lennon_wall": Place(50.086111, 14.406944, "레넌 벽"),
    "st_nicholas_mala": Place(50.087781, 14.403611, "성 니콜라스"),
    "nerudova": Place(50.088611, 14.399444, "네루도바"),
    "hradcany_square": Place(50.089290, 14.396134, "흐라드차니 광장"),
    "matthias_gate": Place(50.089890, 14.398750, "마티아스 문"),
    "pohorelec": Place(50.087639, 14.389312, "Pohořelec"),
    "strahov_monastery": Place(50.085963, 14.389282, "스트라호프 수도원"),
    "strahov_library": Place(50.086293, 14.388709, "스트라호프 도서관"),
    "strahov_brewery": Place(50.086809, 14.388306, "수도원 양조장"),
    "loreta_square": Place(50.090000, 14.390000, "로레타 광장"),
    "st_vitus": Place(50.090833, 14.400556, "성 비투스"),
    "old_royal_palace": Place(50.090631, 14.401739, "구왕궁"),
    "st_george": Place(50.091111, 14.402194, "성 이르지"),
    "golden_lane": Place(50.092036, 14.404176, "황금소로"),
    "lobkowicz_palace": Place(50.091608, 14.404853, "로브코비츠"),
    "wallenstein_garden": Place(50.089872, 14.405964, "발트슈타인 정원"),
    "namesti_republiky_b": Place(50.088910, 14.430471, "Náměstí Republiky B"),
    "mustek_ab": Place(50.083784, 14.423339, "Můstek A/B"),
    "staromestska_a": Place(50.088185, 14.417633, "Staroměstská A"),
    "malostranska_a": Place(50.091236, 14.409492, "Malostranská A"),
    "cafe_imperial": Place(50.089867, 14.432861, "Café Imperial"),
    "grand_cafe_orient": Place(50.087000, 14.425511, "Grand Café Orient"),
    "pilsnerka": Place(50.082082, 14.418782, "Pilsnerka"),
    "cafe_savoy": Place(50.080926, 14.407216, "Café Savoy"),
    "kuchyn": Place(50.089345, 14.397868, "Kuchyň"),
    "lobkowicz_cafe": Place(50.091608, 14.404853, "로브코비츠 카페"),
    "porks": Place(50.087486, 14.406049, "Pork's"),
    "cafe_louvre": Place(50.082067, 14.418731, "Café Louvre"),
    "bakeshop": Place(50.089944, 14.422575, "Bakeshop"),
}


VLTAVA = [
    (50.108, 14.438),
    (50.103, 14.432),
    (50.099, 14.425),
    (50.095, 14.417),
    (50.091, 14.411),
    (50.087, 14.412),
    (50.083, 14.413),
    (50.078, 14.414),
    (50.073, 14.414),
    (50.068, 14.417),
    (50.063, 14.420),
    (50.056, 14.421),
]


MAPS = [
    {
        "id": "prague-city-structure",
        "title": "강·언덕·역사도시로 읽는 프라하",
        "subtitle": "동쪽은 시장·시민도시, 서쪽은 성·귀족도시, 북쪽은 전망·산업 재사용, 남쪽은 요새",
        "extent": (14.382, 50.054, 14.455, 50.109),
        "points": ["hotel_a", "hotel_b", "old_town", "new_town", "josefov", "mala_strana", "hradcany", "vysehrad", "letna", "holesovice"],
        "routes": [
            ("왕의 길 개념축", COLORS["walk"], "", ["hotel_a", "old_town", "hotel_b", "mala_strana", "hradcany"]),
            ("북부 확장축", COLORS["tram"], "18,12", ["josefov", "letna", "holesovice"]),
            ("남부 확장축", COLORS["metro"], "8,12", ["old_town", "new_town", "vysehrad"]),
        ],
        "note": "지역 핀은 행정경계 중심이 아닌 설명용 앵커다. 강·지형·역사 관계를 읽는 개념도다.",
    },
    {
        "id": "hotel-a-old-town-walk",
        "title": "Hotel Paris에서 읽는 구시가지 동쪽",
        "subtitle": "숙소 - 시민회관 - 화약탑 - 큐비즘 - 시장광장 - 천문시계",
        "extent": (14.418, 50.081, 14.433, 50.093),
        "points": ["hotel_a", "municipal_house", "powder_tower", "black_madonna", "estates_theatre", "old_town_square", "astronomical_clock", "spanish_synagogue", "namesti_republiky_b", "mustek_ab"],
        "routes": [
            ("기본 도보 순서", COLORS["walk"], "", ["hotel_a", "municipal_house", "powder_tower", "black_madonna", "estates_theatre", "old_town_square", "astronomical_clock", "hotel_a"]),
            ("요세포프 선택 확장", COLORS["gold"], "16,12", ["old_town_square", "spanish_synagogue", "hotel_a"]),
        ],
        "note": "선은 설명용 순서이며 실제 도로 라우팅이 아니다. 공사·통제·횡단은 오프라인 지도에서 확인한다.",
    },
    {
        "id": "hotel-b-river-walk",
        "title": "Charles Bridge Palace에서 읽는 강과 양안",
        "subtitle": "야간 다리 루프, 클레멘티눔 지식축, Slavia·국립극장 아침축",
        "extent": (14.401, 50.078, 14.419, 50.093),
        "points": ["hotel_b", "smetana_museum", "old_town_bridge_tower", "charles_bridge", "clementinum", "cafe_slavia", "national_theatre", "lennon_wall", "st_nicholas_mala", "staromestska_a", "malostranska_a"],
        "routes": [
            ("07.26 야간 순서", COLORS["river"], "", ["hotel_b", "smetana_museum", "old_town_bridge_tower", "charles_bridge", "hotel_b"]),
            ("07.27 아침 순서", COLORS["garnet"], "", ["hotel_b", "cafe_slavia", "national_theatre", "hotel_b"]),
            ("서안 선택 확장", COLORS["gold"], "16,12", ["charles_bridge", "lennon_wall", "st_nicholas_mala", "malostranska_a"]),
        ],
        "note": "카를교와 강변은 돌바닥·혼잡을 감안한다. 차량 승하차 지점은 호텔에 별도 확인한다.",
    },
    {
        "id": "royal-route",
        "title": "왕의 길: 시장도시에서 성까지",
        "subtitle": "하나의 도로명이 아니라 거리와 광장을 잇는 대관 의례 동선",
        "extent": (14.394, 50.083, 14.431, 50.095),
        "points": ["hotel_a", "hotel_b", "powder_tower", "black_madonna", "old_town_square", "clementinum", "old_town_bridge_tower", "charles_bridge", "st_nicholas_mala", "nerudova", "hradcany_square", "matthias_gate", "malostranska_a"],
        "routes": [
            ("왕의 길 설명 순서", COLORS["garnet"], "", ["powder_tower", "black_madonna", "old_town_square", "clementinum", "old_town_bridge_tower", "charles_bridge", "st_nicholas_mala", "nerudova", "hradcany_square", "matthias_gate"]),
            ("하산·이탈 지점", COLORS["metro"], "8,12", ["st_nicholas_mala", "malostranska_a"]),
        ],
        "note": "화약탑-카를교는 대체로 평탄하고 말라스트라나-흐라드차니는 급경사다.",
    },
    {
        "id": "castle-hill-route",
        "title": "성은 건물 하나가 아니라 능선 위 도시다",
        "subtitle": "Pohořelec에서 스트라호프·흐라드차니·성 단지·말라스트라나로 내려오는 축",
        "extent": (14.386, 50.084, 14.411, 50.095),
        "points": ["pohorelec", "strahov_monastery", "strahov_library", "strahov_brewery", "loreta_square", "hradcany_square", "kuchyn", "matthias_gate", "st_vitus", "old_royal_palace", "st_george", "golden_lane", "lobkowicz_palace", "wallenstein_garden", "malostranska_a"],
        "routes": [
            ("완만한 하행 설명축", COLORS["walk"], "", ["pohorelec", "strahov_monastery", "strahov_library", "strahov_brewery", "loreta_square", "hradcany_square", "matthias_gate", "st_vitus", "old_royal_palace", "st_george", "golden_lane", "lobkowicz_palace", "wallenstein_garden", "malostranska_a"]),
        ],
        "note": "2026-07-12에는 Pražský hrad·Královský letohrádek 정류장을 이용할 수 없다. 당일 PID 공지를 확인한다.",
    },
    {
        "id": "food-cafe-map",
        "title": "두 호텔에서 이어지는 프라하 식문화",
        "subtitle": "확정 일정과 선택지를 날짜별로 분리해 보는 카페·식당 위치도",
        "extent": (14.386, 50.078, 14.435, 50.095),
        "points": ["hotel_a", "hotel_b", "kuchyn", "lobkowicz_cafe", "strahov_brewery", "porks", "pilsnerka", "cafe_savoy", "wallenstein_garden", "cafe_imperial", "cafe_slavia", "grand_cafe_orient", "cafe_louvre", "bakeshop"],
        "routes": [
            ("D2 성 지구·저녁", COLORS["garnet"], "", ["kuchyn", "strahov_brewery", "porks"]),
            ("D5 카페·정원", COLORS["river"], "", ["cafe_savoy", "wallenstein_garden", "cafe_imperial"]),
            ("선택·백업 위치", COLORS["option"], "14,14", ["grand_cafe_orient", "cafe_louvre", "bakeshop"]),
        ],
        "note": "지도에 있다는 사실은 예약 완료를 뜻하지 않는다. 예약 상태는 1장 기준표가 우선이다.",
    },
]


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def project(lat: float, lon: float, extent: tuple[float, float, float, float]) -> tuple[float, float]:
    min_lon, min_lat, max_lon, max_lat = extent
    x = 62 + ((lon - min_lon) / (max_lon - min_lon)) * 820
    y = 790 - ((lat - min_lat) / (max_lat - min_lat)) * 590
    return x, y


def polyline(points: list[tuple[float, float]], color: str, dash: str = "", width: int = 8) -> str:
    coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="0.88"{dash_attr}/>'
    )


def render_map(config: dict) -> str:
    c = COLORS
    extent = config["extent"]
    visible_river = [project(lat, lon, extent) for lat, lon in VLTAVA if extent[1] - 0.004 <= lat <= extent[3] + 0.004 and extent[0] - 0.004 <= lon <= extent[2] + 0.004]
    river_svg = polyline(visible_river, c["river"], width=28) if len(visible_river) >= 2 else ""

    route_svg = []
    for _label, color, dash, keys in config["routes"]:
        route_svg.append(polyline([project(P[key].lat, P[key].lon, extent) for key in keys], color, dash))

    markers = []
    legend_rows = []
    for index, key in enumerate(config["points"], start=1):
        place = P[key]
        x, y = project(place.lat, place.lon, extent)
        if key == "hotel_a":
            fill, token = c["hotel_a"], "A"
        elif key == "hotel_b":
            fill, token = c["hotel_b"], "B"
        else:
            fill, token = c["garnet"], str(index)
        markers.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="18" fill="{fill}" stroke="#fff" stroke-width="4"/>'
            f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="800" fill="#fff">{token}</text>'
        )
        legend_rows.append((token, place.label, fill))

    route_legend = []
    route_y = 198
    for label, color, dash, _keys in config["routes"]:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        route_legend.append(
            f'<line x1="982" y1="{route_y}" x2="1030" y2="{route_y}" stroke="{color}" stroke-width="6" stroke-linecap="round"{dash_attr}/>'
            f'<text x="1044" y="{route_y + 7}" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="18" font-weight="700" fill="{c["ink"]}">{esc(label)}</text>'
        )
        route_y += 31

    list_y = route_y + 15
    point_legend = []
    for token, label, fill in legend_rows:
        point_legend.append(
            f'<circle cx="995" cy="{list_y}" r="13" fill="{fill}"/>'
            f'<text x="995" y="{list_y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="800" fill="#fff">{esc(token)}</text>'
            f'<text x="1020" y="{list_y + 6}" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="17" fill="{c["ink"]}">{esc(label)}</text>'
        )
        list_y += 30

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc">
  <title id="title">{esc(config["title"])}</title>
  <desc id="desc">{esc(config["subtitle"])}</desc>
  <defs>
    <clipPath id="mapClip"><rect x="55" y="185" width="840" height="620" rx="22"/></clipPath>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M 48 0 L 0 0 0 48" fill="none" stroke="{c["line"]}" stroke-width="1" opacity=".35"/></pattern>
  </defs>
  <rect width="1400" height="900" fill="{c["paper"]}"/>
  <rect x="24" y="24" width="1352" height="852" rx="22" fill="none" stroke="{c["line"]}" stroke-width="2"/>
  <text x="62" y="64" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="18" font-weight="800" fill="{c["garnet"]}">PRAHA ORIENTATION · OFFLINE SCHEMATIC</text>
  <text x="62" y="112" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="39" font-weight="800" fill="{c["ink"]}">{esc(config["title"])}</text>
  <text x="62" y="148" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="20" fill="{c["muted"]}">{esc(config["subtitle"])}</text>
  <rect x="55" y="185" width="840" height="620" rx="22" fill="url(#grid)" stroke="{c["line"]}" stroke-width="2"/>
  <g clip-path="url(#mapClip)">
    <path d="M 150 760 C 260 650, 230 500, 360 390 C 465 300, 610 270, 820 225" fill="none" stroke="{c["gold"]}" stroke-width="2" stroke-dasharray="10 14" opacity=".25"/>
    {river_svg}
    {''.join(route_svg)}
    {''.join(markers)}
  </g>
  <text x="72" y="228" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="{c["river"]}">VLTAVA</text>
  <path d="M 850 250 L 850 205 L 842 220 M 850 205 L 858 220" fill="none" stroke="{c["ink"]}" stroke-width="3"/>
  <text x="850" y="190" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="800" fill="{c["ink"]}">N</text>
  <rect x="952" y="174" width="394" height="631" rx="18" fill="#fffdf9" stroke="{c["line"]}" stroke-width="2"/>
  <text x="982" y="178" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="15" font-weight="800" fill="{c["garnet"]}">동선 개념선</text>
  {''.join(route_legend)}
  <line x1="980" y1="{route_y + 1}" x2="1318" y2="{route_y + 1}" stroke="{c["line"]}"/>
  {''.join(point_legend)}
  <text x="62" y="844" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="17" fill="{c["muted"]}">{esc(config["note"])}</text>
  <text x="1338" y="844" text-anchor="end" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="15" fill="{c["muted"]}">WGS84 좌표 비례 · 도로 라우팅 아님 · 2026-07-10 검증</text>
</svg>
'''


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "generated_at": "2026-07-10",
        "privacy": "offline generation; no itinerary or hotel coordinates sent to external services",
        "coordinate_system": "WGS84 / EPSG:4326",
        "coordinate_sources": "official hotel sites, Wikidata, OpenStreetMap references and repository route data",
        "navigation_scope": "schematic relationship maps; not turn-by-turn routing",
        "maps": [],
    }
    for config in MAPS:
        target = OUTPUT_DIR / f'{config["id"]}.svg'
        target.write_text(render_map(config), encoding="utf-8", newline="\n")
        manifest["maps"].append(
            {
                "id": config["id"],
                "title": config["title"],
                "points": [
                    {"key": key, "lat": P[key].lat, "lon": P[key].lon, "label": P[key].label}
                    for key in config["points"]
                ],
            }
        )
        print(f"Generated {target}")
    (OUTPUT_DIR / "map-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
