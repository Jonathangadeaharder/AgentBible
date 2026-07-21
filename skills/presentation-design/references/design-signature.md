# Design signature — a reusable visual identity

A "signature" is one coherent visual identity — type, color, CeTZ drawing style,
Fletcher node/edge style — captured once and reused across every deck, so a
person's or team's presentations look like *theirs*. This module defines an
interactive setup interview that produces the signature, and the architecture
that makes it reusable across projects.

Run this **once** per person/team (or when they want to restyle), not per deck.
It is optional: without a signature, decks use the template defaults. When a
signature exists, decks import it.

Everything here obeys the skill's core principles — a signature changes *how*
things look, never the Assertion-Evidence structure, the low-cognitive-load
discipline, or the WCAG contrast floors in `accessibility.md`.

## Contents

1. The setup interview (6 phases)
2. How choices map to code
3. The signature architecture (local package + CSS)  [verified]
4. Installing the signature as a local Typst package  [verified]
5. A verified starter `lib.typ`
6. Technical gotchas the generator must handle

---

## 1. The setup interview

Run with `AskUserQuestion`, one phase at a time, each with 2–3 options. Keep
options technologically compatible so no combination produces a broken or
inaccessible deck. Recommend a default in each phase.

**Phase 1 — Format & density.** `16:9` modern screen (default) vs `4:3` classic
academic (higher density, conference projectors). Both stay in Slidev; this sets
`aspectRatio` and the base type scale. (A pure-Typst/PDF path via `touying` is
possible if the user drops the web requirement — see `typst-pipeline.md` §8.)

**Phase 2 — Typography.** Pick a pairing (display/body + a matching math font so
equations share the weight):
- *Technical modern* — Fira Sans + Fira Math.
- *Humanist minimal* — Jost* (a free Futura-like) + Noto Sans Math.
- *Classic academic* — New Computer Modern + New Computer Modern Math.

**Phase 3 — Palette & contrast mode.** Anchor the same colors in both the Slidev
CSS layer and the Typst color variables:
- *Dark* — deep background (e.g. `#1a1a2e`), luminous accents (cyan/pink/purple).
- *Paper* — warm cream background, dark-gray (not pure-black) text; low eye strain.
- *Monochrome print* — grayscale for PDF/print, subtle grid contours.
- Guardrail: whatever the choice, text↔background must clear **4.5:1** (aim >7:1).
  Re-check after applying — see `accessibility.md`.

**Phase 4 — CeTZ drawing style.** How plots/geometry look:
- *School-book* — axes crossing at the origin, arrow tips, no enclosing frame,
  minimal/no grid.
- *Technical grid* — full frame, dashed major/minor grid behind the data.

**Phase 5 — Fletcher node aesthetic.**
- *Structural* — angular shapes (rect/parallelogram/hexagon), thin precise
  outline, transparent/lightly-tinted fill.
- *Organic* — rounded pills/ellipses with a soft fill for depth.

**Phase 6 — Edge & arrowhead style.**
- *Curved* — gentle Bézier bends, slim stealth-style heads, automatic
  path-shortening so lines meet the node outline.
- *Orthogonal* — strict horizontal/vertical segments with corner radii and
  solid right-angle heads.

**Phase 7 — Image language & personality.** How visuals carry story and soul:
- *Vector illustration first (preferred for control)* — draw custom metaphors directly with CeTZ inside Typst (stylized ants on branch, object icons, organic forms). Lives in the repo, perfectly scalable, no external AI. Use the helpers in `signature-theme/lib.typ`.
- *Photographic & atmospheric* — real photos only when a specific capture adds irreplaceable emotional or documentary value.
- *Schematic / diagram-first* — Fletcher + CeTZ for logic and precision (use when the idea is best expressed structurally).

Save the answers to a small JSON (e.g. `signature.json`) so the signature can be
regenerated or tweaked later without re-interviewing.

## 2. How choices map to code

Each phase writes into two artifacts kept in lockstep:

- the **Typst preamble** (`lib.typ`): color `#let`s, a theme function that sets
  `text`/`math.equation` fonts and fills, the CeTZ style dict, and `node.with` /
  `edge.with` helpers.
- the **Slidev CSS** (`styles.css`): `:root` tokens mirroring the same colors and
  fonts so HTML chrome and Typst SVGs match exactly.

Keep one source of truth for color: pick the hex values once, write them into
both files. (The addon can also pull a CSS variable into Typst by writing
`var(name)` — no leading dashes — but duplicating the hex is simplest and most
portable.)

## 3. The signature architecture  [verified]

```
signature-theme/            ← becomes a local Typst package
├── typst.toml              ← package metadata (name, version, entrypoint)
└── lib.typ                 ← colors + apply-theme + CeTZ style + node/edge helpers

<deck>/
├── slides.md               ← imports the signature in its ```typst blocks
├── styles.css              ← :root tokens mirroring the signature colors/fonts
└── setup/main.ts
```

Two ways to reference the signature from a deck's ```typst blocks — **both
verified to render through slidev-addon-typst**:

- **Project-local:** copy `lib.typ` to the deck's `setup/` and
  `#import "/setup/lib.typ": *`. Paths starting with `/` resolve to the deck
  (project) root. Good for a one-off deck.
- **Cross-project (the signature):** install once as a local package and
  `#import "@local/signature-theme:0.1.0": *` from any deck, at any folder depth,
  offline. This is the reuse mechanism — prefer it.

Why a package and not a shared file path: Typst resolves relative imports against
the *defining* file and confines `/`-absolute paths to the project root, so a
`lib.typ` sitting outside the deck folder is blocked by the compiler sandbox.
Local packages are the sanctioned way out — they resolve regardless of location.

## 4. Installing the signature as a local Typst package  [verified]

Place `typst.toml` + `lib.typ` under the OS "local" package dir at
`local/<name>/<version>/`:

- **Linux:** `~/.local/share/typst/packages/local/signature-theme/0.1.0/`
  (honors `$XDG_DATA_HOME`)
- **macOS:** `~/Library/Application Support/typst/packages/local/signature-theme/0.1.0/`
- **Windows:** `%APPDATA%\typst\packages\local\signature-theme\0.1.0\`

`scripts/install_signature.sh <signature-theme-dir> [version]` detects the OS and
copies the files into the right place. After install, any deck can
`#import "@local/signature-theme:0.1.0": *`. Verified: a block importing a
freshly-installed `@local/signature-theme` renders correctly with no registry
access.

Bump the version folder (`0.2.0`, …) when the signature changes so old decks that
pin a version keep compiling.

## 5. A verified starter `lib.typ`

Uses only constructs confirmed to compile through the addon (colors, `text` /
`math.equation` show rules, a CeTZ style dict with the mark-stroke fix, and
`node.with` / `edge.with` helpers). Fill the values from the interview.

```typst
#import "@preview/cetz:0.4.2"
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import fletcher.shapes: pill, hexagon, diamond

#let sig-bg     = rgb("#1a1a2e")
#let sig-fg     = rgb("#f5f5fa")
#let sig-accent = rgb("#8be9fd")
#let sig-accent2 = rgb("#ff79c6")
#let sig-muted  = rgb("#6272a4")

// Fonts + colors for INLINE use in Slidev (no `set page` — see gotchas).
#let sig-theme(body) = {
  set text(font: ("Fira Sans", "Inter", "system-ui", "sans-serif"), fill: sig-fg)
  show math.equation: set text(font: ("Fira Math", "New Computer Modern Math"))
  body
}

// CeTZ style — note the mark stroke is isolated so a dashed global
// stroke does not fragment arrowheads.
#let sig-cetz = (
  stroke: 0.9pt + sig-fg,
  mark: (stroke: (dash: none), fill: sig-accent2),
)

// Fletcher helpers. Arrowhead via the "-|>" shorthand (solid stealth-like);
// swap to bend:/corner: at the call site for curved vs orthogonal edges.
#let sig-node = node.with(shape: pill, stroke: 1.2pt + sig-accent,
                          fill: sig-bg.lighten(8%), inset: 0.5em)
#let sig-edge = edge.with(stroke: 1pt + sig-fg)
```

Usage inside a deck (verified pattern — wrap non-math in `html.frame`):

```typst
#import "@local/signature-theme:0.1.0": *
#html.frame(sig-theme(diagram(spacing: 3em, {
  sig-node((0,0), [X], name: <x>)
  sig-node((2,0), [Y], name: <y>)
  sig-edge(<x>, <y>, "-|>", label: [f])
})))
```

## 6. Technical gotchas the generator must handle

- **Never `set page(...)` inside `html.frame` or inside an inline signature used
  by Slidev.** It errors ("page configuration is not allowed inside of
  containers") or forces PDF pagination. `set page` belongs only to a
  *pure-Typst/PDF* build (touying), not the Slidev-inline path. The starter
  `sig-theme` above deliberately sets only `text`/`math`.
- **Isolate mark strokes in CeTZ.** A global `set-style(stroke: (dash: "dashed"))`
  is inherited by arrowhead outlines and renders fragmented heads. Reset it:
  `set-style(stroke: (dash: "dashed"), mark: (stroke: (dash: none)))`.
- **Literal `@` in Typst markup is a reference.** Text like "email me @acme" or a
  package name shown in content triggers `label does not exist`. Escape as `\@`
  or avoid `@` in displayed content. (Verified failure mode.)
- **Fletcher bounding boxes are rectangular.** Non-rectangular nodes (circles,
  triangles) can leave edges docking off the visible outline or `enclose` groups
  with slack. Tighten with a shape `fit` factor where the shape supports it, and
  prefer label-reference edges so Fletcher snaps to the outline. For dense
  auto-layout, the `autograph` package can position nodes via Graphviz
  (`circo`/`dot`) — treat it as advanced/optional and confirm it compiles in the
  target environment before relying on it.
- **Keep contrast legal after theming.** Re-run the contrast check from
  `accessibility.md` on the chosen palette; luminous-on-dark and gray-on-cream
  both need ≥ 4.5:1 for body text.
