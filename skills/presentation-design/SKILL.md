---
name: presentation-design
description: >-
  Build, redesign, or critique presentation slides and decks that are grounded
  in cognitive science — Assertion-Evidence structure, minimal cognitive load,
  Picture-Superiority, strict visual hierarchy, WCAG accessibility — and free of
  generic "AI-slop." Use this whenever the user wants to make a presentation,
  build or improve a slide deck, create a pitch deck, fix ugly / overloaded /
  text-heavy slides, prepare a talk or lecture, or mentions slides, deck,
  PowerPoint, Keynote, Google Slides, or Slidev — even if they never say the
  words "good design." Also use when reviewing an existing deck for clarity,
  hierarchy, overflow, contrast, or signs of generic AI generation. The skill
  builds decks as Slidev (Markdown + HTML/CSS) and self-verifies by rendering to
  images and actually looking at them before delivering.

The evolved focus: clear cognitive science + richer, image-driven, personality-forward decks that have soul (strong specific metaphors, memorable hooks, images as story carriers).
---

# Presentation Design

A slide is not a document you narrate. It is a visual aid whose only job is to
lower the audience's cognitive load while a human speaks. Every decision in this
skill traces back to one idea from cognitive science: the working memory of your
audience is tiny and easily overwhelmed, so the deck must spend that budget on
*understanding the content* (germane load) and waste none of it on decoding a
bad layout (extraneous load). When in doubt, remove something.

This skill produces decks in **English** and builds them as **Slidev**
(Markdown + a CSS theme), because that lets you render every slide to an image
and inspect it — the only reliable way to catch overflow, weak contrast, and
broken hierarchy. Prose and layout live in Markdown + CSS; **math and precise
vector diagrams are compiled by Typst** (via `slidev-addon-typst`, enabled by
default) into inline SVG — see `references/typst-pipeline.md`. Full theory lives
in the reference files; read them when the task touches their area.

## The non-negotiables

These are the highest-leverage rules. They come from Mayer, Alley, Kosslyn,
Tufte, and Paivio (see `references/cognitive-design.md`). Follow them unless the
user explicitly overrides:

1. **Headlines carry the point with clarity and voice.** Body slides typically use a full-sentence assertion (≤2 lines). Title, character, and section slides often benefit from shorter, punchier, personality-forward hooks ("Fixing Windsurf", "Fun With TURBOMED", "The Unicode Barrier") that feel human and memorable. The test: does the title make the idea stick and feel like *you*?
2. **The body is image-driven.** The image should do the heavy lifting and stand on its own. The viewer should understand the point from the visual + spoken words without the slide explaining "this is a vector illustration of..." or meta commentary about how it was made. Prioritize rich, story-carrying images (metaphorical illustrations, concrete scenes) that make the idea concrete and memorable. Use CeTZ vector drawings for full control and consistency when creating custom metaphors. Keep text to short labels or ≤2 call-outs. The image itself is the message.
3. **Never make the audience read and listen to the same words.** Reading full
   sentences off a slide while the speaker says them collides in the phonological
   loop and destroys retention (Redundancy Principle). Speakers *paraphrase*
   headlines; they never read them aloud.
4. **One idea per slide.** Segment. A five-step process is five slides (or one
   slide built up in five clicks), never one crowded slide.
5. **Show rich, story-carrying images.** Strong images (photos, custom illustrations, or metaphors using real objects) paired with speech create deep memory and emotional connection. Prioritize images that feel alive and specific to the idea. Prefer a memorable photo or illustration over a generic or purely schematic diagram when it carries personality and the point.
6. **Verify by looking.** Renderers do not honor your CSS the way you expect.
   After building, render to images and read them. This is a gate, not a nicety
   (see Phase 3).
7. **A process is a slide sequence, not a picture.** Any algorithm, mechanism,
   or evolution over time (a search frontier expanding, pheromone trails
   reinforcing, a population converging over generations) unfolds as **one slide
   per state**, with the visual at the identical position and scale on every
   slide so flipping through reads like an animation. A single static diagram of
   a multi-step process deletes the very thing being taught. Build the visual as
   one parameterized component (`:step="n"` / `:stage="n"` / `:generation="n"`),
   never N divergent drawings.
8. **Concrete before abstract.** Introduce every formalism by a ladder:
   (1) a real scene the audience can picture (a truck and boxes to pack),
   (2) visual intuition with **no numbers and no math** (some packings are
   obviously better), (3) only then the encoding (boxes → bit string),
   (4) then the dynamics on the encoding (populations of bit strings evolving,
   one generation per slide). Never open a worked example with the abstraction.
9. **The slide whispers; the notes speak.** A body slide carries ≤ ~20 on-slide
   words; the full argument lives in presenter notes (the last `<!-- ... -->`
   block of the slide). Notes are mandatory on every body slide — they are the
   speaker's script and they are embedded in the PPTX export. When a slide feels
   text-heavy, the fix is almost always "move it to the notes", not "shrink it".

**Image as storyteller and personality carrier.** Your strongest decks use images not merely as evidence but as the emotional and narrative core. Choose the right tool for the visual:

- **CeTZ (Typst)**: technical diagrams, precise flows, mathy or schematic elements. Full control, vector, offline.
- **Zdog**: expressive, round, pseudo-3D organic/personality illustrations (ants on a branch, characters, objects with volume and charm). Still vector-style output (canvas rendered in the deck), dramatically more "alive" than flat CeTZ for metaphorical scenes. See `assets/zdog/`.

Prefer a memorable custom illustration (Zdog or CeTZ) over generic or purely schematic when it carries personality. Never label the image with how it was produced. The image itself is the message.

## Workflow

Work in three phases and do not skip Phase 1. The most common failure is opening
the tool first and letting its template dictate the thinking.

### Phase 1: Framework-first planning (before any tool)

Open no software yet. On paper / in notes, answer four questions
(from `references/anti-ai-slop.md`, the antidote to generic decks):

- **The decision:** what should the audience *do* or believe after this? Be
  concrete ("approve €500k for the CRM upgrade"), not "give an update."
- **The main headwind:** the biggest objection or worry in the room.
- **The evidence:** the specific data points that answer that headwind.
- **The logical flow:** the argument order that most inevitably leads to the
  decision.
- **Visual metaphor hunt:** what concrete image, photo, everyday object, or scene could make this idea feel alive, emotional, or memorable? (e.g. ants on a branch with food for evolution, an open-hood classic car for legacy code).

Then define **one core message** for the whole talk, storyboard the arc
(hook → structured body → clear conclusion). For body slides write a clear assertion or sharp hook (full sentence preferred but not mandatory for title/character slides). If it won't compress into two lines, the thinking isn't done — fix the thinking, not the font size.

Cap the structure: a 10–15 min talk gets **at most 3 sections**; even long talks
stay ≤5. Budget roughly one slide per minute (2–3 min/slide for long, dense
talks).

### Phase 2: Build in Assertion-Evidence (Slidev)

Use the starter in `assets/deck-template/` — it already encodes the layouts,
WCAG-safe design tokens, and the heading-hierarchy fix. Read
`references/build-slidev.md` for the technical how-to (setup, the render
pipeline, and the environment fixes that make rendering work in this sandbox).

Slide typology (from Alley's AES):

- **Title slide:** a striking, high-resolution key image (atmospheric, metaphorical, or personality-forward) + a memorable title or hook — not a name on a blank background. The image should feel like the soul of the talk and ideally recur or echo later. Never label the image with how it was produced.
- **Mapping slide:** a *visual* agenda. A two-line assertion headline
  ("This talk covers three parts of X") with the sections shown as
  representative images/icons, not a bulleted list.
- **Body slides:** left-aligned headline (full-sentence assertion or sharp hook) on top; the rest of the slide is rich, story-carrying image(s) first. Body text only as short labels or ≤2 call-outs. Prefer specific metaphorical or illustrative images over schematic diagrams when they make the idea more human and memorable.
- **Closing slide:** restate the single most important message as a clear
  assertion backed by a parallel visual. Put "Thank you / Questions" as a small
  footer so the core message stays on screen during Q&A. Never end on a blank
  "Thanks!" or "Questions?" slide.
- **Punchline slides:** running jokes and memes give a talk soul — but a joke is
  a *beat inside the narrative*, placed **after** the setup that pays it off
  (sad Dijkstra only lands after the ants have found the shortest path without
  him). A meme is never the deck title, the cover, or a section heading; if a
  source deck used one as a title, treat it as a punchline to relocate, not a
  name to keep.

Apply the quantitative rules below and the accessibility rules in
`references/accessibility.md` as you go.

#### Math and diagrams — the Typst pipeline (default)

The template ships with `slidev-addon-typst` enabled, so math and precise
diagrams go through Typst and render as crisp inline SVG in the deck's own
typographic system. Full guidance and verified snippets are in
`references/typst-pipeline.md`; the load-bearing rules:

- **All math goes in a ```typst fenced block.** A bare `$…$` in the Markdown body
  is *not* Typst-processed and renders as literal italic text.
- **Wrap any non-math graphic in `#html.frame(...)`** — a CeTZ canvas or a
  Fletcher `diagram(...)` is invisible on web export otherwise.
- **Diagrams:** use **Fletcher** (nodes + arrows: flowcharts, state machines,
  commutative diagrams) on top of **CeTZ** (raw geometry). Connect nodes by
  logical label references (`edge(<a>, <b>, "-|>")`) so arrows re-snap when text
  changes; import packages inside each block.
- **A failed Typst block renders empty, not an error** — if a diagram is missing
  from a render, it failed to compile; read the export log. CeTZ/Fletcher need
  the Typst package registry on first compile (math works offline).

Keep the discipline of this skill even inside Typst: a diagram is *evidence* for the slide's assertion, not decoration. However, when a rich photo, custom illustration, or strong visual metaphor will make the idea more human, memorable, or personality-forward, prefer it over a schematic diagram. The Typst pipeline is excellent for precise math and flows; it is not the default for every visual.

#### Zdog illustrations (expressive personality visuals)

For organic, "alive", metaphorical scenes where CeTZ feels too flat or technical, use **Zdog** (a lightweight pseudo-3D engine that produces round, charming vector-style output).

- Install `zdog`.
- Drop `assets/zdog/` contents into the deck (`components/ZdogIllustration.vue` + sibling `illustrations/`).
- Use `<ZdogIllustration illustration="your-scene" :width="620" :height="260" />`.
- Scenes are plain JS factories using Zdog primitives (Ellipse, Shape for legs/paths, Anchors for groups + 3D transforms). They look substantially richer and more personality-forward than basic CeTZ ants or objects.
- Canvas renders are captured correctly by the export pipeline (PNG/PDF).
- Still respect "show don't tell" — never put "made with Zdog" or medium labels on the slide.

See the ant-on-branch example for "Biological Inspiration" and the component source for how to author new ones. Combine with the same image-driven slide structure.

#### Design signature (a reusable visual identity)

If someone wants their decks to share one consistent look, run the one-time
design-signature interview (`references/design-signature.md`): a short,
option-based Q&A over format, typography, palette, CeTZ style, and Fletcher
node/edge style. It generates a `signature-theme` (a Typst preamble +
matching Slidev CSS tokens) and installs it as a local Typst package, so every
deck imports the same identity with `#import "@local/signature-theme:0.1.0": *`
(verified to resolve offline, at any folder depth). Offer this the first time a
person builds a deck, or when they ask to restyle. A signature only changes the
*look* — never the Assertion-Evidence structure or the accessibility floors.

#### When bullet points are actually the right tool

Bullets are not banned — they beat images for recall of specific facts, numbers,
and procedures, and they help non-native speakers and accessibility. Use them
for precise data, ordered steps, or logical sequences. But keep them disciplined
(the "Rule of Seven"): **3–5 bullets max, one line each, revealed one at a time
as the speaker gets to them, and paired with a visual.** Details and the
evidence for both sides are in `references/cognitive-design.md`.

### Phase 3 — Render and QA gate (mandatory)

This is where decks are actually made good. Do not deliver a deck you have not
looked at rendered.

1. **Render** the deck with `scripts/render_deck.sh`. It exports **PNG + PDF +
   PPTX in one run** — all three, always. The PPTX embeds the presenter notes
   and is the delivery format (it is the only one Keynote imports *with* notes);
   the PDF is the sharing format; the PNGs exist so you can look at them.
2. **Look at every slide.** Read each exported PNG and check it against the
   visual rubric:
   - text overflow, truncation, collision with the footer, or edge-touching
   - broken hierarchy (is the slide title clearly the largest, boldest thing? a
     title smaller than the body cards is the classic Slidev bug — see below)
   - contrast too low; color used as the *only* signal
   - charts: right type? (bars for comparison/categories, lines for trends —
     avoid pie charts for anything but a couple of parts-of-a-whole)
   - cramped or, conversely, empty slides; ≥30–40% whitespace present
   - typos, especially in headlines and figure labels
   - Does the main image feel alive, specific, and personality-forward (rich photo, strong metaphor, or illustrative scene), or is it generic/schematic? Does the slide have soul?
3. **Run the anti-slop gate** from `references/anti-ai-slop.md`: scan for the
   red-flag vocabulary, check every number is consistent across slides and has a
   source, confirm no empty template sections, and run the **"Why test"** — you
   must be able to justify every slide, graphic, and figure out loud. Anything
   you can't explain is slop; cut it.
4. **Fix and re-render** until the rubric passes. Iterate; don't ship on the
   first render.

The reason this gate exists: CSS frequently does not render the way the source
implies. A real example this template guards against — Slidev's base layer
silently overrides bare `h1`/`h2` font sizes, so titles render at body size and
the whole hierarchy inverts, while class-based styles look fine. You cannot catch
this by reading the Markdown; you catch it by looking at the picture. Trust the
render, not the source.

## Quantitative rules

Apply these as defaults; they operationalize the theory.

| Parameter | Target | Why |
|---|---|---|
| Text per slide | ≤ 30–40 words | Stops the audience reading instead of listening |
| Slides / timing | ~7–10 for a 10-min talk (~1 slide/min) | Prevents rushing; 2–3 min/slide for long dense talks |
| Sections | ≤ 3 (10–15 min), ≤ 5 ever | Fits the audience's structural working memory |
| Headline | Full sentence, ≤ 2 lines, left-aligned | The Assertion; forces a real point |
| Font families | ≤ 2 (one display, one body) | Visual calm; consistency signals competence |
| Title size | ≥ 28 pt (deck-relative); clearly largest element | Legibility from the back row; correct hierarchy |
| Body min size | ≥ 18 pt equivalent | Readable at distance |
| Whitespace | ≥ 30–40% of the slide unused | Gives the visual system rest |
| Contrast | ≥ 4.5:1 (normal), ≥ 3:1 (≥28pt); aim > 7:1 | WCAG AA; readable on bad projectors |
| Bullets (if used) | ≤ 3–5, one line each, built in, paired with a visual | Rule of Seven; caps extraneous load |
| Presenter notes | On every body slide (last `<!-- … -->` block) | The speaker script; embedded in PPTX export |
| Page numbers | `{{ $slidev.nav.currentPage }} / {{ $slidev.nav.total }}` | Hardcoded numbers desynchronize the moment slides are added |
| Export | PNG + PDF + **PPTX with notes**, 1920×1080 16:9 | PPTX is the only format Keynote imports with speaker notes |

## Separate the projected deck from the handout

A slide optimized to be *read* and a slide optimized to *support a speaker* are
different documents; one file cannot be both (Tufte). The projected deck is
visual and sparse. If the audience needs something to read or archive, produce a
separate written document (a prose PDF / memo) with the detail, and hand that
out. Offer this split whenever the user says the deck also has to "stand alone"
or "be sent around afterwards."

## Reference files

Read the one that matches the task; don't load them all pre-emptively.

- `references/cognitive-design.md` — the science: Cognitive Load Theory, Mayer's
  12 multimedia principles (with best/worst practice), Kosslyn's 8 perception
  principles, Picture-Superiority / dual coding, the Assertion-Evidence structure
  and its empirical results, the bullet-point evidence, and Tufte's critique.
  Read when designing content or justifying a design choice.
- `references/anti-ai-slop.md` — how to detect and remove generic AI output:
  Framework-First planning, the GACTF prompt model, red-flag vocabulary lists,
  visual/data/narrative failure patterns, file-metadata forensics, and the
  pre-delivery QA gate. Read during Phase 1 and the Phase 3 gate.
- `references/accessibility.md` — WCAG contrast math and thresholds, designing
  for color-blindness (redundant coding), backgrounds and dyslexia, screen-reader
  alt-text and reading order, typography minimums. Read whenever choosing colors,
  charts, or handling an audience with access needs.
- `references/build-slidev.md` — the technical how-to for building and rendering
  the deck: template layout, `render_deck.sh`, the sandbox environment fixes
  (local install dir, Chromium's missing `libXdamage` stub, Playwright env
  vars), and the render→inspect→fix loop. Read at the start of Phase 2/3.
- `references/typst-pipeline.md` — the default math/diagram pipeline: enabling
  `slidev-addon-typst`, Typst mode discipline, `html.frame` wrapping, CeTZ
  geometry and Fletcher node/arrow diagrams (with verified, version-correct
  syntax), coordinate/axis inversion, step animation, and the network/version
  caveats. Read whenever a slide needs an equation or a precise diagram.
- `references/zdog-illustrations.md` — using Zdog for expressive, round,
  personality illustrations (ants, objects, characters). When to choose it over
  CeTZ, how to integrate the Vue wrapper + scene factories, and authoring tips.
- `references/design-signature.md` — the one-time interview that captures a
  reusable visual identity (type, color, CeTZ/Fletcher style) and installs it as
  a local Typst package so every deck shares the look. Read when a person wants a
  consistent house style or asks to restyle their decks.

## Assets and scripts

- `assets/deck-template/` — a ready Slidev deck: `slides.md` (title, mapping,
  body, closing, plus math and Fletcher example slides), `styles.css` (WCAG-safe
  tokens + the hierarchy fix), `setup/main.ts`, `package.json` (with
  `slidev-addon-typst` enabled). Copy it as the starting point for a new deck.
- `assets/signature-theme/` — starter reusable identity (`typst.toml` + a
  verified `lib.typ` with colors, a theme function, a CeTZ style, and Fletcher
  node/edge helpers). Customize via the design-signature interview.
- `assets/zdog/` — Zdog-based expressive illustrations. Includes a reusable
  `ZdogIllustration.vue` wrapper + illustration factories (e.g. biological
  inspiration ants). Use for personality-forward metaphorical scenes. Install
  `zdog` and drop the folder into a deck's `components/` (plus `illustrations/`
  next to it). Canvas output is captured perfectly on export.
- `scripts/render_deck.sh` — installs the toolchain and exports the deck to PNG
  and PDF, handling the sandbox quirks. Usage in `references/build-slidev.md`.
- `scripts/install_signature.sh` — installs a `signature-theme` as a local Typst
  package (cross-platform) so decks import it with `@local/…`.
