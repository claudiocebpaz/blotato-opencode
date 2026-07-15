# Transport policy — API / MCP / browser

> How to talk to Blotato. General rule: **use whatever is most convenient, don't stay limited
> by the API.** There are 3 paths, in order of preference.

## Tier 1 — Direct API (default)
`scripts/blotato.py` against `https://backend.blotato.com/v2` with `BLOTATO_API_KEY`.
- **When:** by default, especially in Claude Code (TUI/VS Code). Fast and portable.
- **Requires:** the key in `.env` (project root).

## Tier 2 — MCP (when convenient or the key is missing)
The MCP's `blotato_*` tools (already connected in Cowork/Desktop).
- **When:**
  - There's no `BLOTATO_API_KEY` configured (the MCP doesn't need it, it uses its own auth).
  - It's more convenient (some tools poll internally, e.g. `blotato_create_source`).
  - You're in Cowork/Desktop where the MCP is already at hand.
- **Note:** API and MCP expose **the same** capabilities (1:1 mapping). The MCP doesn't unlock
  anything the API doesn't have; it's just another access path. Choose by convenience, not by power.

Quick API ↔ MCP mapping:
`/users/me`→`blotato_get_user` · `/users/me/accounts`→`blotato_list_accounts` ·
`/posts`→`blotato_create_post` · `/source-resolutions-v3`→`blotato_create_source` ·
`/videos/from-templates`→`blotato_create_visual` · `/schedules`→`blotato_list_schedules` ·
`/schedule/slots`→(via API) · analytics/comments/messages→`blotato_*` equivalents.

## Tier 3 — Browser (only for what is 100% app-only)
Drive the Blotato app (my.blotato.com) with Claude in Chrome / computer-use.
- **When:** ONLY for features that neither API nor MCP expose. Specifically:
  - The app's polished **AI Agent / Remix** (better writing quality than `source-resolutions`).
  - Configuring native Brand Kits, or any UI tweak.
- **When NOT:** for publishing/scheduling/generating visuals/writing from instructions → that's already
  in Tier 1/2, don't drop down to the browser.
- **Watch out:** it's slower and more fragile. Last resort, with the user's approval.

## Decision rule
1. Can the API do it? → Tier 1 (or Tier 2 if it's more convenient or the key is missing).
2. Is it a capability that neither API nor MCP have (e.g. the app's AI Agent quality)? → Tier 3.
3. Never refuse a task "because the API can't": go up a tier until you solve it.
