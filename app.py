import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import re
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
import time

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZDFheute WhatsApp Artikel-Checker",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700;900&family=Source+Serif+4:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Root Variables ── */
:root {
    --zdf-orange: #FF6A00;
    --zdf-orange-light: #FF8C33;
    --zdf-orange-pale: #FFF0E6;
    --zdf-dark: #1A1A1A;
    --zdf-mid: #3D3D3D;
    --zdf-gray: #6B6B6B;
    --zdf-light: #F5F5F5;
    --zdf-white: #FFFFFF;
    --zdf-green: #1DB954;
    --zdf-red: #E53E3E;
    --radius: 12px;
    --shadow: 0 4px 24px rgba(0,0,0,0.08);
    --shadow-hover: 0 8px 32px rgba(255,106,0,0.15);
}

/* ── Global Reset ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #FAFAFA;
    color: var(--zdf-dark);
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #FAFAFA 0%, #FFF5EE 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Header ── */
.zdf-header {
    background: linear-gradient(135deg, var(--zdf-dark) 0%, #2D2D2D 100%);
    color: white;
    padding: 40px 48px 36px;
    border-radius: 0 0 24px 24px;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}
.zdf-header::before {
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0;
    width: 40%;
    background: linear-gradient(135deg, transparent 0%, rgba(255,106,0,0.08) 100%);
}
.zdf-header-badge {
    display: inline-block;
    background: var(--zdf-orange);
    color: white;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    margin-bottom: 12px;
}
.zdf-header h1 {
    font-size: clamp(22px, 3vw, 36px);
    font-weight: 900;
    margin: 0 0 8px 0;
    line-height: 1.15;
    letter-spacing: -0.5px;
}
.zdf-header h1 .accent { color: var(--zdf-orange); }
.zdf-header p {
    font-size: 15px;
    color: rgba(255,255,255,0.65);
    margin: 0;
    max-width: 560px;
}

/* ── Cards ── */
.card {
    background: var(--zdf-white);
    border-radius: var(--radius);
    padding: 28px 32px;
    box-shadow: var(--shadow);
    border: 1px solid rgba(0,0,0,0.04);
    margin-bottom: 20px;
    transition: box-shadow 0.2s ease;
}
.card:hover { box-shadow: var(--shadow-hover); }
.card-title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: var(--zdf-orange);
    margin-bottom: 16px;
}

/* ── Info Box ── */
.info-box {
    background: var(--zdf-orange-pale);
    border-left: 4px solid var(--zdf-orange);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 16px 20px;
    margin-bottom: 20px;
    font-size: 14px;
    line-height: 1.6;
    color: var(--zdf-mid);
}
.info-box ul { margin: 8px 0 0 0; padding-left: 20px; }
.info-box li { margin-bottom: 4px; }
.info-box strong { color: var(--zdf-dark); }

/* ── Stats Row ── */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1;
    min-width: 120px;
    background: var(--zdf-white);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border: 1px solid rgba(0,0,0,0.04);
    text-align: center;
}
.stat-number {
    font-size: 36px;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--zdf-gray);
}
.stat-orange { color: var(--zdf-orange); }
.stat-green { color: var(--zdf-green); }
.stat-red { color: var(--zdf-red); }

/* ── Article Cards ── */
.article-card {
    background: var(--zdf-white);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border: 1px solid rgba(0,0,0,0.05);
    display: flex;
    align-items: flex-start;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: all 0.15s ease;
}
.article-card:hover {
    border-color: var(--zdf-orange);
    box-shadow: 0 4px 16px rgba(255,106,0,0.1);
    transform: translateY(-1px);
}
.article-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 5px;
}
.dot-green { background: var(--zdf-green); }
.dot-red { background: var(--zdf-red); }
.article-content { flex: 1; min-width: 0; }
.article-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--zdf-dark);
    margin-bottom: 4px;
    line-height: 1.4;
}
.article-meta {
    font-size: 12px;
    color: var(--zdf-gray);
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
}
.article-url {
    font-size: 11px;
    color: var(--zdf-orange);
    text-decoration: none;
    word-break: break-all;
    display: block;
    margin-top: 3px;
}
.badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 20px;
}
.badge-cat {
    background: rgba(255,106,0,0.1);
    color: var(--zdf-orange);
}
.badge-published {
    background: rgba(29,185,84,0.12);
    color: var(--zdf-green);
}
.badge-missing {
    background: rgba(229,62,62,0.1);
    color: var(--zdf-red);
}

/* ── Tab Styling ── */
[data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--zdf-light) !important;
    border-radius: 10px;
    padding: 4px;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: var(--zdf-white) !important;
    color: var(--zdf-orange) !important;
    box-shadow: var(--shadow) !important;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(255,106,0,0.35) !important;
    border-radius: var(--radius) !important;
    background: var(--zdf-orange-pale) !important;
    transition: border-color 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--zdf-orange) !important;
}

/* ── Progress & Spinner ── */
[data-testid="stProgress"] > div > div {
    background: var(--zdf-orange) !important;
}

/* ── Divider ── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, var(--zdf-orange) 0%, transparent 100%);
    margin: 32px 0;
    opacity: 0.25;
}

/* ── Export Button ── */
[data-testid="stDownloadButton"] button {
    background: var(--zdf-orange) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--zdf-orange-light) !important;
}

/* ── Footer ── */
.zdf-footer {
    background: var(--zdf-dark);
    color: rgba(255,255,255,0.6);
    border-radius: 16px 16px 0 0;
    padding: 24px 32px;
    margin: 40px -1rem -1rem -1rem;
    font-size: 13px;
    text-align: center;
    line-height: 1.6;
}
.zdf-footer a {
    color: var(--zdf-orange);
    text-decoration: none;
    font-weight: 600;
}
.zdf-footer .heart { color: var(--zdf-orange); }

/* ── Category Pills ── */
.cat-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    margin: 3px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Search bar ── */
[data-testid="stTextInput"] input {
    border: 1.5px solid rgba(0,0,0,0.1) !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--zdf-orange) !important;
    box-shadow: 0 0 0 3px rgba(255,106,0,0.1) !important;
}

/* ── Streamlit button override ── */
.stButton button {
    background: var(--zdf-orange) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 8px 24px !important;
    transition: all 0.15s ease !important;
}
.stButton button:hover {
    background: var(--zdf-orange-light) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(255,106,0,0.3) !important;
}

.stSelectbox [data-baseweb="select"] {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ───────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SITEMAPS = [
    "https://www.zdfheute.de/sitemap.xml",
    "https://www.zdfheute.de/sitemap-index.xml",
    "https://www.heute.de/sitemap.xml",
]

# Nur diese Domains sind gültig für Artikel
VALID_ARTICLE_DOMAINS = ["zdfheute.de", "heute.de"]

# URL-Segmente, die auf Videos/keine Artikel hinweisen → ausschließen
VIDEO_BLOCKLIST = [
    "/video/", "/videos/", "/video-", "-video-",
    "/live/", "/livestream/", "/sendung/",
    "/serien-und-filme/", "/filme/", "/serien/",
    "/sport/live", "/zdfmediathek/",
    "/3sat/", "/arte/", "/kika/",
    ".html",   # ZDF Mediathek-Videos enden oft auf -100.html
]

# URL muss eines dieser Segmente enthalten, damit es ein Artikel ist
ARTICLE_ALLOWLIST = [
    "/nachrichten/", "/politik/", "/wirtschaft/", "/gesellschaft/",
    "/panorama/", "/sport/", "/wissen/", "/kultur/", "/ratgeber/",
    "/thema/", "/aktuell/", "/regional/",
]

CATEGORY_RULES = {
    "Macht und Folgen": [
        "politik", "analyse", "international", "wahl", "regierung", "bundestag",
        "bundesrat", "europaeisch", "krieg", "konflikt", "diplomatie", "ausland",
        "usa", "russland", "china", "ukraine", "nahost", "israel", "gaza",
    ],
    "Gut zu wissen": [
        "service", "ratgeber", "wetter", "gesundheit", "verbraucher", "finanzen",
        "recht", "tipps", "hilfe", "erklaer", "wie-", "was-ist", "haushalt",
    ],
    "Zwischen Tat und Aufklärung": [
        "crime", "true-crime", "krimi", "mord", "prozess", "urteil", "gericht",
        "verbrechen", "polizei", "ermittlung", "taeter", "opfer", "kriminalitaet",
    ],
    "Trends, Pop & Kurioses": [
        "pop", "kultur", "musik", "film", "serie", "social-media", "tiktok",
        "instagram", "trend", "kuriosum", "skurril", "viral", "celebrity",
        "unterhaltung", "lifestyle", "gaming",
    ],
}


# ─── UTILITY FUNCTIONS ───────────────────────────────────────────────────────
def classify_article(url: str, title: str = "") -> str:
    text = (url + " " + title).lower()
    for cat, keywords in CATEGORY_RULES.items():
        if any(kw in text for kw in keywords):
            return cat
    return "Sonstige Artikel"


def is_valid_article_url(url: str) -> bool:
    """
    Gibt True zurück, wenn die URL ein echter Artikel auf zdfheute.de / heute.de ist.
    Schließt Videos, Mediathek, zdf.de, 3sat, etc. aus.
    """
    if not url:
        return False
    url_lower = url.lower()

    # Muss von zdfheute.de oder heute.de sein
    if not any(domain in url_lower for domain in VALID_ARTICLE_DOMAINS):
        return False

    # zdf.de (ohne zdfheute) rausfiltern
    parsed = urlparse(url_lower)
    hostname = parsed.hostname or ""
    if hostname in ("www.zdf.de", "zdf.de"):
        return False

    # Video-URLs ausschließen
    if any(block in url_lower for block in VIDEO_BLOCKLIST):
        return False

    return True


def normalize_url(url: str) -> str:
    if not isinstance(url, str):
        return ""
    url = url.strip().rstrip("/")
    url = re.sub(r"\?.*$", "", url)
    url = re.sub(r"#.*$", "", url)
    return url.lower()


def parse_date_flexible(date_str: str):
    if not date_str:
        return None
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d.%m.%Y %H:%M",
    ]
    date_str = str(date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:len(fmt)], fmt).date()
        except (ValueError, TypeError):
            pass
    return None


def fetch_url(url: str, timeout: int = 10) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


# ─── SCRAPING FUNCTIONS ───────────────────────────────────────────────────────
def scrape_sitemap(sitemap_url: str, start_date: date, end_date: date) -> list[dict]:
    articles = []
    html = fetch_url(sitemap_url, timeout=15)
    if not html:
        return articles

    try:
        root = ET.fromstring(html.encode("utf-8") if isinstance(html, str) else html)
    except ET.ParseError:
        return articles

    ns = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "news": "http://www.google.com/schemas/sitemap-news/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }

    # Check if it's a sitemap index (links to other sitemaps)
    sitemaploc_tags = root.findall(".//sm:sitemap/sm:loc", ns)
    if sitemaploc_tags:
        # Limit to relevant sitemaps by checking lastmod
        for loc_tag in sitemaploc_tags[:30]:
            child_url = loc_tag.text.strip() if loc_tag.text else ""
            if child_url and ("news" in child_url or "heute" in child_url or "zdf" in child_url):
                child_articles = scrape_sitemap(child_url, start_date, end_date)
                articles.extend(child_articles)
                if len(articles) > 2000:
                    break
        return articles

    # Regular sitemap with <url> entries
    for url_tag in root.findall(".//sm:url", ns):
        loc = url_tag.findtext("sm:loc", namespaces=ns) or ""
        lastmod = url_tag.findtext("sm:lastmod", namespaces=ns) or ""

        # News sitemap specific fields
        news_title = url_tag.findtext(".//news:title", namespaces=ns) or ""
        pub_date_str = url_tag.findtext(".//news:publication_date", namespaces=ns) or lastmod

        if not loc:
            continue

        # Filter: nur echte zdfheute.de-Artikel, keine Videos
        if not is_valid_article_url(loc):
            continue

        pub_date = parse_date_flexible(pub_date_str) if pub_date_str else None

        if pub_date and (pub_date < start_date or pub_date > end_date):
            continue

        articles.append({
            "url": normalize_url(loc),
            "title": news_title,
            "date": pub_date,
            "category": classify_article(loc, news_title),
            "source": "sitemap",
        })

    return articles


def scrape_zdf_homepage_and_categories(start_date: date, end_date: date) -> list[dict]:
    """Scrape zdfheute.de Kategorie-Seiten für Artikel-Links."""
    articles = []
    visited = set()

    category_pages = [
        "https://www.zdfheute.de",
        "https://www.zdfheute.de/nachrichten",
        "https://www.zdfheute.de/nachrichten/politik",
        "https://www.zdfheute.de/nachrichten/wirtschaft",
        "https://www.zdfheute.de/nachrichten/gesellschaft",
        "https://www.zdfheute.de/nachrichten/panorama",
        "https://www.zdfheute.de/nachrichten/sport",
        "https://www.zdfheute.de/nachrichten/wissen",
        "https://www.heute.de",
    ]

    for page_url in category_pages:
        if page_url in visited:
            continue
        visited.add(page_url)

        html = fetch_url(page_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href.startswith("http"):
                href = urljoin("https://www.zdfheute.de", href)

            # Strenger Filter: nur echte Artikel-URLs
            if not is_valid_article_url(href):
                continue

            norm_url = normalize_url(href)
            if norm_url in visited:
                continue
            visited.add(norm_url)

            # Datum aus URL extrahieren
            date_match = re.search(r"/(\d{4})/(\d{2})/(\d{2})/", href)
            pub_date = None
            if date_match:
                try:
                    pub_date = date(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3)),
                    )
                except ValueError:
                    pass

            if pub_date and (pub_date < start_date or pub_date > end_date):
                continue

            title = a_tag.get_text(strip=True) or ""
            articles.append({
                "url": norm_url,
                "title": title[:200],
                "date": pub_date,
                "category": classify_article(norm_url, title),
                "source": "html_scrape",
            })

    return articles


def enrich_article_metadata(articles: list[dict], max_enrich: int = 30) -> list[dict]:
    """Fetch individual article pages to get better title/date for articles missing metadata."""
    enriched = 0
    for art in articles:
        if enriched >= max_enrich:
            break
        if art.get("title") and art.get("date"):
            continue
        html = fetch_url(art["url"], timeout=8)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # Title
        if not art.get("title"):
            for sel in ["h1", 'meta[property="og:title"]', "title"]:
                tag = soup.select_one(sel)
                if tag:
                    art["title"] = (tag.get("content") or tag.get_text(strip=True))[:200]
                    break

        # Date
        if not art.get("date"):
            for sel in [
                'meta[property="article:published_time"]',
                'time[datetime]',
                'meta[name="date"]',
            ]:
                tag = soup.select_one(sel)
                if tag:
                    raw = tag.get("datetime") or tag.get("content") or ""
                    art["date"] = parse_date_flexible(raw)
                    if art["date"]:
                        break

        enriched += 1
        time.sleep(0.1)

    return articles


def collect_zdf_articles(start_date: date, end_date: date, progress_cb=None) -> pd.DataFrame:
    """Main function to collect ZDF articles from multiple sources."""
    all_articles = []

    if progress_cb:
        progress_cb(0.05, "🔍 Starte Sitemap-Abfragen...")

    # 1. Try sitemaps
    for i, sm_url in enumerate(SITEMAPS):
        arts = scrape_sitemap(sm_url, start_date, end_date)
        all_articles.extend(arts)
        if progress_cb:
            progress_cb(0.05 + 0.3 * (i + 1) / len(SITEMAPS), f"📡 Sitemap {i+1}/{len(SITEMAPS)} gescannt ({len(all_articles)} Artikel)")

    # 2. HTML scraping from category pages
    if progress_cb:
        progress_cb(0.45, "🕸️ Scrape Kategorie-Seiten...")

    html_arts = scrape_zdf_homepage_and_categories(start_date, end_date)
    all_articles.extend(html_arts)

    if progress_cb:
        progress_cb(0.65, f"🔎 {len(all_articles)} Artikel gefunden – bereinige Daten...")

    # 3. Deduplicate
    seen = {}
    for art in all_articles:
        u = art["url"]
        if u not in seen:
            seen[u] = art
        else:
            # Merge: prefer entries with more data
            existing = seen[u]
            if not existing.get("title") and art.get("title"):
                existing["title"] = art["title"]
            if not existing.get("date") and art.get("date"):
                existing["date"] = art["date"]

    deduped = list(seen.values())

    if progress_cb:
        progress_cb(0.75, f"✅ {len(deduped)} eindeutige Artikel nach Deduplizierung")

    # 4. Enrich metadata for articles missing title/date
    if progress_cb:
        progress_cb(0.80, "📝 Anreichern von Metadaten (max. 30 Artikel)...")

    enrich_article_metadata(deduped, max_enrich=30)

    if progress_cb:
        progress_cb(0.95, "🏁 Finalisiere Ergebnisse...")

    df = pd.DataFrame(deduped)
    if df.empty:
        return df

    # Filter by date (for articles where we managed to get a date)
    df_with_date = df[df["date"].notna()].copy()
    df_without_date = df[df["date"].isna()].copy()

    if not df_with_date.empty:
        df_with_date = df_with_date[
            (df_with_date["date"] >= start_date) & (df_with_date["date"] <= end_date)
        ]

    df = pd.concat([df_with_date, df_without_date], ignore_index=True)
    df["title"] = df["title"].fillna("(Kein Titel)")
    df["category"] = df["category"].fillna("Sonstige Artikel")

    return df


# ─── EXCEL LOADING ─────────────────────────────────────────────────────────
def load_excel_urls(uploaded_file) -> list[str]:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Fehler beim Lesen der Excel-Datei: {e}")
            return []

    # Find URL column (flexible: look for 'URL', 'url', 'Link', etc.)
    url_col = None
    for col in df.columns:
        if str(col).strip().lower() in ("url", "link", "artikel", "artikel-url", "artikel url"):
            url_col = col
            break

    if url_col is None:
        # Try to detect by column position (D = index 3 usually)
        if len(df.columns) >= 4:
            url_col = df.columns[3]
        elif len(df.columns) > 0:
            url_col = df.columns[0]

    if url_col is None:
        st.error("Keine URL-Spalte gefunden. Bitte sicherstellen, dass eine Spalte 'URL' vorhanden ist.")
        return []

    urls = df[url_col].dropna().astype(str).tolist()
    urls = [u.strip() for u in urls if u.strip().startswith("http")]

    # Nur zdfheute.de / heute.de Artikel, keine Videos
    urls_filtered = [u for u in urls if is_valid_article_url(u)]
    excluded = len(urls) - len(urls_filtered)
    if excluded > 0:
        st.info(f"ℹ️ {excluded} URLs aus der Excel-Datei wurden ausgeschlossen (Videos, zdf.de, andere Domains).")
    return urls_filtered


# ─── EXPORT ────────────────────────────────────────────────────────────────
def build_export_excel(published: pd.DataFrame, missing: pd.DataFrame) -> bytes:
    import io
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        if not published.empty:
            published.to_excel(writer, sheet_name="Bereits veröffentlicht", index=False)
        if not missing.empty:
            missing.to_excel(writer, sheet_name="Noch nicht veröffentlicht", index=False)
    return buf.getvalue()


# ─── ARTICLE CARD RENDERER ────────────────────────────────────────────────
CAT_COLORS = {
    "Macht und Folgen": "#2563EB",
    "Gut zu wissen": "#059669",
    "Zwischen Tat und Aufklärung": "#7C3AED",
    "Trends, Pop & Kurioses": "#DB2777",
    "Sonstige Artikel": "#6B7280",
}

def render_article_card(art: dict, published: bool):
    dot_cls = "dot-green" if published else "dot-red"
    status_badge = (
        '<span class="badge badge-published">✔ Im WhatsApp-Kanal</span>'
        if published else
        '<span class="badge badge-missing">✘ Nicht veröffentlicht</span>'
    )
    cat = art.get("category", "Sonstige Artikel")
    cat_color = CAT_COLORS.get(cat, "#6B7280")
    date_str = str(art.get("date", "Unbekannt"))
    title = art.get("title", "(Kein Titel)")
    url = art.get("url", "")

    return f"""
    <div class="article-card">
        <div class="article-dot {dot_cls}"></div>
        <div class="article-content">
            <div class="article-title">{title}</div>
            <div class="article-meta">
                <span>📅 {date_str}</span>
                <span style="background:{cat_color}18; color:{cat_color}; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">{cat}</span>
                {status_badge}
            </div>
            <a href="{url}" target="_blank" class="article-url">🔗 {url}</a>
        </div>
    </div>
    """


# ─── MAIN APP ──────────────────────────────────────────────────────────────
def main():
    # ── HEADER ──
    st.markdown("""
    <div class="zdf-header">
        <div class="zdf-header-badge">ZDF Digital · WhatsApp Tool</div>
        <h1>ZDFheute <span class="accent">🧡</span> ZDF Digital<br>WhatsApp Artikel-Checker</h1>
        <p>Prüft, welche Artikel von ZDFheute bereits im WhatsApp-Kanal erschienen sind – und zeigt dir, was noch fehlt.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── INFO BOX ──
    st.markdown("""
    <div class="info-box">
    Dieses Tool gleicht ab, welche Web/App-Artikel von ZDFheute bereits auf dem WhatsApp-Kanal erschienen sind.
    Am Ende zeigt es dir nur die Artikel an, die noch nicht publiziert wurden – gefiltert nach den Kategorien,
    die die User*innen am meisten interessieren:
    <ul>
      <li><strong>🏛️ Macht und Folgen</strong> (Politik, Analysen &amp; internationale Themen): tiefgründige Inhalte, hohe Verweildauer</li>
      <li><strong>💡 Gut zu wissen</strong> (Service, Ratgeber &amp; Wetter): sehr performante Service-Inhalte</li>
      <li><strong>🔍 Zwischen Tat und Aufklärung</strong> (True Crime): Kriminalitätsreportagen &amp; Prozesse</li>
      <li><strong>🎵 Trends, Pop &amp; Kurioses</strong> (Popkultur, Social Media &amp; Kurioses)</li>
      <li><strong>📰 Sonstige Artikel</strong>: alles andere</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # ── UPLOAD + DATE FILTER ROW ──
    col_upload, col_dates = st.columns([3, 2], gap="large")

    with col_upload:
        st.markdown('<div class="card-title">📂 Piano-Excel-Datei hochladen</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "👉 Hier Piano-Excel-Datei hochladen",
            type=["xlsx", "xls"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.success(f"✅ Datei geladen: **{uploaded_file.name}**")

    with col_dates:
        st.markdown('<div class="card-title">📅 Datumsfilter</div>', unsafe_allow_html=True)
        today = date.today()
        default_start = today - timedelta(days=7)

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            start_date = st.date_input("Startdatum", value=default_start, key="start")
        with d_col2:
            end_date = st.date_input("Enddatum", value=today, key="end")

        if start_date > end_date:
            st.error("Startdatum muss vor dem Enddatum liegen.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── RUN BUTTON ──
    run_col, _ = st.columns([2, 5])
    with run_col:
        run_check = st.button("🚀 Artikel-Check starten", use_container_width=True)

    if not run_check:
        if not uploaded_file:
            st.info("⬆️ Bitte lade zuerst die Piano-Excel-Datei hoch und klicke auf **Artikel-Check starten**.")
        else:
            st.info("✅ Datei geladen. Klicke auf **Artikel-Check starten**, um den Abgleich zu beginnen.")
        # Footer
        st.markdown("""
        <div class="zdf-footer">
            Du hast Feedback oder dir ist etwas aufgefallen? <span class="heart">🧡</span>
            Schreibe oder schicke deine Anmerkungen jederzeit direkt an
            <a href="mailto:matthias.schmickl@zdf.de">Matthias Schmickl</a>.
        </div>
        """, unsafe_allow_html=True)
        return

    if not uploaded_file:
        st.error("⚠️ Bitte lade zuerst die Piano-Excel-Datei hoch.")
        return

    # ── LOAD EXCEL ──
    with st.spinner("📊 Lese Excel-Datei..."):
        excel_urls_raw = load_excel_urls(uploaded_file)

    if not excel_urls_raw:
        st.error("Keine gültigen URLs in der Excel-Datei gefunden. Bitte prüfe das Format.")
        return

    excel_urls_norm = set(normalize_url(u) for u in excel_urls_raw)
    st.success(f"📋 **{len(excel_urls_norm)} URLs** aus der Excel-Datei geladen.")

    # ── SCRAPE ZDF ──
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_cb(val: float, msg: str):
        progress_bar.progress(val)
        status_text.info(msg)

    progress_cb(0.02, "🌐 Verbinde mit ZDFheute-Servern...")

    zdf_df = collect_zdf_articles(start_date, end_date, progress_cb=progress_cb)

    progress_bar.progress(1.0)
    status_text.empty()
    progress_bar.empty()

    if zdf_df.empty:
        st.warning("⚠️ Es konnten keine Artikel von ZDFheute gefunden werden. Bitte versuche es später erneut oder prüfe deine Internetverbindung.")
        return

    # ── MATCHING LOGIC ──
    zdf_df["url_norm"] = zdf_df["url"].apply(normalize_url)

    published_mask = zdf_df["url_norm"].isin(excel_urls_norm)
    published_df = zdf_df[published_mask].copy()
    not_published_df = zdf_df[~published_mask].copy()

    # URLs in Excel but NOT found on ZDF at all (might be older articles)
    excel_in_zdf = set(zdf_df["url_norm"].tolist())
    excel_not_scraped = [u for u in excel_urls_raw if normalize_url(u) not in excel_in_zdf]

    # ── STATS ──
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-number stat-orange">{len(excel_urls_norm)}</div>
            <div class="stat-label">Excel-URLs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number stat-orange">{len(zdf_df)}</div>
            <div class="stat-label">ZDF-Artikel<br>gefunden</div>
        </div>
        <div class="stat-card">
            <div class="stat-number stat-green">{len(published_df)}</div>
            <div class="stat-label">Im WhatsApp-<br>Kanal</div>
        </div>
        <div class="stat-card">
            <div class="stat-number stat-red">{len(not_published_df)}</div>
            <div class="stat-label">Noch nicht<br>veröffentlicht</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── EXPORT ──
    export_bytes = build_export_excel(
        published_df[["url", "title", "date", "category"]],
        not_published_df[["url", "title", "date", "category"]],
    )
    st.download_button(
        label="⬇️ Ergebnisse als Excel exportieren",
        data=export_bytes,
        file_name=f"zdf_artikel_check_{start_date}_{end_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs([
        f"✘ Noch nicht veröffentlicht ({len(not_published_df)})",
        f"✔ Bereits im WhatsApp-Kanal ({len(published_df)})",
        f"📋 Alle ZDF-Artikel ({len(zdf_df)})",
    ])

    def render_tab(df: pd.DataFrame, tab_key: str, published: bool):
        if df.empty:
            st.info("Keine Artikel in dieser Kategorie gefunden.")
            return

        # Category filter + search
        filter_col1, filter_col2 = st.columns([2, 3])
        with filter_col1:
            cats = ["Alle Kategorien"] + sorted(df["category"].unique().tolist())
            selected_cat = st.selectbox("🏷️ Kategorie filtern", cats, key=f"cat_{tab_key}")
        with filter_col2:
            search_q = st.text_input("🔍 Suche in Titeln/URLs", placeholder="Suchwort eingeben...", key=f"search_{tab_key}")

        filtered = df.copy()
        if selected_cat != "Alle Kategorien":
            filtered = filtered[filtered["category"] == selected_cat]
        if search_q:
            mask = (
                filtered["title"].str.contains(search_q, case=False, na=False) |
                filtered["url"].str.contains(search_q, case=False, na=False)
            )
            filtered = filtered[mask]

        st.caption(f"Zeige **{len(filtered)}** von **{len(df)}** Artikeln")

        # Sort
        if "date" in filtered.columns:
            filtered = filtered.sort_values("date", ascending=False, na_position="last")

        for _, row in filtered.head(200).iterrows():
            st.markdown(render_article_card(row.to_dict(), published), unsafe_allow_html=True)

        if len(filtered) > 200:
            st.caption(f"_Zeige die ersten 200 Ergebnisse. Exportiere als Excel für die vollständige Liste._")

    with tab1:
        render_tab(not_published_df, tab_key="missing", published=False)

    with tab2:
        render_tab(published_df, tab_key="published", published=True)

    with tab3:
        render_tab(zdf_df, tab_key="all", published=False)

    # ── FOOTER ──
    st.markdown("""
    <div class="zdf-footer">
        Du hast Feedback oder dir ist etwas aufgefallen? <span class="heart">🧡</span>
        Schreibe oder schicke deine Anmerkungen jederzeit direkt an
        <a href="mailto:matthias.schmickl@zdf.de">Matthias Schmickl</a>.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
