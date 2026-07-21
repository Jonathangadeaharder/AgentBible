#import "@preview/cetz:0.4.2"
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import fletcher.shapes: circle as fcircle

#let sig-bg      = rgb("#1a1a2e")
#let sig-fg      = rgb("#f5f5fa")
#let sig-accent  = rgb("#8be9fd")
#let sig-accent2 = rgb("#ff79c6")
#let sig-muted   = rgb("#6272a4")
#let sig-surface = rgb("#1e1e24")

#let sig-theme(body) = {
  set text(font: ("Avenir Next", "Inter", "system-ui", "sans-serif"), fill: sig-fg)
  show math.equation: set text(font: ("New Computer Modern Math", "STIX Two Math"))
  body
}

#let sig-cetz = (
  stroke: 1.2pt + sig-fg,
  mark: (stroke: (dash: none), fill: sig-accent2, width: 1.6pt),
)

#let sig-node-rect = node.with(
  shape: rect,
  stroke: 1.8pt + sig-accent2,
  fill: sig-accent2.darken(30%),
  inset: 0.55em,
)

#let sig-node-circle = node.with(
  shape: fcircle,
  stroke: 1.8pt + sig-accent,
  fill: sig-accent.darken(28%),
  inset: 0.5em,
)

#let sig-edge = edge.with(
  stroke: 1.4pt + sig-fg,
)

// Illustrative helpers (CeTZ). Use inside cetz.canvas.

#let sig-branch(start, end) = {
  cetz.draw.line(start, end)
  for i in range(3) {
    let off = (i - 1) * 0.15
    cetz.draw.line(
      (start.at(0), start.at(1) + off),
      (end.at(0), end.at(1) + off),
      stroke: 1pt + rgb("#5C4033").darken(20%)
    )
  }
}

#let sig-ant(x, y, s: 1, phase: 0) = {
  let p = phase
  cetz.draw.circle((x, y), radius: 0.18 * s, fill: rgb("#B71C1C"), stroke: none)
  cetz.draw.circle((x + 0.13 * s, y), radius: 0.07 * s, fill: rgb("#9B1C2E"), stroke: none)
  cetz.draw.circle((x + 0.25 * s, y), radius: 0.10 * s, fill: rgb("#C62828"), stroke: none)
  cetz.draw.circle((x + 0.38 * s, y), radius: 0.082 * s, fill: rgb("#8B0000"), stroke: none)
  cetz.draw.circle((x + 0.415 * s, y + 0.028 * s), radius: 0.017 * s, fill: rgb("#FFEB3B"), stroke: none)
  cetz.draw.circle((x + 0.415 * s, y - 0.028 * s), radius: 0.017 * s, fill: rgb("#FFEB3B"), stroke: none)
  cetz.draw.line((x + 0.03 * s, y - 0.04 * s), (x - 0.10 * s, y - 0.17 * s), stroke: 0.6pt + rgb("#4A0000"))
  cetz.draw.line((x - 0.10 * s, y - 0.17 * s), (x - 0.20 * s, y - 0.09 * s + p*0.03), stroke: 0.45pt + rgb("#4A0000"))
  cetz.draw.line((x + 0.03 * s, y + 0.04 * s), (x - 0.10 * s, y + 0.17 * s), stroke: 0.6pt + rgb("#4A0000"))
  cetz.draw.line((x - 0.10 * s, y + 0.17 * s), (x - 0.20 * s, y + 0.09 * s - p*0.03), stroke: 0.45pt + rgb("#4A0000"))
  cetz.draw.bezier((x + 0.43 * s, y + 0.015 * s), (x + 0.59 * s, y + 0.13 * s), (x + 0.49 * s, y + 0.04 * s), stroke: 0.45pt + rgb("#5D001A"))
  cetz.draw.bezier((x + 0.43 * s, y - 0.015 * s), (x + 0.57 * s, y - 0.09 * s), (x + 0.49 * s, y - 0.03 * s), stroke: 0.45pt + rgb("#5D001A"))
}

#let sig-simple-food(pos, kind: "sandwich", s: 1) = {
  if kind == "sandwich" {
    // Simple sandwich shape
    rect((pos.at(0)-0.2cm*s, pos.at(1)-0.1cm*s), (pos.at(0)+0.2cm*s, pos.at(1)+0.1cm*s), fill: rgb("#D2B48C"), stroke: 0.8pt + black)
    // Lettuce hint
    line((pos.at(0)-0.15cm*s, pos.at(1)), (pos.at(0)+0.15cm*s, pos.at(1)), stroke: 1.5pt + rgb("#228B22"))
  } else if kind == "soda" {
    // Glass
    rect((pos.at(0)-0.08cm*s, pos.at(1)-0.18cm*s), (pos.at(0)+0.08cm*s, pos.at(1)+0.12cm*s), fill: rgb("#2F4F4F"), stroke: 1pt + sig-fg)
    // Straw
    line((pos.at(0), pos.at(1)+0.12cm*s), (pos.at(0)+0.05cm*s, pos.at(1)+0.25cm*s), stroke: 2pt + rgb("#FF6347"))
  } else if kind == "turkey" {
    // Very simplified bird shape
    circle(pos, radius: 0.15cm*s, fill: rgb("#CD853F"), stroke: 0.8pt + black)
    circle((pos.at(0)+0.12cm*s, pos.at(1)), radius: 0.08cm*s, fill: rgb("#8B4513"))  // head
  }
}

// Additional helpers for richer scenes
#let sig-leaf(pos, s: 1) = {
  // Simple leaf shape
  circle((pos.at(0), pos.at(1)), radius: 0.12cm*s, fill: rgb("#228B22"), stroke: 0.5pt + rgb("#006400"))
  line((pos.at(0), pos.at(1)-0.1cm*s), (pos.at(0), pos.at(1)+0.1cm*s), stroke: 0.8pt + rgb("#006400"))
}

#let sig-flower(pos, s: 1) = {
  // Simple flower
  for angle in (0, 60, 120, 180, 240, 300) {
    let rad = 0.12cm * s
    let x = pos.at(0) + rad * calc.cos(angle * 1deg)
    let y = pos.at(1) + rad * calc.sin(angle * 1deg)
    circle((x, y), radius: 0.08cm*s, fill: rgb("#FF69B4"), stroke: none)
  }
  circle(pos, radius: 0.06cm*s, fill: rgb("#FFD700"), stroke: 0.5pt + rgb("#FFA500"))
}

#let sig-anthill(pos, s: 1) = {
  // Simple anthill
  bezier((pos.at(0)-0.3cm*s, pos.at(1)), (pos.at(0)+0.3cm*s, pos.at(1)), (pos.at(0), pos.at(1)+0.25cm*s), fill: rgb("#8B7355"), stroke: 1pt + rgb("#5C4033"))
  // Entrance
  circle((pos.at(0), pos.at(1)+0.05cm*s), radius: 0.06cm*s, fill: rgb("#3D2914"), stroke: none)
}
