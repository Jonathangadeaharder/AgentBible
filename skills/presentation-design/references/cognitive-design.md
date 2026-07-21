# The science of effective slides

Why the rules in `SKILL.md` are the rules. Read the section you need; each ends
with the concrete design implication.

## Contents

1. Working memory and Cognitive Load Theory
2. Mayer's Cognitive Theory of Multimedia Learning (12 principles)
3. The Assertion-Evidence structure (and its evidence)
4. Tufte's critique of the "cognitive style of PowerPoint"
5. Kosslyn's 8 principles of perception
6. Picture-Superiority and dual coding
7. The bullet-point debate and the Rule of Seven

---

## 1. Working memory and Cognitive Load Theory

Humans process visual and auditory information through **separate, limited**
channels. Baddeley's model: a *phonological loop* (speech/text), a
*visuo-spatial sketchpad* (images/space), an *episodic buffer* that integrates
them and links to unlimited long-term memory, all steered by a *central
executive* that allocates attention. The bottleneck is the two input channels.

Sweller's **Cognitive Load Theory** names three loads on working memory:

- **Intrinsic** — the inherent difficulty of the material. Managed by
  *segmenting*: break complex content into small, sequential pieces.
- **Extraneous** — load created by *how* information is presented: visual
  clutter, poor text/image coordination, decorative noise. This is wasted
  budget. **Killing extraneous load is the primary job of slide design.**
- **Germane** — the productive effort of building mental models and moving them
  into long-term memory. Good design frees budget for this.

Capacity is small. Miller's classic estimate was 7±2 chunks; for genuinely new,
complex material the usable number is lower. When intrinsic + extraneous load
exceeds capacity, you get **cognitive overload** — the transfer to long-term
memory stalls entirely. This is the mechanism behind "Death by PowerPoint."

**Implication:** every element that isn't carrying the point is extraneous load.
Remove it. Segment complex ideas across slides or builds.

---

## 2. Mayer's Cognitive Theory of Multimedia Learning

Core premise: people learn more deeply from **words + coordinated images** than
from words alone. Mayer's twelve research-based principles double as slide rules.

| Principle | Mechanism | Best practice | Worst practice |
|---|---|---|---|
| Multimedia | Image and speech use two channels | Diagram/photo supports the spoken explanation | Text-only slides |
| Coherence | Irrelevant detail steals capacity | Strip logos, background music, decorative frames | Sound effects, purely decorative stock photos |
| Redundancy | On-screen text + identical narration overloads the phonological loop | Show a graphic; explain it aloud with *no* on-slide sentence | Reading verbatim bullet text aloud |
| Spatial contiguity | Visual search between figure and text tires the eye | Put labels *in/next to* the figure | Legend on the opposite side from the figure |
| Temporal contiguity | Delay breaks the mental link | Show visual and say the words at the same time | Graphic minutes before/after the explanation |
| Modality | On-screen text and a graphic split the visual channel | Complex visual + spoken narration only | Detailed diagram + long adjacent paragraph |
| Signaling | Cues steer attention | Contrasting arrows, circles, color to highlight the key point | Complex data with no visual guidance |
| Segmenting | Complex flows need digestible steps | One multi-step process → a sequence of simple slides | A whole workflow crammed on one slide |
| Pre-training | Knowing key terms first frees processing | Define core terms before the complex system | Diving into system analysis with no vocabulary |
| Personalization | A conversational tone activates cognition | Informal "I / we / you" in the talk | Stiff, over-academic distance |
| Voice | Human voices create social presence | Lively, well-modulated human narration | Monotone / robotic text-to-speech |
| Image | A permanent "talking head" adds nothing | Speaker on screen briefly (trust), then focus on visuals | Speaker's face parked next to the content throughout |

**The redundancy number to remember:** retention drops on average **~79%** when
a graphic is presented with *both* written text and identical narration — the
eye is torn between reading and looking. Don't do it.

Strong, specific images also carry affective and emotional weight beyond pure information transfer. A memorable metaphorical or atmospheric image creates attachment and long-term recall that a clean schematic rarely matches. In your strongest decks, images often function as the emotional protagonist of the idea (e.g. a snowy road for "fixing", a broken classic car for legacy code, ants foraging with food for evolution).

---

## 3. The Assertion-Evidence structure

The default PowerPoint/Google Slides layout — a short topic phrase on top and a
hierarchical bullet list below — systematically violates the principles above.
Michael Alley (Penn State) replaced it with **Assertion-Evidence (AES)**:

```
Traditional (worst practice)        Assertion-Evidence (best practice)
┌───────────────────────────┐       ┌───────────────────────────────────┐
│           TOPIC           │       │  ASSERTION (a full sentence, ≤2 ln) │
├───────────────────────────┤       ├───────────────────────────────────┤
│ • bullet 1                │       │            ┌───────────┐            │
│ • bullet 2   (text wall,  │       │            │  VISUAL   │            │
│ • bullet 3    split focus)│       │            │  EVIDENCE │            │
└───────────────────────────┘       │            └───────────┘            │
                                     └───────────────────────────────────┘
```

**Slide typology:**

- **Title slide** — a striking, high-res key image + title, not a name on white.
  Prefer an image that recurs later in the talk.
- **Mapping slide** — a *visual* agenda: a two-line assertion headline with
  sections shown as images, not a text list. ≤3 sections for 10–15 min; ≤5 ever.
- **Body slides** — left-aligned full-sentence assertion (≤2 lines) on top;
  the body is visual evidence (photo, drawing, chart, process). Body text only as
  short labels or ≤2 call-outs.
- **Closing slide** — restate the single core message as an assertion + a
  parallel visual. "Thanks/Questions" is a small footer, so the message stays up
  during Q&A. Never a blank "Thank you!" slide.

**Metacognitive bonus for the presenter:** writing an assertion headline forces
you to analyze the data, extract the one key finding, and state it in a complete
sentence. If you can't fit it in two lines, the slide's point is still too
complex or unclear. The format makes muddled thinking visible — to you, first.

**Empirical results (Garner & Alley, engineering students, unfamiliar MRI/tumor
topic):**

| Test | Traditional (topic + bullets) | Assertion-Evidence |
|---|---|---|
| Conceptual understanding (essay) | Lower scores; frequent misconceptions | Significantly higher; accurate grasp of the dynamic process |
| Higher-order transfer (quiz) | Worse on transfer tasks | Markedly better |
| Retention after 1 week | Steep drop in recalled detail | Significantly stronger across all question types |

---

## 4. Tufte's critique of PowerPoint

Edward Tufte (*The Cognitive Style of PowerPoint*) argues the default medium
degrades analytical quality:

- **"PowerPoint phluff":** low-resolution slides carry little real content
  (Tufte's median: ~40 words per text slide ≈ 8 seconds of reading), so the void
  gets filled with templates, animations, shadows, and logos. Thin content →
  more phluff → thinner substance: a vicious cycle.
- **Relentless sequentiality:** slides force information into a temporal queue
  ("one damn slide after another"), but humans reason *spatially and
  comparatively* — we understand data best seen side by side. Bullet hierarchies
  also **de-quantify**: numbers lose units and precision, arguments become
  slogans.
- **Real stakes:** in the Challenger and Columbia reviews, NASA's safety analyses
  lived in deeply nested bullet decks. Critical risks (e.g., foam strike) were
  buried on low hierarchy levels or softened into vague, unit-less phrases; the
  structured superficiality helped lull decision-makers into false confidence.
- **Recommendation for high-stakes technical/business meetings:** consider
  *no projected slides at all*. Hand out a well-structured written report (text,
  tables, high-res graphics side by side). People read ~3× faster than a speaker
  talks, then discuss at a higher level. See the deck/handout split in `SKILL.md`.

---

## 5. Kosslyn's 8 principles of perception

Stephen Kosslyn (*Clear and to the Point*) grounds design in how the brain
perceives. Grouped by the three goals of a presentation:

**Goal A — connect with the audience**

1. **Relevance** — deliver neither too much nor too little; anything that doesn't
   serve the point is ballast. Cut it.
2. **Appropriate knowledge** — match the audience's vocabulary and prior
   knowledge; unexplained acronyms or notation cause instant disengagement.

**Goal B — direct and hold attention**

3. **Salience** — the eye is drawn automatically to large differences (size,
   color, motion). Use salience deliberately to point at the key element.
4. **Discriminability** — two elements must differ *enough* to be seen as
   distinct; weak text/background contrast or near-identical chart lines block
   perception.
5. **Perceptual organization** — the brain groups by Gestalt laws (proximity,
   similarity, closure). Use color and spacing to structure implicitly: all
   titles one color; captions physically next to their figures.

**Goal C — promote understanding and memory**

6. **Compatibility** — form must match meaning. Time flows left-to-right in a
   linear graphic; showing a temporal sequence as a vertical pie chart fights the
   mental metaphor and confuses.
7. **Informative changes** — people assume every visual change carries meaning.
   Changing font/background/positions mid-deck for no reason sends the brain
   hunting for significance and wastes attention. Keep the deck visually
   consistent.
8. **Capacity limitations** — attention and processing are strictly limited;
   never present too much at once. Portion the content so it's grasped
   effortlessly.

**Concrete Kosslyn finding — never underline for emphasis.** The brain reads by
a word's outer *shape*, not letter by letter. An underline clips the descenders
of p, g, q, y, j, destroying that shape and measurably slowing reading. Use
**bold** for emphasis instead. (Kosslyn also showed these 8 principles are
violated just as often in academic talks as in business talks — expertise in the
subject does not imply competence in slide design.)

---

## 6. Picture-Superiority and dual coding

The **Picture-Superiority Effect (PSE):** images are remembered far better than
words. Paivio's **dual coding theory** explains it: a written word is encoded
once (verbal channel); a picture is encoded twice — as a visual representation
*and* as its mental name — leaving a much stronger memory trace. Decoding images
is also evolutionarily cheap; translating abstract text into meaning costs more
neural energy.

Evidence:

- **Butcher:** learners grasp complex physics with less mental effort and higher
  precision when text is paired with well-matched illustrations vs. text alone.
- **Medina:** recall of a purely spoken message after 72h ≈ **10%**; add a
  fitting concrete image and it jumps to ≈ **65%**.
- **Chris Hadfield's TED talk:** 35 slides, all high-res personal photos/video,
  zero bullet points — a benchmark for emotionally and cognitively efficient
  visual storytelling.

**Implication:** default to a concrete, relevant image or a clean chart. Prefer a
**bar chart** (the brain compares lengths precisely) over pie/donut charts (angle
and area comparisons are imprecise).

---

## 7. The bullet-point debate and the Rule of Seven

Neither extreme (ban all bullets vs. bullets-everywhere) is supported.

**The danger of bullet walls:** faced with a text wall, the audience switches to
scan mode, reads the slide silently ~3× faster than the speaker talks, and tunes
the speaker out — divided attention plus an overloaded phonological loop.

**The real strength of structured text** (from a controlled business-scenario
pilot):

- **Detail recall:** for specific data points, numbers, and facts, bullet text
  beat image-only slides decisively — correct recall on a key question rose
  **+149%** with bullets vs. **+67%** for the image-only version.
- **Speaker perception:** presenters backed by structured bullets were rated
  better prepared and more competent than those using only emotional images.
- **Accessibility:** for people with auditory-processing differences, non-native
  speakers, and some cognitive disabilities, concise bullets are an essential
  visual scaffold.

**The synthesis — disciplined bullets via the "Rule of Seven":**

- ≤ 3–5 bullets per slide.
- Each bullet ≤ 1 line — no wrapped sentences.
- Reveal them one at a time (builds) as the speaker reaches each.
- Pair the list with a visual (icon or diagram).

Use bullets when the payload is precise data, ordered steps, or a logical
sequence. Use images when the payload is a concept, relationship, or emotion.
Keep either disciplined so extraneous load stays minimal.
