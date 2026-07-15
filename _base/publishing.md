# Mecánica de la API de Blotato

> Todo el trabajo pesado (generar visuales, agendar, publicar) lo hace Blotato por API.
> Base URL: `https://backend.blotato.com/v2` · Header: `blotato-api-key: <API_KEY>`
> Todo es asíncrono: creás → te devuelve un id → poleás estado.
> El cliente Python en `scripts/blotato.py` envuelve todo esto.

## Autenticación
- Header en cada request: `blotato-api-key: <API_KEY>`.
- La key se saca en Settings → API de my.blotato.com. **Generarla termina el trial y activa el plan pago.**
- La key puede terminar en `=` (padding base64): es parte de la key, no la recortes.
- Validar: `GET /users/me`.

## Regla de oro: nada se publica directo
**Siempre** agendar. Al crear un post, pasar `scheduledTime` (ISO 8601) **o** `useNextFreeSlot: true`.
Si no mandás ninguno de los dos, publica al instante. ⚠️ Estos campos van al **nivel raíz**,
hermanos de `post`. Si los metés adentro de `post`, se ignoran y publica ya.

## Endpoints clave

| Método | Path | Para qué |
|---|---|---|
| GET | `/users/me` | Validar la key |
| GET | `/users/me/accounts` | Listar cuentas → obtener `accountId` |
| GET | `/users/me/accounts/:id/subaccounts` | Páginas de FB / LinkedIn → `pageId` |
| POST | `/videos/from-templates` | **Generar** carrusel / imagen / video |
| GET | `/videos/creations/:id` | Polear estado del visual → `imageUrls` / `mediaUrl` |
| POST | `/source-resolutions-v3` | Extraer contenido de URL / video / texto |
| GET | `/source-resolutions-v3/:id` | Polear extracción |
| POST | `/posts` | Crear + agendar post |
| GET | `/posts/:id` | Polear estado de publicación |
| GET | `/schedule/slots` | Ver slots del calendario |
| POST | `/schedule/slots` | Crear slots (cadencia) |

## Crear + agendar un post

```json
{
  "post": {
    "accountId": "<ACCOUNT_ID>",
    "content": { "text": "…", "mediaUrls": ["https://…"], "platform": "linkedin" },
    "target": { "targetType": "linkedin", "pageId": "<PAGE_ID>" }
  },
  "useNextFreeSlot": true
}
```

Reglas:
- `content.platform` DEBE ser idéntico a `target.targetType`.
- `mediaUrls`: URLs públicas (las que devuelve el visual-producer). `[]` si es solo texto.
- Facebook exige `target.pageId`. LinkedIn `pageId` opcional (omitir = perfil personal).
- Twitter no pide campos extra.
- Respuesta: `{ "postSubmissionId": "..." }` → polear `GET /posts/:id` (`in-progress`/`published`/`failed`).

## Escribir el copy (lo hace Blotato, no Claude)

Blotato escribe el texto por API vía `source-resolutions-v3` con `customInstructions`.
Claude solo arma el brief + las instrucciones; Blotato genera.

```bash
# Escribir desde un brief/topic (Blotato redacta)
python scripts/blotato.py write \
  --brief "AI agent loops: por qué los loops sin corte queman tokens" \
  --instructions "Write a LinkedIn post in English. Hook-first (first 140 chars). ~1300 chars. \
One idea. Voice: technical, direct, no fluff. Wedge: most 'AI agents' are a while-loop with extra steps. \
Comment-driving CTA. No em dashes, no hashtags in body."

# Con investigación web previa (Blotato usa perplexity-query)
python scripts/blotato.py write --research --brief "latest on AI agent reliability" --instructions "..."
```
Devuelve `{ "title", "content" }`. Ese `content` es el copy. Reglas:
- Las instrucciones DEBEN incluir: idioma, plataforma, largo, hook-first, voz + wedge de la
  marca, tipo de CTA, y las reglas de voz (sin em dashes, hashtags, etc.). Salen del brand-brief + platform-specs.
- Si el grader lo rechaza, se **regenera con instrucciones corregidas** (Claude no reescribe).
- Equivalente MCP: `blotato_create_source` (ver `transport.md`).

> Nota: el AI Agent pulido de la app da mejor calidad pero es app-only. Si `write` no alcanza,
> se puede subir a Tier 3 (navegador) — ver `transport.md`.

## Generar un visual (lo hace Blotato)

```json
{ "templateId": "53cfec04-...", "inputs": { ... }, "render": true }
```
Respuesta `{ "item": { "id": "...", "status": "queueing" } }` → polear `GET /videos/creations/:id`
hasta `status: "done"` → usar `imageUrls` (carrusel/imagen) o `mediaUrl` (video) como `mediaUrls` del post.
Ver el catálogo y los inputs en `templates.md`.

## Cadencia (Schedule Slots)
Los slots definen el calendario y se definen en **UTC**. `useNextFreeSlot` cae en el próximo
slot libre de esa plataforma/cuenta. Sin slots configurados, `useNextFreeSlot` no tiene dónde caer.
Crear con `POST /schedule/slots` body `{ "slots": [ { hour, minute, day, selectedTargets:[...] } ] }`.

## Rate limits / gotchas
- `POST /posts` y `POST /videos/from-templates`: 30/min. Polling: 60/min.
- `429` → el mensaje dice en cuántos segundos reintentar.
- Confundir `postSubmissionId` (polling de publicación) con el id de post publicado (analytics) es error común.
