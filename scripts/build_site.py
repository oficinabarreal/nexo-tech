#!/usr/bin/env python3
"""
nexo-tech: Generador de sitio estático
Genera HTML limpio, rápido, optimizado para SEO y AdSense
"""
import json
import os
import re
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────────

SITE_NAME = "nexo-tech"
SITE_DESC = "Tecnología, creatividad y Android — curado por IA"
SITE_URL = "https://oficinabarreal.github.io/nexo-tech"
OUTPUT_DIR = "docs"  # GitHub Pages lee de /docs

# ─── Templates ───────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | nexo-tech</title>
    <meta name="description" content="{description}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <link rel="stylesheet" href="assets/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <nav class="nav">
        <a href="/" class="logo">nexo<span>tech</span></a>
        <div class="nav-links">
            <a href="/#tech">Tech</a>
            <a href="/#ai">IA</a>
            <a href="/#creative">Creative</a>
            <a href="/#android">Android</a>
        </div>
    </nav>
    
    <main>
        {content}
    </main>
    
    <footer>
        <p>Hecho con costo $0 desde un Android con Termux</p>
        <p>Contenido curado por <a href="https://github.com/oficinabarreal">Hermes Agent</a></p>
    </footer>
    
    <script src="assets/js/main.js"></script>
</body>
</html>"""

ARTICLE_TEMPLATE = """
<article class="article">
    <header>
        <span class="category category-{category}">{category_label}</span>
        <h1>{title}</h1>
        <div class="meta">
            <span>📅 {date}</span>
            <span>📰 {source}</span>
            <span>🔥 Tendencia: {trend}/10</span>
        </div>
    </header>
    
    <div class="content">
        {summary}
        
        {chart_html}
        
        <div class="angle">
            <h3>💬 Ángulo de debate</h3>
            <p>{angle}</p>
        </div>
        
        <div class="tags">
            {tags_html}
        </div>
        
        <a href="{link}" target="_blank" class="read-more">
            Leer noticia original →
        </a>
    </div>
</article>
"""

CARD_TEMPLATE = """
<div class="card" data-category="{category}">
    <div class="card-header">
        <span class="category category-{category}">{category_label}</span>
        <span class="trend">🔥 {trend}</span>
    </div>
    <h2><a href="{url}">{title}</a></h2>
    <p>{description}</p>
    <div class="card-footer">
        <span>{source}</span>
        <span>{date}</span>
    </div>
</div>
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────

CATEGORY_LABELS = {
    "tech_news": "Tech",
    "ai_ml": "IA/ML",
    "android": "Android",
    "creative": "Creative",
    "gadgets": "Gadgets",
}

def make_chart_html(items: list) -> str:
    """Genera gráfico de distribución por categoría."""
    cats = {}
    for item in items:
        cat = item.get("category", "tech_news")
        cats[cat] = cats.get(cat, 0) + 1
    
    labels = json.dumps([CATEGORY_LABELS.get(k, k) for k in cats.keys()])
    data = json.dumps(list(cats.values()))
    
    return f"""
    <div class="chart-container">
        <canvas id="categoryChart"></canvas>
    </div>
    <script>
    new Chart(document.getElementById('categoryChart'), {{
        type: 'doughnut',
        data: {{
            labels: {labels},
            datasets: [{{
                data: {data},
                backgroundColor: ['#ff0044', '#00ccff', '#00ff88', '#ffaa00', '#aa44ff']
            }}]
        }},
        options: {{
            responsive: true,
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ color: '#ccc' }} }}
            }}
        }}
    }});
    </script>
    """

def make_tags_html(tags: list) -> str:
    """Genera HTML de tags."""
    return " ".join(f'<span class="tag">{t}</span>' for t in tags)

# ─── Generadores ─────────────────────────────────────────────────────────────

def generate_homepage(items: list) -> str:
    """Genera la homepage."""
    # Cards por categoría
    cards_html = ""
    for item in items:
        cat = item.get("category", "tech_news")
        url = f"articles/{item.get('slug', 'article')}.html"
        
        cards_html += CARD_TEMPLATE.format(
            category=cat,
            category_label=CATEGORY_LABELS.get(cat, cat),
            trend=item.get("trend_score", 5),
            url=url,
            title=item["title"],
            description=item.get("summary", item["description"])[:200],
            source=item.get("source_name", ""),
            date=item.get("date", "")[:16],
        )
    
    chart = make_chart_html(items)
    
    content = f"""
    <section class="hero">
        <h1>nexo<span>tech</span></h1>
        <p>Tecnología, creatividad y Android — curado por IA</p>
        <p class="subtitle">Hecho desde un teléfono Android con costo $0</p>
    </section>
    
    <section class="stats">
        <div class="stat">
            <div class="num">{len(items)}</div>
            <div class="label">Artículos hoy</div>
        </div>
        <div class="stat">
            <div class="num">{len(set(i.get('category') for i in items))}</div>
            <div class="label">Categorías</div>
        </div>
        <div class="stat">
            <div class="num">{len(set(i.get('source_name') for i in items))}</div>
            <div class="label">Fuentes</div>
        </div>
    </section>
    
    <section class="chart-section">
        <h2>📊 Distribución por categoría</h2>
        {chart}
    </section>
    
    <section class="articles">
        <h2>🔥 Últimas noticias</h2>
        <div class="card-grid">
            {cards_html}
        </div>
    </section>
    """
    
    return HTML_TEMPLATE.format(
        title="Inicio",
        description=SITE_DESC,
        content=content,
    )

def generate_article_page(item: dict) -> str:
    """Genera página de artículo individual."""
    cat = item.get("category", "tech_news")
    
    content = ARTICLE_TEMPLATE.format(
        category=cat,
        category_label=CATEGORY_LABELS.get(cat, cat),
        title=item["title"],
        date=item.get("date", "")[:16],
        source=item.get("source_name", ""),
        trend=item.get("trend_score", 5),
        summary=item.get("summary", item["description"]),
        chart_html="",  # TODO: chart por artículo
        angle=item.get("angle", "¿Qué opinás?"),
        tags_html=make_tags_html(item.get("tags", [])),
        link=item["link"],
    )
    
    return HTML_TEMPLATE.format(
        title=item["title"],
        description=item.get("summary", item["description"])[:160],
        content=content,
    )

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=== nexo-tech: Generador de sitio ===\n")
    
    # Cargar noticias curadas
    try:
        with open("content/curated_news.json") as f:
            data = json.load(f)
            items = data["items"]
    except FileNotFoundError:
        print("Error: content/curated_news.json no existe.")
        sys.exit(1)
    
    # Crear directorios
    os.makedirs(f"{OUTPUT_DIR}/articles", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/assets/css", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/assets/js", exist_ok=True)
    
    # Generar homepage
    homepage = generate_homepage(items)
    with open(f"{OUTPUT_DIR}/index.html", "w") as f:
        f.write(homepage)
    print("  ✓ index.html")
    
    # Generar artículos individuales
    for item in items:
        slug = re.sub(r'[^a-z0-9]+', '-', item["title"].lower())[:50]
        item["slug"] = slug
        
        article_html = generate_article_page(item)
        with open(f"{OUTPUT_DIR}/articles/{slug}.html", "w") as f:
            f.write(article_html)
        print(f"  ✓ articles/{slug}.html")
    
    print(f"\nSitio generado en {OUTPUT_DIR}/")
    print(f"Total: 1 homepage + {len(items)} artículos")

if __name__ == "__main__":
    main()
