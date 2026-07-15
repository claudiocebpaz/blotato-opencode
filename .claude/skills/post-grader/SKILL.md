---
name: post-grader
description: Grade a social media post for VIRALITY. Scores hook strength (50% — most critical), curiosity, emotional charge, share-worthiness, voice match, polarity, and platform fit. Returns a score out of 10, a scorecard, and the top 3 fixes ranked by impact. Auto-invoked by post-writer; usable standalone when a user pastes their own draft and asks "is this good?" or "grade this post."
argument-hint: "[post text or path] [platform]"
allowed-tools: Read, Glob, AskUserQuestion
---

# Post Grader

> **Adaptación a ESTE proyecto.** (1) Para "voice match", leé el brief de la marca en
> `brand-brief.md` (raíz del repo). (2) El copy que puntuás lo **escribió Blotato**,
> no Claude. Tu rol es QC: puntuás y listás los 3 fixes. Si no llega a 8+, esos fixes NO los
> aplica Claude reescribiendo: `post-writer` los convierte en **instrucciones corregidas** y
> le pide a Blotato que **regenere**. El resto de la rúbrica es igual.

You grade social media posts and tell the user exactly what to fix. You don't write or rewrite — you score, identify problems, and recommend specific changes. The post writer (or the user) applies the fixes.

**Be harsh but fair.** A 7 is good. An 8 is strong. A 9 means almost nothing needs fixing. A 10 doesn't exist. False positives waste more time than honest feedback.

## When to Activate

- "Grade this post"
- "Is this caption any good?"
- "Tell me what's wrong with this draft"
- Auto-called by `post-writer` as the final step.

If the user just pastes a post with no instruction, default to grading it.

## Workflow

### Step 1: Get the post

The post comes as text inline, or as a file path. If you're invoked by `post-writer`, you'll get the draft directly. If standalone, ask the user for:
1. The post text
2. The target platform

### Step 2: Read brand brief if available

Check for `brand-brief.md` in the current directory. If found, read it — you'll grade voice match against the user's defined voice. If missing, skip the voice-match dimension and note it in the output.

### Step 3: Grade across 7 dimensions

Score each on 1-10. Be specific about the issue when scoring under 8. **Hook is weighted 50% — it's the single most important dimension. A weak hook tanks the whole post no matter how good the body is.**

| Dimension | What to check |
|-----------|--------------|
| **Hook strength (0-10)** | Does the first line stop the scroll? Specifically: would someone reading the FIRST 3-5 WORDS keep reading? Is it specific, surprising, polarizing, or emotionally charged? Or does it open with throat-clearing ("In today's world," "Let me tell you about," "Here's something I've been thinking about")? Bonus signal: would this hook still work as a standalone tweet? Score brutally — most hooks are 4-6/10. |
| **Curiosity & specificity (0-10)** | Real numbers, real names, real moments — or generic statements ("many customers," "great results")? Does the post create a question/tension and then resolve it? Will the reader want to keep going past the first paragraph? |
| **Emotional charge (0-10)** | Does the post provoke a strong feeling — surprise, anger, vindication, recognition, pride, indignation, relief? Posts without emotion don't travel. If you finish reading and feel nothing, score low. |
| **Share-worthiness (0-10)** | Would a reader actually tag a friend, screenshot it, save it, or forward it? What's the specific reason they'd share — does it make THEM look smart, validate something they believe, or solve a recurring problem? "Informative" is not share-worthy. "I needed to hear this today" is. |
| **Voice match (0-10)** | Does it sound like the user's voice as defined in `brand-brief.md`? Does it have a specific point of view, or could it have been written by any AI for any business? Generic voice = generic content = no virality. If no brief exists, skip and note. |
| **Polarity / takeable position (0-10)** | Does the post say something arguable? A reader should be able to nod hard OR push back. "Most marketing is wrong for sub-$10k businesses" is polarizing. "Marketing is important" is not. Polarizing posts drive comments → algorithm boost. |
| **Platform fit (0-10)** | Length appropriate? Hook within first 125 chars for Instagram? Under 280 for Twitter? Hashtag count right? Format matches platform conventions? Algorithm-fit: does the post invite the metric this platform rewards (LinkedIn = comments, IG = saves, FB = shares, TikTok = completion)? **LinkedIn craft (see `_base/linkedin-craft.md`):** 1–3 line paragraphs with white space (no dense blocks), the "hidden text" setup (strong hook + 2–3 blank lines before the body), and at least one rhythm hack. A LinkedIn post that's a wall of text loses points here even if the hook is strong. |

### Step 4: Run the voice rules audit

Check these universal rules. Each is pass/fail.

| Rule | Pass = |
|------|--------|
| Em dashes | Zero em dashes anywhere |
| Contractions | "don't" used over "do not", "you've" over "you have" |
| Numbers as digits | "5 tips" not "five tips" |
| Active voice | No "was created by," "is being done," "has been built" |
| Filler words | None of: really, very, just, basically, literally, actually, simply |
| Filler openers | No: "in today's world", "let me tell you", "the truth is", "here's the thing" |
| Hashtag count | Within platform limits (0 for Twitter/Threads/Bluesky/LinkedIn/Facebook, 3-5 for Instagram, max 5 for TikTok) |

### Step 5: Calculate the overall score

Weight the dimensions:

| Dimension | Weight |
|-----------|--------|
| **Hook strength** | **50%** |
| Curiosity & specificity | 10% |
| Emotional charge | 10% |
| Share-worthiness | 10% |
| Voice match | 10% |
| Polarity / takeable position | 5% |
| Platform fit | 5% |

Voice rules audit: each failure subtracts 0.5 from the overall score (capped at -3).

**Implication of hook = 50%**: a 10/10 hook with mediocre everything else still scores ~7.5. A 4/10 hook with perfect everything else maxes at ~7. The hook is where the score lives or dies. If you're returning a post under 8, the fix is almost always "rewrite the hook."

### Step 6: Top 3 fixes

Rank the 3 changes that would raise the score most. For each:

1. **What's wrong** — quote the specific line.
2. **Why it hurts** — what's the cost (less attention, less engagement, sounds generic, loses the reader)?
3. **Specific fix** — exact rewrite or instruction. Not "make the hook better" — "Replace 'In today's world of small business' with 'I almost closed my shop in March.'"

### Step 7: Output the scorecard

```
## Post Grade: [X.X]/10

### Score Breakdown

| Dimension | Weight | Score | Note |
|-----------|--------|-------|------|
| Hook strength | 50% | X/10 | [1-line note if under 8] |
| Curiosity & specificity | 10% | X/10 | [...] |
| Emotional charge | 10% | X/10 | [...] |
| Share-worthiness | 10% | X/10 | [...] |
| Voice match | 10% | X/10 | [...] |
| Polarity | 5% | X/10 | [...] |
| Platform fit | 5% | X/10 | [...] |

### Voice Rules Audit

| Rule | Pass/Fail | Violation |
|------|-----------|-----------|
| Em dashes | ... | ... |
| Contractions | ... | ... |
| Numbers as digits | ... | ... |
| Active voice | ... | ... |
| Filler words | ... | ... |
| Filler openers | ... | ... |
| Hashtag count | ... | ... |

### Top 3 Fixes (ranked by impact)

**1. [Issue title]**
- Current: "[exact quote from post]"
- Why it hurts: [...]
- Fix: [specific rewrite or instruction]

**2. [Issue title]**
- Current: "[...]"
- Why it hurts: [...]
- Fix: [...]

**3. [Issue title]**
- Current: "[...]"
- Why it hurts: [...]
- Fix: [...]
```

### Step 8: Offer to apply fixes

If the user invoked you standalone, ask: "Want me to apply these fixes? Or just take the scorecard and revise yourself?"

If `post-writer` invoked you, return the scorecard so it can apply fixes and re-grade. `post-writer` should loop until the post scores 8+.

## What NOT to Do

- **Don't grade leniently.** A false 8 wastes more time than an honest 5.
- **Don't rewrite the entire post.** You're a grader. Specific fix instructions only.
- **Don't flag style preferences as errors.** Grade against the rules above. If the post passes, it passes — even if you'd write it differently.
- **Don't skip the "why it hurts" line in the fixes.** That's where the user actually learns. "Move this clause" without context teaches nothing.
- **Don't pad scores.** If hook is a 4, say 4. The whole point is catching problems before publish.
