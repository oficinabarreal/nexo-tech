# nexo-tech — Flujo de trabajo diario

## Ritmo

**Mañana temprano (o cuando puedas):**

1. Yo ejecuto `fetch_news.py` y `filter_news.py`
2. Te presento el resumen del día:
   - Top 10 noticias rankeadas
   - Las 3 más fuertes con análisis rápido
   - Sugerencia de ángulo para cada una
3. Vos elegís 2-3 noticias y me decís:
   - Cuáles te gustan
   - Si querés agregar tu opinión o si uso la que generé
4. Yo genero los artículos y hago deploy

**Tiempo total de tu parte:** 5-10 minutos
**Tiempo total de mi parte:** 15-20 minutos

## Qué buscamos en cada noticia

1. **Relevancia** — ¿A la gente le importa esto?
2. **Originalidad** — ¿Podemos agregar un ángulo que otros no tienen?
3. **SEO** — ¿La gente busca esto en Google?
4. **Monetización** — ¿Tiene CPC alto? ¿Patrocinadores potenciales?

## Categorías (rotamos para cubrir todo)

| Categoría | Frecuencia | Por qué |
|-----------|------------|---------|
| Tech News | Todos los días | Base del tráfico |
| IA/ML | 3x/semana | Alto CPC, mucha demanda |
| Android | 2x/semana | Tu expertise, nicho fiel |
| Creative Coding | 1x/semana | Diferenciador visual |
| Gadgets | 1x/semana | Afiliados, reviews |

## Métricas que seguimos

- Artículos publicados (meta: 30 para AdSense)
- Views por artículo
- Fuentes de tráfico
- Categorías con mejor rendimiento
- Comentarios/interacciones

## Evolución

**Fase 1 (mes 1-2):** Publicar diario, construir base de contenido
**Fase 2 (mes 3):** Aplicar a Google AdSense
**Fase 3 (mes 4+):** Agregar afiliados, patrocinios
**Fase 4:** Invertir en modelos premium con las ganancias

## Comandos útiles

```bash
# Fetch manual
cd ~/nexo-tech && python scripts/fetch_news.py

# Filtrar
python scripts/filter_news.py

# Generar sitio
python scripts/build_site.py

# Deploy manual
git add -A && git commit -m "Update" && git push
```
