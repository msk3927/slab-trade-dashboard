"""슬라브(HS 720712) 국가별 수출·수입 세계 지도 대시보드."""

from __future__ import annotations

import base64
import math
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
FONT = "Hyundai Harmony"
ALL = "(지도 전체)"
FLOWS = ("Export", "Import")
FLOW_KO = {"Export": "수출", "Import": "수입"}

# English name -> ISO-3, latitude, longitude, Korean label.
# Coordinates are country anchors used for flow lines.
_ROWS = [
    ("FRANCE", "FRA", 46.6, 2.2, "프랑스"),
    ("NETHERLANDS", "NLD", 52.2, 5.3, "네덜란드"),
    ("GERMANY", "DEU", 51.2, 10.4, "독일"),
    ("ITALY", "ITA", 42.8, 12.6, "이탈리아"),
    ("UNITED KINGDOM", "GBR", 54.0, -2.5, "영국"),
    ("PORTUGAL", "PRT", 39.6, -8.0, "포르투갈"),
    ("SPAIN", "ESP", 40.2, -3.7, "스페인"),
    ("SWITZERLAND", "CHE", 46.8, 8.2, "스위스"),
    ("CZECH REPUBLIC", "CZE", 49.8, 15.5, "체코"),
    ("SLOVAKIA", "SVK", 48.7, 19.5, "슬로바키아"),
    ("CYPRUS", "CYP", 35.1, 33.2, "키프로스"),
    ("SOUTH KOREA", "KOR", 36.4, 127.8, "대한민국"),
    ("BELGIUM", "BEL", 50.5, 4.5, "벨기에"),
    ("POLAND", "POL", 52.1, 19.4, "폴란드"),
    ("AUSTRIA", "AUT", 47.6, 14.1, "오스트리아"),
    ("CANADA", "CAN", 56.1, -106.3, "캐나다"),
    ("LUXEMBOURG", "LUX", 49.8, 6.1, "룩셈부르크"),
    ("SLOVENIA", "SVN", 46.1, 14.8, "슬로베니아"),
    ("U S A", "USA", 39.8, -98.6, "미국"),
    ("BRAZIL", "BRA", -10.8, -53.1, "브라질"),
    ("INDIA", "IND", 22.8, 79.0, "인도"),
    ("THAILAND", "THA", 15.0, 101.0, "태국"),
    ("MOROCCO", "MAR", 31.8, -7.1, "모로코"),
    ("GREECE", "GRC", 39.1, 22.0, "그리스"),
    ("SWEDEN", "SWE", 62.8, 16.2, "스웨덴"),
    ("HUNGARY", "HUN", 47.2, 19.4, "헝가리"),
    ("ROMANIA", "ROU", 45.9, 24.9, "루마니아"),
    ("EGYPT", "EGY", 26.8, 30.8, "이집트"),
    ("CHINA", "CHN", 35.0, 103.5, "중국"),
    ("DENMARK", "DNK", 56.2, 9.5, "덴마크"),
    ("FINLAND", "FIN", 64.0, 26.0, "핀란드"),
    ("JAPAN", "JPN", 36.5, 138.0, "일본"),
    ("ESTONIA", "EST", 58.6, 25.0, "에스토니아"),
    ("LITHUANIA", "LTU", 55.2, 23.9, "리투아니아"),
    ("MALAYSIA", "MYS", 4.2, 102.0, "말레이시아"),
    ("TURKEY", "TUR", 39.0, 35.2, "튀르키예"),
    ("PAKISTAN", "PAK", 30.4, 69.3, "파키스탄"),
    ("ARGENTINA", "ARG", -34.6, -64.2, "아르헨티나"),
    ("MALTA", "MLT", 35.9, 14.4, "몰타"),
    ("LATVIA", "LVA", 56.9, 24.6, "라트비아"),
    ("CROATIA", "HRV", 45.1, 15.2, "크로아티아"),
    ("ALGERIA", "DZA", 28.0, 2.6, "알제리"),
    ("MEXICO", "MEX", 23.6, -102.5, "멕시코"),
    ("IRISH REPUBLIC", "IRL", 53.2, -8.2, "아일랜드"),
    ("SERBIA", "SRB", 44.0, 21.0, "세르비아"),
    ("KENYA", "KEN", 0.2, 37.9, "케냐"),
    ("SOUTH AFRICA", "ZAF", -29.0, 25.0, "남아프리카"),
    ("BOSNIA-HERZEGOVINA", "BIH", 44.2, 17.7, "보스니아"),
    ("BULGARIA", "BGR", 42.7, 25.3, "불가리아"),
    ("NORWAY", "NOR", 64.5, 11.0, "노르웨이"),
    ("ISRAEL", "ISR", 31.4, 35.0, "이스라엘"),
    ("INDONESIA", "IDN", -2.2, 118.0, "인도네시아"),
    ("ICELAND", "ISL", 64.9, -18.6, "아이슬란드"),
    ("UTD ARAB EMIRATES", "ARE", 24.2, 54.0, "아랍에미리트"),
    ("UKRAINE", "UKR", 49.0, 31.4, "우크라이나"),
    ("SAUDI ARABIA", "SAU", 24.0, 45.0, "사우디아라비아"),
    ("TAIWAN", "TWN", 23.7, 121.0, "대만"),
    ("NEW ZEALAND", "NZL", -41.5, 172.5, "뉴질랜드"),
    ("KAZAKHSTAN", "KAZ", 48.0, 67.0, "카자흐스탄"),
    ("CAMBODIA", "KHM", 12.6, 104.9, "캄보디아"),
    ("OMAN", "OMN", 21.5, 57.0, "오만"),
    ("SINGAPORE", "SGP", 1.35, 103.8, "싱가포르"),
    ("AUSTRALIA", "AUS", -25.3, 133.8, "호주"),
    ("ECUADOR", "ECU", -1.5, -78.2, "에콰도르"),
    ("CHILE", "CHL", -35.7, -71.5, "칠레"),
    ("QATAR", "QAT", 25.3, 51.2, "카타르"),
    ("VIETNAM", "VNM", 16.0, 107.8, "베트남"),
    ("UZBEKISTAN", "UZB", 41.4, 64.6, "우즈베키스탄"),
    ("KUWAIT", "KWT", 29.3, 47.5, "쿠웨이트"),
    ("ANGOLA", "AGO", -12.3, 17.5, "앙골라"),
    ("COLOMBIA", "COL", 4.1, -72.9, "콜롬비아"),
    ("MACEDONIA", "MKD", 41.6, 21.7, "북마케도니아"),
    ("JORDAN", "JOR", 31.2, 36.8, "요르단"),
    ("RUSSIA", "RUS", 56.0, 44.0, "러시아"),
    ("COSTA RICA", "CRI", 9.9, -84.2, "코스타리카"),
    ("URUGUAY", "URY", -32.5, -55.8, "우루과이"),
    ("BAHRAIN", "BHR", 26.0, 50.5, "바레인"),
    ("COUNTRIES AND TERRITORIES NOT SPECIFIED", "", None, None, "미상"),
    ("LIBYA", "LBY", 26.3, 17.2, "리비아"),
    ("KYRGISTAN", "KGZ", 41.2, 74.7, "키르기스스탄"),
    ("VENEZUELA", "VEN", 7.0, -66.0, "베네수엘라"),
    ("LAOS", "LAO", 18.2, 103.8, "라오스"),
    ("BRITISH VIRGIN ISLANDS", "VGB", 18.4, -64.6, "버진아일랜드"),
    ("IRAN", "IRN", 32.4, 53.7, "이란"),
    ("BHUTAN", "BTN", 27.5, 90.4, "부탄"),
    ("SURINAM", "SUR", 4.0, -56.0, "수리남"),
    ("TANZANIA", "TZA", -6.4, 34.9, "탄자니아"),
    ("SYRIA", "SYR", 35.0, 38.5, "시리아"),
    ("SRI LANKA", "LKA", 7.9, 80.7, "스리랑카"),
    ("NORTHERN IRELAND", "", 54.6, -6.8, "북아일랜드"),
    ("GREENLAND", "GRL", 72.0, -40.0, "그린란드"),
    ("NIUE ISLAND", "NIU", -19.05, -169.87, "니우에"),
    ("COOK ISLAND", "COK", -21.2, -159.8, "쿡제도"),
    ("BURMA", "MMR", 21.0, 96.0, "미얀마"),
]
COUNTRIES = {row[0]: row[1:] for row in _ROWS}
ISO_TO_NAME = {meta[0]: name for name, meta in COUNTRIES.items() if meta[0]}

ALIASES = {
    "USA": "U S A",
    "US": "U S A",
    "U.S.A": "U S A",
    "U.S.A.": "U S A",
    "UNITED STATES": "U S A",
    "UNITED STATES OF AMERICA": "U S A",
    "UK": "UNITED KINGDOM",
    "U.K.": "UNITED KINGDOM",
    "GREAT BRITAIN": "UNITED KINGDOM",
    "KOREA": "SOUTH KOREA",
    "REPUBLIC OF KOREA": "SOUTH KOREA",
    "KOREA, REPUBLIC OF": "SOUTH KOREA",
    "KOREA, REP.": "SOUTH KOREA",
    "CZECHIA": "CZECH REPUBLIC",
    "TURKIYE": "TURKEY",
    "TÜRKIYE": "TURKEY",
    "UAE": "UTD ARAB EMIRATES",
    "UNITED ARAB EMIRATES": "UTD ARAB EMIRATES",
    "MYANMAR": "BURMA",
    "VIET NAM": "VIETNAM",
    "RUSSIAN FEDERATION": "RUSSIA",
    "IRELAND": "IRISH REPUBLIC",
    "SURINAME": "SURINAM",
    "KYRGYZSTAN": "KYRGISTAN",
    "NORTH MACEDONIA": "MACEDONIA",
    "SLOVAK REPUBLIC": "SLOVAKIA",
}

GOLD = [[0.0, "#3a2e1c"], [0.35, "#8a6a32"], [0.7, "#e0c48a"], [1.0, "#fff4d2"]]
PIE_COLORS = ["#fff4d2", "#f0d7a2", "#e0c48a", "#d4af77", "#c4a15a", "#b8924e"]


EN_FIX = {
    "U S A": "United States",
    "SOUTH KOREA": "South Korea",
    "UNITED KINGDOM": "United Kingdom",
    "CZECH REPUBLIC": "Czech Republic",
    "IRISH REPUBLIC": "Ireland",
    "UTD ARAB EMIRATES": "United Arab Emirates",
    "SAUDI ARABIA": "Saudi Arabia",
    "NEW ZEALAND": "New Zealand",
    "SOUTH AFRICA": "South Africa",
    "COSTA RICA": "Costa Rica",
    "SRI LANKA": "Sri Lanka",
    "NORTHERN IRELAND": "Northern Ireland",
    "BRITISH VIRGIN ISLANDS": "British Virgin Islands",
    "BOSNIA-HERZEGOVINA": "Bosnia and Herzegovina",
    "COUNTRIES AND TERRITORIES NOT SPECIFIED": "Unspecified",
    "BURMA": "Myanmar",
    "MACEDONIA": "North Macedonia",
    "KYRGISTAN": "Kyrgyzstan",
    "SURINAM": "Suriname",
    "NIUE ISLAND": "Niue",
    "COOK ISLAND": "Cook Islands",
}


def lang() -> str:
    return st.session_state.get("slab_lang", "ko")


def tr(ko_text: str, en_text: str) -> str:
    return en_text if lang() == "en" else ko_text


def ko(name: str) -> str:
    meta = COUNTRIES.get(str(name))
    return meta[3] if meta else str(name)


def cname(name: str) -> str:
    if name == "기타":
        return tr("기타", "Other")
    if lang() == "ko":
        return ko(name)
    return EN_FIX.get(str(name), str(name).title())


def role_name(flow: str) -> str:
    if flow == "Export":
        return tr("수출국", "Export countries")
    return tr("수입국", "Import countries")


def phrase(name: str, flow: str) -> str:
    role = role_name(flow)
    if lang() == "en":
        return f"{cname(name)} {role[0].lower()}{role[1:]}"
    return f"{cname(name)}의 {role}"


def coords(name: str):
    meta = COUNTRIES.get(str(name))
    if not meta or meta[1] is None or meta[2] is None:
        return None
    return float(meta[1]), float(meta[2])


def iso_of(name: str):
    meta = COUNTRIES.get(str(name))
    if not meta or not meta[0]:
        return None
    return meta[0]


def canon_country(value) -> str:
    text = str(value).strip().upper()
    text = " ".join(text.split())
    return ALIASES.get(text, text)


def fmt_ton(value: float) -> str:
    value = float(value)
    if lang() == "en":
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        if value >= 1_000:
            return f"{value / 1_000:.1f}K"
        return f"{value:,.0f}"
    if value >= 1_000_000:
        text = f"{value / 1_000_000:.1f}백만"
    elif value >= 10_000:
        text = f"{value / 10_000:.1f}만"
    elif value >= 1_000:
        text = f"{value / 1_000:.1f}천"
    else:
        return f"{value:,.0f}"
    return text.replace(".0백만", "백만").replace(".0만", "만").replace(".0천", "천")


def fmt_full(value: float) -> str:
    unit = tr("톤", "t")
    return f"{float(value):,.0f} {unit}"


def clean_hs(value) -> str:
    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def norm_flow(value) -> str:
    text = str(value).strip().lower()
    if text.startswith("export") or text.startswith("수출"):
        return "Export"
    if text.startswith("import") or text.startswith("수입"):
        return "Import"
    return ""


def find_default() -> Path | None:
    found = [
        path
        for path in APP_DIR.glob("Kang Others - Imports and Exports*.xlsx")
        if not path.name.startswith("~$")
    ]
    if not found:
        return None
    return max(found, key=lambda path: path.stat().st_mtime)


def _pick(columns, aliases, lookup):
    for alias in aliases:
        if alias in columns:
            return alias
        if alias.lower() in lookup:
            return lookup[alias.lower()]
    return None


def read_trade(source) -> pd.DataFrame:
    raw = pd.read_excel(source, engine="openpyxl")
    raw.columns = [str(col).strip() for col in raw.columns]
    lookup = {col.lower(): col for col in raw.columns}
    reporter = _pick(raw.columns, ["기준국가", "reporter", "reporting country"], lookup)
    flow = _pick(raw.columns, ["수출/수입", "수출수입", "flow", "trade flow"], lookup)
    year = _pick(raw.columns, ["YEAR", "연도", "year"], lookup)
    month = _pick(raw.columns, ["MONTH", "월", "month"], lookup)
    partner = _pick(raw.columns, ["대상국가", "partner", "partner country"], lookup)
    tonnes = _pick(raw.columns, ["Tonnes", "TONNES", "톤", "물량", "tonnes", "net tonnes"], lookup)
    hs = _pick(raw.columns, ["TARIFF_CODE", "HS", "hs"], lookup)
    desc = _pick(raw.columns, ["TARIFF_DESCRIPTION", "DESCRIPTION", "품목"], lookup)
    if not all([reporter, flow, year, month, partner, tonnes]) and raw.shape[1] >= 8:
        cols = list(raw.columns)
        reporter, flow, year, month = cols[0], cols[1], cols[2], cols[3]
        hs, desc = cols[4], cols[5]
        partner, tonnes = cols[6], cols[7]
    if not all([reporter, flow, year, month, partner, tonnes]):
        found = ", ".join(map(str, raw.columns))
        raise ValueError(
            tr(
                "같은 양식이 아닙니다. 기준국가, 수출/수입, YEAR, MONTH, 대상국가, Tonnes 열이 필요합니다. ",
                "This file does not match the layout. Required columns: reporter, export/import, YEAR, MONTH, partner, Tonnes. ",
            )
            + tr(f"현재 열: {found}", f"Columns found: {found}")
        )

    frame = pd.DataFrame(
        {
            "reporter": raw[reporter].map(canon_country),
            "flow": raw[flow].map(norm_flow),
            "year": pd.to_numeric(raw[year], errors="coerce"),
            "month": pd.to_numeric(raw[month], errors="coerce"),
            "partner": raw[partner].map(canon_country),
            "tonnes": pd.to_numeric(
                raw[tonnes].astype(str).str.replace(",", "", regex=False).str.strip(),
                errors="coerce",
            ),
            "hs": raw[hs].map(clean_hs) if hs else "",
            "desc": raw[desc].astype(str).str.strip() if desc else "",
        }
    )
    frame = frame.dropna(subset=["year", "month", "tonnes"])
    frame = frame[frame["flow"].isin(FLOWS) & (frame["tonnes"] > 0)]
    frame = frame[(frame["reporter"] != "") & (frame["partner"] != "")]
    if frame.empty:
        raise ValueError(tr("수출·수입 물량이 있는 행을 찾지 못했습니다.", "No export or import rows were found."))
    frame["year"] = frame["year"].astype(int)
    frame["month"] = frame["month"].astype(int)
    return frame.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def cached_read(path_str: str, mtime: float) -> pd.DataFrame:
    del mtime
    return read_trade(path_str)


def load_default(path: Path) -> pd.DataFrame:
    try:
        return cached_read(str(path), path.stat().st_mtime)
    except OSError:
        temp_path = Path(tempfile.gettempdir()) / "slab_trade_copy.xlsx"
        shutil.copy(path, temp_path)
        return cached_read(str(temp_path), temp_path.stat().st_mtime)


def reset_selection() -> None:
    for flow in FLOWS:
        st.session_state[f"slab_map_nonce_{flow}"] = st.session_state.get(f"slab_map_nonce_{flow}", 0) + 1
        st.session_state[f"slab_table_nonce_{flow}"] = st.session_state.get(f"slab_table_nonce_{flow}", 0) + 1
        st.session_state[f"slab_sel_{flow}"] = None
        st.session_state[f"slab_prev_{flow}"] = None
        st.session_state[f"slab_box_{flow}"] = ALL


@st.cache_data(show_spinner=False)
def font_face_css() -> str:
    faces = []
    for filename, weight in (("현대하모니+L.ttf", 300), ("현대하모니+M.ttf", 500), ("현대하모니+B.ttf", 700)):
        font_path = APP_DIR / filename
        if not font_path.exists():
            continue
        encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
        faces.append(
            f"""
            @font-face {{
              font-family: "{FONT}";
              src: url("data:font/ttf;base64,{encoded}") format("truetype");
              font-weight: {weight};
              font-style: normal;
              font-display: swap;
            }}
            """
        )
    return "\n".join(faces)


def inject_css() -> None:
    st.markdown(
        "<style>\n"
        + font_face_css()
        + """
        html, body, .stApp, .stApp p, .stApp span, .stApp label, .stApp button,
        .stApp input, .stApp textarea, .stApp li,
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stCaptionContainer"],
        div[data-testid="stWidgetLabel"],
        div[data-testid="stWidgetLabel"] p {
          font-family: "Hyundai Harmony", sans-serif !important;
        }
        .top-kicker, .focus-kicker, .panel-title, .stat-strip b { font-weight: 700; }
        .top-title, .focus-name { font-weight: 500; }
        .top-sub, .focus-meta, .stat-strip { font-weight: 300; }
        .stApp {
          background:
            radial-gradient(900px 420px at 50% -10%, rgba(120, 88, 36, 0.28), transparent 55%),
            #07080c;
          color: #f6f0e4;
        }
        .stApp::before {
          content: "";
          position: fixed;
          top: 0; left: 0; right: 0;
          height: 3px;
          background: linear-gradient(90deg, transparent, #d4af77, transparent);
          z-index: 100;
        }
        .block-container { padding-top: 1.1rem; padding-bottom: 1.4rem; max-width: 100%; }
        header[data-testid="stHeader"] { background: transparent; }
        footer { visibility: hidden; }
        .top-kicker {
          color: #b9a588; letter-spacing: 0.22em; font-size: 11px; margin: 0;
        }
        .top-title {
          color: #f3d7a2; font-size: 30px; font-weight: 560; letter-spacing: 0.08em;
          margin: 2px 0 0;
        }
        .top-sub { color: #b7aa96; font-size: 13px; margin: 4px 0 0; }
        .stat-strip {
          display: flex; gap: 18px; flex-wrap: wrap;
          color: #e6d3ae; font-size: 13px; letter-spacing: 0.04em;
          border-top: 1px solid rgba(212,175,119,0.28);
          border-bottom: 1px solid rgba(212,175,119,0.28);
          padding: 8px 2px; margin: 8px 0 12px;
        }
        .stat-strip b { color: #fff4d2; font-weight: 600; }
        .focus {
          border: 1px solid rgba(212,175,119,0.55);
          background: rgba(18,15,12,0.88);
          padding: 12px 14px;
          margin: 4px 0 10px;
        }
        .focus-kicker { color: #c4b59a; letter-spacing: 0.16em; font-size: 11px; }
        .focus-name { color: #fff4d2; font-size: 22px; margin-top: 4px; }
        .focus-meta { color: #e6d3ae; font-size: 13px; margin-top: 4px; }
        .panel-title {
          color: #f0d7a2; font-size: 13px; letter-spacing: 0.14em;
          border-bottom: 1px solid rgba(212,175,119,0.35);
          padding: 2px 2px 6px; margin: 0 0 4px;
        }
        div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] {
          border: 1px solid rgba(212,175,119,0.38);
          background: rgba(8,8,10,0.72);
        }
        div[data-baseweb="tab-list"] {
          gap: 8px; background: transparent;
          border-bottom: 1px solid rgba(212,175,119,0.25);
        }
        button[data-baseweb="tab"] {
          background: transparent;
          border: 1px solid rgba(212,175,119,0.35);
          color: #c4b59a;
          letter-spacing: 0.18em;
          padding: 6px 22px;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
          background: linear-gradient(180deg, rgba(212,175,119,0.28), rgba(212,175,119,0.06));
          color: #fff4d2;
          border-color: #d4af77;
        }
        div[data-testid="stFileUploader"] section {
          border: 1px solid rgba(212,175,119,0.55);
          background: rgba(16,14,12,0.82);
          border-radius: 0;
        }
        div[data-testid="stFileUploader"] label { color: #f0d7a2; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def panel_title(text: str) -> None:
    st.markdown(f'<div class="panel-title">{text}</div>', unsafe_allow_html=True)


def point_dict(point) -> dict:
    if isinstance(point, dict):
        return point
    return {
        key: getattr(point, key, None)
        for key in ("customdata", "location", "curve_number", "curveNumber")
    }


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return list(value)
    except TypeError:
        return [value]


def selection_points(event):
    if event is None:
        return []
    selected = event.get("selection") if isinstance(event, dict) else getattr(event, "selection", None)
    if selected is None:
        return []
    points = selected.get("points") if isinstance(selected, dict) else getattr(selected, "points", None)
    return list(points or [])


def country_from_points(points, reporters: set[str]):
    found = None
    best = -1
    for point in points:
        data = point_dict(point)
        custom = as_list(data.get("customdata"))
        name = custom[0] if custom else None
        role = custom[3] if len(custom) >= 4 else None
        if role != "reporter":
            iso = data.get("location")
            if iso in ISO_TO_NAME:
                name = ISO_TO_NAME[iso]
                role = "reporter"
        if role == "reporter" and name in reporters:
            curve = data.get("curve_number")
            if curve is None:
                curve = data.get("curveNumber") or 0
            if curve >= best:
                best = curve
                found = name
    return found


def table_rows(event):
    if event is None:
        return []
    selected = event.get("selection") if isinstance(event, dict) else getattr(event, "selection", None)
    if selected is None:
        return []
    rows = selected.get("rows") if isinstance(selected, dict) else getattr(selected, "rows", None)
    return list(rows or [])


def on_country_change(flow: str) -> None:
    value = st.session_state.get(f"slab_box_{flow}_{lang()}", ALL)
    st.session_state[f"slab_box_{flow}"] = value
    selected = None if value == ALL else value
    st.session_state[f"slab_sel_{flow}"] = selected
    st.session_state[f"slab_prev_{flow}"] = selected
    st.session_state[f"slab_map_nonce_{flow}"] = st.session_state.get(f"slab_map_nonce_{flow}", 0) + 1
    st.session_state[f"slab_table_nonce_{flow}"] = st.session_state.get(f"slab_table_nonce_{flow}", 0) + 1


def chart_layout(fig: go.Figure, height: int, title: str, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(size=14, color="#f0d7a2", family=FONT), x=0, xanchor="left", y=0.98, yanchor="top"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f6f0e4", family=FONT),
        margin=dict(l=8, r=12, t=58 if legend else 42, b=8),
        hoverlabel=dict(bgcolor="#1a150e", bordercolor="#d4af77", font=dict(color="#f6e7c1", family=FONT)),
        showlegend=legend,
        legend=dict(
            orientation="h",
            y=1.02,
            yanchor="bottom",
            x=1,
            xanchor="right",
            font=dict(color="#f0d7a2", family=FONT, size=12),
        ),
    )
    return fig


def build_map(totals: pd.DataFrame, links: pd.DataFrame, selected: str | None, flow: str) -> tuple[go.Figure, int]:
    fig = go.Figure()
    ranked = totals.sort_values("tonnes", ascending=False).reset_index(drop=True)
    names, isos, logs, custom = [], [], [], []
    for rank, row in enumerate(ranked.itertuples(index=False), start=1):
        iso = iso_of(row.reporter)
        if not iso:
            continue
        names.append(row.reporter)
        isos.append(iso)
        logs.append(math.log10(max(float(row.tonnes), 1)))
        custom.append([row.reporter, cname(row.reporter), float(row.tonnes), "reporter", rank])

    ticks = []
    if custom:
        amounts = [item[2] for item in custom]
        low, high = min(amounts), max(amounts)
        ticks = [low]
        if high > low * 10:
            ticks.append(10 ** ((math.log10(max(low, 1)) + math.log10(high)) / 2))
        if high != low:
            ticks.append(high)
    fig.add_trace(
        go.Choropleth(
            locations=isos,
            z=logs,
            locationmode="ISO-3",
            colorscale=GOLD,
            customdata=custom,
            marker_line_color="#1a140c",
            marker_line_width=0.6,
            colorbar=dict(
                title=dict(text=tr("톤", "t"), font=dict(color="#f0d7a2", size=12, family=FONT)),
                tickfont=dict(color="#f6f0e4", size=11),
                bgcolor="rgba(0,0,0,0)",
                thickness=10,
                len=0.52,
                x=1.02,
                outlinewidth=0,
                tickvals=[math.log10(max(tick, 1)) for tick in ticks],
                ticktext=[fmt_ton(tick) for tick in ticks],
            ),
            hovertemplate="<b>%{customdata[1]}</b><br>"
            + tr("%{customdata[4]}위", "#%{customdata[4]}")
            + "<br>%{customdata[2]:,.0f} "
            + tr("톤", "t")
            + "<extra></extra>",
        )
    )

    missing = 0
    if selected:
        chosen = iso_of(selected)
        if chosen:
            fig.add_trace(
                go.Choropleth(
                    locations=[chosen],
                    z=[1],
                    locationmode="ISO-3",
                    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    showscale=False,
                    marker_line_width=2.2,
                    marker_line_color="#fff4d2",
                    hoverinfo="skip",
                )
            )
        origin = coords(selected)
        bundle = links[links["reporter"] == selected].sort_values("tonnes")
        drawable = []
        for row in bundle.itertuples(index=False):
            if row.partner == selected:
                missing += 1
                continue
            target = coords(row.partner)
            if origin is None or target is None:
                missing += 1
                continue
            drawable.append((row, target))
        peak = max((float(row.tonnes) for row, _ in drawable), default=0)
        for row, target in drawable:
            width = 1.2 + 6.8 * (math.log1p(float(row.tonnes)) / math.log1p(peak)) if peak else 1.6
            if flow == "Export":
                hover = f"{cname(selected)} → {cname(row.partner)}<br>{fmt_full(row.tonnes)}"
            else:
                hover = f"{cname(row.partner)} → {cname(selected)}<br>{fmt_full(row.tonnes)}"
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin[1], target[1]],
                    lat=[origin[0], target[0]],
                    mode="lines",
                    line=dict(width=width + 3.2, color="rgba(212,175,119,0.16)"),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin[1], target[1]],
                    lat=[origin[0], target[0]],
                    mode="lines",
                    line=dict(width=width, color="rgba(255,236,196,0.95)"),
                    text=hover,
                    hoverinfo="text",
                    showlegend=False,
                )
            )
        if drawable:
            reporter_names = set(ranked["reporter"])
            lons = [target[1] for _, target in drawable]
            lats = [target[0] for _, target in drawable]
            sizes = [
                8 + 20 * math.sqrt(float(row.tonnes) / peak) if peak else 10
                for row, _ in drawable
            ]
            custom_pts = []
            for row, _ in drawable:
                role = "reporter" if row.partner in reporter_names else "partner"
                custom_pts.append([row.partner, cname(row.partner), float(row.tonnes), role])
            labels = [""] * len(drawable)
            for index in range(max(0, len(drawable) - 6), len(drawable)):
                labels[index] = cname(drawable[index][0].partner)
            fig.add_trace(
                go.Scattergeo(
                    lon=lons,
                    lat=lats,
                    mode="markers+text",
                    text=labels,
                    textposition="top center",
                    textfont=dict(color="#fff4d2", size=11),
                    customdata=custom_pts,
                    marker=dict(
                        size=sizes,
                        color="#f0d7a2",
                        line=dict(width=0.6, color="#fff8e8"),
                        opacity=0.92,
                    ),
                    hovertemplate="<b>%{customdata[1]}</b><br>%{customdata[2]:,.0f} " + tr("톤", "t") + "<extra></extra>",
                    showlegend=False,
                )
            )
        if origin:
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin[1]],
                    lat=[origin[0]],
                    mode="markers",
                    customdata=[[selected, ko(selected), 0, "reporter"]],
                    marker=dict(size=14, color="#fff8e8", line=dict(width=2, color="#d4af77")),
                    hovertemplate=f"<b>{cname(selected)}</b><extra></extra>",
                    showlegend=False,
                )
            )

    caption = phrase(selected, flow) if selected else tr("나라를 클릭하세요", "Click a country")
    fig.update_layout(
        height=680,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=36, b=0),
        font=dict(color="#f6f0e4", family=FONT),
        hoverlabel=dict(bgcolor="#1a150e", bordercolor="#d4af77", font_color="#f6e7c1"),
        annotations=[
            dict(
                text=caption,
                x=0.01,
                y=0.98,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=16, color="#f3d7a2", family=FONT),
                align="left",
            )
        ],
        uirevision=flow,
    )
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="#14120e",
        showocean=True,
        oceancolor="#07080c",
        showcountries=True,
        countrycolor="#4a3d2b",
        countrywidth=0.5,
        coastlinecolor="#6a5a42",
        coastlinewidth=0.6,
        showframe=False,
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
        lataxis_range=[-52, 84],
        lonaxis_range=[-168, 188],
    )
    return fig, missing


def build_bar(names: list[str], values: list[float], title: str) -> go.Figure:
    pairs = sorted(zip(names, values), key=lambda item: item[1])
    labels = [cname(name) for name, _ in pairs]
    amounts = [value for _, value in pairs]
    fig = go.Figure(
        go.Bar(
            x=amounts,
            y=labels,
            orientation="h",
            marker=dict(
                color=amounts,
                colorscale=[[0, "#6b5428"], [1, "#fff4d2"]],
                showscale=False,
            ),
            hovertemplate="%{y}<br>%{x:,.0f} " + tr("톤", "t") + "<extra></extra>",
        )
    )
    fig.update_xaxes(gridcolor="rgba(212,175,119,0.12)", title=tr("톤", "t"), tickfont=dict(color="#e6d3ae", family=FONT))
    fig.update_yaxes(
        automargin=True,
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(color="#fff6df", size=14, family=FONT),
    )
    laid = chart_layout(fig, 360, title)
    laid.update_layout(margin=dict(l=12, r=16, t=42, b=8))
    return laid


def build_monthly(frame: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure()
    palette = ["#8c7340", "#f0d7a2", "#fff4d2", "#5c4a2c"]
    months = list(range(1, 13))
    for index, year in enumerate(sorted(frame["year"].unique())):
        part = frame[frame["year"] == year].set_index("month")["tonnes"]
        fig.add_bar(
            x=[tr(f"{month}월", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month - 1]) for month in months],
            y=[float(part.get(month, 0)) for month in months],
            name=str(int(year)),
            marker_color=palette[index % len(palette)],
            hovertemplate="%{x}<br>%{y:,.0f} " + tr("톤", "t") + "<extra>%{fullData.name}</extra>",
        )
    fig.update_xaxes(
        gridcolor="rgba(0,0,0,0)",
        automargin=True,
        tickangle=-35,
        tickfont=dict(color="#e6d3ae", size=11, family=FONT),
    )
    fig.update_yaxes(
        gridcolor="rgba(212,175,119,0.12)",
        automargin=True,
        tickfont=dict(color="#e6d3ae", family=FONT),
        title=dict(text=tr("톤", "t"), font=dict(family=FONT, color="#e6d3ae")),
    )
    return chart_layout(fig, 360, title, legend=True)


def build_donut(names: list[str], values: list[float], title: str) -> go.Figure:
    ordered = sorted(zip(names, values), key=lambda item: item[1], reverse=True)
    if len(ordered) > 5:
        head = ordered[:5]
        rest = sum(value for _, value in ordered[5:])
        head.append(("기타", rest))
        ordered = head
    labels = [cname(name) for name, _ in ordered]
    amounts = [value for _, value in ordered]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=amounts,
            hole=0.64,
            sort=False,
            marker=dict(colors=PIE_COLORS, line=dict(color="#07080c", width=2)),
            textinfo="percent",
            textfont=dict(color="#1a150e", size=11),
            hovertemplate="%{label}<br>%{value:,.0f} " + tr("톤", "t") + " (%{percent})<extra></extra>",
        )
    )
    center = fmt_ton(sum(amounts)) if amounts else "-"
    fig.update_layout(
        annotations=[
            dict(
                text=center,
                x=0.5,
                y=0.5,
                font=dict(size=16, color="#f3d7a2", family=FONT),
                showarrow=False,
            )
        ]
    )
    return chart_layout(fig, 340, title)


def render_tab(frame: pd.DataFrame, flow: str) -> None:
    sub = frame[frame["flow"] == flow]
    if sub.empty:
        st.warning(tr(f"선택한 기간에 {FLOW_KO[flow]} 실적이 없습니다.", f"No {flow.lower()} volume in this period."))
        return

    totals = sub.groupby("reporter", as_index=False)["tonnes"].sum().sort_values("tonnes", ascending=False)
    links = sub.groupby(["reporter", "partner"], as_index=False)["tonnes"].sum()
    reporters = totals["reporter"].tolist()
    reporter_set = set(reporters)
    grand = float(totals["tonnes"].sum())

    sel_key = f"slab_sel_{flow}"
    prev_key = f"slab_prev_{flow}"
    box_key = f"slab_box_{flow}"
    map_nonce_key = f"slab_map_nonce_{flow}"
    table_nonce_key = f"slab_table_nonce_{flow}"
    row_sig_key = f"slab_row_sig_{flow}"
    pending_key = f"slab_pending_box_{flow}"
    for key, default in (
        (sel_key, None),
        (prev_key, None),
        (map_nonce_key, 0),
        (table_nonce_key, 0),
    ):
        st.session_state.setdefault(key, default)

    if pending_key in st.session_state:
        pending = st.session_state.pop(pending_key)
        if pending in reporter_set:
            st.session_state[sel_key] = pending
            st.session_state[prev_key] = pending
            st.session_state[box_key] = pending
        else:
            st.session_state[sel_key] = None
            st.session_state[prev_key] = None
            st.session_state[box_key] = ALL

    selected = st.session_state.get(sel_key)
    if selected not in reporter_set:
        selected = None
        st.session_state[sel_key] = None
    if box_key not in st.session_state or st.session_state[box_key] not in ([ALL] + reporters):
        st.session_state[box_key] = selected or ALL

    one = links[links["reporter"] == selected] if selected else links.iloc[0:0]
    one = one.sort_values("tonnes", ascending=False)
    sel_total = float(one["tonnes"].sum()) if selected else 0.0
    scope = sub[sub["reporter"] == selected] if selected else sub
    monthly = scope.groupby(["year", "month"], as_index=False)["tonnes"].sum()
    role = role_name(flow)

    left, right = st.columns([1.45, 1.0], gap="small")
    with left:
        panel_title(tr(f"{role} 지도  ·  색이 밝을수록 물량이 많습니다", f"{role} map  ·  brighter means more volume"))
        figure, missing = build_map(totals, links, selected, flow)
        event = st.plotly_chart(
            figure,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            theme=None,
            key=f"slab_map_{flow}_{st.session_state[map_nonce_key]}",
            config={"displayModeBar": False},
        )
        picked = country_from_points(selection_points(event), reporter_set)
        if picked and picked != st.session_state.get(prev_key):
            st.session_state[prev_key] = picked
            st.session_state[sel_key] = picked
            st.session_state[box_key] = picked
            st.session_state[table_nonce_key] += 1
            st.rerun()
        note = tr(
            "나라를 누르면 상대국과 선으로 연결됩니다. 선이 굵을수록 물량이 큽니다.",
            "Click a country to link its partners. Thicker lines mean more volume.",
        )
        if missing:
            note += tr(f" 위치를 특정할 수 없는 {missing}건은 표에만 있습니다.", f" {missing} rows have no map location and appear only in the list.")
        st.caption(note)

    with right:
        pick_col, clear_col = st.columns([4, 1])
        with pick_col:
            widget_key = f"{box_key}_{lang()}"
            st.session_state[widget_key] = st.session_state.get(box_key, ALL)
            st.selectbox(
                role,
                [ALL] + reporters,
                format_func=lambda name: tr("전체", "All") if name == ALL else cname(name),
                key=widget_key,
                on_change=on_country_change,
                args=(flow,),
            )
        with clear_col:
            if st.button(tr("해제", "Clear"), key=f"slab_clear_{flow}", use_container_width=True):
                st.session_state[pending_key] = ALL
                st.session_state[map_nonce_key] += 1
                st.session_state[table_nonce_key] += 1
                st.rerun()

        if selected:
            share = (sel_total / grand * 100) if grand else 0
            top_partner = cname(one.iloc[0]["partner"]) if not one.empty else "-"
            table_names = one["partner"].tolist()
            table_values = one["tonnes"].tolist()
            table_title = phrase(selected, flow)
            list_label = role
            base_total = sel_total
            st.markdown(
                f"""
                <div class="focus">
                  <div class="focus-kicker">{role}</div>
                  <div class="focus-name">{cname(selected)}</div>
                  <div class="focus-meta">{fmt_full(sel_total)} · {tr(f"{one['partner'].nunique()}개국", f"{one['partner'].nunique()} countries")} · {share:.1f}% · {tr('1위', 'Top')} {top_partner}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            table_names = reporters
            table_values = totals["tonnes"].tolist()
            table_title = role
            list_label = role
            base_total = grand
            st.markdown(
                f"""
                <div class="focus">
                  <div class="focus-kicker">{role}</div>
                  <div class="focus-name">{tr("나라를 고르세요", "Choose a country")}</div>
                  <div class="focus-meta">{tr(f"고르면 그 나라의 {role}이 표시됩니다", f"The list becomes that country's {role.lower()}.")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        panel_title(table_title)
        view = pd.DataFrame(
            {
                tr("순위", "Rank"): list(range(1, len(table_names) + 1)),
                list_label: [cname(name) for name in table_names],
                tr("물량(톤)", "Tonnes"): [int(round(value)) for value in table_values],
                tr("비중", "Share"): [f"{(value / base_total * 100):.1f}%" if base_total else "-" for value in table_values],
            }
        )
        table_event = st.dataframe(
            view,
            hide_index=True,
            use_container_width=True,
            height=520,
            on_select="rerun",
            selection_mode="single-row",
            key=f"slab_table_{flow}_{st.session_state[table_nonce_key]}",
            column_config={tr("물량(톤)", "Tonnes"): st.column_config.NumberColumn(format="%,d")},
        )
        rows = table_rows(table_event)
        if rows:
            chosen = table_names[int(rows[0])]
            signature = (st.session_state[table_nonce_key], int(rows[0]), chosen)
            if signature != st.session_state.get(row_sig_key):
                st.session_state[row_sig_key] = signature
                if chosen in reporter_set:
                    st.session_state[pending_key] = chosen
                    st.session_state[map_nonce_key] += 1
                    st.session_state[table_nonce_key] += 1
                    st.rerun()
                else:
                    st.toast(tr(f"{cname(chosen)} : 이번 조건에서는 실적이 없습니다.", f"{cname(chosen)}: no volume in this period."))

    if selected:
        bar_names = one["partner"].head(12).tolist()
        bar_values = one["tonnes"].head(12).tolist()
        bar_title = phrase(selected, flow)
        month_title = tr(f"{cname(selected)} 월별 {FLOW_KO[flow]}", f"{cname(selected)} monthly {flow.lower()}")
        donut_names = one["partner"].tolist()
        donut_values = [float(value) for value in one["tonnes"]]
        donut_title = tr(f"{role} 비중", f"{role} share")
    else:
        bar_names = reporters[:12]
        bar_values = [float(value) for value in totals["tonnes"].head(12)]
        bar_title = tr(f"{role} 상위", f"Top {role.lower()}")
        month_title = tr(f"월별 {FLOW_KO[flow]}", f"Monthly {flow.lower()}")
        donut_names = reporters
        donut_values = [float(value) for value in totals["tonnes"]]
        donut_title = tr(f"{role} 비중", f"{role} share")

    c1, c2, c3 = st.columns([1.15, 1.05, 0.8], gap="small")
    with c1:
        st.plotly_chart(build_bar(bar_names, bar_values, bar_title), use_container_width=True, theme=None)
    with c2:
        st.plotly_chart(build_monthly(monthly, month_title), use_container_width=True, theme=None)
    with c3:
        st.plotly_chart(build_donut(donut_names, donut_values, donut_title), use_container_width=True, theme=None)


def source_banner(frame: pd.DataFrame, label: str) -> None:
    export_total = float(frame.loc[frame["flow"] == "Export", "tonnes"].sum())
    import_total = float(frame.loc[frame["flow"] == "Import", "tonnes"].sum())
    start = frame.sort_values(["year", "month"]).iloc[0]
    end = frame.sort_values(["year", "month"]).iloc[-1]
    codes = sorted({str(code) for code in frame["hs"].dropna().unique() if str(code)})
    desc = " · ".join(dict.fromkeys(str(text) for text in frame["desc"].dropna() if str(text) and str(text) != "nan"))
    hs_text = ", ".join(codes) if codes else "-"
    st.markdown(
        f"""
        <div class="stat-strip">
          <span>{tr("자료", "File")} <b>{label}</b></span>
          <span>{tr("기간", "Period")} <b>{int(start.year)}-{int(start.month):02d} ~ {int(end.year)}-{int(end.month):02d}</b></span>
          <span>{tr("수출", "Exports")} <b>{fmt_full(export_total)}</b></span>
          <span>{tr("수입", "Imports")} <b>{fmt_full(import_total)}</b></span>
          <span>HS <b>{hs_text}</b></span>
          <span>{desc}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_period(frame: pd.DataFrame) -> pd.DataFrame:
    years = sorted(int(year) for year in frame["year"].unique())
    codes = sorted({str(code) for code in frame["hs"].dropna().unique() if str(code)})
    year_key = "slab_years"
    if year_key in st.session_state:
        kept = [year for year in st.session_state[year_key] if year in years]
        st.session_state[year_key] = kept or years
    code_key = "slab_codes"
    if code_key in st.session_state:
        kept_codes = [code for code in st.session_state[code_key] if code in codes]
        st.session_state[code_key] = kept_codes or codes

    f1, f2, f3 = st.columns([1.2, 1.4, 1.4])
    with f1:
        chosen_years = st.multiselect(tr("연도", "Year"), years, default=years, key=year_key)
    with f2:
        month_span = st.slider(tr("월", "Month"), 1, 12, (1, 12), key="slab_months")
    with f3:
        if len(codes) > 1:
            chosen_codes = st.multiselect("HS", codes, default=codes, key=code_key)
        else:
            chosen_codes = codes
            shown = codes[0] if codes else "-"
            st.caption(f"HS {shown}")
    if not chosen_years:
        return frame.iloc[0:0]
    masked = frame[frame["year"].isin(chosen_years) & frame["month"].between(month_span[0], month_span[1])]
    if chosen_codes:
        masked = masked[masked["hs"].astype(str).isin(chosen_codes)]
    return masked


def load_source() -> tuple[pd.DataFrame, str]:
    default_path = find_default()
    uploaded = st.file_uploader(
        tr("동일 양식 엑셀 업로드", "Upload the same Excel layout"),
        type=["xlsx"],
        key="slab_upload",
        help=tr(
            "열 구성이 같으면 지도와 집계가 이 파일로 바뀝니다. 기준국가, 수출/수입, YEAR, MONTH, TARIFF_CODE, TARIFF_DESCRIPTION, 대상국가, Tonnes",
            "Same columns replace the map: reporter, export/import, YEAR, MONTH, TARIFF_CODE, TARIFF_DESCRIPTION, partner, Tonnes",
        ),
    )
    if uploaded is not None:
        signature = (uploaded.name, uploaded.size)
        if st.session_state.get("slab_sig") != signature:
            try:
                frame = read_trade(uploaded)
            except Exception as exc:
                st.error(tr(f"파일을 읽지 못했습니다. {exc}", f"Could not read the file. {exc}"))
                if "slab_df" not in st.session_state:
                    st.stop()
                return st.session_state["slab_df"], st.session_state.get("slab_label", uploaded.name)
            st.session_state["slab_df"] = frame
            st.session_state["slab_label"] = uploaded.name
            st.session_state["slab_sig"] = signature
            reset_selection()
        return st.session_state["slab_df"], st.session_state["slab_label"]

    if default_path is None:
        st.info(tr("같은 양식의 엑셀을 올리면 대시보드가 채워집니다.", "Upload an Excel file in the same layout to fill the dashboard."))
        st.stop()
    signature = ("default", str(default_path), default_path.stat().st_mtime)
    if st.session_state.get("slab_sig") != signature:
        try:
            frame = load_default(default_path)
        except Exception as exc:
            st.error(tr(f"기본 파일을 읽지 못했습니다. 엑셀이 열려 있으면 닫거나, 같은 파일을 업로드해 주세요. {exc}", f"Could not read the default file. Close it in Excel or upload a copy. {exc}"))
            st.stop()
        st.session_state["slab_df"] = frame
        st.session_state["slab_label"] = default_path.name
        st.session_state["slab_sig"] = signature
        reset_selection()
    return st.session_state["slab_df"], st.session_state["slab_label"]


def main() -> None:
    st.set_page_config(
        page_title=tr("슬라브 수출·수입", "Slab trade"),
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.session_state.setdefault("slab_lang", "ko")
    inject_css()
    head_lang, head_left, head_right = st.columns([0.4, 2.3, 1.2], vertical_alignment="center")
    with head_lang:
        if st.button("EN" if lang() == "ko" else "한글", key="slab_lang_btn", use_container_width=True):
            st.session_state["slab_lang"] = "en" if lang() == "ko" else "ko"
            st.rerun()
    with head_left:
        st.markdown(
            f"""
            <p class="top-kicker">HYUNDAI CORPORATION</p>
            <p class="top-title">{tr("슬라브 국가별 수출 · 수입", "Slab exports and imports")}</p>
            <p class="top-sub">{tr("세계 지도에서 국가를 누르면 상대국과 선으로 이어집니다.", "Click a country on the map to link its partners.")}</p>
            """,
            unsafe_allow_html=True,
        )
    with head_right:
        frame, label = load_source()
    source_banner(frame, label)
    filtered = apply_period(frame)
    if filtered.empty:
        st.warning(tr("선택한 연도·월에 실적이 없습니다.", "No volume for the selected year and month."))
        return
    export_tab, import_tab = st.tabs([tr("수출", "Exports"), tr("수입", "Imports")])
    with export_tab:
        render_tab(filtered, "Export")
    with import_tab:
        render_tab(filtered, "Import")
    st.caption(tr(
        "물량은 각 나라의 신고치입니다. 국가별 합계를 모두 더하면 세계 순수출과 같지 않을 수 있습니다.",
        "Volumes are reported by each country. Adding them up is not the same as world net exports.",
    ))


if __name__ == "__main__":
    main()
