# Accessibility (WCAG) for slides

Accessible design is not optional polish — it decides whether people with low
vision, color-blindness, or reading differences can follow at all, and it makes
the deck more legible for *everyone* in a badly-dimmed room. The reference
standard is the Web Content Accessibility Guidelines (WCAG 2.1/2.2).

## Contrast

Contrast is the ratio of relative luminance between text and background, from
**1:1** (none) to **21:1** (black on white). WCAG thresholds depend on text size:

- **Normal text** (below 18 pt, or below 14 pt bold): **≥ 4.5:1**.
- **Large text** (≥ 18 pt, or ≥ 14 pt bold): **≥ 3:1**.

Point-to-pixel conversion: **1 pt ≈ 1.333 px**. So "large" means about
**≥ 24 px** normal or **≥ 18.5 px** bold in CSS terms.

Practical rule: set slide **titles ≥ 28 pt**, which comfortably clears the 3:1
bar and stays legible from the back of a room. Even so, aim for a **high** ratio
in general — **> 7:1** is the target for body text under Universal Design, since
projectors and sunlit rooms erode contrast badly.

The template in `assets/deck-template/styles.css` ships tokens that already meet
AA; if you change colors, re-check the pairing with a contrast checker.

## Color-blindness — never encode by color alone

A significant share of any audience has red-green or blue-yellow color vision
deficiency, so color must never be the *only* channel carrying meaning.

- **Avoid ambiguous pairs:** red/green, blue/green, green/gray, and green/yellow
  have near-identical perceived brightness for color-blind viewers and merge.
- **Add a redundant channel:** if red = bad and green = good in a chart, also mark
  them with distinct **symbols** (✗ vs ✓) or **patterns** (hatched vs solid), not
  just hue.
- **Test** by desaturating the slide to grayscale — if the distinction survives,
  it's robust.

## Backgrounds and readability

- Avoid busy background images, patterns, and gradients behind text — they wreck
  legibility.
- Prefer **homogeneous, matte, lightly-tinted** backgrounds (soft pastel or cream
  tones): they cut glare and make text markedly easier to read for people with
  dyslexia. (A calm dark background with high-contrast text works equally well;
  the template offers both.)

## Screen readers and reading order

For blind or low-vision people who consume the deck afterward via a screen
reader:

- **Alt text on every image and diagram** — a precise description of what it
  shows and why it matters, not "image1.png".
- **Verify the reading order.** Screen readers announce objects in the order they
  were *created*, which usually scrambles the meaning. Check and set the logical
  reading order in the tool's metadata / accessibility pane.

## Typography minimums (recap)

- Titles ≥ 28 pt and clearly the largest element on the slide.
- Body ≥ 18 pt equivalent.
- ≤ 2 font families (one display, one body).
- Emphasis with **bold**, never underline (underlines clip descenders and slow
  reading — see `cognitive-design.md` §5).
