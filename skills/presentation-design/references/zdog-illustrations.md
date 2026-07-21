# Zdog Illustrations

Zdog is the tool for expressive, round, personality-forward vector-style illustrations when CeTZ feels too technical or flat.

## When to use Zdog vs CeTZ

- **Zdog**: Ants on a branch, characters, cars, everyday objects with charm and slight 3D volume. Great for metaphorical "soul" slides.
- **CeTZ / Fletcher + Typst**: Precise technical diagrams, flows, math, node graphs, anything that needs perfect alignment and typography integration.

Both produce crisp output. Zdog renders to canvas (captured perfectly on Slidev PNG/PDF export via Playwright).

## How to add to a deck

1. `pnpm add -D zdog`
2. Copy `presentation-design/assets/zdog/` into your deck:
   - `components/ZdogIllustration.vue`
   - `components/illustrations/your-scene.js`
3. Use:

```md
<ZdogIllustration illustration="your-scene" :width="620" :height="260" />
```

Place inside a `.diagram-frame` or evidence area for consistent sizing.

## Authoring a new scene

See `biological-inspiration.js`. The factory receives the `illo` and builds using:

- `new Zdog.Anchor({ addTo, translate, rotate, scale })`
- `new Zdog.Ellipse({ diameter, stroke, color, fill, translate })`
- `new Zdog.Shape({ path: [{x,y,z}, ...], stroke, color })`

Use 3D coordinates. A gentle rotate on the root anchor gives the classic Zdog "cute isometric" look.

Keep "show don't tell": the illustration stands alone. No labels about the technology.

## Performance / export

- Canvas is fine for export.
- Keep scenes reasonably small (hundreds of elements max).
- Disable `dragRotate` for static slides.

Example scenes live next to the component so dynamic import works.
