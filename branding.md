# Branding — TEMPLATE

> Visual identity for YOUR brand. The `visual-producer` skill reads this to inject colors, font,
> and logo into carousels/images (Blotato template API or the HTML→PNG carousel generator in
> `scripts/carousel/`). Replace every `<PLACEHOLDER>`.

## Palette
- **Background:** `<#RRGGBB>`
- **Text:** `<#RRGGBB>`
- **Muted / secondary:** `<#RRGGBB>`
- **Accent:** `<#RRGGBB>` (use sparingly — ~10% of the surface max)

## Typography
- **Primary font:** `<Font Name>` (Google Fonts name, or a websafe fallback)
- **Mono / accent font:** `<Font Name>` (optional)

## Logo
- **Wordmark / mark:** `<how the logo renders — text, CSS mark, or an image path>`
- **Asset path (if image):** `assets/logo.png` (optional)

## Format defaults
- **Carousel aspect:** 4:5 (1080×1350) for feed; 1:1 (1080×1080) alt.
- **Image model default:** `fal-ai/imagen4/preview/fast`

> Tip: the carousel scaffold `scripts/carousel/brand-template.html` already exposes these as CSS
> variables in `:root` and a `{b} your brand` logo placeholder — edit them to match this file.
