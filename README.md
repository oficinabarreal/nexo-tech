# nexo-tech

**Blog de tecnología, creatividad y Android** — contenido curado por IA, visualizaciones interactivas, todo desde un teléfono con costo $0.

## Qué es

Un sitio de noticias y artículos tech donde Hermes (big-pickle) actúa como curador:
1. Fetch de noticias de múltiples fuentes (RSS)
2. Filtrado por relevancia y tendencia (NVIDIA GLM-5.1)
3. Generación de resúmenes con ángulo original
4. Visualizaciones interactivas (Chart.js + SVG)
5. Publicación automática en GitHub Pages

## Nichos

- **Tech News** — noticias de hardware, software, IA, gadgets
- **Creative Coding** — arte generativo, demos, tutoriales
- **Android/Termux** — desarrollo mobile, trucos, herramientas
- **Visualizaciones** — gráficos interactivos de datos tech

## Stack

| Capa | Tecnología |
|------|-----------|
| Hosting | GitHub Pages ($0) |
| Backend | Python scripts + GitHub Actions |
| IA | NVIDIA GLM-5.1 (gratis) |
| Frontend | HTML + CSS + Chart.js + SVG |
| Fuentes | RSS feeds (TechCrunch, The Verge, etc.) |

## Estructura

```
nexo-tech/
├── scripts/
│   ├── fetch_news.py      # Fetch de RSS feeds
│   ├── filter_news.py     # Filtrado IA + scoring
│   ├── generate_post.py   # Generación de artículo
│   └── build_site.py      # Generador estático
├── content/               # Artículos generados
├── templates/             # HTML templates
├── assets/
│   ├── css/               # Estilos
│   ├── js/                # Chart.js, interactivos
│   └── img/               # Imágenes generadas
├── .github/workflows/
│   └── daily-post.yml     # Pipeline diario
└── index.html             # Homepage
```

## Flujo diario

```
06:00 UTC — GitHub Actions se dispara
    ↓
fetch_news.py — Lee 10+ RSS feeds
    ↓
filter_news.py — IA clasifica y rankea (top 5)
    ↓
generate_post.py — Redacta artículo + gráfico
    ↓
build_site.py — Genera HTML estático
    ↓
git push — Deploy automático a GitHub Pages
```

## Monetización

- Google AdSense (después de 30+ artículos originales)
- Patrocinios de herramientas dev
- Afiliados de hardware/gadgets
