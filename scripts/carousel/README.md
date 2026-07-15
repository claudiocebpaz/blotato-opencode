# Branded carousel generator (HTML → PNG)

> **Why it exists:** Blotato's "Tutorial Carousel" template produces **ugly, generic**
> carousels (it doesn't respect the brand's identity). For truly branded carousels
> —at Brand Kit level— we render our own HTML/CSS to PNG and upload those images to Blotato.
> This is the preferred path for carousels; Blotato's template is the last resort.

## Flow

1. **Edit the content** in a copy of the template:
   `cp scripts/carousel/brand-template.html posts/<slug>.carousel.html`
   Each `<div class="slide">` is one image. The chrome (logo `{b}`, pill, kicker, footer,
   watermark) is already styled; replace the colors/font/logo with those from `branding.md`. Included patterns:
   title, body, numbered (01/02/03), closing slide with highlight.

2. **Render to PNG** (headless Chrome + Puppeteer; the font is fetched from Google Fonts):
   ```bash
   NODE_PATH="$HOME/node_modules" node scripts/carousel/render.js <the-copy>.html <outDir>
   ```
   Output: `slide1.png`, `slide2.png`, ... at 2160×2700 (2x, crisp). Requires Google Chrome
   installed (override with `CHROME_PATH=...`) and `puppeteer` resolvable (it's in `~/node_modules`).

3. **Upload each PNG to Blotato** to get public URLs.
   - **With MCP available:** `blotato_create_presigned_upload_url` → `curl -X PUT "<presignedUrl>"
     -H "Content-Type: image/png" --data-binary "@slideN.png"` → use the `publicUrl`. A presigned
     token is single-use; if a PUT fails, request a new one.
   - **Without MCP (direct API, session without Blotato's MCP server configured):** `POST
     https://backend.blotato.com/v2/media` (header `blotato-api-key`) with body
     `{"url": "data:image/png;base64,<base64 content>"}` — Blotato re-hosts the data URL and
     returns `{"url": "<publicUrl>", "id": "..."}`. Build it with Python (`base64.b64encode` +
     `urllib.request`), not with plain curl/shell: the base64 of a carousel PNG is too
     long to pass comfortably via `-d` in the shell. `POST /media` with a normal public URL
     (not data:) also works if the image is already hosted elsewhere.
   - ⚠️ **Upload ONE at a time and verify**, not in a loop (it desyncs easily, and sandbox tools
     may silently block repeated curl loops). After uploading, check each
     URL: `curl -s -o /dev/null -w "%{http_code} %{size_download}" <publicUrl>` — it should return `200`
     and the size should match the local file *exactly* (`ls -la slideN.png`). A size
     that doesn't match = crossed order or a broken upload.

4. **Schedule / update the post** with those `publicUrl`s as `mediaUrls` (order = slide order).
   `blotato.py post --media "url1,url2,..."` or, if it was already scheduled, `blotato_update_schedule`.

## Notes
- Palette and font come from `branding.md`. Keep your accent color limited (~10% max).
- LinkedIn builds the carousel/document from 2–10 images; respect that range.
- 4:5 aspect ratio (1080×1350) works well in feed. For 1:1, change `.slide` to 1080×1080.
- The `{h}` logo is drawn with CSS (it doesn't need the hosted avatar PNG).
