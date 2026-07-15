---
name: post-scheduler
description: Schedule a finished social post to one or more platforms via the Blotato REST API (direct, not MCP). Handles single- and multi-platform scheduling, resolves accounts from the brand's accounts.md, applies a final pre-publish check, and returns scheduled time + post IDs. Triggers on "schedule this," "post this to [platform]," or as the final step in content-coach, post-writer and repurpose flows. Falls back to saving a copy-paste file if the API key isn't set.
argument-hint: "[post text or path] [platform(s)] [optional time]"
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion
---

# Post Scheduler (API directa)

You take an approved post and ship it to the Blotato **calendar** via the direct REST API
(`scripts/blotato.py`), NOT via MCP. You do NOT write or revise the post — that's `post-writer`'s
job. By the time a post reaches you, it's been graded and approved. **Nothing publishes
immediately: everything is scheduled.**

> **Por qué API directa:** este proyecto usa `scripts/blotato.py` (requiere `BLOTATO_API_KEY`
> en `scripts/.env`) para ser más rápido y funcionar igual en Claude Code, Desktop y Cowork,
> sin depender del MCP.

## When to Activate
- "Schedule this post" / "Agendá esto a LinkedIn de tu marca"
- Auto-called as the final step of `content-coach`, `post-writer`, or `repurpose` after approval.

## Workflow

### Step 1: Get inputs
1. **Post text** — inline, or path to a file (idealmente `posts/....md`).
2. **Platform(s)** — one or more from: instagram, facebook, twitter, linkedin.
3. **Cuenta** — para resolver el `accountId`/`pageId` correcto (leé `_base/accounts.md`).
4. **Media** — las `mediaUrls` que devolvió `visual-producer` (o vacío si es solo texto).
5. **Time** — por defecto `--next-free-slot`; o un ISO timestamp si el usuario lo especificó.

Si falta la plataforma o la marca, preguntá. No adivines.

### Step 2: Final pre-publish check
Antes de tocar la API, revisá el post una vez más:
- [ ] Cero em dashes
- [ ] Sin relleno prohibido ("really", "very", "just", "basically", "literally", "actually")
- [ ] Sin aperturas de relleno ("in today's world", "let me tell you")
- [ ] Voz activa; contracciones usadas
- [ ] Nº de hashtags correcto (0 en Twitter/LinkedIn/Facebook; 3-5 en Instagram)
- [ ] Instagram: hay `mediaUrls` adjuntas
- [ ] LinkedIn: sin links externos en el cuerpo

Si algo falla, **frená y reportá**. Esperá respuesta explícita del usuario. No auto-arregles.

### Step 3: Resolvé la cuenta
Leé `_base/accounts.md`. Por ejemplo:
- LinkedIn → `--account <ACCOUNT_ID> --page <PAGE_ID>`
- X → `--account <ACCOUNT_ID>`

Facebook requiere `--page` (pageId) obligatorio. Si una plataforma tiene varias cuentas posibles, preguntá cuál.

### Step 4: Agendá (una llamada por plataforma)
```bash
python scripts/blotato.py post \
  --account <accountId> --platform <linkedin|twitter|instagram|facebook> \
  [--page <pageId>] \
  --text-file <path> \
  [--media "<url1,url2,...>"] \
  --next-free-slot            # o: --schedule "2026-07-20T13:00:00Z"
```
Reglas:
- **Siempre** `--next-free-slot` o `--schedule`. El script se niega a publicar sin uno de los dos.
- El script garantiza `content.platform == target.targetType`.
- Multi-plataforma: una llamada por plataforma. Si el copy excede el límite de una plataforma, preguntá cómo manejarlo (acortar / saltar / override). No truncar solo.

### Step 5: Reportá
Mostrá una tabla de confirmación:
```
## Agendado
| Plataforma | Marca | Cuenta | Hora | Estado | postSubmissionId |
|---|---|---|---|---|---|
| LinkedIn | tu marca | <PAGE_ID> | Próximo slot libre | scheduled | abc-123 |
| Twitter | tu marca | <PLATFORM_HANDLE> | Próximo slot libre | scheduled | def-456 |

Ver y editar en https://my.blotato.com/scheduler
```
Para fallas parciales (3 de 5 ok), reportá éxito y falla por separado. No hagas rollback.

### Step 6: Fallback (sin API key)
Si `python scripts/blotato.py whoami` falla o no hay `scripts/.env`:
```
Blotato no está conectado (falta la API key en scripts/.env). Guardo el post para pegarlo a mano.
```
Guardá en `posts/<slug>-ready-to-paste.txt`:
```
=== POST PARA [PLATAFORMA] ===
Agendar para: [hora o "posteo manual"]

[TEXTO DEL POST]

=== FIN ===
```
Si es multi-plataforma, un bloque por plataforma. Decile el path al usuario. Nunca falles el flujo.

## Manejo de errores
- **401/403** → la API key falla o expiró. Avisá para revisar `scripts/.env` o regenerar la key.
- **429** → rate limit; esperá los segundos que dice el mensaje y reintentá una vez.
- **`--next-free-slot` sin slots** → no hay slots para esa plataforma/cuenta. Avisá para crear
  slots (`python scripts/blotato.py slots-create ...`) o usar `--schedule` con hora exacta.
- **Post sobre el límite de chars** → no truncar; preguntá.
- **Falla de red** → reintentá una vez; si vuelve a fallar, guardá al fallback y reportá.

## What NOT to Do
- No auto-arreglar problemas de voz: solo flag y preguntar (eso es de post-grader/post-writer).
- No saltear el pre-check: es la última línea de defensa.
- No publicar al instante por defecto. Solo publicá ya si el usuario dice explícitamente "post now".
- No reportar "listo" sin el `postSubmissionId`.
