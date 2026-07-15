# Platform specifications

> Limits, the CTA each algorithm rewards, and max cadence. The `post-writer` and the
> `post-grader` read this to adapt each piece. Exceeding the cadence lowers reach.

## Quick table

| Platform | Copy length | Hook | CTA rewarded | Hashtags | Max cadence/day |
|---|---|---|---|---|---|
| LinkedIn | 1,200–1,500 chars | first ~140 chars (before "see more") | **comments** (~2x vs likes) | 3–5 optional, at the end | 2 |
| X / Twitter | 280 (ideal 60–100) | first 3 words | **replies** (~75x vs likes) | 0 | 5 (<10k), 15 (>10k) |
| Instagram | 2,200 (hook in 125) | first 125 chars | feed: **saves**; reels: **completion** | 3–5 niche, at the end | 1 image + 4 reels |
| Facebook | 40–80 optimal | short sentence | **shares** ("tag someone") | 0 | 4 reels |

## CTA per platform (use the one the algorithm rewards)

- **LinkedIn** → polarizing question / "what would you add?" (seeks comments).
- **X** → polarizing take / "tell me I'm wrong" (seeks replies).
- **Instagram feed** → "save this for later" / "send it to whoever needs it".
- **Instagram reels** → a hook that retains to the end + "save".
- **Facebook** → "tag someone who…" (seeks shares).

## Rules per platform

**LinkedIn**
- **Full craft in `_base/linkedin-craft.md`** (mobile-first format, "hidden text",
  5 rhythm hacks, 8-step storytelling). Always load it for LinkedIn pieces.
- No external links in the body (they kill reach) → link in the first comment.
- Space out the text, no blocks: paragraphs of 1–3 lines + white space.
- **Hidden text:** strong hook up top, 2–3 blank lines, then the body (forces the "see more").
- Emojis YES, but **only functional and in moderation** (✅/❌, markers), not decorative.
- Repost the same post in the afternoon to resurface it.
- Carousels = a PDF document Blotato builds from 2–10 images (no video). See `templates.md`.
- Via API you CANNOT: publish Articles, create polls, repost, or put video inside a carousel.

**X / Twitter**
- No hashtags, no links in the body of the main tweet.
- **Emojis YES on X** (unlike LinkedIn): one lead emoji per tweet in threads breaks the
  plain-text brick and gives rhythm/scannability. It should map to the concept (🛑 stop, ⏱️ cap,
  ✅ check, 🧠 memory, 💬 CTA). One per tweet, no spam. The tweet-1 hook can stay clean.
- Threads: tweet 1 is pure hook; link only in the last tweet.
- New accounts: warm up 1–2 weeks posting manually before automating.

**Instagram**
- **Always requires media** (won't publish text only).
- Carousel = 2–10 images.
- Via API you CANNOT: label "AI Generated", third-party music, or a link sticker in Stories (add them by hand in the app).
- Account must be Business or Creator.

**Facebook**
- Requires a Page + `pageId`.
- Videos always publish as Reels (9:16).
- No engagement bait like "comment YES".

## Warm-up for new accounts (critical)
Never connect third-party apps or mass-post on a freshly created account (they flag it
as a bot). Warm up manually 1–2 weeks (4 for TikTok, 2 for Pinterest) before automating.
