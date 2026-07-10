#!/usr/bin/env python3
"""Generate fixed-itinerary schematic SVG maps for the Swiss PDF guidebook."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "guidebook" / "swiss" / "maps"

COLORS = {
    "ink": "#1d2926",
    "muted": "#65716e",
    "paper": "#fbfbf8",
    "red": "#d52b1e",
    "pine": "#176b5b",
    "lake": "#2d7694",
    "orange": "#c76b22",
    "line": "#c9d2ce",
    "soft": "#edf3f0",
}


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def shell(title: str, subtitle: str, body: str, legend: str) -> str:
    c = COLORS
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(subtitle)}</desc>
  <rect width="1400" height="900" fill="{c['paper']}"/>
  <rect x="0" y="0" width="24" height="900" fill="{c['red']}"/>
  <text x="78" y="78" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="30" font-weight="800" fill="{c['red']}">FIXED ROUTE MAP · 축척 아님</text>
  <text x="78" y="135" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="48" font-weight="800" fill="{c['ink']}">{esc(title)}</text>
  <text x="78" y="181" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="24" fill="{c['muted']}">{esc(subtitle)}</text>
  <line x1="78" y1="215" x2="1322" y2="215" stroke="{c['line']}" stroke-width="3"/>
  {body}
  <rect x="78" y="818" width="1244" height="1" fill="{c['line']}"/>
  <text x="78" y="858" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="19" fill="{c['muted']}">{esc(legend)}</text>
</svg>
"""


def node(
    x: int,
    y: int,
    number: str,
    title: str,
    note: str,
    color: str,
    *,
    label_x: int | None = None,
    label_y: int | None = None,
    anchor: str = "start",
) -> str:
    c = COLORS
    label_x = x + 48 if label_x is None else label_x
    label_y = y - 7 if label_y is None else label_y
    return f"""
  <circle cx="{x}" cy="{y}" r="31" fill="{color}"/>
  <text x="{x}" y="{y + 9}" text-anchor="middle" font-family="Arial, sans-serif" font-size="25" font-weight="800" fill="#ffffff">{esc(number)}</text>
  <text x="{label_x}" y="{label_y}" text-anchor="{anchor}" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="26" font-weight="800" fill="{c['ink']}">{esc(title)}</text>
  <text x="{label_x}" y="{label_y + 32}" text-anchor="{anchor}" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="19" fill="{c['muted']}">{esc(note)}</text>
"""


def line(x1: int, y1: int, x2: int, y2: int, color: str, label: str = "", dash: bool = False) -> str:
    dash_attr = ' stroke-dasharray="13 10"' if dash else ""
    label_svg = ""
    if label:
        label_svg = f'<text x="{(x1 + x2) // 2}" y="{(y1 + y2) // 2 - 13}" text-anchor="middle" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="18" font-weight="700" fill="{color}">{esc(label)}</text>'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="9" stroke-linecap="round"{dash_attr}/>{label_svg}'


def lucerne_walk() -> str:
    c = COLORS
    body = f"""
  <path d="M 800 240 C 760 350, 790 430, 720 520 C 650 610, 690 710, 610 780" fill="none" stroke="{c['lake']}" stroke-width="54" opacity="0.18"/>
  <text x="740" y="505" transform="rotate(-60 740 505)" font-family="Arial, sans-serif" font-size="20" fill="{c['lake']}">REUSS</text>
  {line(1030, 690, 1080, 350, c['pine'], '도보')}
  {line(1080, 350, 1180, 515, c['orange'], '장보기')}
  {line(1080, 350, 820, 330, c['pine'], '도보')}
  {line(820, 330, 620, 545, c['pine'], '도보')}
  {line(620, 545, 405, 565, c['pine'], '도보')}
  {line(405, 565, 330, 385, c['pine'], '도보')}
  {node(1030, 690, '1', 'Luzern Bahnhof / Pier', '역 지하 Coop·선착장 기준점', c['red'], label_x=982, label_y=680, anchor='end')}
  {node(1080, 350, '2', 'Hotel Luzernerhof', 'Alpenstrasse 3 · 고정 숙소', c['red'], label_x=1130, label_y=290)}
  {node(820, 330, '3', 'Hofkirche', '호텔 인근 첫 산책', c['pine'], label_x=772, label_y=300, anchor='end')}
  {node(620, 545, '4', 'Lion Monument', '1792년 스위스 근위대 추모', c['pine'])}
  {node(405, 565, '5', 'Chapel Bridge', '카펠교·수탑·회화 패널', c['pine'], label_x=357, label_y=555, anchor='end')}
  {node(330, 385, '6', 'Old Town', 'Kornmarkt·Weinmarkt·강변', c['pine'])}
  {node(1180, 515, '7', 'Coop Löwencenter', '물·아침·산악 간식', c['orange'], label_x=1180, label_y=580, anchor='middle')}
"""
    return shell(
        "07.16 루체른 도착일 도보 축",
        "역에서 숙소로 이동한 뒤 확정된 호프교회·사자상·카펠교·구시가지 순서를 그대로 표시",
        body,
        "빨강 = 예약·숙소 기준점 · 초록 = 확정 산책축 · 주황 = 장보기 · 실시간 영업은 공식 지점 페이지 확인",
    )


def rigi_loop() -> str:
    c = COLORS
    body = f"""
  <ellipse cx="730" cy="515" rx="485" ry="245" fill="{c['lake']}" opacity="0.08"/>
  {line(270, 650, 500, 665, c['lake'], '배 09:12-10:09')}
  {line(500, 665, 690, 315, c['red'], '산악열차')}
  {line(690, 315, 840, 470, c['red'], '15:00-15:15 산악열차')}
  {line(840, 470, 1035, 630, c['orange'], '케이블카')}
  {line(1035, 630, 1110, 695, c['pine'], '도보')}
  {line(1110, 695, 270, 650, c['lake'], '배 17:05-17:47')}
  {node(270, 650, '1', 'Luzern Pier 1', '09:12 출발 · 17:47 복귀축', c['red'], label_x=222, label_y=710, anchor='end')}
  {node(500, 665, '2', 'Vitznau', '10:09 도착 · 10:15 환승', c['red'], label_x=548, label_y=710)}
  {node(690, 315, '3', 'Rigi Kulm station', '10:47 역 도착 · 정상은 오르막 도보', c['red'])}
  {node(840, 470, '4', 'Rigi Kaltbad', '15:15 도착 · 16:10 케이블카', c['red'])}
  {node(1035, 630, '5', 'Weggis cable car', '계곡역 하차', c['red'], label_x=987, label_y=615, anchor='end')}
  {node(1110, 695, '6', 'Weggis Pier', '17:05 Luzern행 배', c['red'], label_x=1158, label_y=735)}
"""
    return shell(
        "07.17 리기산 라운드트립",
        "Luzern-Pier 1에서 출발해 Vitznau·Rigi Kulm·Kaltbad·Weggis를 거쳐 같은 날 복귀",
        body,
        "파랑 = 유람선 · 빨강 = 산악열차 · 주황 = 케이블카 · 초록 = 선착장 연결 도보",
    )


def interlaken_axis() -> str:
    c = COLORS
    body = f"""
  <rect x="102" y="292" width="1196" height="390" rx="30" fill="{c['soft']}"/>
  <path d="M 110 660 C 380 605, 700 705, 1290 625" fill="none" stroke="{c['lake']}" stroke-width="26" opacity="0.25"/>
  <text x="985" y="675" font-family="Arial, sans-serif" font-size="19" fill="{c['lake']}">AARE</text>
  {line(150, 650, 320, 520, c['pine'])}
  {line(320, 520, 470, 360, c['pine'])}
  {line(320, 520, 700, 310, c['pine'])}
  {line(150, 650, 760, 620, c['pine'])}
  {line(760, 620, 1120, 620, c['pine'])}
  {line(1120, 620, 1060, 380, c['pine'])}
  {line(1060, 380, 980, 250, c['red'], '', True)}
  {node(150, 650, '1', 'Interlaken West', '숙소 하차역으로 확정', c['red'], label_x=198, label_y=705)}
  {node(320, 520, '2', '65 Hauptstrasse', '스위스:인터젠의방', c['red'], label_x=272, label_y=470, anchor='end')}
  {node(470, 360, '3', 'Coop Unterseen', '숙소 생활권 장보기', c['orange'], label_x=422, label_y=300, anchor='end')}
  {node(700, 310, '4', 'Stadthausplatz', '1279년 기원 운터젠 중심', c['pine'], label_x=748, label_y=245)}
  {node(760, 620, '5', 'Höhematte', '15:00 비행 뒤 착륙·산책', c['red'], label_x=760, label_y=560, anchor='middle')}
  {node(1120, 620, '6', 'Interlaken Ost', '융프라우요흐 환승 허브', c['red'], label_x=1072, label_y=540, anchor='end')}
  {node(1060, 380, '7', 'Harderbahn valley', '확정 일정 밖 선택지', c['pine'], label_x=1012, label_y=315, anchor='end')}
  {node(980, 250, '8', 'Harder Kulm', '여유 시간·운행 확인 시만', c['orange'], label_x=930, label_y=235, anchor='end')}
"""
    return shell(
        "인터라켄 West-숙소-Ost 생활권",
        "숙소·Coop·운터젠은 West 생활권, 15:00 패러글라이딩은 회에마테, 융프라우요흐 환승은 Ost",
        body,
        "빨강 = 고정 역·예약 활동 · 초록 = 도보 생활권 · 주황 = 장보기·확정 일정 밖 선택지",
    )


def grindelwald_first() -> str:
    c = COLORS
    body = f"""
  <path d="M 155 700 L 520 690 L 750 530 L 900 370 L 1070 300" fill="none" stroke="{c['line']}" stroke-width="28" stroke-linecap="round"/>
  {line(180, 700, 420, 625, c['pine'])}
  {line(420, 625, 585, 610, c['pine'])}
  {line(585, 610, 760, 495, c['red'])}
  {line(760, 495, 905, 380, c['red'])}
  {line(905, 380, 1080, 300, c['red'])}
  {line(1080, 300, 1180, 385, c['pine'])}
  {line(1080, 300, 1190, 585, c['orange'], 'Bachalpsee 왕복', True)}
  {node(180, 700, '1', 'Grindelwald station', '11:10 도착 · 고정 이동', c['red'], label_x=228, label_y=750)}
  {node(420, 625, '2', 'Hotel Gletscherblick', '체크인 전 짐 보관 확인', c['red'], label_x=372, label_y=605, anchor='end')}
  {node(585, 610, '3', 'Firstbahn valley', '마지막 하산 시간 확인', c['red'], label_x=633, label_y=665)}
  {node(760, 495, '4', 'Bort', '중간역', c['red'])}
  {node(905, 380, '5', 'Schreckfeld', '중간역', c['red'], label_x=857, label_y=365, anchor='end')}
  {node(1080, 300, '6', 'First', 'Cliff Walk 우선', c['red'])}
  {node(1190, 585, '7', 'Bachalpsee', '날씨·체력·시간 충족 시만', c['orange'], label_x=1142, label_y=635, anchor='end')}
"""
    return shell(
        "그린델발트-피르스트 선택지 구조",
        "피르스트는 07.20 확정 일정이 아니다. 별도 방문을 공부할 때만 중간역과 Bachalpsee 관계를 읽는다",
        body,
        "이 지도 전체는 확정 일정 밖 학습용 · 실제 방문 시 공식 운행·날씨·마지막 하산편 확인",
    )


def jungfraujoch_route() -> str:
    c = COLORS
    body = f"""
  {line(155, 650, 335, 650, c['pine'])}
  {line(335, 650, 515, 650, c['red'])}
  {line(515, 650, 730, 535, c['red'])}
  {line(730, 535, 900, 420, c['red'])}
  {line(900, 420, 1080, 310, c['red'])}
  {line(1080, 310, 1180, 245, c['orange'])}
  {node(155, 650, '1', '65 Hauptstrasse', '운터젠 고정 숙소', c['red'], label_x=92, label_y=580)}
  {node(335, 650, '2', 'Interlaken West', '출발 전 SBB 연결 확인', c['red'], label_x=335, label_y=700, anchor='middle')}
  {node(515, 650, '3', 'Interlaken Ost', '융프라우권 환승 허브', c['red'], label_x=565, label_y=680)}
  {node(730, 535, '4', 'Grindelwald Terminal', 'Eiger Express 환승', c['red'], label_x=682, label_y=515, anchor='end')}
  {node(900, 420, '5', 'Eigergletscher', '산악열차 환승', c['red'])}
  {node(1080, 310, '6', 'Jungfraujoch station', '3,454m · 철도역', c['red'], label_x=1032, label_y=295, anchor='end')}
  {node(1180, 245, '7', 'Sphinx', '3,571m · 알레치 빙하 조망', c['orange'], label_x=1132, label_y=205, anchor='end')}
  <rect x="160" y="745" width="1080" height="50" rx="12" fill="{c['soft']}"/>
  <text x="700" y="777" text-anchor="middle" font-family="Malgun Gothic, Noto Sans KR, sans-serif" font-size="19" font-weight="700" fill="{c['ink']}">2026.05.01-10.31 좌석 예약 의무 · 예약과 별도로 유효한 승차권 필요 · 출발 전 웹캠·운행 확인</text>
"""
    return shell(
        "07.19 융프라우요흐 고정 이동축",
        "운터젠 숙소에서 Interlaken Ost·Grindelwald Terminal·Eigergletscher를 거쳐 융프라우요흐로 왕복",
        body,
        "빨강 = 확정 고산 교통축 · 주황 = 현지 수직 이동·전망대 · 정확한 출발편은 예약 원문과 당일 SBB 확인",
    )


def grindelwald_village_spa() -> str:
    c = COLORS
    body = f"""
  {line(170, 650, 390, 540, c['pine'])}
  {line(390, 540, 610, 520, c['pine'])}
  {line(610, 520, 830, 500, c['orange'])}
  {line(830, 500, 1035, 610, c['pine'])}
  {line(1035, 610, 1120, 350, c['red'])}
  {line(1120, 350, 1035, 610, c['red'])}
  {node(170, 650, '1', 'Grindelwald station', '11:10 도착', c['red'])}
  {node(390, 540, '2', 'Hotel Gletscherblick', 'Kirchbühlstrasse 14', c['red'], label_x=342, label_y=520, anchor='end')}
  {node(610, 520, '3', 'Dorfstrasse', '아이거·샬레·마을 산책', c['pine'], label_x=610, label_y=440, anchor='middle')}
  {node(830, 500, '4', 'Coop Eigershop', 'Dorfstrasse 107 · 이동식', c['orange'], label_x=878, label_y=455)}
  {node(1035, 610, '5', 'Hotel Gletscherblick', '17시대 저녁·휴식', c['red'], label_x=987, label_y=665, anchor='end')}
  {node(1120, 350, '6', 'Hotel Belvedere BelAqua', '20:00-22:00 · 사전 확인', c['red'], label_x=1072, label_y=330, anchor='end')}
"""
    return shell(
        "07.20 그린델발트 마을·장보기·BelAqua",
        "11:10 도착 뒤 호텔, Dorfstrasse, Coop Eigershop, 저녁 휴식, 20:00 BelAqua 순서",
        body,
        "빨강 = 고정 숙소·시간축 · 초록 = 마을 산책 · 주황 = 장보기 · BelAqua 외부 입장은 반드시 사전 확인",
    )


def southbound() -> str:
    c = COLORS
    body = f"""
  {line(170, 340, 510, 340, c['red'], '11:17-11:54')}
  {line(510, 340, 855, 340, c['red'], '11:59-12:23')}
  {line(855, 340, 1185, 340, c['red'], '12:38-13:13')}
  {line(1185, 340, 1040, 590, c['red'], '13:25-13:40')}
  {line(1040, 590, 700, 590, c['orange'], '14:03-14:32')}
  {line(700, 590, 370, 590, c['orange'], '15:49-17:32')}
  {line(370, 590, 170, 590, c['red'], '17:42-18:35')}
  {node(170, 340, '1', 'Grindelwald', '11:17 출발', c['red'], label_x=218, label_y=300)}
  {node(510, 340, '2', 'Interlaken Ost', '11:54/11:59', c['red'], label_x=558, label_y=390)}
  {node(855, 340, '3', 'Spiez', '12:23/12:38', c['red'], label_x=903, label_y=300)}
  {node(1185, 340, '4', 'Brig', '13:13/13:25', c['red'], label_x=1137, label_y=390, anchor='end')}
  {node(1040, 590, '5', 'Iselle', '13:40/14:03 버스', c['red'], label_x=1088, label_y=530)}
  {node(700, 590, '6', 'Domodossola', '14:32/15:49', c['red'], label_x=748, label_y=650)}
  {node(370, 590, '7', 'Sesto Calende', '17:32/17:42', c['red'], label_x=418, label_y=530)}
  {node(170, 590, '8', 'Milano Centrale', '18:35 도착', c['red'], label_x=218, label_y=650)}
"""
    return shell(
        "07.21 남행 환승 개념도",
        "Grindelwald에서 Milano Centrale까지 예약된 순서와 시간을 그대로 시각화",
        body,
        "빨강 = 철도 · 주황 = 예약에 포함된 버스/통합표 구간 · 모든 시각은 예약 원문 기준",
    )


MAPS = {
    "lucerne-fixed-walk.svg": lucerne_walk,
    "rigi-fixed-loop.svg": rigi_loop,
    "interlaken-living-axis.svg": interlaken_axis,
    "grindelwald-first-axis.svg": grindelwald_first,
    "jungfraujoch-fixed-route.svg": jungfraujoch_route,
    "grindelwald-village-spa.svg": grindelwald_village_spa,
    "southbound-transfer.svg": southbound,
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, factory in MAPS.items():
        target = OUTPUT_DIR / filename
        target.write_text(factory(), encoding="utf-8", newline="\n")
        print(f"Generated {target}")


if __name__ == "__main__":
    main()
