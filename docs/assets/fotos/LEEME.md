# Fotos de las visitas a los territorios

Pon aquí tus mejores fotos, en la carpeta de cada territorio:

| Carpeta | Uso |
|---|---|
| `portada/` | Foto principal de la escena 01 (se usa la primera por orden alfabético) |
| `cali/`, `tumaco/`, `buenaventura/`, `francisco-pizarro/`, `otros/` | Galería y escena de experiencia situada |

## Antes de publicar: 3 reglas

1. **Consentimiento.** Una foto sale en el sitio solo si en `fotos.json` tiene `"consent": true`. Si hay personas reconocibles, confirma su permiso por escrito (en menores, el de su acudiente). En la duda, usa fotos de espacios, manos, paisaje o personas de espaldas.
2. **Descripción.** Cada foto necesita `"alt"` (qué se ve, para personas que usan lector de pantalla) y de preferencia `"caption"` y `"credit"`.
3. **Sin ubicación oculta.** Las fotos del celular guardan las coordenadas GPS. Usa `python tools/prepare_photos.py` (ver el README): borra esos datos y reduce el tamaño.

## Cómo agregar una foto

1. Copia las fotos originales a `fotos_originales/` (esa carpeta no se sube a GitHub).
2. Ejecuta `python tools/prepare_photos.py cali` (cambia `cali` por el territorio).
3. Abre `assets/fotos/fotos.json`: el script añade cada foto con `"consent": false`. Escribe `alt`, `caption`, `credit` y cambia a `true` solo si tienes permiso.
4. Ejecuta `python build.py` y abre `docs/index.html`.

Consejo: formato horizontal para la portada (mínimo 1600 px de ancho), JPG, menos de 1,5 MB cada una.
