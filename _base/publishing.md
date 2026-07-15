# Blotato API mechanics

> All the heavy lifting (generating visuals, scheduling, publishing) is done by Blotato via API.
> Base URL: `https://backend.blotato.com/v2` · Header: `blotato-api-key: <API_KEY>`
> Everything is asynchronous: you create → it returns an id → you poll status.
> The Python client in `scripts/blotato.py` wraps all of this.

## Authentication
- Header on every request: `blotato-api-key: <API_KEY>`.
- The key comes from Settings → API at my.blotato.com. **Generating it ends the trial and activates the paid plan.**
- The key may end in `=` (base64 padding): it's part of the key, don't trim it.
- Validate: `GET /users/me`.

## Golden rule: nothing publishes directly
**Always** schedule. When creating a post, pass `scheduledTime` (ISO 8601) **or** `useNextFreeSlot: true`.
If you send neither, it publishes instantly. ⚠️ These fields go at the **root level**,
siblings of `post`. If you put them inside `post`, they're ignored and it publishes right away.

## Key endpoints

| Method | Path | For what |
|---|---|---|
| GET | `/users/me` | Validate the key |
| GET | `/users/me/accounts` | List accounts → get `accountId` |
| GET | `/users/me/accounts/:id/subaccounts` | FB / LinkedIn pages → `pageId` |
| POST | `/videos/from-templates` | **Generate** carousel / image / video |
| GET | `/videos/creations/:id` | Poll the visual's status → `imageUrls` / `mediaUrl` |
| POST | `/source-resolutions-v3` | Extract content from URL / video / text |
| GET | `/source-resolutions-v3/:id` | Poll the extraction |
| POST | `/posts` | Create + schedule a post |
| GET | `/posts/:id` | Poll publish status |
| GET | `/schedule/slots` | View calendar slots |
| POST | `/schedule/slots` | Create slots (cadence) |

## Create + schedule a post

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

Rules:
- `content.platform` MUST be identical to `target.targetType`.
- `mediaUrls`: public URLs (the ones the visual-producer returns). `[]` if it's text only.
- Facebook requires `target.pageId`. LinkedIn `pageId` is optional (omit = personal profile).
- Twitter doesn't ask for extra fields.
- Response: `{ "postSubmissionId": "..." }` → poll `GET /posts/:id` (`in-progress`/`published`/`failed`).

## Writing the copy (Blotato does it, not Claude)

Blotato writes the text via API through `source-resolutions-v3` with `customInstructions`.
Claude only assembles the brief + the instructions; Blotato generates.

```bash
# Write from a brief/topic (Blotato drafts)
python scripts/blotato.py write \
  --brief "AI agent loops: why uncut loops burn tokens" \
  --instructions "Write a LinkedIn post in English. Hook-first (first 140 chars). ~1300 chars. \
One idea. Voice: technical, direct, no fluff. Wedge: most 'AI agents' are a while-loop with extra steps. \
Comment-driving CTA. No em dashes, no hashtags in body."

# With prior web research (Blotato uses perplexity-query)
python scripts/blotato.py write --research --brief "latest on AI agent reliability" --instructions "..."
```
Returns `{ "title", "content" }`. That `content` is the copy. Rules:
- The instructions MUST include: language, platform, length, hook-first, the brand's voice + wedge,
  CTA type, and the voice rules (no em dashes, hashtags, etc.). They come from the brand-brief + platform-specs.
- If the grader rejects it, it's **regenerated with corrected instructions** (Claude doesn't rewrite).
- MCP equivalent: `blotato_create_source` (see `transport.md`).

> Note: the app's polished AI Agent gives better quality but is app-only. If `write` isn't enough,
> you can go up to Tier 3 (browser) — see `transport.md`.

## Generate a visual (Blotato does it)

```json
{ "templateId": "53cfec04-...", "inputs": { ... }, "render": true }
```
Response `{ "item": { "id": "...", "status": "queueing" } }` → poll `GET /videos/creations/:id`
until `status: "done"` → use `imageUrls` (carousel/image) or `mediaUrl` (video) as the post's `mediaUrls`.
See the catalog and inputs in `templates.md`.

## Cadence (Schedule Slots)
Slots define the calendar and are set in **UTC**. `useNextFreeSlot` lands in the next
free slot for that platform/account. With no slots configured, `useNextFreeSlot` has nowhere to land.
Create with `POST /schedule/slots` body `{ "slots": [ { hour, minute, day, selectedTargets:[...] } ] }`.

## Rate limits / gotchas
- `POST /posts` and `POST /videos/from-templates`: 30/min. Polling: 60/min.
- `429` → the message says how many seconds to wait before retrying.
- Confusing `postSubmissionId` (publish polling) with the published post id (analytics) is a common error.
