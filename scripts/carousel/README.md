# Generador de carruseles branded (HTML → PNG)

> **Por qué existe:** el template "Tutorial Carousel" de Blotato genera carruseles **feos y
> genéricos** (no respeta la identidad de la marca). Para carruseles branded de verdad
> —al nivel del Brand Kit— renderizamos HTML/CSS propio a PNG y subimos esas imágenes a Blotato.
> Este es el camino preferido para carruseles; el template de Blotato queda como último recurso.

## Flujo

1. **Editá el contenido** en una copia del template:
   `cp scripts/carousel/brand-template.html posts/<slug>.carousel.html`
   Cada `<div class="slide">` es una imagen. El chrome (logo `{b}`, pill, kicker, footer,
   watermark) ya está estilado; reemplazá colores/fuente/logo con los de `branding.md`. Patrones incluidos:
   título, cuerpo, numerado (01/02/03), cierre con highlight.

2. **Renderizá a PNG** (Chrome headless + Puppeteer; la fuente se baja de Google Fonts):
   ```bash
   NODE_PATH="$HOME/node_modules" node scripts/carousel/render.js <la-copia>.html <outDir>
   ```
   Salida: `slide1.png`, `slide2.png`, ... a 2160×2700 (2x, crisp). Requiere Google Chrome
   instalado (override con `CHROME_PATH=...`) y `puppeteer` resoluble (está en `~/node_modules`).

3. **Subí cada PNG a Blotato** para obtener URLs públicas.
   - **Con MCP disponible:** `blotato_create_presigned_upload_url` → `curl -X PUT "<presignedUrl>"
     -H "Content-Type: image/png" --data-binary "@slideN.png"` → usá el `publicUrl`. Un token
     presignado es de un solo uso; si un PUT falla, pedí uno nuevo.
   - **Sin MCP (API directa, sesión sin server MCP de Blotato configurado):** `POST
     https://backend.blotato.com/v2/media` (header `blotato-api-key`) con body
     `{"url": "data:image/png;base64,<contenido en base64>"}` — Blotato re-hostea el data URL y
     devuelve `{"url": "<publicUrl>", "id": "..."}`. Armalo con Python (`base64.b64encode` +
     `urllib.request`), no con curl/shell puro: el base64 de un PNG de carrusel es demasiado
     largo para pasarlo cómodo por `-d` en la shell. `POST /media` con una URL pública normal
     (no data:) también funciona si la imagen ya está alojada en otro lado.
   - ⚠️ **Subí de a UNO y verificá**, no en un loop (se desalinea fácil, y las tools de sandbox
     pueden bloquear loops de curl repetidos silenciosamente). Después de subir, chequeá cada
     URL: `curl -s -o /dev/null -w "%{http_code} %{size_download}" <publicUrl>` — debe dar `200`
     y el tamaño debe coincidir *exacto* con el archivo local (`ls -la slideN.png`). Un tamaño
     que no coincide = orden cruzado o subida rota.

4. **Agendá / actualizá el post** con esos `publicUrl` como `mediaUrls` (orden = orden de slides).
   `blotato.py post --media "url1,url2,..."` o, si ya estaba agendado, `blotato_update_schedule`.

## Notas
- Paleta y fuente salen de `branding.md`. Mantené tu color de acento acotado (~10% máx).
- LinkedIn arma el carrusel/documento con 2–10 imágenes; respetá ese rango.
- Aspecto 4:5 (1080×1350) va bien en feed. Para 1:1 cambiá `.slide` a 1080×1080.
- El logo `{h}` está dibujado por CSS (no necesita el PNG del avatar alojado).
