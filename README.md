# Narrativa digital multimodal: brecha digital y racismo algorítmico

Sitio web editorial (HTML + CSS + un poco de JavaScript opcional) generado con Python a partir de un solo
archivo de contenido. Producto de la **Actividad 1.1 — Curaduría y producción de una narrativa digital
multimodal** (Narrativas Digitales, Maestría en Comunicación, Culturas Digitales y Visualización de Datos,
Universidad Santo Tomás).

**Qué incluye**

- 12 escenas, una pregunta por escena, con barra de progreso, navegación activa y animaciones al hacer scroll.
- **Cintas en movimiento (marquee)** con conceptos y preguntas clave; se pausan al pasar el cursor y se detienen
  si la persona activa "reducir movimiento".
- **Galería de fotos de los territorios** con ampliación y una cinta de fotos. Se arma sola con lo que pongas en `assets/fotos/`.
- Seis fuentes curadas en tarjetas desplegables (`<details>`, sin JavaScript).
- Responsivo, accesible (enlace de salto, foco visible, textos alternativos), imprimible.
- Sin dependencias para construir el sitio: Python 3.8+ (biblioteca estándar). Pillow solo para preparar fotos.

## Estructura

```
├── content.json            # TODO el texto, enlaces y cintas
├── build.py                # genera docs/index.html
├── check.py                # lista de verificación previa a la entrega
├── tools/prepare_photos.py # limpia (sin GPS), reduce y registra tus fotos
├── fotos_originales/       # AQUÍ copias las fotos tal como salen del celular (no se sube a GitHub)
├── assets/
│   ├── style.css  main.js
│   ├── img/                # mapa, capturas, miniatura (gráficos, no fotos de campo)
│   └── fotos/
│       ├── portada/  cali/  tumaco/  buenaventura/  francisco-pizarro/  otros/
│       ├── fotos.json      # alt, pie de foto, crédito y consentimiento de cada foto
│       └── LEEME.md
└── docs/                   # sitio generado (para GitHub Pages)
```

## Cómo agregar tus fotos de las visitas

1. Copia las fotos a `fotos_originales/`.
2. `pip install pillow` (una sola vez) y luego `python tools/prepare_photos.py cali`
   (usa `portada`, `tumaco`, `buenaventura`, `francisco-pizarro` u `otros` según corresponda).
   Esto **borra la ubicación GPS**, reduce el peso y copia la foto a `assets/fotos/cali/`.
3. En `assets/fotos/fotos.json` escribe `alt` (qué se ve), `caption` y `credit`, y cambia `consent` a `true`
   **solo si tienes permiso** de quienes aparecen (en menores, de su acudiente).
4. `python build.py` y abre `docs/index.html`.

Una foto **no se publica** si le falta `consent: true` o `alt`. `build.py` te avisa cuáles quedaron fuera.
La primera foto de `portada/` se usa como imagen de la escena 01.

Consejos: portada en horizontal (mínimo 1600 px de ancho); mezcla territorio, prácticas digitales, educación,
conectividad y producción cultural, y evita mostrar a las comunidades solo desde la carencia o la violencia.

## Uso

```bash
python build.py            # construye docs/index.html
python check.py            # palabras, [pendientes], fotos, GPS, enlaces
python build.py --strict   # falla si quedan [marcadores] sin completar
```

## Qué debes completar tú

1. **Análisis (escena 09):** tu texto de 400–500 palabras, escrito con tus palabras y con citas en el texto.
2. **Justificación de cada fuente** (escena `voces`): qué es, pertinencia, confiabilidad, voz y límite.
3. **Imágenes de `assets/img/`:** `02_mapa_pacifico.png`, `06_coded_bias_thumbnail.jpg`, `10_onlife_afro_interface.png`.
4. **Nota de uso de IA** (escena `fuentes`): escribe exactamente lo que hiciste.
5. **Verifica las cifras** de la escena `dato` (24 % y 79 %) en la fuente original.

Edita las cintas en `content.json` (escenas de tipo `marquee` y la lista `marquee` de la escena `gancho`).

## Publicar en GitHub Pages

1. Sube el repositorio (incluye `docs/`).
2. *Settings → Pages → Deploy from a branch →* rama `main`, carpeta `/docs`.
3. Pega el enlace publicado en el documento de entrega.

## Ética y privacidad

- Las fotos del celular guardan la ubicación exacta: usa siempre `prepare_photos.py`.
- La escena 08 usa solo una síntesis anonimizada de los registros de campo; no pongas edad exacta, barrio, voz ni rostro.
- Usa imágenes propias, institucionales o con licencia, y acredítalas. *Coded Bias* se enlaza; no se redistribuye.
- `.gitignore` excluye `fotos_originales/`, `campo_privado/` y audios.

## Licencia

Elige una licencia para el código (por ejemplo MIT) y otra para el contenido (por ejemplo CC BY 4.0).

## Autoría

Mackmot Pachotto Ambrose · Universidad Santo Tomás · 2026.
