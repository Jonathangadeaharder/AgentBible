# Typst / CeTZ / Fletcher pipeline in Slidev

This is the default rendering path for math and precise diagrams. Prose and
layout stay in Slidev's Markdown + the CSS theme; **math** and **vector
diagrams** are compiled by Typst (via `slidev-addon-typst`) into inline SVG, so
they scale crisply and share one typographic system.

Status of the guidance below:
- **[compiled]** — verified by actually rendering it with the addon.
- **[docs]** — taken from the maintainers' official READMEs (CeTZ 0.5.2,
  Fletcher 0.5.8); authoritative but compile it once in your environment,
  because the package registry is required (see "Network" below).

## Contents

1. Setup and how the addon works
2. Mode discipline (the #1 source of errors)
3. Math
4. CeTZ (canvas geometry)
5. Fletcher (node/arrow diagrams)
6. Coordinates and the axis inversion
7. Step-by-step animation across clicks
8. Network / versions / troubleshooting

---

## 1. Setup and how the addon works  [compiled]

Enable the addon in the deck headmatter:

```yaml
---
addons:
  - slidev-addon-typst
---
```

Then write Typst inside fenced ```typst blocks. The addon compiles each block as
an **HTML-target** Typst document and injects the resulting SVG into the slide.
Two consequences you must design around:

- It runs at Markdown-transform (build) time in Node, not per-click. There is no
  live Typst reactivity to Slidev clicks (see §7).
- A block that fails to compile is replaced by **empty output** — the slide
  still renders, the diagram just silently disappears. So "my diagram vanished"
  usually means a Typst error; check the export log.

Nice touch: the addon maps `var(name)` inside Typst to the CSS variable
`--name` — write the name **without** the leading dashes, e.g. `stroke:
var(accent)` maps to `var(--accent)`. It only works for color values; when in
doubt (or for portability) use a literal `rgb("#…")`, as the examples below do.

## 2. Mode discipline — the #1 source of errors

Typst has three modes and mixing them up is the most common failure:

- **Markup mode** (default): plain text and elements.
- **Code mode**: entered with `#`, for function calls and expressions.
- **Math mode**: entered with `$ … $`.

Rules that actually bite:

- **Math must live inside a ```typst block.** A bare `$…$` typed in the Slidev
  Markdown body is **not** processed by Typst — it renders as literal italic
  text (verified). Put every equation in a ```typst block. *[compiled]*
- **Inside math, quote literal words.** `$vec(v)_"screen"$` renders "screen" as
  upright text; `$vec(v)_screen$` treats s,c,r,e,e,n as separate variables.
- **Wrap non-math graphics in `#html.frame(...)`.** Math equations are
  auto-framed by the addon's prelude, but a `cetz.canvas(...)` or a
  `diagram(...)` returns ordinary content and will *not* show up on HTML export
  unless you wrap it: `#html.frame(diagram(...))`. *[compiled]*
- **Don't `set page(...)` inside `html.frame`** — "page configuration is not
  allowed inside of containers." Size via the content itself. *[compiled]*
- **Import inside the block.** Declare `#import "@preview/…"` within each ```typst
  block; there is no shared global scope across blocks. *[docs/compiled]*

## 3. Math  [compiled]

````md
```typst
$ M = mat(s_x, 0, t_x; 0, s_y, t_y; 0, 0, 1) $
```
````

Block equations use `$ … $` with spaces; inline uses `$…$` without. For a
custom size, `#show math.equation: set text(size: 20pt)` at the top of the block.

## 4. CeTZ — programmable canvas  [docs]

CeTZ is the geometry layer (TikZ-like). Import version **0.4.2** (the latest
that runs on the addon's bundled compiler, Typst 0.13.1 — CeTZ 0.5.0+ needs
Typst ≥0.14.0 and fails silently under the addon).

````md
```typst
#import "@preview/cetz:0.4.2"
#html.frame(cetz.canvas({
  import cetz.draw: *
  set-style(stroke: rgb("#38bdf8") + 1.5pt)
  grid((0,0), (4,3), stroke: luma(80%) + .4pt)
  circle((2,1.5), radius: 1, name: "c")
  line((0,0), (4,3))
  content("c.north", [$P(x,y)$], anchor: "south", padding: .15)
}))
```
````

Reliable `cetz.draw` primitives: `line`, `rect`, `circle`, `arc`, `bezier`,
`grid`, `content`, `set-style`, and named anchors (give a shape `name: "c"`, then
reference `"c.north"`, `"c.center"`, etc.).

**For richer personality-driven visuals:** CeTZ is excellent for custom vector *illustrations*, not just technical diagrams. Draw stylized metaphors (branch with ants carrying food, simple object icons, organic curves) directly as vector paths. This gives full control, perfect scalability, and matches the image-rich style from your other decks without any external AI or raster files. See the helpers in `signature-theme/lib.typ` (sig-ant, sig-branch, etc.) as starting points. Always wrap in `#html.frame(sig-theme(...))`.

Corrections vs. common (AI-written) examples: there is **no `point()` draw
function** — use `circle(.., radius: …)` or a named anchor. Mark/arrowhead
styling changed across versions; prefer drawing arrows with Fletcher (§5) rather
than hand-styling CeTZ marks.

## 5. Fletcher — node & arrow diagrams  [docs]

Fletcher (current **0.5.8**, needs Typst ≥ 0.13) sits on CeTZ and is the right
tool for flowcharts, state machines, and commutative diagrams. These are the
maintainer's own README examples — known-good.

Flowchart with shapes:

````md
```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import fletcher.shapes: diamond, pill, hexagon
#html.frame(diagram(
  spacing: (12mm, 10mm),
  node-stroke: 1pt + rgb("#38bdf8"),
  {
    node((0,0), [Input], shape: pill, name: <in>)
    node((1,0), [Has Typst?], shape: diamond, name: <check>)
    node((2,0), [Inline SVG], shape: pill, name: <out>)
    node((1,1), [Plain HTML], shape: hexagon, name: <html>)
    edge(<in>, <check>, "-|>", [parse])
    edge(<check>, <out>, "-|>", [yes], label-pos: .5)
    edge(<check>, <html>, "-|>", [no], bend: 30deg)
  }
))
```
````

Math-mode diagram (concise, `&` separates nodes):

````md
```typst
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#html.frame(diagram(cell-size: 15mm, $
  G edge(f, ->) edge("d", pi, ->>) & im(f) \
  G slash ker(f) edge("ur", tilde(f), "hook-->")
$))
```
````

Key API facts (from the changelog):
- Reference nodes by `name: <id>` and connect with `edge(<a>, <b>, "-|>")`; named
  edges work in 0.5.8, CeTZ anchors in edge coords (`edge(<a.east>, …)`) since
  0.5.3.
- Edge arrowheads are shorthand strings: `"->"`, `"-|>"`, `"<->"`, `"hook-->"`,
  `"--|>"`, `"->>"`, etc.
- Multi-segment routes: `edge(<a>, <b>, "d,r,u", "-|>")` — the route string
  goes **before** the marks. Putting it after the marks fails to parse.
  [verified in 0.5.8]
- Curved edges: `bend: 30deg`; right-angled: `corner: left/right`.
- **`corner:` only on edges that actually change direction.** `corner: right`
  on a straight/colinear edge asserts "Adjacent vertices must be distinct"
  and the block renders empty. Use `corner:` only on diagonal edges.
  [verified failure in 0.5.8]
- **Group/enclose:** `node(enclose: (<a>, <b>), stroke: red)` draws a boundary
  around existing nodes.
- **Self-loops** need a bend so the two endpoints don't coincide:
  `edge(<n>, <n>, bend: 130deg)`. (This is the correct fix for the "zero-radius
  loop" problem — a real `bend`, not an epsilon coordinate hack.)

## 6. Coordinates and axis inversion  [docs]

CeTZ uses a Cartesian canvas (+y is up, one unit = 1cm). Fletcher uses an
**elastic grid** indexed like a matrix: `(col, row)`, and **row index grows
downward** — the opposite of CeTZ's y. So a Fletcher node at `(0,1)` sits *below*
`(0,0)`. Keep this in mind when mixing: since 0.5.0 Fletcher accepts CeTZ-style
coordinate expressions (relative, polar, named) alongside elastic `(col,row)`
points, but the two conventions differ in y-direction.

Prefer **logical label references** for edges (`edge(<a>, <b>)`) over absolute
vector coordinates. Fletcher then computes where the arrow meets each node's
outline automatically, and the arrows stay correct when node text (and therefore
size) changes.

## 7. Step-by-step animation across clicks  [docs]

The pasted research suggested passing Slidev's click state into Typst via
`sys.inputs` and re-rendering per click. That does **not** work with this addon:
compilation happens once at build time, so `sys.inputs` is fixed per deck, not
per click. Use one of these instead:

- **`fletcher.hide(..)`** — draw the final diagram but hide later elements,
  reserving their space so the layout doesn't jump. Combine with duplicated
  slides (one per reveal) so each step is a full render. This is the officially
  intended mechanism for incremental diagrams.
- **Multiple slides** — the simplest robust approach: one slide per state, each a
  complete `diagram(...)`. Keep node positions identical so nothing shifts.
- **Layout stability for overlays** — when you *do* add an element in a later
  state, place it outside the elastic grid using an offset from a stable anchor,
  e.g. a node at `(rel: (10mm, -5mm), to: <stable>)`, so the base grid isn't
  recomputed and existing nodes don't jump.

## 8. Network, versions, troubleshooting

- **Network (important):** the first compile of any deck using `@preview/cetz`
  or `@preview/fletcher` downloads those packages from `packages.typst.org`.
  Environments that block that host (some locked-down sandboxes) will silently
  render diagram blocks as empty. Packages are cached after the first successful
  fetch. If diagrams come out blank, check registry access first. Math (no
  package) works fully offline.
- **Version matching:** the addon bundles a Typst compiler via
  `@myriaddreamin/typst-ts-node-compiler` (≈ Typst 0.13 at addon 1.0.x). CeTZ and
  Fletcher pin a minimum Typst; if a compile error mentions the Typst version,
  pin the packages to versions compatible with the addon's compiler (e.g. an
  older CeTZ) or update the addon. Check the compiler version with
  `cat node_modules/@myriaddreamin/typst-ts-node-compiler/package.json`.
- **Debugging a vanished diagram:** run the export from a terminal and read the
  log — the addon prints Typst errors and diagnostics even though it emits empty
  output for the failed block.
- **Alternative — touying:** if the deliverable is a *PDF-native* deck rather
  than a web deck, the pure-Typst framework `touying` handles `#pause` /
  `#meanwhile` animations natively (including CeTZ/Fletcher) via an internal
  reducer, but it does not run Vue/HTML. Use it only when you've dropped the
  Slidev/web requirement.
