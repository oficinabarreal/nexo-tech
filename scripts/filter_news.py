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

def generate_batch_summary(items: list) -> list:
    """Genera resúmenes en batch (una sola llamada IA para todos)."""
    system = """Sos el curador de nexo-tech, un blog de tecnología, creatividad y Android.
Redactá resúmenes concisos, con ángulo original, en español.
Sé técnico pero accesible. Conectá la noticia con tendencias."""
    
    # Preparar lista para IA
    lista = ""
    for i, item in enumerate(items, 1):
        lista += f"{i}. {item['title']}\n   Fuente: {item.get('source_name', '?')}\n   Desc: {item['description'][:150]}\n\n"
    
    prompt = f"""Estas son las top {len(items)} noticias de hoy. Para cada una, generá:
- resumen (2 oraciones)
- ángulo de debate (1 pregunta)
- tags (3 keywords)
- trend_score (1-10)

Noticias:
{lista}

Respondé SOLO con JSON válido (array de objetos):
[{{"i":1, "resumen":"...", "angle":"...", "tags":["..."], "trend_score":8}}, ...]"""
    
    response = call_ai(prompt, system)
    
    # Parsear
    import re
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            for d in data:
                idx = d.get("i", 0) - 1
                if 0 <= idx < len(items):
                    items[idx]["summary"] = d.get("resumen", "")
                    items[idx]["angle"] = d.get("angle", "")
                    items[idx]["tags"] = d.get("tags", [])
                    items[idx]["trend_score"] = d.get("trend_score", 5)
    except Exception as e:
        print(f"  [WARN] Parse error: {e}")
        # Fallback: sin IA, usar descripción
        for item in items:
            item["summary"] = item["description"][:300]
            item["angle"] = ""
            item["tags"] = []
            item["trend_score"] = 5
    
    return items

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
    
    # Generar resúmenes con IA (batch)
    print("\nGenerando resúmenes con IA (batch)...")
    curated = generate_batch_summary(top_items)
    
    print(f"\nTop 10 curadas:")
    for i, item in enumerate(curated, 1):
        print(f"  {i}. [{item['category']}] {item['title'][:60]}...")
        print(f"     Resumen: {item.get('summary', '')[:80]}...")
    
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
