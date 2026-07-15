---
name: repurpose
description: Turns one long-form input (blog post, newsletter, YouTube transcript, or script) into 3 platform-native LinkedIn posts, 5 X/Twitter threads, and 2 short-form video scripts for Reels/TikTok. Extracts the core themes first, opens every output with a tested hook from the viral-hooks library, sizes each to its platform, and runs post-grader before returning. Triggers on "repurpose this," "turn this into posts," "break this into content," or any paste of long content with a request for multiple posts.
argument-hint: "[paste long-form content] [optional: platforms to prioritize]"
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Repurpose

> **Adaptación a ESTE proyecto (Blotato).** Dos cambios:
> - **La extracción de la fuente la hace Blotato**, no vos a mano. Para URLs/videos:
>   `python scripts/blotato.py source --type <youtube|article|tiktok|twitter|text> --url "..." --instructions "..."`.
>   Poléa hasta `completed` y usá ese contenido como input.
> - **Batch:** produce el batch en el idioma y wedge de tu marca (`brand-brief.md`). Corré las
>   piezas independientes (por plataforma) en paralelo con Task. Guardá los borradores en `posts/`.
> El resto (3 LinkedIn + 5 X threads + 2 scripts, hooks de viral-hooks, grader a 8+) igual.

You take one long piece of content and turn it into a week of platform-native posts. The creator gives you a blog post, an email newsletter, a YouTube transcript, or a raw script. You return 3 LinkedIn posts, 5 X threads, and 2 short-form video scripts — each one written for its platform, not copy-pasted across them.

This skill solves the two hardest parts of content distribution at once: turning one idea into many posts, and making sure each one gets read.

## When to Activate

- "Repurpose this [blog post / newsletter / transcript / video]"
- "Turn this into LinkedIn and Twitter content"
- "Give me a week of posts from this"
- The user pastes a long block of content and asks for posts.

If the input is short (a single idea, under a paragraph), this is the wrong skill — hand off to [post-writer](post-writer.md) instead.

## Workflow

### Step 1: Load context

1. Look for `brand-brief.md` in the current directory. If it exists, read it — use the voice, audience, CTA, and **Strong Opinion / Wedge** to shape every output. If it's missing, do not block. Repurpose works without a brief. Mention once that running [brand-brief](brand-brief.md) first sharpens the voice, then continue.
2. Confirm the source type (blog, newsletter, transcript, script). Transcripts and raw scripts have filler and verbal tics — plan to cut them.

### Step 2: Extract the core themes

Read the full input. Pull out:

- **The 1 central thesis** — the single biggest idea.
- **3-7 supporting points** — distinct sub-ideas, each strong enough to stand alone as a post.
- **Every concrete asset** — specific numbers, names, stories, quotes, results, and contrarian takes. These are the raw material for hooks and proof.

List the themes back to the user in 2-3 lines before writing, so they can redirect if you missed the point. Keep it short — do not make them approve an outline.

### Step 3: Map themes to outputs

You produce exactly:

- **3 LinkedIn posts** — pick the 3 themes with the most professional or story-driven angle.
- **5 X (Twitter) threads** — pick 5 themes that break into a sequence of punchy beats.
- **2 short-form video scripts** (Reels / TikTok) — pick the 2 most visual or emotional themes.

Reuse a strong theme across formats only when the angle changes. Do not publish the same post twice in different fonts.

### Step 4: Open every output with a hook

For the top of every post, thread, and script, invoke the [viral-hooks](viral-hooks.md) skill. Pass it the theme and the platform. It returns a tested hook pattern filled with specifics from the content. Never open with a generic AI intro.

- Match the hook category to the theme: a result or number → The Receipt, a strong opinion → Contrarian, a mistake → Negative Frame.
- Vary the category across the batch. A feed of 10 posts that all open the same way reads as formulaic.

### Step 5: Write each output to its platform

**LinkedIn posts (3):**
- Hook in the first 2 lines (about 140 characters before "...see more").
- 1,200-1,500 characters is the sweet spot.
- One idea per post. Short paragraphs, line breaks for skim.
- End with a comment-driving CTA (LinkedIn weights comments about 2x likes): a polarizing question or "what would you add?"
- No external links in the body. 3-5 hashtags optional at the end.

**X (Twitter) threads (5):**
- Tweet 1 is the hook. Under 280 characters, ideally 60-100. It has to earn the tap on "show this thread."
- 4-7 tweets per thread. One beat per tweet. No tweet should need the next to make sense.
- No hashtags. No links until the final tweet.
- Last tweet: a reply-driving CTA or a recap, plus an optional link or follow ask.

**Short-form video scripts (2):**
- **Hook (first 1.7 seconds):** the spoken line and the on-screen text. Both must stop the scroll. Pull from viral-hooks.
- **Body (15-40 seconds):** spoken script in short lines, with [on-screen text] and [b-roll / visual] cues in brackets.
- **CTA (final 3 seconds):** "Follow for more," "Save this," or "Comment [keyword]."
- Format as: `HOOK`, `BODY`, `CTA`. Keep total spoken length under 45 seconds.

### Step 6: Apply universal voice rules

Every output follows these:

- Contractions always (don't, you've, it's).
- Active voice, short sentences.
- Address the reader as "you."
- Numbers as digits ("3 tips" not "three tips").
- No em dashes in the post copy.
- One concrete idea per post.
- Specific details over generic claims. Pull the real numbers and names from the source.

### Step 7: Grade and improve

Run [post-grader](post-grader.md) on each output. The grader weights hook strength at 50%. Apply its fixes. Do not return any post scoring below 8/10 — loop on the hook until it clears.

### Step 8: Return the batch

Group the output by platform with clear headers:

```
## LinkedIn (3 posts)
### Post 1 — [theme] — [hook category] — [score]/10
[full post]
...

## X Threads (5)
### Thread 1 — [theme] — [hook category] — [score]/10
1/ [hook tweet]
2/ ...
...

## Short-Form Video Scripts (2)
### Script 1 — [theme] — [hook category]
HOOK: [spoken] / [on-screen text]
BODY: ...
CTA: ...
```

After the batch, ask: "Want me to schedule any of these? I can hand them to post-scheduler." If they say yes, pass the chosen posts to [post-scheduler](post-scheduler.md).

## What NOT to Do

- Don't copy the same text across platforms. Each platform gets a native rewrite, not a reformat.
- Don't exceed or shrink the counts. 3 LinkedIn, 5 X threads, 2 video scripts. If the source is too thin to support 10 distinct angles, say so and produce fewer strong posts rather than padding with weak ones.
- Don't open any output with a generic AI intro. Every top line comes from viral-hooks.
- Don't return a post below 8/10. Loop on the grader.
- Don't make the user approve a long outline. A 2-3 line theme summary is enough before you write.
- Don't leave transcript filler ("um," "you know," "so basically") in the output.
