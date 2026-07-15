# CLAUDE.md — Orchestration guide

This repo is a **multi-agent social media system for ONE brand**. **Claude (Opus)
coordinates and controls; Blotato's models write the copy** (via `blotato.py write`) and
**Blotato does as much of the generation as possible** (visuals, source extraction, calendar) via its
direct REST API (not MCP). Claude **does not write**: it assembles the brief + the instructions, and
**verifies locally** the result (voice, format, wedge, score) before anything moves forward.

> **Single-brand framework.** This kit orchestrates a single brand (the one you configure in
> `brand-brief.md` + `branding.md` + `_base/accounts.md`). It runs identically in **Claude Code** and
> **opencode** on a shared core. It does not include multi-brand routing.

## Principles (don't break these)
1. **Nothing publishes directly.** Everything goes to Blotato's calendar (`useNextFreeSlot` or `scheduledTime`).
2. **Blotato does; Claude directs.** **Blotato writes the copy** (`source-resolutions` /
   `scripts/blotato.py write`), generates visuals, extracts sources and schedules. Claude routes, assembles
   instructions, does QC and decides. Claude **does not write**: if the grader fails, it regenerates with
   corrected instructions.
3. **Flexible transport.** Direct API by default; MCP when convenient or when the key is missing;
   browser only for app-only features (see `_base/transport.md`). Don't get limited by the API.
4. **Your brand has its own voice:** its language, voice and wedge. Every topic comes out in that voice; it never
   sounds like generic AI or a mechanical translation.
5. **The hook is 50%.** Iterate it (in the instructions to Blotato) before the body.
6. **Human approval before scheduling.**
7. **Opus coordinates and controls; everything delegable gets delegated.** Any task that can be isolated goes to
   a subagent (Task/subagent tool), and in parallel when there are no dependencies. **Opus (the
   orchestrator) only coordinates, decides and does the final control** — the local verification of each
   piece (voice, format, wedge, score) before approving is Opus's, it is not delegated. Everything else
   (write-via-Blotato, grade, generate visuals, schedule, script I/O) is delegated to the cheapest model
   that resolves it without losing quality: **Haiku** for the mechanical/deterministic, **Sonnet**
   for what needs judgment. Goal: minimize tokens that don't add value (see "Model routing").

## How the flow is triggered
The front door is **social-manager**: the single orchestrator you talk to in natural language
("publish something about X", "post this on LinkedIn and Instagram"). It knows your brand's accounts and
platforms (LinkedIn, X/Twitter, Instagram, Facebook), **asks one question at a time until it is
95% sure**, and runs the pipeline **post-writer → post-grader → visual-producer →
post-scheduler**, with human approval before scheduling. When a topic goes out to several
platforms, it runs one instance of the pipeline per platform in parallel (Task/subagent tool).

social-manager **runs on Opus and only coordinates**: it delegates each pipeline step to subagents
(copywriter and scheduler on Sonnet; **visual-producer on Opus** for the visual/branding judgment) and
pushes mechanical tasks down to Haiku **when Opus itself decides so** at delegation time, in parallel when there are no
dependencies. Opus **verifies locally** each piece that comes back before human approval
(see "Model routing"). It never spends its context on delegable work.

If the user arrives vague ("I don't even know what to post"), start with **content-coach** (idea
brainstorm) and then pass the chosen idea to the pipeline. The user can also throw a topic directly.

**Log:** every publication is recorded in `POSTS-LOG.md` with its live URL (written by
`scripts/blotato.py post --log ...`). No posts without being logged.

## Model routing (token efficiency)
Rule: **delegate aggressively and use the cheapest model that resolves the task without losing quality.**
The orchestrator runs on Opus and must not spend its context on mechanical work — it distributes it across
subagents (Task/subagent tool) and runs them **in parallel** when there are no dependencies between them.

| Level | Model | For what | Examples |
|---|---|---|---|
| Mechanical / deterministic | **Haiku** | script I/O, reads, formatting, polling, logging | `blotato.py accounts/templates/post-status`, copy assets to the repo, backfill URL, write LOG rows, validate frontmatter |
| With judgment | **Sonnet** | copy, grading, voice QC | post-writer (copywriter), post-grader, repurpose |
| Orchestration / **control** | **Opus** | routing, questions to the human, **final local verification**, visual/branding decision | social-manager, visual-producer, final QC before the human, approve/discard |

**Haiku is at Claude's discretion.** There is no fixed Haiku subagent: when the orchestrator (Opus)
delegates, **it decides in the moment** whether an isolable task is mechanical/deterministic enough
to push it down to Haiku (model override when launching the Task). When in doubt, Sonnet. Quality is never
sacrificed for cost — cheap routing is a decision by Claude, not a blind rule.

> In **opencode** the per-agent model is inherited from `opencode.json` → `model` (the agents do NOT fix a
> model). In **Claude Code** the model override is passed when launching the subagent (Task tool).

**Control loop (who verifies what):**
- The **Sonnet subagent auto-grades and iterates** with `post-grader` inside the pipeline (hook = 50%),
  regenerating via Blotato with corrected instructions until it reaches 8+. That is fast and cheap.
- **Opus does the final local verification** of the piece that comes back from the subagent **against the
  repo guidelines** (`_base/voice.md`, `_base/platform-specs.md`, `_base/linkedin-craft.md`
  when applicable, + the brand's `brand-brief.md`/`branding.md`/wedge): voice, format, hook, score,
  platform rules. That control is not delegated: it is the orchestrator's quality gate.
- **Agreement loop (≥90%).** Opus repeats verify → correct → regenerate via Blotato **until it is
  at least 90% in agreement** with what Blotato returns according to those guidelines. Each round
  **bounces back to the subagent with the concrete correction** (Opus does not rewrite by hand). Only when
  it reaches ≥90% does the piece go to human approval.
- If after several rounds it does not converge at 90%, **stop and bring in the person** with the diagnosis
  (which guideline is not met and why), instead of looping indefinitely or lowering the standard.

How to apply it:
- **One subagent per isolable unit** (platform × piece). Don't put into a single agent what
  can be parallelized.
- **Pass minimal context** to each subagent: only the files it needs (`_base/` + the brand's
  + the specific draft), not the whole repo. The subagent returns only the result, not dumps.
- **Batch independent calls** in the same message so they run at once.
- **Move up a model only if the cheap one fails** QC — not the other way around. If the grader drops below 8, retry
  before escalating the model.
- The cost of starting a subagent only pays off when it isolates real work; don't delegate trivial
  one-liners that the orchestrator resolves in a single tool call.

## Skills (in `.claude/skills/`)
Base: the **7 official skills from Blotato's content pack** (see README for the link to the official
pack), adapted to this single-brand repo + direct API, **plus** `visual-producer` (a custom extension,
because the official pack does not generate visuals via API).

| Skill | Role | Who does the work | Origin |
|---|---|---|---|
| social-manager | **single front door** / orchestrator | Claude directs | custom |
| content-coach | brainstorm for the "I don't know what to post" case | Claude | official (adapted) |
| brand-brief | brand voice setup | Claude | official (adapted) |
| viral-hooks | library of 100 hooks | Claude | official |
| post-writer | native copy per platform | Claude (Blotato methodology) | official (adapted) |
| post-grader | scores hook/virality, loop to 8+ | Claude | official (adapted) |
| visual-producer | carousel/image/video | **Blotato** (template API) | custom |
| repurpose | 1 source → many pieces | **Blotato** extracts + Claude adapts | official (adapted) |
| post-scheduler | schedules to the calendar | **Blotato** (direct API, not MCP) | official (rewritten to API) |

Adaptations applied to the official skills: (1) the `brand-brief.md` lives at the repo root;
(2) always load `_base/`; (3) `visual-producer` step between writing and scheduling; (4)
`post-scheduler` uses `scripts/blotato.py` instead of MCP.

**Runtime-agnostic.** The same `_base/`, `scripts/` and `SKILL.md` are read by both runtimes:
Claude Code (`.claude/`) and opencode (`.opencode/`). opencode discovers the skills natively from
`.claude/skills/` (verify with `opencode debug skill`), so there is **a single copy** of the core and
the per-runtime adapters are thin. See `ANALYSIS.md`.

## Shared context (in `_base/`)
`voice.md` (universal rules), `hooks.md` (points to viral-hooks), `platform-specs.md`
(limits + CTA + cadence), `linkedin-craft.md` (LinkedIn format/rhythm/storytelling),
`templates.md` (Blotato's visual catalog),
`publishing.md` (API mechanics + how Blotato writes), `transport.md` (API/MCP/browser),
`accounts.md` (accounts **template** — fill in with your IDs).
**Always load `_base/` + the brand's files (`brand-brief.md`, `branding.md`) before generating.**

## API (script)
Everything goes through `scripts/blotato.py` (requires `BLOTATO_API_KEY` in `.env` at the project root).
`whoami` validates · `accounts` lists · `templates` discovers visuals · `write` **Blotato writes
the copy** · `source` extracts · `visual` generates · `post` schedules · `post-status` polls/backfills
the live URL · `slots-list/slots-create` cadence.
The `post` command **refuses** to publish without `--next-free-slot` or `--schedule`. Pass it
`--log POSTS-LOG.md --draft <file>` so it records the publication with its URL.
An MCP alternative is available for each one (see `_base/transport.md`).

## Saving convention
Everything generated stays in the repo (not just in the log): the **final content** and the
**rendered visuals** are persisted, so what was published can be audited and so the voice
improves over time by reviewing what already went out.

### Slug — required format

`<YYYY-MM-DD>-<topic-slug>[-<variant>]` — all **lowercase**, hyphenated, no special
characters or accents.

- `YYYY-MM-DD` = schedule/publication date, NOT creation date.
- `<topic-slug>` = 2-5 words of the topic, no auxiliary verbs, no articles. Examples:
  `ai-day2-credentials`, `ai-dirty-data`, `ai-pilot-hidden-costs`, `ai-production-reality`.
  Rules:
  - Start with the main category/topic (`ai-`, `web3-`, etc. when applicable).
  - No dates inside the slug (the date is already the prefix).
  - No filler words: `post`, `article`, `linkedin`, `tweet`, `update`.
- `<variant>` (optional) = `-personal`, `-page`, `-company`, `-promo`, `-thread`, etc. Only
  when the same piece has variants that coexist in the repo (e.g. personal profile vs
  LinkedIn Company Page on the same date).

**Same slug in draft, assets and log.** If the draft is `2026-07-15-ai-pilot-hidden-costs-linkedin-personal.md`,
the assets live in `2026-07-15-ai-pilot-hidden-costs/` (without `-linkedin-personal` —
the platform/variant is already in the draft's frontmatter).

### Concrete paths

- **Approved drafts** → `posts/<slug>-<platform>.md` with frontmatter:
  `topic, brand, platform, hook_pattern, score, status, scheduled_time, media_urls` (Blotato
  URLs) and, if it carries a visual, `local_media` (paths of the assets saved in the repo) +
  `carousel_html` (if applicable). Saved on approval/scheduling, not on publishing.
  Variants: `<slug>-linkedin-personal.md`, `<slug>-linkedin-page.md`, `<slug>-twitter.md`,
  `<slug>-instagram.md`, etc.
- **Rendered visuals (the files, not just the URL)** → `posts/assets/<slug>/`
  with `slide1.png`…`slideN.png` for a carousel, or `image.png` for a single image. The
  `visual-producer` **must copy the rendered PNG/MP4 from the scratchpad to the repo** before
  finishing and also return those local paths. The carousel's source HTML lives in
  `posts/<slug>.carousel.html` (same slug as the assets dir, without a platform
  suffix). Reason: Blotato's CDN URL is external and can go down; the repo has
  to keep the bytes, not just the link.
- **Publications** → row in `POSTS-LOG.md` (date, platform, status, scheduled, live
  URL, submissionId, draft). Written by the `--log` flag of `post`; URL backfill with
  `post-status`.
- **Human-approved examples** (pieces that were liked, to reuse as a template) →
  `examples/<slug>.md` with the recipe + the reference copy.
