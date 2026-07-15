---
name: post-writer
description: Write a complete social media post (hook + body + CTA) from a topic or idea, sized for the target platform. Reads brand-brief.md for voice and audience context, applies proven hook patterns, and auto-runs post-grader as a final quality pass before returning the post. Triggers on "write me a post about X," "draft a [platform] post," or any specific writing request with a topic.
argument-hint: "[topic or idea] [platform]"
allowed-tools: Read, Write, Edit, Glob, AskUserQuestion
---

# Post Writer

> **⚠️ CAMBIO DE ROL EN ESTE PROYECTO: el que ESCRIBE es Blotato, no Claude.**
> Claude NO redacta el copy. Este skill arma las **instrucciones** y le pide a Blotato que
> genere el texto (vía `source-resolutions-v3` / `python scripts/blotato.py write`). Toda la
> metodología de abajo (11 patrones de hook, reglas de CTA, reglas de voz, constraints por
> plataforma) NO es lo que Claude escribe: es lo que Claude **le instruye a Blotato**.
>
> **Flujo:**
> 1. Recibís `[topic] [plataforma]`. Leé `brand-brief.md` (idioma + wedge) +
>    `_base/` (voice, hooks, platform-specs). El brief vive en la raíz del repo.
>    **Si la plataforma es LinkedIn, cargá también `_base/linkedin-craft.md`** e incluí sus
>    reglas (formato mobile-first, "texto oculto", hacks de ritmo, storytelling 8 pasos) en
>    las instrucciones a Blotato.
> 2. **Armá el bloque de instrucciones** para Blotato, incluyendo: idioma de la marca,
>    plataforma + su largo/constraints, "hook-first" y qué patrón de hook usar (de `viral-hooks`),
>    la voz + el **wedge** de la marca, el tipo de CTA que premia la plataforma, y las reglas de
>    voz (`_base/voice.md`: sin em dashes, sin palabras prohibidas, hashtags correctos).
> 3. **Llamá a Blotato para que escriba:**
>    ```bash
>    python scripts/blotato.py write --brief "<topic + ángulo>" --instructions "<el bloque del paso 2>"
>    ```
>    (o el equivalente MCP `blotato_create_source` si es más conveniente — ver `_base/transport.md`).
>    Usá `--research` si conviene que Blotato investigue la web primero.
> 4. Tomá el `content` que devolvió Blotato y pasalo a **post-grader**.
> 5. Si el grader puntúa < 8, **NO reescribas vos**: corregí las **instrucciones** (hook más
>    fuerte, más específico, etc.) y volvé a llamar a `write`. Loop hasta 8+.
> 6. Guardá el copy aprobado en `posts/YYYY-MM-DD-<slug>-<plataforma>.md`. Si lleva
>    visual, indicá qué template para `visual-producer`.
>
> El resto del documento describe la metodología que va DENTRO de las instrucciones a Blotato.

You take an idea and a platform, and return a finished post: hook, body, CTA. The output is graded and improved before the user sees it. They get a polished draft, not a first draft.

## When to Activate

- "Write me a [platform] post about [topic]"
- "Draft an Instagram caption for [idea]"
- User has both a topic AND a platform in mind.

If the topic is missing, ask. If the platform is missing, ask. Don't fill in defaults.

## Workflow

### Step 1: Load context

1. Look for `brand-brief.md` in the current directory. **If missing, automatically invoke the `brand-brief` skill to capture it now.** Don't tell the user to "run brand-brief first" — just walk them through the brief, save it, then continue.
2. Read the brief once it exists. Pay special attention to the **Strong Opinion / Wedge** section — that's the viral fuel for contrarian-take and "most people think X" hooks.
3. Confirm the topic and platform with the user if either is unclear.

### Step 2: Pick a hook pattern

**The hook is 50% of the post-grader score. If the hook is weak, the post can't recover.** Pick a pattern that fits the topic AND the user's wedge from `brand-brief.md`.

Choose ONE of these proven patterns. These are public templates from top short-form creators.

**1. The Reframe (one-liner flip)**
> Common belief, flipped in one sentence.
> Example: "Your 9-5 isn't killing your dreams. Wasting your 5-9 is."

**2. The Parallel Contrast**
> [Group A] does X. [Group B] does Y.
> Example: "Rich people buy time. Poor people buy stuff."

**3. The Specific Number Hook**
> Lead with a concrete, surprising number.
> Example: "I tested 47 candle scents. Only 3 sold."

**4. The Question Hook**
> Open with a question that makes the reader stop and answer.
> Example: "What's the one thing you'd quit if you weren't scared?"

**5. The Vulnerable Story Hook**
> Drop the persona. Lead with a real moment.
> Example: "I almost shut down my shop in March. Here's what saved it."

**6. The Contrarian Take**
> State the unpopular position.
> Example: "Most marketing advice is wrong for businesses under $10k/month."

**7. The Pain Point List**
> Stack 2-3 specific pains the reader recognizes.
> Example: "You spend hours writing posts. Nobody comments. You wonder if it's worth it."

**8. The Behind-the-Scenes Hook**
> "Here's what nobody tells you about [thing]."
> Example: "Here's what nobody tells you about handmade businesses."

**9. The Receipts Hook (high-virality, credibility-driven)**
> "I [did specific thing] for [time period]. Here's what happened."
> Or: "I tested [N] [things]. Only [smaller N] worked."
> Example: "I tested 47 candle scents. Only 3 sold."
> Example: "I posted on Instagram every day for 90 days. Engagement dropped 60%."
> Why it works: specific numbers + earned right to speak + curiosity gap (what happened?).

**10. The "Most People" Reverse Hook (high-virality, polarizing)**
> "Most people think [common belief]. Here's why they're wrong."
> Or: "[Audience] keeps telling me [X]. They're missing the point."
> Example: "Most candle makers think scent is the product. The product is calm."
> Example: "Every coach tells you to find your niche. Find your enemy first."
> Why it works: forces the reader to pick a side. Polarity drives comments. Pull the wedge from `brand-brief.md`.

**11. The Stolen Lesson Hook (high-virality, tactical)**
> "I copied [specific thing]. Here's what happened."
> Or: "[Famous person/brand] does [specific thing]. I tried it. Result: [outcome]."
> Example: "I copied Apple's product page format. Sales went up 23%."
> Example: "Hormozi gives away his entire course for free. I copied that. My email list 4x'd."
> Why it works: borrowed credibility + tested-by-me proof + the reader can copy it too.

**Pattern picking guide:**
- Customer story → Vulnerable Story Hook (#5)
- Strong opinion / wedge → Reverse Hook (#10) or Reframe (#1)
- Numbers / data / case study → Receipts Hook (#9) or Specific Number Hook (#3)
- Industry critique → Reframe (#1), Contrarian Take (#6), or Reverse Hook (#10)
- Tip / how-to → Stolen Lesson Hook (#11) or Pain Point List (#7)
- Recognition / "you do this" → Pain Point List (#7) or Vulnerable Story (#5)

When in doubt, prefer #9, #10, or #11 — they have the highest virality ceiling.

### Step 2.5: Iterate on the hook (CRITICAL)

Because hook = 50% of the score, write the hook FIRST and rewrite it 3-5 times before touching the body.

1. Draft 3 hook variations using different patterns from above.
2. Read each one out loud. Would you stop scrolling for it?
3. Apply the **first 3-words test**: do the first 3 words alone create curiosity, surprise, or emotional pull? "Here's what I" — fail. "I tested 47" — pass. "Most people think" — pass.
4. Pick the strongest variation. Refine it until every word earns its place. Cut filler ("really," "actually," "just," "the truth is").
5. The final hook should pass these checks:
   - Specific number, name, or moment in it (not abstract)
   - Creates a question the reader needs answered
   - Could stand alone as a tweet
   - Doesn't sound like AI

Don't proceed to the body until the hook is genuinely strong. A weak hook = wasted body.

### Step 3: Draft the body

Body rules (apply ALL):

- **Length**: Match platform constraints (see Platform Constraints below).
- **Specificity**: Use real numbers, real names, real situations. Not "many customers" — "the customer who emailed me Tuesday."
- **One idea**: One concrete insight per post. If it's two ideas, save the second for another post.
- **You/your**: Address the reader directly. Not "people who run small businesses" — "you, running your business."
- **Active voice, short sentences**: Mix in 1-2 short sentences for rhythm.
- **No filler**: Cut "in today's world," "let me tell you," "the truth is."
- **LinkedIn only** — apply `_base/linkedin-craft.md`: 1–3 line paragraphs with white space, the
  "hidden text" trick (strong hook, then 2–3 blank lines, then body to force the "see more"),
  at least one rhythm hack (rule of 3 / sentence ladder / numbered list / anaphora), and the
  8-step story structure when the angle is narrative. Functional emojis only (✅/❌), in moderation.

### Step 4: Add the CTA

One CTA per post. Not three. Pull from `brand-brief.md` (the "Primary CTA" field), but adapt to **what the platform's algorithm rewards** (see Step 4.5 below).

**Share-driving CTAs (strongest — they trigger the metric algorithms reward most):**
- "Tag someone who needs to hear this." (drives shares + tags)
- "Save this for [specific moment they'll need it]." (drives saves)
- "Send this to one person who [specific trait]." (drives DMs)
- "Screenshot this and put it on your wall." (drives saves + shares)

**Comment-driving CTAs (great for LinkedIn, Twitter, Threads):**
- "What's the [specific thing] you'd add to this list?"
- "Is this you, or am I overthinking it?"
- "Tell me I'm wrong." (polarizing, drives comments)
- A polarizing question that forces the reader to pick a side

**DM-driving CTAs (great for Instagram, Facebook lead gen):**
- "Comment '[KEYWORD]' and I'll send you [specific resource]."
- "DM me '[KEYWORD]' if you want my [thing]."
- These trigger DM automations and grow lists.

**Weak CTAs to avoid:**
- "What do you think?" (too vague — produces nothing)
- "Like and share!" (begging, algorithm penalizes)
- "Click the link in bio" (only works with strong reason)
- "Let me know in the comments" (passive, no specificity)

### Step 4.5: Match the CTA to the platform's algorithm

Each platform rewards a different metric. Pick the CTA that drives THAT metric.

| Platform | What it rewards most | Best CTA type |
|----------|---------------------|---------------|
| LinkedIn | Comments (2x weight vs likes) | Polarizing question, "what would you add?" |
| Instagram (feed) | Saves, then shares | "Save this for...", "Send this to..." |
| Instagram (Reels) | Completion, then saves | On-screen text + "Save for later" |
| Facebook | Shares, saves | "Tag someone who needs this" |
| Twitter / X | Replies (75x weight vs likes) | Polarizing take, "tell me I'm wrong" |
| Threads | Replies | Same as Twitter |
| TikTok | Watch-time / completion | Hook in first 1.7s; on-screen text "wait for it" |
| Substack Notes | Restacks (= shares) | Punchy, screenshottable insight |

### Step 5: Apply universal voice rules

Run this checklist before passing to grader:

- [ ] Contractions used (don't, you've, it's, won't)
- [ ] Zero em dashes
- [ ] Numbers written as digits ("5 tips" not "five tips")
- [ ] Active voice throughout
- [ ] No "really," "very," "just," "literally," "actually," "basically" — these are filler
- [ ] No metaphors that aren't earning their keep
- [ ] Reads like a real person, not a content template

### Step 6: Auto-invoke post-grader

Run the `post-grader` skill on your draft. Get the score and fix recommendations. Apply them. Re-grade if needed. **Do not return a post scoring below 8/10.** Loop until it scores 8+.

### Step 7: Return the final post

```
**Platform**: [platform]
**Hook pattern used**: [name]
**Quality score**: [X/10]

---
[Final post text]
---

**Why this works**: [1 sentence on what makes it strong]
```

If the user is in a `content-coach` flow, hand off to scheduling. If they invoked you directly, ask if they want to schedule via `post-scheduler` or just take the text.

## Platform Constraints (essentials)

- **Twitter/X**: 280 chars max. Sweet spot 60-100 chars. No hashtags. No links in body.
- **Threads**: 500 chars max. No hashtags.
- **Bluesky**: 300 chars max. No hashtags.
- **LinkedIn**: Hook in first 2 lines (~140 chars before "See more"). Sweet spot 1,200-1,500 chars. No external links in body. 3-5 hashtags optional at end.
- **Instagram**: Hook in first 125 chars. Requires media. 3-5 niche hashtags at end. One CTA.
- **Facebook**: 40-80 chars optimal. No hashtags. No engagement bait ("comment YES").
- **TikTok caption**: Under 150 chars for most posts. 5 hashtags max. Keyword in first 30 chars.

When a post is for multiple platforms, write the longer-platform version, then ask if they want a shortened version for stricter platforms (Twitter/Bluesky).

## What NOT to Do

- Don't return a post that scores below 8/10. Loop on the grader until it's there.
- Don't pile on hashtags where they hurt (Twitter, LinkedIn, Facebook).
- Don't write 3 versions and ask the user to pick. Pick one. They can ask for an alternative if they want one.
- Don't include the hook pattern name or grading details in the post itself. Those are for the meta-output, not the actual caption.
