---
# Assertion-Evidence deck template (evolved for richer, image-driven, personality-forward decks).
# Replace content, keep the structure. Body slides lead with strong images and clear hooks.
# Hunt for specific metaphors and memorable visuals during planning.
theme: none
title: Talk Title Goes Here
info: One-line description of the talk.
highlighter: shiki
lineNumbers: false
drawings: false
mdc: true
addons:
  - slidev-addon-typst
colorSchema: dark
fonts:
  sans: 'Inter'
  mono: 'JetBrains Mono'
# The first frontmatter block styles slide 1 only:
class: center
---

<!-- ============================================================
     TITLE SLIDE
     A striking key image (atmospheric, metaphorical, or personality-forward) + a memorable hook.
     Not a name on a blank page. Use a strong photo or illustration that feels like the soul of the talk.
     Put your image in ./images/ and reference it.
     ============================================================ -->

<div class="eyebrow">Your Team · Context</div>

# Fixing Windsurf (or your memorable hook)

<p class="kicker">A one-sentence promise, or a sharp, personality-forward line that makes the idea stick.</p>

<div class="foot"><span><span class="brand">BRAND</span> · Talk Title</span><span>1</span></div>

---

<!-- ============================================================
     MAPPING SLIDE (visual agenda)
     Assertion headline + sections shown as cards/images, not a bullet list.
     Keep to <=3 sections for a 10-15 min talk; <=5 ever.
     ============================================================ -->

# This talk builds one argument in three moves

<div class="grid-3" style="margin-top: 12px;">
  <div class="card">
    <h3>01 Setup</h3>
    <p>The problem and why it matters now.</p>
  </div>
  <div class="card">
    <h3>02 Evidence</h3>
    <p>What the data actually shows.</p>
  </div>
  <div class="card">
    <h3>03 Decision</h3>
    <p>What we should do, and the ask.</p>
  </div>
</div>

<div class="foot"><span><span class="brand">BRAND</span> · Overview</span><span>2</span></div>

---

<!-- ============================================================
     BODY SLIDE: the workhorse.
     Title = a full-sentence ASSERTION (<=2 lines). Body = ONE visual.
     Replace the placeholder with a real photo/diagram/chart.
     Add at most two .callout annotations. Cite the source.
     Speaker PARAPHRASES this line; never reads it aloud.
     ============================================================ -->

# The claim this slide proves (or a sharp hook)

<div class="evidence">
  <!-- Place rich visual here: ZdogIllustration for personality scenes,
       CeTZ for diagrams, or photo. The component lives in components/.
       <ZdogIllustration illustration="biological-inspiration" /> -->
</div>

<p class="kicker">Short label or one powerful sentence under the image if needed.</p>

<p class="source">Source: Author, Publication, Year.</p>

<div class="foot"><span><span class="brand">BRAND</span> · 01 Setup</span><span>3</span></div>

---

<!-- ============================================================
     BODY SLIDE: rich metaphorical image example (personality-forward).
     Use a specific, memorable image that tells the story.
     ============================================================ -->

# Everyday objects reveal the real constraints

<div class="evidence" style="text-align: center;">
  <!-- Rich image or detailed CeTZ scene here. The visual stands alone. -->
</div>

<p class="kicker">The image makes the abstraction human and specific.</p>

<div class="foot"><span><span class="brand">BRAND</span> · 02 Evidence</span><span>4</span></div>

---

<!-- ============================================================
     BODY SLIDE with a chart.
     Use BARS for comparisons/categories and LINES for trends.
     Avoid pie/donut charts (angle/area are hard to compare).
     ============================================================ -->

# Bars beat pies because the eye compares lengths precisely

<div class="evidence">
  <div class="card" style="width: 72%; text-align:center; color: var(--ink-dim);">
    [ Bar chart here. One idea. Direct labels, no legend hunt. ]
  </div>
  <div class="callout" style="margin-left: 20px;">
    Highlight the one bar that carries the point in <em>accent</em> color.
  </div>
</div>

<p class="source">Source: your dataset, with the exact query/time frame.</p>

<div class="foot"><span><span class="brand">BRAND</span> · 02 Evidence</span><span>4</span></div>

---

<!-- ============================================================
     BODY SLIDE with DISCIPLINED bullets (Rule of Seven).
     Use ONLY for precise data / ordered steps / logical sequences.
     <=3-5 points, one line each, revealed one at a time (<v-clicks>),
     paired with a visual. Otherwise prefer an image.
     ============================================================ -->

# Three conditions must all hold before we proceed

<div class="grid-2">
  <div>
    <v-clicks>

    - Condition one, stated in a single line
    - Condition two, stated in a single line
    - Condition three, stated in a single line

    </v-clicks>
  </div>
  <div class="evidence" style="margin-top:0;">
    <div class="card" style="width:100%; text-align:center; color: var(--ink-dim);">
      [ Icon or small diagram pairing the list ]
    </div>
  </div>
</div>

<div class="foot"><span><span class="brand">BRAND</span> · 03 Decision</span><span>5</span></div>

---

<!-- ============================================================
     BODY SLIDE with an equation (Typst pipeline, default).
     Math MUST be inside a ```typst block. A bare $..$ in the
     Markdown body is NOT Typst-processed. Renders as inline SVG.
     ============================================================ -->

# The projection maps world coordinates onto the screen

<div class="evidence">

```typst
#show math.equation: set text(size: 24pt, fill: white)
$ vec(v)_"screen" = M dot vec(v)_"world" + vec(t), quad
  M = mat(s_x, 0, t_x; 0, s_y, t_y; 0, 0, 1) $
```

</div>

<div class="foot"><span><span class="brand">BRAND</span> · 02 Evidence</span><span>6</span></div>

---

<!-- ============================================================
     BODY SLIDE with a Fletcher diagram (Typst pipeline, default).
     Non-math graphics MUST be wrapped in #html.frame(...).
     Connect nodes by <label> refs so arrows re-snap on edits.
     Needs the Typst package registry on first compile.
     ============================================================ -->

# The compiler routes each block to the right renderer

<div class="evidence">

```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import fletcher.shapes: diamond, pill, hexagon
#html.frame(diagram(
  spacing: (15mm, 11mm),
  node-stroke: 1.2pt + rgb("#38bdf8"),
  edge-stroke: 1.2pt + rgb("#64748b"),
  {
    node((0, 0), [Markdown], shape: pill, fill: rgb("#1e293b"), name: <in>)
    node((1, 0), [Typst block?], shape: diamond, fill: rgb("#1e293b"), name: <check>)
    node((2, 0), [Inline SVG], shape: pill, fill: rgb("#1e293b"), name: <svg>)
    node((1, 1), [Plain HTML], shape: hexagon, fill: rgb("#1e293b"), name: <html>)
    edge(<in>, <check>, "-|>", [parse])
    edge(<check>, <svg>, "-|>", [yes])
    edge(<check>, <html>, "-|>", [no], bend: 30deg)
  }
))
```

</div>

<div class="foot"><span><span class="brand">BRAND</span> · 02 Evidence</span><span>7</span></div>

---

<!-- ============================================================
     CLOSING SLIDE
     Restate the ONE core message as an assertion + a parallel visual.
     "Thanks / Questions" is a small footer so the message stays on
     screen through Q&A. Never a blank "Thank you!" slide.
     ============================================================ -->

<!-- class applies to this slide only -->

# The one sentence you want them to remember

<p class="kicker" style="margin-top: 14px;">A short reinforcing line, backed by the key visual from earlier.</p>

<div class="foot"><span><span class="brand">BRAND</span> · Thank you: let's discuss</span><span>8</span></div>

<style>
/* make just the closing slide centered like the title */
.slidev-layout { justify-content: center; align-items: center; text-align: center; }
.slidev-layout h1 { text-align: center; max-width: 100%; font-size: 3.2rem !important; }
.slidev-layout h1::after { margin-left: auto; margin-right: auto; }
</style>
