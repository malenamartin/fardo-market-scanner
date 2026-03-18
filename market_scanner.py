#!/usr/bin/env python3
"""
market_scanner.py
Escanea noticias del sector (RSS feeds) y titulares de competidores.
- Guarda reporte_mercado.txt  (siempre el más reciente)
- Guarda reportes/reporte_mercado_YYYY-MM-DD.txt (histórico)
- Devuelve exit-code 1 si ocurre un error crítico (para GitHub Actions)
"""

import sys
import os
import feedparser
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from pathlib import Path

# ── Configuración ────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Search Engine Journal": "https://www.searchenginejournal.com/feed/",
    "TechCrunch":            "https://techcrunch.com/feed/",
    "Product Hunt":          "https://www.producthunt.com/feed",
    "The Verge – AI":        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
}

COMPETITORS = {
    "Profound (tryprofound.com)": "https://www.tryprofound.com",
    "Semrush Blog":               "https://www.semrush.com/blog/",
    "Ahrefs Blog":                "https://ahrefs.com/blog/",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TOP_N        = 3
LATEST_FILE  = "reporte_mercado.txt"
HISTORY_DIR  = Path("reportes")


# ── Helpers ──────────────────────────────────────────────────────────────────
def divider(char="─", width=65):
    return char * width


def section(title):
    return f"\n{'═' * 65}\n  {title}\n{'═' * 65}"


def fetch_rss(name, url, n=TOP_N):
    """Descarga y parsea un RSS feed. Usa requests para evitar SSL issues en macOS."""
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, verify=False)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:n]:
            results.append({
                "title": entry.get("title", "(sin título)").strip(),
                "link":  entry.get("link", ""),
                "date":  entry.get("published", entry.get("updated", "")),
            })
        if not feed.entries:
            results.append({"title": "[Feed vacío o sin entradas accesibles]", "link": url, "date": ""})
    except requests.exceptions.HTTPError as e:
        results.append({"title": f"[HTTP {e.response.status_code}]", "link": url, "date": ""})
    except Exception as e:
        results.append({"title": f"[Error al leer feed: {e}]", "link": "", "date": ""})
    return results


def fetch_competitor_headlines(name, url, n=TOP_N):
    """Extrae titulares de la página del competidor usando BeautifulSoup."""
    headlines = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        seen = set()
        for article in soup.find_all("article", limit=10):
            for tag in ("h1", "h2", "h3"):
                heading = article.find(tag)
                if heading:
                    text = heading.get_text(strip=True)
                    if text and text not in seen and len(text) > 10:
                        seen.add(text)
                        link_tag = article.find("a", href=True)
                        headlines.append({
                            "title": text,
                            "link":  link_tag["href"] if link_tag else url,
                        })
                    break
            if len(headlines) >= n:
                break

        if len(headlines) < n:
            for tag in soup.find_all(["h2", "h3"], limit=30):
                text = tag.get_text(strip=True)
                if text and text not in seen and len(text) > 10:
                    seen.add(text)
                    link_tag = tag.find("a", href=True) or tag.find_parent("a")
                    headlines.append({
                        "title": text,
                        "link":  link_tag["href"] if link_tag else url,
                    })
                if len(headlines) >= n:
                    break

    except requests.exceptions.HTTPError as e:
        headlines.append({"title": f"[HTTP {e.response.status_code} – bloqueado o redirigido]", "link": url})
    except requests.exceptions.ConnectionError:
        headlines.append({"title": "[Sin conexión o dominio no resuelto]", "link": url})
    except Exception as e:
        headlines.append({"title": f"[Error: {e}]", "link": url})

    return headlines[:n]


# ── Construcción del reporte ──────────────────────────────────────────────────
def build_report(date_str: str) -> str:
    lines = []
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    lines.append("╔" + "═" * 63 + "╗")
    lines.append("║" + "  REPORTE DE MERCADO – MARKET SCANNER".center(63) + "║")
    lines.append("║" + f"  Generado: {now}".center(63) + "║")
    lines.append("╚" + "═" * 63 + "╝")

    # ── Sección 1: RSS Feeds ─────────────────────────────────────────────────
    lines.append(section("1.  NOTICIAS DESTACADAS DEL SECTOR  (RSS Feeds)"))

    for feed_name, feed_url in RSS_FEEDS.items():
        lines.append(f"\n  [{feed_name}]")
        lines.append(f"  {feed_url}")
        lines.append("  " + divider("·", 61))
        items = fetch_rss(feed_name, feed_url)
        if not items:
            lines.append("  (No se encontraron entradas)")
        for i, item in enumerate(items, 1):
            lines.append(f"  {i}. {item['title']}")
            if item["date"]:
                lines.append(f"     Fecha : {item['date']}")
            if item["link"]:
                lines.append(f"     URL   : {item['link']}")

    # ── Sección 2: Competidores ──────────────────────────────────────────────
    lines.append(section("2.  TITULARES RECIENTES DE COMPETIDORES"))

    for comp_name, comp_url in COMPETITORS.items():
        lines.append(f"\n  [{comp_name}]")
        lines.append(f"  {comp_url}")
        lines.append("  " + divider("·", 61))
        items = fetch_competitor_headlines(comp_name, comp_url)
        if not items:
            lines.append("  (No se pudieron extraer titulares)")
        for i, item in enumerate(items, 1):
            lines.append(f"  {i}. {item['title']}")
            if item["link"] and item["link"] != comp_url:
                link = item["link"]
                if not link.startswith("http"):
                    link = urljoin(comp_url, link)
                lines.append(f"     URL   : {link}")

    # ── Pie ──────────────────────────────────────────────────────────────────
    lines.append("\n" + "═" * 65)
    lines.append(f"  Fin del reporte  ·  {now}")
    lines.append("═" * 65 + "\n")

    return "\n".join(lines)


# ── Guardado de archivos ──────────────────────────────────────────────────────
def save_report(report: str, date_str: str):
    # 1. Siempre sobreescribe el archivo "latest"
    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓  Guardado: {LATEST_FILE}")

    # 2. Histórico con fecha en carpeta /reportes
    HISTORY_DIR.mkdir(exist_ok=True)
    history_file = HISTORY_DIR / f"reporte_mercado_{date_str}.txt"
    with open(history_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✓  Histórico: {history_file}")


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Escaneando feeds y competidores… ({date_str})\n")

    try:
        report = build_report(date_str)
        save_report(report, date_str)
        print("\n" + report)
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
