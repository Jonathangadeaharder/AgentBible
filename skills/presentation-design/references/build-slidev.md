# Building and rendering the deck (Slidev)

The technical how-to for Phase 2/3. The goal of using Slidev is not the tool
itself — it's that a Markdown+CSS deck can be **rendered to images and inspected**,
which is the only reliable way to catch overflow, contrast, and hierarchy bugs.

## Start from the template

Copy `assets/deck-template/` to a working folder (e.g., inside the user's project):

```
my-deck/
├── slides.md        # the deck; edit this
├── styles.css       # theme tokens + the hierarchy fix; edit tokens to rebrand
├── setup/main.ts    # loads styles.css (leave as-is)
├── package.json
└── images/          # put photos/diagrams here; reference as ./images/x.png
```

Then:

- Replace `BRAND` and the section labels in the `.foot` of each slide.
- Write a **full-sentence assertion** as each body slide's `#` headline.
- Put one visual in each `.evidence` region (real image/diagram/chart), and cite
  it in the `.source` line.
- Recolor by editing the `:root` tokens in `styles.css` (a light, dyslexia-friendly
  alternative is included as a comment). Keep contrast ≥ 4.5:1 — see
  `accessibility.md`.
- For equations or precise diagrams, use the Typst pipeline (enabled by default
  via `addons: [slidev-addon-typst]` in the headmatter): put math in ```typst
  blocks and diagrams in `#html.frame(...)`. Full rules and verified CeTZ/Fletcher
  syntax are in `typst-pipeline.md`. Diagram packages need registry access on
  first compile; if a diagram renders blank, that's the cause.

Optional live preview while editing: `npm install && npm run dev` (opens a local
server). Not required for rendering.

## Render with the script

```bash
bash scripts/render_deck.sh /abs/path/to/my-deck
```

This installs the toolchain (first run only), exports every slide to
`my-deck/renders/slide-NN.png`, and writes `my-deck/deck.pdf` **and**
`my-deck/deck.pptx`. Re-runs are fast (install, browser, and stubs are cached).

All three outputs, every run — never PDF alone. The PPTX is built by
`scripts/build_pptx.py` (called by the render script): each rendered PNG becomes
a full-bleed 16:9 slide and the slide's presenter notes are embedded as PPTX
speaker notes. **PPTX is the delivery format** — it is the only format Keynote
imports with the notes intact; the PDF is for sharing/printing.

## Slide separators and frontmatter — get these right or slides silently merge

Slidev's parser is strict about `---`:

- A slide separator is a line containing exactly `---` with a **blank line
  before and after it**. Without the padding, the separator can be read as
  frontmatter fencing and entire slides get eaten into YAML — the export
  "succeeds" with fewer, garbled slides.
- A per-slide frontmatter block (`layout: center`, `class: text-center`, …)
  must sit **immediately** after the separator:

  ```
  (blank line)
  ---
  layout: center
  class: text-center
  ---
  (blank line)
  # Slide content starts here
  ```

  If a blank line sneaks in between the separator and the frontmatter, the
  frontmatter renders as a *separate, nearly-empty slide* and the real slide
  duplicates — the classic "same title appears twice, deck has N+2 pages" bug.
- **Edit `slides.md` directly with targeted edits.** Do not regenerate the whole
  file from ad-hoc regex/Python scripts — every observed separator corruption
  came from a generator script that mishandled the rules above. If you must
  script a transformation, split on separators with a real parser discipline and
  re-verify the slide count in the export log afterwards.
- **Sanity check after every render:** the number of exported PNGs must equal
  the number of slides you think the deck has. A mismatch means a separator bug,
  even if the export reported success.

## Presenter notes and page numbers

- Presenter notes are the **last `<!-- ... -->` block** of a slide. Every body
  slide gets one (see SKILL.md rule 9); they become PPTX speaker notes.
- Never hardcode page numbers in footers. Use Slidev's counters so inserting a
  slide can't desynchronize the deck:

  ```html
  <div class="foot"><span>…</span><span>{{ $slidev.nav.currentPage }} / {{ $slidev.nav.total }}</span></div>
  ```

## The render → inspect → fix loop (Phase 3 gate)

1. Run the script.
2. **Read every PNG** and check the visual rubric from `SKILL.md` Phase 3:
   overflow / footer collision / edge-touch; title is clearly the largest element;
   contrast; color-not-the-only-signal; correct chart type; whitespace present;
   typos in headlines and labels.
3. Fix `slides.md` / `styles.css` and re-render. Iterate until it passes. Do not
   ship on the first render.

Concrete fixes for the usual problems:

- **Content overflows / collides with the footer:** the assertion is too long or
  the evidence too tall. Shorten the headline, trim call-outs, or reduce the
  visual's size. As a global relief valve, reduce `.slidev-layout` padding
  slightly.
- **Title looks small / hierarchy inverted:** this is the Slidev base-layer
  override. It's already fixed in `styles.css` via `.slidev-layout h1 { … !important }`.
  Do **not** "simplify" those rules to a bare `h1 {}` — the bug returns and you
  won't see it in the source, only in the render.
- **Low contrast:** pick tokens with a higher luminance gap; verify with a
  contrast checker (`accessibility.md`).

## Why the script does what it does (troubleshooting)

If you ever render manually instead of via the script, these are the environment
facts that make or break it:

- **Install on the local filesystem, not a network-mounted folder.** `npm install`
  on a mount is slow and hits `ENOTEMPTY` on rename. The script stages sources in
  `$HOME/.ae-deck-build` and renders there.
- **Use `npm`.** `corepack enable`/`pnpm` may fail with a permission error when
  it tries to symlink into a system path.
- **Chromium needs `libXdamage.so.1`** (and sometimes other X libs) which minimal
  sandboxes lack and which can't be `apt`-installed without root or network
  access to the mirror. The script detects missing libs via `ldd`, extracts the
  relevant undefined symbols from the Chromium binary, and compiles a tiny no-op
  stub `.so` with `gcc`, then adds it to `LD_LIBRARY_PATH`. Headless Chromium
  never actually calls these functions, so no-ops are safe.
- **Playwright browsers** install into a local cache via
  `PLAYWRIGHT_BROWSERS_PATH` so they persist across runs.
- Exports are **1920×1080 16:9**; the deck uses `theme: none` so no theme package
  is required.

## Common authoring pitfalls

- **Duplicate `class:` key in the headmatter.** The first frontmatter block both
  configures the deck and styles slide 1; if you add `class:` there, make sure
  there isn't already one (duplicate YAML keys break parsing).
- **Image paths** are relative to the deck folder (`./images/…`); the script
  copies `images/` into the build dir for you.
- **Per-slide overrides** go in a `<style>` block on that slide (the closing slide
  in the template shows this) or via a `class:` in that slide's frontmatter.
- Keep it to **≤ 2 font families** and let whitespace breathe (≥ 30–40%).
- **Inline-SVG / Vue-component `<text>` renders huge.** The slide's CSS
  `font-size` cascades into SVG `<text>`, and **CSS beats an SVG presentation
  attribute** — so `font-size="15"` set on a `<g>` ancestor is ignored and the
  label inflates to body size (tiny nodes, giant labels). Set the size *directly
  on each `<text>`* — as an attribute (`<text font-size="13">`, which wins
  because it's on the element itself) or, to be bulletproof, as an inline style
  (`style="font:bold 15px …"`). Never rely on font-size inherited from a parent
  `<g>` inside a slide. You only catch this by looking at the render.
- **Never put `>`/`>=`/`<` in a Vue binding expression inside an SVG/HTML
  template.** `:opacity="step>=1 ? 1 : 0.3"` — the `>` is read as a tag close,
  so every attribute *after* the first comparison is silently dropped. The
  element keeps its earlier attributes and loses stroke/opacity/etc., so
  dynamic edges and nodes render invisible while static ones look fine (a
  maddening partial failure). Fix: compute the values in `<script setup>`
  (a `computed` returning a color/number/array) and bind the plain result;
  keep all comparisons out of the template.
