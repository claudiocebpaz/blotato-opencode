# ANALYSIS — extending the Blotato pack into a multi-agent, multi-runtime system

*Written for the Blotato team. This is a partner-to-partner writeup of what we changed, why, and
what we'd love to see upstream. It's about **multi-agent orchestration** and **multi-runtime
portability** — not about any specific brand.*

---

## Where we started

Blotato's official content pack is a clean, well-scoped set of **7 skills** — content-coach,
brand-brief, viral-hooks, post-writer, post-grader, repurpose, post-scheduler. Out of the box it's:

- **Single-assistant.** One model reads the skills and does everything in one context — brief,
  write, grade, schedule.
- **Claude-only.** The skills are authored for Claude Code's `.claude/skills/` convention.
- **MCP-first.** Scheduling and media go through the Blotato MCP server.

That's a great starting point. The gaps we hit were about **scale of a real posting operation**:
one context doing every step burns tokens on mechanical work, there's no separation between "who
decides" and "who executes," visuals aren't covered, and we wanted to run the same system in a
second runtime.

## What we added

### 1. Multi-agent orchestration + explicit model routing
We split the flow into an **orchestrator** and **subagents**, and made cost a first-class routing
decision:

- **Opus orchestrates and owns the final QC gate.** It routes, asks the human clarifying questions,
  and verifies each returned piece against the repo's guidelines (`_base/voice.md`,
  `platform-specs.md`, `linkedin-craft.md`, plus the brand brief) before human approval. This check
  is never delegated — it's the quality gate.
- **Sonnet does judgment work** — copywriting (the write→grade loop), grading, voice QC.
- **Haiku does mechanical work** — script I/O, polling, log rows, asset copying, frontmatter checks.

The rule is *cheap-by-default, escalate only on QC failure*. Each isolable unit (platform × piece)
goes to its own subagent, in parallel when there are no dependencies, and each subagent gets
**only** the files it needs — not the whole repo. The net effect is that Opus never spends its
context on derivable work, and the token cost tracks the value of each step.

The control loop is deliberate: the copywriter **self-grades** with `post-grader` (hook = 50%) and
regenerates via Blotato until 8+. Then Opus does a **local verification** against the guidelines and
loops "verify → correct → regenerate via Blotato" until it's ≥90% in agreement — bouncing concrete
corrections back to the subagent rather than hand-editing. If it can't converge, it stops and brings
the human the diagnosis instead of lowering the bar.

### 2. A visuals skill (`visual-producer`)
The official pack doesn't generate visuals over the API, so we added one. It picks a template,
injects the brand's palette/font/logo, calls Blotato's **visual template API**, polls to done, and
saves the rendered bytes into the repo (not just the CDN URL). For truly branded carousels — where
the stock "Tutorial Carousel" looks generic — it renders our own **HTML→PNG** carousel
(`scripts/carousel/`) and uploads the PNGs via presigned URLs.

### 3. REST transport
We moved the default transport from MCP to **direct REST** through `scripts/blotato.py` (`write`,
`source`, `visual`, `post`, `post-status`, `slots-*`). MCP stays available as a fallback. This made
the system scriptable, debuggable, and runnable in headless/automation contexts where standing up an
MCP server is friction. A hard safety rule lives in the script: `post` **refuses** to publish
without `--next-free-slot` or `--schedule` — nothing goes out directly, everything hits the
calendar.

## Porting to opencode (the multi-runtime part)

The interesting finding: **opencode already supports Claude's skills natively.** We verified
empirically (opencode v1.17.18):

- `opencode debug skill` lists all 9 skills resolving to the project's `.claude/skills/` — **no
  plugin, no symlink, no config** required. opencode reads a `SKILL.md`'s `name` + `description`
  and ignores the rest, so the files are compatible as-is.
- `.opencode/agents/*.md` load as subagents natively (`mode: subagent`, `description`, model
  inherited from `opencode.json`).
- Project instructions load via `opencode.json` → `"instructions": ["CLAUDE.md"]` (opencode's
  documented instructions field), analogous to how Claude Code reads `CLAUDE.md`.

So the port is **not** a fork. There is **one** copy of the core (`_base/`, `scripts/`, the 9
`SKILL.md`), and each runtime is a **thin adapter**:

- `.claude/` — skills + agents in Claude Code's convention (agents carry `model:` for routing).
- `.opencode/` — three agent files + `opencode.json`. The agents are deliberately thin: they name
  the real skills (which now load) and defer methodology to the `SKILL.md` files, rather than
  re-inlining it.

Editing a `_base/*.md` or a `SKILL.md` changes behavior in **both** runtimes with no second file to
touch. We considered the SDK plugin route (`context.skill.transform(...)` to add a skills source)
but didn't need it — native discovery is simpler and has no moving parts. Worth noting for anyone
who assumes opencode needs a plugin to see Claude skills: it doesn't.

## Product feedback for Blotato

Offered as a partner, in priority order:

1. **Ship an official visuals skill.** Visuals are the highest-leverage gap in the pack. A
   first-party skill over the template API (with brand palette/font injection) would save every
   serious user from rolling their own, and would make carousels/infographics a native part of the
   pipeline instead of a bolt-on.
2. **Lead with REST; keep MCP as a mode.** MCP-only is real friction for scripting, automation, and
   headless runs. A documented REST path (or shipping the pack with a thin REST client) lowers the
   barrier a lot. MCP is great for interactive use — just not the only door.
3. **Separate "portable core" from "runtime adapter" in the pack's own structure.** The pack's
   value is the methodology (`_base/` + `SKILL.md`); the runtime wiring (`.claude/` vs `.opencode/`)
   is a thin shell. Structuring the official pack that way — one core, small per-runtime adapters —
   would make it trivially portable to opencode and anything else that reads `SKILL.md`, and would
   signal that skills are runtime-agnostic assets.
4. **Document the native opencode compatibility.** It's a genuine selling point that a Blotato
   Claude skill drops straight into opencode with zero glue. Saying so (and showing `opencode debug
   skill`) would help users adopt the pack in whichever runtime they already use.

## Acceptance we held ourselves to

- Both runtimes load the 9 skills from the **single** in-repo copy (verified: `opencode debug
  skill` → all 9 resolve to `.claude/skills/`; Claude Code reads the same directory).
- Thin adapters only — no duplicated methodology between `.claude/` and `.opencode/`.
- No secrets in the repo — `scripts/.env` gitignored, `opencode.json` uses `{env:BLOTATO_API_KEY}`,
  and the only key placeholder is in `scripts/.env.example`.
- Brand-agnostic — one brand per clone, configured in `brand-brief.md` + `branding.md` +
  `_base/accounts.md`; no brand or multi-brand routing baked into the framework.
