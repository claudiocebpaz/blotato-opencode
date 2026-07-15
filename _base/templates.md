# Blotato visual template catalog

> Blotato generates the visuals. Claude picks the template and assembles the `inputs` (injecting
> the brand's colors/font from its `branding.md`). Endpoint: `POST /videos/from-templates`.
> Poll it until `done` and use `imageUrls` / `mediaUrl` as the post's media.
> To discover ALL templates and their inputs live: `GET /videos/templates?fields=id,name,description,inputs`.

## Default image model (cost control)
The image model drives the cost: it ranges from **1 credit** (Flux Schnell) to **50** (Nano Banana Pro) per image.
- **Recommended default:** `fal-ai/imagen4/preview/fast` (7 credits) — a good balance.
- **Cheap for tests:** `replicate/black-forest-labs/flux-schnell` (1 credit).
- **Legible text inside the image:** Nano Banana models (15–50).
- Reserve the expensive ones for standout pieces. Uploaded URLs (not generated) don't spend credits.

## Templates chosen for this project

### Instagram Carousel Slideshow — `53cfec04-2500-41cf-8cc1-ba670d2c341a`
Generates 1 AI image per slide (pure images, no text overlay). Model field: `model`.
```json
{ "templateId": "53cfec04-2500-41cf-8cc1-ba670d2c341a",
  "inputs": {
    "slidePrompts": ["prompt slide 1", "prompt slide 2", "..."],
    "model": "nano-banana-pro",
    "aspectRatio": "4:5" } }
```
`slidePrompts`: 1–10, each 5–1000 chars. `aspectRatio`: 1:1, 4:5, 5:4, 16:9, 9:16.

### Image Slideshow with text overlay — `5903b592-1255-43b4-b9ac-f8ed7cbf6a5f`
Images (uploaded OR generated) + text per slide. **The best for carousels with a message.**
```json
{ "templateId": "/base/v2/image-slideshow/5903b592-1255-43b4-b9ac-f8ed7cbf6a5f/v1",
  "inputs": {
    "slides": [ { "imageSource": "URL or AI prompt", "textOverlay": "≤300 chars" } ],
    "aiImageModel": "fal-ai/imagen4/preview/fast",
    "textPosition": "bottom", "textStyle": "modern", "textColor": "#000000",
    "aspectRatio": "4:5", "transition": "fade" } }
```

### Tutorial Carousel (minimalist) — `2491f97b-1b47-4efa-8b96-8c651fa7b3d5`
Structured carousel: title + numbered items + CTA + profile slide. **Ideal for LinkedIn.**
Accepts branding: `backgroundColor`, `borderColor`, `textColor`, `font`, `profileImage`.
Required fields: `mainTitle`, `authorName`, `ctaButtonText`, `contentItems[]`, `ctaTitle`, `ctaActions[]`,
`profileName`, `profileTitle`, `profileDescription`, `profileCta`.

### Centered Quote Card — `9f4e66cd-b784-4c02-b2ce-e6d0765fd4c0`
The simplest one. `inputs: { "quotes": ["text 10–350 chars"] }` (1–20 quotes → 1 card each).

### Infographic (e.g. Newspaper) — `07a5b5c5-387c-49e3-86b1-de822cd2dfc7`
A single generated image. `inputs: { "description": "topic 10–500", "footerText": "CTA 2–100" }`.
Same shape for the infographic family (Breaking News, Chalkboard, Billboard, etc.).

### AI Story Video with voice — `5903fe43-514d-40ee-a060-0d6628c5f8fd`
AI images + ElevenLabs voice + captions. For faceless reels.
```json
{ "templateId": "/base/v2/ai-story-video/5903fe43-514d-40ee-a060-0d6628c5f8fd/v1",
  "inputs": {
    "scenes": [ { "mediaSource": "URL or AI prompt", "script": "voice-over for this scene" } ],
    "voiceName": "Brian (American, deep)",
    "captionPosition": "center", "aspectRatio": "9:16" } }
```

## How the branding is injected
The `visual-producer` reads the brand's `branding.md` and maps:
`color_primario → backgroundColor`, `color_texto → textColor`, `color_acento → borderColor/highlightColor`,
`fuente → font`, `logo_url → profileImage`, `aspect_ratio_default → aspectRatio`.
This way each brand renders with its own identity without depending on Blotato's native Brand Kit.

## Note
Generating **a single standalone image from a prompt** isn't in the API (it's app-only).
Solve it with an image-output template (an infographic or a 1-slide carousel).
