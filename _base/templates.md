# Catálogo de templates visuales de Blotato

> Blotato genera los visuales. Claude elige el template y arma los `inputs` (inyectando
> los colores/fuente de la marca desde su `branding.md`). Endpoint: `POST /videos/from-templates`.
> Poléalo hasta `done` y usá `imageUrls` / `mediaUrl` como media del post.
> Para descubrir TODOS los templates y sus inputs en vivo: `GET /videos/templates?fields=id,name,description,inputs`.

## Modelo de imagen por defecto (control de costo)
El modelo de imagen manda el costo: va de **1 crédito** (Flux Schnell) a **50** (Nano Banana Pro) por imagen.
- **Default recomendado:** `fal-ai/imagen4/preview/fast` (7 créditos) — buen balance.
- **Barato para pruebas:** `replicate/black-forest-labs/flux-schnell` (1 crédito).
- **Texto legible dentro de la imagen:** modelos Nano Banana (15–50).
- Reservar los caros para piezas destacadas. URLs subidas (no generadas) no gastan créditos.

## Templates elegidos para este proyecto

### Instagram Carousel Slideshow — `53cfec04-2500-41cf-8cc1-ba670d2c341a`
Genera 1 imagen IA por slide (imágenes puras, sin texto encima). Campo de modelo: `model`.
```json
{ "templateId": "53cfec04-2500-41cf-8cc1-ba670d2c341a",
  "inputs": {
    "slidePrompts": ["prompt slide 1", "prompt slide 2", "..."],
    "model": "nano-banana-pro",
    "aspectRatio": "4:5" } }
```
`slidePrompts`: 1–10, cada uno 5–1000 chars. `aspectRatio`: 1:1, 4:5, 5:4, 16:9, 9:16.

### Image Slideshow con texto encima — `5903b592-1255-43b4-b9ac-f8ed7cbf6a5f`
Imágenes (subidas O generadas) + texto por slide. **El mejor para carruseles con mensaje.**
```json
{ "templateId": "/base/v2/image-slideshow/5903b592-1255-43b4-b9ac-f8ed7cbf6a5f/v1",
  "inputs": {
    "slides": [ { "imageSource": "URL o prompt IA", "textOverlay": "≤300 chars" } ],
    "aiImageModel": "fal-ai/imagen4/preview/fast",
    "textPosition": "bottom", "textStyle": "modern", "textColor": "#000000",
    "aspectRatio": "4:5", "transition": "fade" } }
```

### Tutorial Carousel (minimalista) — `2491f97b-1b47-4efa-8b96-8c651fa7b3d5`
Carrusel estructurado: título + items numerados + CTA + slide de perfil. **Ideal para LinkedIn.**
Acepta branding: `backgroundColor`, `borderColor`, `textColor`, `font`, `profileImage`.
Campos req: `mainTitle`, `authorName`, `ctaButtonText`, `contentItems[]`, `ctaTitle`, `ctaActions[]`,
`profileName`, `profileTitle`, `profileDescription`, `profileCta`.

### Quote Card centrada — `9f4e66cd-b784-4c02-b2ce-e6d0765fd4c0`
Lo más simple. `inputs: { "quotes": ["texto 10–350 chars"] }` (1–20 quotes → 1 card c/u).

### Infografía (ej. Newspaper) — `07a5b5c5-387c-49e3-86b1-de822cd2dfc7`
Imagen única generada. `inputs: { "description": "tema 10–500", "footerText": "CTA 2–100" }`.
Misma forma para la familia de infografías (Breaking News, Chalkboard, Billboard, etc.).

### AI Story Video con voz — `5903fe43-514d-40ee-a060-0d6628c5f8fd`
Imágenes IA + voz ElevenLabs + captions. Para reels faceless.
```json
{ "templateId": "/base/v2/ai-story-video/5903fe43-514d-40ee-a060-0d6628c5f8fd/v1",
  "inputs": {
    "scenes": [ { "mediaSource": "URL o prompt IA", "script": "voz de esta escena" } ],
    "voiceName": "Brian (American, deep)",
    "captionPosition": "center", "aspectRatio": "9:16" } }
```

## Cómo se inyecta el branding
El `visual-producer` lee `branding.md` de la marca y mapea:
`color_primario → backgroundColor`, `color_texto → textColor`, `color_acento → borderColor/highlightColor`,
`fuente → font`, `logo_url → profileImage`, `aspect_ratio_default → aspectRatio`.
Así cada marca renderiza con su identidad sin depender del Brand Kit nativo de Blotato.

## Nota
La generación de **una sola imagen suelta desde prompt** no está en la API (es solo app).
Se resuelve con un template de output imagen (infografía o carrusel de 1 slide).
