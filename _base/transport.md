# Política de transporte — API / MCP / navegador

> Cómo hablar con Blotato. Regla general: **usá lo más conveniente, no te quedes limitado
> por el API.** Hay 3 vías, en orden de preferencia.

## Tier 1 — API directa (default)
`scripts/blotato.py` contra `https://backend.blotato.com/v2` con `BLOTATO_API_KEY`.
- **Cuándo:** por defecto, sobre todo en Claude Code (TUI/VS Code). Rápido y portable.
- **Requiere:** la key en `scripts/.env`.

## Tier 2 — MCP (cuando convenga o falte la key)
Las herramientas `blotato_*` del MCP (ya conectado en Cowork/Desktop).
- **Cuándo:**
  - No hay `BLOTATO_API_KEY` configurada (el MCP no la necesita, usa su propia auth).
  - Es más cómodo (algunas tools poléan internamente, ej. `blotato_create_source`).
  - Estás en Cowork/Desktop donde el MCP ya está a mano.
- **Nota:** API y MCP exponen **las mismas** capacidades (mapeo 1:1). El MCP no desbloquea
  nada que el API no tenga; es solo otra vía de acceso. Elegí por conveniencia, no por poder.

Mapeo rápido API ↔ MCP:
`/users/me`→`blotato_get_user` · `/users/me/accounts`→`blotato_list_accounts` ·
`/posts`→`blotato_create_post` · `/source-resolutions-v3`→`blotato_create_source` ·
`/videos/from-templates`→`blotato_create_visual` · `/schedules`→`blotato_list_schedules` ·
`/schedule/slots`→(vía API) · analytics/comments/messages→`blotato_*` equivalentes.

## Tier 3 — Navegador (solo para lo que es 100% app-only)
Manejar la app de Blotato (my.blotato.com) con Claude in Chrome / computer-use.
- **Cuándo:** SOLO para features que ni API ni MCP exponen. En concreto:
  - El **AI Agent / Remix** pulido de la app (mejor calidad de escritura que `source-resolutions`).
  - Configurar Brand Kits nativos, o cualquier ajuste de UI.
- **Cuándo NO:** para publicar/agendar/generar visuales/escribir por instrucciones → eso ya
  está en Tier 1/2, no bajes a navegador.
- **Ojo:** es más lento y frágil. Última opción, con aprobación del usuario.

## Regla de decisión
1. ¿Lo puede hacer el API? → Tier 1 (o Tier 2 si es más cómodo o falta la key).
2. ¿Es una capacidad que ni API ni MCP tienen (ej. calidad del AI Agent de la app)? → Tier 3.
3. Nunca rechaces una tarea "porque el API no puede": subí de tier hasta resolverla.
