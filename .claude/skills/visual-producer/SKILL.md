---
name: visual-producer
description: >
  Generates the visual media for a post using Blotato's template API (carousels, images,
  infographics, AI videos). Use when a post needs an image, carousel, or video. Picks a
  template, injects the brand's colors/fonts, calls Blotato, polls, and returns media URLs.
allowed-tools: Read, Bash
---

# visual-producer (Blotato genera)

> **Extensión propia del proyecto.** El pack oficial de Blotato (content-coach, brand-brief,
> post-writer, post-grader, post-scheduler, repurpose, viral-hooks) NO incluye generación
> visual por API. Este skill llena ese hueco: es el que hace que Blotato genere los carruseles,
> imágenes, infografías y videos que después agenda `post-scheduler`. Se invoca entre escribir
> y agendar, cuando la pieza lleva media.

Sos el puente al **motor creativo de Blotato**. Vos elegís el template y armás los inputs;
**Blotato renderiza**. Devolvés las URLs de media listas para el post.

## Contexto que cargás
1. `_base/templates.md` (catálogo + inputs + modelo de imagen por defecto).
2. `branding.md` (colores, fuente, logo, aspect ratio de la marca).

## Proceso
1. **Elegí el template** según la pieza:
   - Carrusel con mensaje (LinkedIn/IG) → Image Slideshow con texto (`5903b592...`) o Tutorial Carousel (`2491f97b...`).
   - Carrusel de imágenes puras (IG) → Instagram Carousel Slideshow (`53cfec04...`).
   - Cita/quote → Quote Card (`9f4e66cd...`).
   - Dato/infografía → familia infografías (`07a5b5c5...`).
   - Reel faceless → AI Story Video con voz (`5903fe43...`).
2. **Inyectá el branding** de la marca en los inputs (backgroundColor, textColor,
   borderColor, font, profileImage, aspectRatio). Ver el mapeo en `templates.md`.
3. **Elegí el modelo de imagen** según prioridad/costo (default `fal-ai/imagen4/preview/fast` = 7 créditos).
4. **Generá y poleá** con el cliente:
   ```bash
   python scripts/blotato.py visual --template <ID> --inputs '<JSON>'
   ```
   El script crea (`POST /videos/from-templates`), poléa (`GET /videos/creations/:id`) hasta
   `done`, y te devuelve `imageUrls` (carrusel/imagen) o `mediaUrl` (video).
5. **Guardá los assets renderizados en el repo (obligatorio).** No dejes el visual solo en el
   scratchpad ni solo como URL del CDN de Blotato. Copiá los archivos renderizados a
   `posts/assets/<slug>/` (`slide1.png`…`slideN.png` para carrusel, `image.png`/`video.mp4`
   para pieza única). Si el carrusel se armó con render local, guardá también el HTML fuente en
   `posts/<slug>.carousel.html`. Motivo: la URL del CDN es externa y puede caerse; el
   repo debe conservar los bytes (ver "Convención de guardado" en `CLAUDE.md`).
6. **Devolvé las URLs de Blotato Y las rutas locales** al orquestador. El orquestador escribe en
   el frontmatter del draft: `media_urls` (URLs de Blotato, las usa `post-scheduler`) y
   `local_media` (las rutas del repo, para el archivo permanente).

## Reglas
- Confirmá el costo estimado si el carrusel usa modelo caro (créditos = nº imágenes × costo/modelo).
- LinkedIn carrusel = documento desde 2-10 imágenes, sin video.
- Instagram siempre requiere media (este agente la provee).
- Si el usuario ya tiene una imagen/URL propia, pasala como `imageSource`/`mediaSource` (no gasta créditos).
- No inventes IDs de template: los del catálogo, o descubrilos con
  `python scripts/blotato.py templates`.
