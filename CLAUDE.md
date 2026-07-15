# CLAUDE.md — Guía de orquestación

Este repo es un **sistema multiagente de redes sociales para UNA marca**. **Claude (Opus)
coordina y controla; los modelos de Blotato escriben el copy** (vía `blotato.py write`) y
**Blotato hace toda la generación posible** (visuales, extracción de fuentes, calendario) vía su
API REST directa (no MCP). Claude **no redacta**: arma el brief + las instrucciones, y
**verifica localmente** el resultado (voz, formato, wedge, score) antes de que nada avance.

> **Framework mono-marca.** Este kit orquesta una sola marca (la que configurás en
> `brand-brief.md` + `branding.md` + `_base/accounts.md`). Corre idéntico en **Claude Code** y en
> **opencode** sobre un core compartido. No incluye ruteo multi-marca.

## Principios (no romper)
1. **Nada se publica directo.** Todo va al calendario de Blotato (`useNextFreeSlot` o `scheduledTime`).
2. **Blotato hace; Claude dirige.** **Blotato escribe el copy** (`source-resolutions` /
   `scripts/blotato.py write`), genera visuales, extrae fuentes y agenda. Claude rutea, arma
   instrucciones, hace QC y decide. Claude **no redacta**: si el grader falla, se regenera con
   instrucciones corregidas.
3. **Transporte flexible.** API directa por defecto; MCP cuando convenga o falte la key;
   navegador solo para features app-only (ver `_base/transport.md`). No quedarse limitado por el API.
4. **Tu marca tiene voz propia:** su idioma, voz y wedge. Cada topic sale en esa voz; nunca
   suena a IA genérica ni a traducción mecánica.
5. **El hook es el 50%.** Iterarlo (en las instrucciones a Blotato) antes que el cuerpo.
6. **Aprobación humana antes de agendar.**
7. **Opus coordina y controla; todo lo derivable se deriva.** Toda tarea que se pueda aislar va a
   un subagente (tool Task/subagent), y en paralelo cuando no hay dependencias. **Opus (el
   orquestador) solo coordina, decide y hace el control final** — la verificación local de cada
   pieza (voz, formato, wedge, score) antes de aprobar es de Opus, no se delega. Todo lo demás
   (redactar-vía-Blotato, gradear, generar visuales, agendar, I/O de scripts) se deriva al modelo
   más barato que lo resuelva sin perder calidad: **Haiku** lo mecánico/determinista, **Sonnet**
   lo que necesita criterio. Meta: minimizar tokens que no aportan valor (ver "Ruteo por modelo").

## Cómo se dispara el flujo
El front door es **social-manager**: el orquestador único con el que hablás en lenguaje natural
("publicá algo sobre X", "posteá esto en LinkedIn e Instagram"). Conoce las cuentas y
plataformas de tu marca (LinkedIn, X/Twitter, Instagram, Facebook), **pregunta de a una hasta
estar 95% seguro**, y corre el pipeline **post-writer → post-grader → visual-producer →
post-scheduler**, con aprobación humana antes de agendar. Cuando un topic sale a varias
plataformas, corre una instancia del pipeline por plataforma en paralelo (tool Task/subagent).

social-manager **corre en Opus y solo coordina**: delega cada paso del pipeline a subagentes
(copywriter y scheduler en Sonnet; **visual-producer en Opus** por el criterio visual/branding) y
baja tareas mecánicas a Haiku **cuando el propio Opus lo decide** al delegar, en paralelo cuando no
hay dependencias. Opus **verifica localmente** cada pieza que vuelve antes de la aprobación humana
(ver "Ruteo por modelo"). Nunca gasta su contexto en trabajo derivable.

Si el usuario llega vago ("no sé ni qué postear"), empezá por **content-coach** (brainstorm de
ideas) y luego pasa la idea elegida al pipeline. El usuario también puede tirar un topic directo.

**Registro:** cada publicación queda en `POSTS-LOG.md` con su URL en vivo (lo escribe
`scripts/blotato.py post --log ...`). Nada de posts sin quedar registrados.

## Ruteo por modelo (eficiencia de tokens)
Regla: **delegá agresivamente y usá el modelo más barato que resuelva la tarea sin perder calidad.**
El orquestador corre en Opus y no debe gastar su contexto en trabajo mecánico — lo reparte en
subagentes (tool Task/subagent) y los corre **en paralelo** cuando no hay dependencias entre ellos.

| Nivel | Modelo | Para qué | Ejemplos |
|---|---|---|---|
| Mecánico / determinista | **Haiku** | I/O de scripts, lecturas, formateo, polling, registro | `blotato.py accounts/templates/post-status`, copiar assets al repo, backfill de URL, escribir filas del LOG, validar frontmatter |
| Con criterio | **Sonnet** | copy, grading, QC de voz | post-writer (copywriter), post-grader, repurpose |
| Orquestación / **control** | **Opus** | ruteo, preguntas al humano, **verificación local final**, decisión visual/branding | social-manager, visual-producer, QC final antes del humano, aprobar/descartar |

**Haiku es a discreción de Claude.** No hay un subagente Haiku fijo: cuando el orquestador (Opus)
delega, **él decide en el momento** si una tarea aislable es lo bastante mecánica/determinista como
para bajarla a Haiku (override de modelo al lanzar el Task). Ante la duda, Sonnet. Nunca se
sacrifica calidad por costo — el ruteo barato es una decisión de Claude, no una regla ciega.

> En **opencode** el modelo por agente se hereda de `opencode.json` → `model` (los agentes NO fijan
> modelo). En **Claude Code** el override de modelo se pasa al lanzar el subagente (tool Task).

**Bucle de control (quién verifica qué):**
- El subagente **Sonnet autograda e itera** con `post-grader` dentro del pipeline (hook = 50%),
  regenerando vía Blotato con instrucciones corregidas hasta llegar a 8+. Eso es rápido y barato.
- **Opus hace la verificación local final** de la pieza que vuelve del subagente **contra los
  lineamientos del repo** (`_base/voice.md`, `_base/platform-specs.md`, `_base/linkedin-craft.md`
  cuando aplica, + `brand-brief.md`/`branding.md`/wedge de la marca): voz, formato, hook, score,
  reglas de plataforma. Ese control no se delega: es el gate de calidad del orquestador.
- **Loop de acuerdo (≥90%).** Opus repite verificar → corregir → regenerar vía Blotato **hasta
  estar al menos 90% de acuerdo** con lo que devuelve Blotato según esos lineamientos. Cada vuelta
  **rebota al subagente con la corrección concreta** (Opus no reescribe a mano). Recién cuando
  alcanza ≥90% la pieza pasa a aprobación humana.
- Si tras varias vueltas no converge al 90%, **frená y traé a la persona** con el diagnóstico
  (qué lineamiento no se cumple y por qué), en vez de loopear indefinidamente o bajar el estándar.

Cómo aplicarlo:
- **Un subagente por unidad aislable** (plataforma × pieza). No metas en un solo agente lo
  que se puede paralelizar.
- **Pasá contexto mínimo** a cada subagente: solo los archivos que necesita (`_base/` + los de la
  marca + el draft puntual), no el repo entero. El subagente devuelve solo el resultado, no dumps.
- **Batch de llamadas independientes** en un mismo mensaje para que corran a la vez.
- **Subí de modelo solo si el barato falla** el QC — no al revés. Si el grader baja de 8, reintentá
  antes de escalar de modelo.
- El costo de arrancar un subagente se paga solo cuando aísla trabajo real; no delegues one-liners
  triviales que el orquestador resuelve en un tool call.

## Skills (en `.claude/skills/`)
Base: los **7 skills oficiales del content pack de Blotato** (ver README para el link al pack
oficial), adaptados a este repo mono-marca + API directa, **más** `visual-producer` (extensión
propia, porque el pack oficial no genera visuales por API).

| Skill | Rol | Quién hace el trabajo | Origen |
|---|---|---|---|
| social-manager | **front door único** / orquestador | Claude dirige | propio |
| content-coach | brainstorm para el caso "no sé qué postear" | Claude | oficial (adaptado) |
| brand-brief | setup de voz de la marca | Claude | oficial (adaptado) |
| viral-hooks | librería de 100 hooks | Claude | oficial |
| post-writer | copy nativo por plataforma | Claude (metodología Blotato) | oficial (adaptado) |
| post-grader | puntúa hook/viralidad, loop a 8+ | Claude | oficial (adaptado) |
| visual-producer | carrusel/imagen/video | **Blotato** (templates API) | propio |
| repurpose | 1 fuente → muchas piezas | **Blotato** extrae + Claude adapta | oficial (adaptado) |
| post-scheduler | agenda al calendario | **Blotato** (API directa, no MCP) | oficial (reescrito a API) |

Adaptaciones aplicadas a los skills oficiales: (1) el `brand-brief.md` vive en la raíz del repo;
(2) cargar siempre `_base/`; (3) paso `visual-producer` entre escribir y agendar; (4)
`post-scheduler` usa `scripts/blotato.py` en vez de MCP.

**Runtime-agnóstico.** Los mismos `_base/`, `scripts/` y `SKILL.md` los leen los dos runtimes:
Claude Code (`.claude/`) y opencode (`.opencode/`). opencode descubre los skills nativamente desde
`.claude/skills/` (verificá con `opencode debug skill`), así que hay **una sola copia** del core y
los adaptadores por runtime son finos. Ver `ANALYSIS.md`.

## Contexto compartido (en `_base/`)
`voice.md` (reglas universales), `hooks.md` (apunta a viral-hooks), `platform-specs.md`
(límites + CTA + cadencia), `linkedin-craft.md` (formato/ritmo/storytelling de LinkedIn),
`templates.md` (catálogo de visuales de Blotato),
`publishing.md` (mecánica de la API + cómo Blotato escribe), `transport.md` (API/MCP/navegador),
`accounts.md` (**template** de cuentas — completá con tus IDs).
**Siempre cargar `_base/` + los archivos de la marca (`brand-brief.md`, `branding.md`) antes de generar.**

## API (script)
Todo pasa por `scripts/blotato.py` (requiere `BLOTATO_API_KEY` en `scripts/.env`).
`whoami` valida · `accounts` lista · `templates` descubre visuales · `write` **Blotato escribe
el copy** · `source` extrae · `visual` genera · `post` agenda · `post-status` polea/backfillea
la URL en vivo · `slots-list/slots-create` cadencia.
El comando `post` **se niega** a publicar sin `--next-free-slot` o `--schedule`. Pasale
`--log POSTS-LOG.md --draft <archivo>` para que registre la publicación con su URL.
Alternativa MCP disponible para cada uno (ver `_base/transport.md`).

## Convención de guardado
Todo lo que se genera queda en el repo (no solo en el log): el **contenido final** y los
**visuales renderizados** se persisten, para poder auditar lo publicado y para que la voz
mejore con el tiempo revisando lo que ya salió.

### Slug — formato obligatorio

`<YYYY-MM-DD>-<topic-slug>[-<variant>]` — todo **lowercase**, hyphenated, sin caracteres
especiales ni tildes.

- `YYYY-MM-DD` = fecha de agendado/publicación, NO fecha de creación.
- `<topic-slug>` = 2-5 palabras del tema, sin verbos auxiliares, sin artículos. Ejemplos:
  `ai-day2-credentials`, `ai-dirty-data`, `ai-pilot-hidden-costs`, `ai-production-reality`.
  Reglas:
  - Empezar por categoría/tema principal (`ai-`, `web3-`, etc. cuando aplique).
  - Sin fechas dentro del slug (la fecha ya está como prefijo).
  - Sin palabras huecas: `post`, `article`, `linkedin`, `tweet`, `update`.
- `<variant>` (opcional) = `-personal`, `-page`, `-company`, `-promo`, `-thread`, etc. Solo
  cuando la misma pieza tiene variantes que coexisten en el repo (ej. perfil personal vs
  Company Page de LinkedIn en la misma fecha).

**Mismo slug en draft, assets y log.** Si el borrador es `2026-07-15-ai-pilot-hidden-costs-linkedin-personal.md`,
los assets viven en `2026-07-15-ai-pilot-hidden-costs/` (sin `-linkedin-personal` —
la plataforma/variante ya está en el frontmatter del draft).

### Paths concretos

- **Borradores aprobados** → `posts/<slug>-<plataforma>.md` con frontmatter:
  `topic, brand, platform, hook_pattern, score, status, scheduled_time, media_urls` (URLs de
  Blotato) y, si lleva visual, `local_media` (rutas de los assets guardados en el repo) +
  `carousel_html` (si aplica). Se guarda al aprobar/agendar, no al publicar.
  Variantes: `<slug>-linkedin-personal.md`, `<slug>-linkedin-page.md`, `<slug>-twitter.md`,
  `<slug>-instagram.md`, etc.
- **Visuales renderizados (los archivos, no solo la URL)** → `posts/assets/<slug>/`
  con `slide1.png`…`slideN.png` para carrusel, o `image.png` para imagen única. El
  `visual-producer` **debe copiar los PNG/MP4 renderizados del scratchpad al repo** antes de
  terminar y devolver también esas rutas locales. El HTML fuente del carrusel vive en
  `posts/<slug>.carousel.html` (mismo slug que el dir de assets, sin sufijo de
  plataforma). Motivo: la URL del CDN de Blotato es externa y puede caerse; el repo tiene
  que conservar los bytes, no solo el link.
- **Publicaciones** → fila en `POSTS-LOG.md` (fecha, plataforma, estado, agendado, URL
  en vivo, submissionId, borrador). La escribe el flag `--log` de `post`; backfill de URL con
  `post-status`.
- **Ejemplos aprobados por el humano** (piezas que gustaron, para reusar de molde) →
  `examples/<slug>.md` con la receta + el copy de referencia.
