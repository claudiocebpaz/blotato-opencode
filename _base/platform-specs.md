# Especificaciones por plataforma

> Límites, CTA que premia cada algoritmo, y cadencia máxima. El `post-writer` y el
> `post-grader` leen esto para adaptar cada pieza. Pasarse de la cadencia baja el alcance.

## Tabla rápida

| Plataforma | Largo copy | Hook | CTA que premia | Hashtags | Cadencia máx/día |
|---|---|---|---|---|---|
| LinkedIn | 1.200–1.500 chars | primeros ~140 chars (antes del "ver más") | **comentarios** (~2x vs likes) | 3–5 opcional, al final | 2 |
| X / Twitter | 280 (ideal 60–100) | primeras 3 palabras | **respuestas** (~75x vs likes) | 0 | 5 (<10k), 15 (>10k) |
| Instagram | 2.200 (hook en 125) | primeros 125 chars | feed: **guardados**; reels: **completación** | 3–5 nicho, al final | 1 imagen + 4 reels |
| Facebook | 40–80 óptimo | frase corta | **shares** ("etiquetá a alguien") | 0 | 4 reels |

## CTA por plataforma (usar el que premia el algoritmo)

- **LinkedIn** → pregunta polarizante / "¿qué le agregarías?" (busca comentarios).
- **X** → take polarizante / "decime que me equivoco" (busca respuestas).
- **Instagram feed** → "guardá esto para después" / "mandáselo a quien lo necesita".
- **Instagram reels** → gancho que retiene hasta el final + "guardá".
- **Facebook** → "etiquetá a alguien que…" (busca shares).

## Reglas por plataforma

**LinkedIn**
- **Craft completo en `_base/linkedin-craft.md`** (formato mobile-first, "texto oculto",
  5 hacks de ritmo, storytelling de 8 pasos). Cargarlo siempre para piezas de LinkedIn.
- Sin links externos en el cuerpo (matan alcance) → link en el primer comentario.
- Espaciar el texto, nada de bloques: párrafos de 1–3 líneas + white space.
- **Texto oculto:** hook potente arriba, 2–3 líneas en blanco, después el cuerpo (fuerza el "ver más").
- Emojis SÍ, pero **solo funcionales y con moderación** (✅/❌, señaladores), no decorativos.
- Repost del mismo post a la tarde para resurfacear.
- Carruseles = documento PDF que Blotato arma desde 2–10 imágenes (sin video). Ver `templates.md`.
- Por API NO se puede: publicar Articles, crear polls, repostear, ni video dentro de carrusel.

**X / Twitter**
- Sin hashtags, sin links en el cuerpo del tweet principal.
- **Emojis SÍ en X** (a diferencia de LinkedIn): un emoji líder por tweet en los hilos rompe el
  ladrillo de texto plano y da ritmo/escaneabilidad. Que mapee al concepto (🛑 stop, ⏱️ cap,
  ✅ check, 🧠 memory, 💬 CTA). Uno por tweet, no spam. El tweet-1 hook puede ir limpio.
- Threads: tweet 1 es hook puro; link solo en el último tweet.
- Cuentas nuevas: calentar 1–2 semanas posteando manual antes de automatizar.

**Instagram**
- **Requiere media siempre** (no publica solo texto).
- Carrusel = 2–10 imágenes.
- Por API NO se puede: label "AI Generated", música de terceros, ni sticker de link en Stories (se agregan a mano en la app).
- Cuenta debe ser Business o Creator.

**Facebook**
- Requiere Page + `pageId`.
- Videos siempre se publican como Reels (9:16).
- Sin engagement bait tipo "comentá SÍ".

## Warm-up de cuentas nuevas (crítico)
Nunca conectar apps de terceros ni postear en masa en una cuenta recién creada (la marcan
como bot). Calentar manual 1–2 semanas (4 para TikTok, 2 para Pinterest) antes de automatizar.
