---
name: post-scheduler
description: Schedule a finished social post to one or more platforms via the Blotato REST API (direct, not MCP). Handles single- and multi-platform scheduling, resolves accounts from the brand's accounts.md, applies a final pre-publish check, and returns scheduled time + post IDs. Triggers on "schedule this," "post this to [platform]," or as the final step in content-coach, post-writer and repurpose flows. Falls back to saving a copy-paste file if the API key isn't set.
argument-hint: "[post text or path] [platform(s)] [optional time]"
allowed-tools: Read, Write, Edit, Glob, Bash, AskUserQuestion
---

# Post Scheduler (direct API)

You take an approved post and ship it to the Blotato **calendar** via the direct REST API
(`scripts/blotato.py`), NOT via MCP. You do NOT write or revise the post — that's `post-writer`'s
job. By the time a post reaches you, it's been graded and approved. **Nothing publishes
immediately: everything is scheduled.**

> **Why direct API:** this project uses `scripts/blotato.py` (requires `BLOTATO_API_KEY`
> in `.env` at the project root) to be faster and work the same in Claude Code, Desktop, and Cowork,
> without depending on MCP.

## When to Activate
- "Schedule this post" / "Schedule this to your brand's LinkedIn"
- Auto-called as the final step of `content-coach`, `post-writer`, or `repurpose` after approval.

## Workflow

### Step 1: Get inputs
1. **Post text** — inline, or path to a file (ideally `posts/....md`).
2. **Platform(s)** — one or more from: instagram, facebook, twitter, linkedin.
3. **Account** — to resolve the correct `accountId`/`pageId` (read `_base/accounts.md`).
4. **Media** — the `mediaUrls` that `visual-producer` returned (or empty if text-only).
5. **Time** — defaults to `--next-free-slot`; or an ISO timestamp if the user specified one.

If the platform or brand is missing, ask. Don't guess.

### Step 2: Final pre-publish check
Before touching the API, review the post one more time:
- [ ] Zero em dashes
- [ ] No banned filler ("really", "very", "just", "basically", "literally", "actually")
- [ ] No filler openers ("in today's world", "let me tell you")
- [ ] Active voice; contractions used
- [ ] Correct number of hashtags (0 on Twitter/LinkedIn/Facebook; 3-5 on Instagram)
- [ ] Instagram: `mediaUrls` are attached
- [ ] LinkedIn: no external links in the body

If anything fails, **stop and report**. Wait for an explicit response from the user. Don't auto-fix.

### Step 3: Resolve the account
Read `_base/accounts.md`. For example:
- LinkedIn → `--account <ACCOUNT_ID> --page <PAGE_ID>`
- X → `--account <ACCOUNT_ID>`

Facebook requires `--page` (pageId) as mandatory. If a platform has several possible accounts, ask which one.

### Step 4: Schedule (one call per platform)
```bash
python scripts/blotato.py post \
  --account <accountId> --platform <linkedin|twitter|instagram|facebook> \
  [--page <pageId>] \
  --text-file <path> \
  [--media "<url1,url2,...>"] \
  --next-free-slot            # or: --schedule "2026-07-20T13:00:00Z"
```
Rules:
- **Always** `--next-free-slot` or `--schedule`. The script refuses to publish without one of the two.
- The script guarantees `content.platform == target.targetType`.
- Multi-platform: one call per platform. If the copy exceeds a platform's limit, ask how to handle it (shorten / skip / override). Don't truncate on your own.

### Step 5: Report
Show a confirmation table:
```
## Scheduled
| Platform | Brand | Account | Time | Status | postSubmissionId |
|---|---|---|---|---|---|
| LinkedIn | your brand | <PAGE_ID> | Next free slot | scheduled | abc-123 |
| Twitter | your brand | <PLATFORM_HANDLE> | Next free slot | scheduled | def-456 |

View and edit at https://my.blotato.com/scheduler
```
For partial failures (3 of 5 ok), report success and failure separately. Don't roll back.

### Step 6: Fallback (no API key)
If `python scripts/blotato.py whoami` fails or there's no `.env` at the root:
```
Blotato is not connected (missing the API key in .env). Saving the post to paste manually.
```
Save to `posts/<slug>-ready-to-paste.txt`:
```
=== POST FOR [PLATFORM] ===
Schedule for: [time or "manual post"]

[POST TEXT]

=== END ===
```
If multi-platform, one block per platform. Tell the user the path. Never fail the flow.

## Error handling
- **401/403** → the API key is failing or expired. Tell the user to check `.env` (root) or regenerate the key.
- **429** → rate limit; wait the number of seconds the message says and retry once.
- **`--next-free-slot` with no slots** → there are no slots for that platform/account. Tell the user to create
  slots (`python scripts/blotato.py slots-create ...`) or use `--schedule` with an exact time.
- **Post over the char limit** → don't truncate; ask.
- **Network failure** → retry once; if it fails again, save to the fallback and report.

## What NOT to Do
- Don't auto-fix voice issues: just flag and ask (that's post-grader/post-writer's job).
- Don't skip the pre-check: it's the last line of defense.
- Don't publish instantly by default. Only publish now if the user explicitly says "post now".
- Don't report "done" without the `postSubmissionId`.
