#!/usr/bin/env python3
"""
nexo-tech: Fetch de noticias desde múltiples RSS feeds
Sin API keys, sin costo, 100% local
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from html import unescape
from urllib.request import Request, urlopen
from urllib.error import URLError

# ─── Feeds RSS ───────────────────────────────────────────────────────────────

FEEDS = {
    # Tech General
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "arstechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "wired": "https://www.wired.com/feed/rss",
    "engadget": "https://www.engadget.com/rss.xml",
    
    # AI / Machine Learning
    "venturebeat_ai": "https://venturebeat.com/category/ai/feed/",
    "the_next_web_ai": "https://thenextweb.com/feed",
    
    # Android / Mobile
    "android_police": "https://www.androidpolice.com/feed/",
    "9to5google": "https://9to5google.com/feed/",
    
    # Creative Coding
    "codrops": "https://tympanus.net/codrops/feed/",
    "css_tricks": "https://css-tricks.com/feed/",
    
    # Spanish
    "xataka": "https://www.xataka.com/feed",
    "genbeta": "https://www.genbeta.com/feed",
}

# ─── Parse RSS ───────────────────────────────────────────────────────────────

def fetch_feed(url: str, timeout: int = 15) -> list:
    """Fetch y parsea un feed RSS."""
    try:
        req = Request(url, headers={"User-Agent": "nexo-tech/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        
        root = ET.fromstring(data)
        items = []
        
        # Handle Atom y RSS
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        # RSS 2.0
        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "").strip()
            pubdate = item.findtext("pubDate", "").strip()
            
            if title and link:
                items.append({
                    "title": unescape(re.sub(r"<[^>]+>", "", title)),
                    "link": link,
                    "description": unescape(re.sub(r"<[^>]+>", "", desc))[:500],
                    "date": pubdate,
                    "source": url,
                })
        
        # Atom
        if not items:
            for entry in root.findall(".//atom:entry", ns):
                title = entry.findtext("atom:title", "", ns).strip()
                link_el = entry.find("atom:link", ns)
                link = link_el.get("href", "") if link_el is not None else ""
                summary = entry.findtext("atom:summary", "", ns).strip()
                published = entry.findtext("atom:published", "", ns).strip()
                
                if title and link:
                    items.append({
                        "title": unescape(re.sub(r"<[^>]+>", "", title)),
                        "link": link,
                        "description": unescape(re.sub(r"<[^>]+>", "", summary))[:500],
                        "date": published,
                        "source": url,
                    })
        
        return items
    
    except Exception as e:
        print(f"  [WARN] Error fetching {url}: {e}", file=sys.stderr)
        return []

def fetch_all() -> list:
    """Fetch todas las fuentes."""
    all_items = []
    
    for name, url in FEEDS.items():
        print(f"  Fetching {name}...")
        items = fetch_feed(url)
        print(f"    → {len(items)} items")
        
        for item in items:
            item["source_name"] = name
        
        all_items.extend(items)
    
    # Deduplicar por título similar
    seen = set()
    unique = []
    for item in all_items:
        key = item["title"].lower()[:50]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    
    print(f"\n  Total: {len(all_items)} items → {len(unique)} únicos")
    return unique

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=== nexo-tech: Fetch de noticias ===\n")
    
    items = fetch_all()
    
    # Guardar raw
    output = {
        "fetched_at": datetime.utcnow().isoformat(),
        "total": len(items),
        "items": items,
    }
    
    with open("content/raw_news.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nGuardado en content/raw_news.json ({len(items)} items)")
    return items

if __name__ == "__main__":
    main()
