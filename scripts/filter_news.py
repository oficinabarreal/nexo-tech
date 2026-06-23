#!/usr/bin/env python3
"""
nexo-tech: Filtrado y curación de noticias por IA
Clasifica, rankea y genera resúmenes con ángulo original
"""
import json
import os
import sys
from datetime import datetime
from urllib.request import Request, urlopen

# ─── Config ──────────────────────────────────────────────────────────────────

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "z-ai/glm-5.1"

# ─── Categorías ──────────────────────────────────────────────────────────────

CATEGORIAS = {
    "tech_news": ["hardware", "software", "startup", "funding", "launch", "release"],
    "ai_ml": ["ai", "artificial intelligence", "machine learning", "llm", "gpt", "neural"],
    "android": ["android", "google pixel", "samsung", "one ui", "termux", "mobile"],
    "creative": ["webgl", "three.js", "creative coding", "generative art", "shader", "svg"],
    "gadgets": ["gadget", "review", "unboxing", "comparison", "benchmark", "test"],
}

# ─── IA ──────────────────────────────────────────────────────────────────────

def call_ai(prompt: str, system: str = "") -> str:
    """Llama a NVIDIA API."""
    if not NVIDIA_API_KEY:
        return "[Sin API key]"
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }).encode()
    
    req = Request(NVIDIA_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {NVIDIA_API_KEY}")
    
    try:
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error: {e}]"

# ─── Filtrado ────────────────────────────────────────────────────────────────

def classify_item(item: dict) -> dict:
    """Clasifica un item por categoría y relevancia."""
    text = (item["title"] + " " + item["description"]).lower()
    
    # Scoring por categoría
    scores = {}
    for cat, keywords in CATEGORIAS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[cat] = score
    
    # Categoría principal
    main_cat = max(scores, key=scores.get) if any(scores.values()) else "tech_news"
    
    # Score de relevancia (0-10)
    relevance = min(10, sum(scores.values()) * 2)
    
    # Bonus por fuentes premium
    premium_sources = {"techcrunch", "theverge", "arstechnica", "wired"}
    if item.get("source_name") in premium_sources:
        relevance = min(10, relevance + 2)
    
    item["category"] = main_cat
    item["scores"] = scores
    item["relevance"] = relevance
    
    return item

def filter_and_rank(items: list, top_n: int = 10) -> list:
    """Filtra y rankea noticias."""
    print("Clasificando noticias...")
    
    classified = [classify_item(item) for item in items]
    
    # Ordenar por relevancia
    ranked = sorted(classified, key=lambda x: x["relevance"], reverse=True)
    
    # Tomar top N
    top = ranked[:top_n]
    
    print(f"Top {top_n} seleccionadas:")
    for i, item in enumerate(top, 1):
        print(f"  {i}. [{item['category']}] {item['title'][:60]}... (score: {item['relevance']})")
    
    return top

# ─── Generación de resumen ──────────────────────────────────────────────────

def generate_summary(item: dict) -> dict:
    """Genera resumen con ángulo original usando IA."""
    system = """Sos el curador de nexo-tech, un blog de tecnología, creatividad y Android.
Redactá resúmenes concisos, con ángulo original, en español.
Sé técnico pero accesible. Conectá la noticia con tendencias.
Formato: 2-3 párrafos cortos. Sin titular (ya lo tenemos)."""
    
    prompt = """Noticia: {title}
Fuente: {source}
Descripción original: {description}

Generá:
1. Un resumen de 2-3 párrafos con ángulo original
2. Un "ángulo de debate" (pregunta abierta para los lectores)
3. Tags: 3-5 tags relevantes
4. Score de tendencia (1-10)

Formato JSON:
{{"resumen": "...", "angle": "...", "tags": ["...", "..."], "trend_score": 8}}""".format(
        title=item["title"],
        source=item.get("source_name", "unknown"),
        description=item["description"]
    )
    
    response = call_ai(prompt, system)
    
    # Parsear JSON de la respuesta
    try:
        # Buscar JSON en la respuesta
        import re
        json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            item["summary"] = data.get("resumen", response[:300])
            item["angle"] = data.get("angle", "")
            item["tags"] = data.get("tags", [])
            item["trend_score"] = data.get("trend_score", 5)
        else:
            item["summary"] = response[:500]
            item["angle"] = ""
            item["tags"] = []
            item["trend_score"] = 5
    except:
        item["summary"] = response[:500]
        item["angle"] = ""
        item["tags"] = []
        item["trend_score"] = 5
    
    return item

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=== nexo-tech: Filtrado IA ===\n")
    
    # Cargar noticias raw
    try:
        with open("content/raw_news.json") as f:
            data = json.load(f)
            items = data["items"]
    except FileNotFoundError:
        print("Error: content/raw_news.json no existe. Corré fetch_news.py primero.")
        sys.exit(1)
    
    print(f"Cargadas {len(items)} noticias\n")
    
    # Filtrar y rankear
    top_items = filter_and_rank(items, top_n=10)
    
    # Generar resúmenes con IA
    print("\nGenerando resúmenes con IA...")
    curated = []
    for i, item in enumerate(top_items, 1):
        print(f"  {i}/10: {item['title'][:50]}...")
        item = generate_summary(item)
        curated.append(item)
    
    # Guardar curado
    output = {
        "curated_at": datetime.utcnow().isoformat(),
        "total": len(curated),
        "items": curated,
    }
    
    with open("content/curated_news.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nGuardado en content/curated_news.json ({len(curated)} items curados)")

if __name__ == "__main__":
    main()
