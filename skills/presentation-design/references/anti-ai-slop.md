# Detecting and removing AI-slop

"AI-slop" is generic, mass-produced deck content that looks polished but lacks
strategic depth, specific relevance, and substance. Generators (Gamma, Tome,
Beautiful.ai, Copilot) build a deck in under a minute by pouring text into rigid
templates — which is fine for a first draft, and fatal for a high-stakes pitch or
board deck. Reviewers notice fast: the median first look at a pitch deck is
**~2 min 14 s** (DocSend), and the cover slide gets more than double the
attention of any other. Visible AI generation reads as low effort and kills
trust silently.

Use this file two ways: as the **Framework-First** planning method in Phase 1,
and as the **pre-delivery QA gate** in Phase 3.

## Contents

1. Framework-First planning + GACTF
2. Linguistic red flags
3. Visual and spatial anomalies
4. Narrative and structural failures
5. Data and logic failures
6. File forensics
7. The pre-delivery QA gate

---

## 1. Framework-First planning (not prompt-first)

The fix for slop is to lead with a framework and use AI only to accelerate a
draft — the content judgment and finishing stay human. Before opening any tool
or writing a prompt, answer in writing:

- **The core decision** — what the audience should decide/do (concrete:
  "approve €500k for the CRM upgrade", not "project update").
- **The main headwind** — the biggest objection (implementation risk, ROI
  horizon, resourcing…).
- **The evidence** — the precise data points that neutralize that objection.
- **The logical flow** — the argument order that most inevitably yields the
  decision.

Only then instruct the AI, using **GACTF** to give it boundaries and a role
instead of a vague ask:

- **Goal** — the specific outcome of the deck.
- **Audience** — who they are and what they already know.
- **Content** — the actual facts, numbers, and sources to use (supply them).
- **Tone** — e.g., direct, technical, non-hype.
- **Format** — structure, length, section count.

---

## 2. Linguistic red flags

LLMs predict likely next tokens, which produces over-smooth, sterile prose
("professional fluff") — grammatical and polite, but generic. Certain words
recur far more than in expert writing. Scan headlines, body, and speaker notes
for these and replace with concrete, specific language.

| Category | AI-typical (avoid) | Human alternatives |
|---|---|---|
| Abstract verbs | delve into, leverage, utilize, harness, streamline, underscore, foster, catalyze | examine, use, apply, simplify, highlight, show, establish, speed up |
| Inflated adjectives | pivotal, robust, innovative, seamless, cutting-edge, game-changing, multifaceted | essential, reliable, new, smooth, direct, complex, significant |
| Metaphor nouns | landscape, realm, tapestry, synergy, testament, treasure trove, ecosystem | market, sector, structure, combination, evidence, data, industry |
| Formal connectors | furthermore, moreover, consequently, notably, in conclusion | also, so, an important point is, (just state the conclusion) |
| Phrase templates | "In today's fast-paced digital world", "unlock the potential", "pave the way", "navigate the complexity" | Delete entirely; state a concrete, quantified market reality |

**Syntactic monotony.** Human writing has *burstiness* — short punchy sentences
interleaved with longer ones. AI output tends toward uniform sentence length and
structure. Also distrust stock rhetorical figures like contrastive negation —
"Not because it's easy, but because it works" / "No theory. No distractions. Just
results." They feel dynamic but carry no information and instantly read as
synthetic. Cut them.

---

## 3. Visual and spatial anomalies

Human designers build the layout around the content; generators pour content
into fixed templates, producing balanced-but-lifeless slides.

| Element | AI-slop tell | Professional standard |
|---|---|---|
| Layout | Rigid symmetry; identical visual weight on every slide regardless of content | Deliberate, content-driven asymmetry; focus on the key point |
| Space use | Text stretches across the full 16:9 width to fill space | Cap text at ~60% width; use whitespace on purpose |
| Depth | Dead-flat 2D (depth is hard to automate) | Subtle, consistent layering — soft shadows, gentle gradients |
| Consistency | Mismatched corner radii, wobbly line weights, clashing icon styles | One design system: uniform radii, harmonized lines, one icon set |
| Contrast | Weak contrast on colored boxes; loud, over-saturated gradient backgrounds | WCAG AA ≥ 4.5:1; muted, professional backgrounds |

**Synthetic imagery tells:** waxy/over-smooth render textures and wrong lighting on generated people or objects; obsession with saturated 3D spheres, floating crystals, glowing vectors that mean nothing; garbled pseudo-text or impossible object fusions; visible "Made with Gamma / Designed with AI" watermarks.

However, deliberately stylized or custom-generated metaphorical images can be excellent when they are specific and carry personality (e.g. ants on a twisting branch with food props for biological inspiration, an open-hood classic car for legacy code, fuel-pump icons for old vs new scripting). These are not slop — they make ideas human and memorable. Distinguish generic slop from intentional illustrative metaphor. Use the latter freely when it serves the story.

**Diagram failures:** generators produce pretty radial shapes but break on logic
— typos and letter substitutions in nodes, structure collapsing beyond 2–3
hierarchy levels (branches overlap, connectors end in space), and "decorative"
diagrams whose labels are just wavy lines or pseudo-text on close inspection.
Build real diagrams; verify every label.

---

## 4. Narrative and structural failures

AI treats slides as isolated units, so the through-line breaks.

- **Simulation over explanation:** the deck imitates what a successful startup
  *should* look like instead of explaining the real operation — dutiful
  Problem/Solution/Market/Team slides filled with platitudes.
- **Prototype fraud:** glossy "cyberpunk" renders in place of real photos of a
  working prototype, masking missing engineering.
- **The "perfectly de-risked" vacuum:** "100% risk-free", "R&D fully complete",
  "product-market fit is perfect" — denying the messy reality of an early venture
  reads as naïve to experienced audiences.
- **Missing core slides:** no real "Why now" (replaced by generic trends); vague
  go-to-market ("social media", "viral growth") instead of concrete channels,
  CAC, and conversion; an unclear "Ask" (amount named, capital allocation to the
  next milestone left blank); an empty or trivially-filled competitive matrix.

---

## 5. Data and logic failures

LLMs optimize tone and structure, not arithmetic — so numbers are a frequent
weak point and an easy tell.

- **Inconsistent metrics:** a different market size (TAM) on the market slide vs.
  the model slide vs. the forecast. **Every number must be identical wherever it
  recurs.**
- **Orphan big numbers:** monumental percentages or dollar figures with no
  legend, time frame, or source.
- **Fabricated validation:** invented historical data, non-existent studies,
  distorted unit economics used to plug gaps.

| Weak area | Typical AI error | Fix |
|---|---|---|
| Competition | No real rivals; claims of monopoly | Real matrix incl. indirect competitors (even "the customer's spreadsheet") |
| Financials | Unrealistic margins ignoring inference/cloud/COGS | Full operating costs; real scaling effects |
| Visualization | Wrong chart type (pie for a time series) | Bars for categories, lines for trends |
| Sourcing | Missing or invented citations | A small, precise source line under each data point |

---

## 6. File forensics

For due-diligence-grade checks, the file itself betrays machine origin — no
visual judgment needed.

- **Metadata / authorship:** on a `.pptx`, Properties → Details shows Author,
  Company, "Last modified by". Unedited AI exports often list a service name
  ("Gamma", "Beautiful.ai") or an API/bot name, plus odd revision numbers and
  implausibly short edit times.
- **Unzip the .pptx:** it's a ZIP archive — rename to `.zip` and extract.
  - `ppt/media/`: humans name assets logically (`CEO_portrait.jpg`,
    `Q3_revenue_chart.png`); generators save long alphanumeric strings from image
    APIs (`image_df234_992l.png`).
  - Slide masters: AI decks often show deeply nested, redundant, messy
    slide-master XML vs. the lean masters of human designers.

---

## 7. The pre-delivery QA gate

Run this before shipping any deck (Phase 3). It is the checklist that turns a
draft into something a decision-maker will trust.

1. **Vocabulary scan** — search for the red-flag words in §2; rewrite hits into
   concrete, specific language. Kill phrase templates and contrastive-negation
   filler.
2. **Number integrity** — every figure is consistent across all slides, has a
   unit and time frame, and carries a source line. No orphan big numbers.
3. **No empty template** — every standard section is actually answered (Why now,
   GTM specifics, the Ask's allocation, a real competitive matrix). Cut or fill
   any placeholder section.
4. **Imagery is real** — no synthetic waxy renders, meaningless 3D geometry,
   pseudo-text diagrams, or tool watermarks. Verify every diagram label.
5. **Slide-sorter sweep** — view all slides as thumbnails; catch drifting logos,
   uneven margins, inconsistent radii/lines, jumping page numbers, visual outliers.
6. **The "Why test"** — for every slide, graphic, and data point, you can state
   out loud why it's there and where the number came from. Anything you cannot
   justify is slop; remove it. This single test catches most of the above.

## 8. Patterns learned from the other skills

These are the AI-giveaway signals that the companion skills (test-review,
check-work, code-review, rigorous-paper-critique, verify-first, grill-with-docs)
catch in their domains, translated to what they look like in a deck. Treat them
as extensions of the red-flag tables above.

### Proxy-signal rejection — from check-work

Passing tests and a green build are not proof of completion; they are proxy
signals. The same trap exists in decks: **a deck that renders without errors is
not a good deck.** A clean export means the Markdown is valid and the Typst
blocks compiled — it says nothing about whether the argument is sound, the
evidence is real, or the audience will understand it. Never accept "it renders"
as the success criterion. The Phase 3 visual rubric exists precisely because the
render is the cheapest gate to clear and the least meaningful one.

### Overclaiming — from rigorous-paper-critique

In academic papers, the most common dishonesty is scope inflation: a local,
single-step, margin-conditional result framed as a global convergence theorem.
The identical tell appears in decks. Flag any headline or claim whose scope
exceeds its evidence:

- "Proven to increase conversions" from a single A/B test on one segment.
- "Industry-leading performance" with no benchmark or comparison cited.
- "Fully scalable" from a architecture diagram, not from load testing.
- "0% downtime" stated without a time frame or measurement method.

The fix is the same as in papers: match the scope of the claim to the scope of
the evidence. If the evidence is local, the claim must be local. If you cannot
narrow the claim to match the evidence, you do not have the evidence — cut it.

### Fuzzy-language sharpening — from grill-with-docs

AI-generated decks are full of overloaded terms that sound precise but carry no
specific meaning. When reviewing a slide, challenge every fuzzy term and demand
a concrete referent:

- "platform" — which platform? what does it do?
- "solution" — a solution to what specific problem, for whom?
- "ecosystem" — name the participants and the value exchange.
- "intelligent" / "smart" — what specific mechanism? a rule? a model? a threshold?
- "next-generation" — what generation is current, and what specifically changed?

If a word cannot be replaced with a concrete noun or a specific mechanism
without losing meaning, it is filler. Replace it or delete the sentence. A deck
that survives this challenge on every slide is a deck that says something.

### Structural slop in generated code — from code-review

The Typst/CeTZ/Fletcher blocks inside a deck are code, and AI-generated code
carries the same structural tells as AI-generated prose. When reviewing a
```typst block, apply code-review discipline:

- **Thin wrappers that add indirection without clarity** — a `sig-plot(body)`
  helper that just calls `cetz.canvas` with two `line` calls and passes `body`
  through. If deleting the wrapper and inlining does not increase complexity,
  the wrapper is slop. Delete it.
- **Copy-pasted blocks** — the same `#import` + `#set-style` + axis-drawing
  boilerplate repeated on every slide instead of centralized in the signature.
  Extract once, import everywhere.
- **Casts and optionality that muddy the contract** — `fill: none` added "just
  in case" on a shape that always has a fill. Remove speculative parameters.
- **Ad-hoc conditionals bolted onto unrelated paths** — a `if sys.inputs.x`
  branch inside a diagram block that only runs in one context. Isolate it or
  remove it.
- **A block that silently renders empty** is the deck equivalent of a failing
  test that passes: it looks green, it hides the bug. Always read the export
  log for Typst errors after rendering.

### AI agent simplification bias — from test-review

"AI-generated tests are 10% more likely to add mocks than human-written
tests." The deck equivalent: AI-generated diagrams are more likely to be
**simplified to the point of meaninglessness** than hand-built ones. A
flowchart reduced to three identical boxes labeled "Input → Process → Output"
tells the audience nothing. A commutative diagram with every arrow labeled
`f`, `g`, `h` and no domains or codomains is decoration, not mathematics.

When a diagram is simpler than the idea it represents, it is not a
simplification — it is a deletion of information. Every node, edge, and label
in a diagram must earn its place by carrying information the audience needs.
If it carries none, it is clip art. Cut it or make it real.

### Two-axis separation — from review

A deck change can pass one axis and fail another, and one will mask the other if
you do not check them separately:

- **Standards axis** — does the slide follow the signature, the WCAG floors, the
  Assertion-Evidence structure, the typography and density rules?
- **Spec axis** — does the slide actually say what the talk needs it to say, with
  real evidence, for this specific audience and decision?

A slide can follow every design rule (Standards pass) and still be the wrong
slide for the argument (Spec fail). A slide can make the right point (Spec pass)
while breaking the visual system (Standards fail). Review both; never let a
clean render on one axis excuse a hollow argument on the other.
