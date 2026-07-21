/**
 * Zdog scene: Ants on a branch — "Biological Inspiration"
 * Rich, personality-forward, pseudo-3D vector illustration.
 *
 * Usage:
 *   import create from './biological-inspiration.js'
 *   const illo = new Zdog.Illustration({ element: canvas })
 *   create(illo)
 */
import Zdog from 'zdog'

export default function createAntBranch(illo, opts = {}) {
  const TAU = Zdog.TAU
  const { width = 620, height = 260 } = opts

  // Main scene anchor, slight tilt for nice 3/4 view
  const scene = new Zdog.Anchor({
    addTo: illo,
    translate: { x: -10, y: 20 },
    rotate: { x: -0.3, y: 0.6 },
    scale: 1.1,
  })

  // === Branch (thick, organic, with volume and twigs) ===
  const branch = new Zdog.Anchor({ addTo: scene, translate: { z: -6 } })

  // Main log body — use a long cylinder-like stack of ellipses + a shape for taper
  const branchColor = '#8B5A2B'
  const branchDark = '#5C4033'
  const branchLight = '#A0522D'

  // Core thick branch using a closed Shape path for silhouette + volume
  new Zdog.Shape({
    addTo: branch,
    path: [
      { x: -180, y: -18 },
      { x: -120, y: -26, z: 4 },
      { x: 30, y: -14, z: 6 },
      { x: 170, y: 22, z: -2 },
      { x: 175, y: 28 },
      { x: 30, y: 18, z: -4 },
      { x: -120, y: 12, z: -6 },
      { x: -180, y: 6 },
    ],
    closed: true,
    stroke: 38,
    color: branchColor,
    fill: true,
  })

  // Lighter top highlight
  new Zdog.Shape({
    addTo: branch,
    path: [
      { x: -175, y: -14 },
      { x: -110, y: -20, z: 3 },
      { x: 25, y: -8, z: 5 },
      { x: 165, y: 16, z: -1 },
    ],
    closed: false,
    stroke: 14,
    color: branchLight,
  })

  // Darker bottom shadow
  new Zdog.Shape({
    addTo: branch,
    path: [
      { x: -175, y: 8 },
      { x: -110, y: 6, z: -3 },
      { x: 25, y: 12, z: -5 },
      { x: 165, y: 26, z: 1 },
    ],
    closed: false,
    stroke: 16,
    color: branchDark,
  })

  // Subtle bark rings / texture lines
  for (let i = -2; i <= 2; i++) {
    const x = i * 55
    new Zdog.Shape({
      addTo: branch,
      path: [
        { x: x - 18, y: -10 + i * 2, z: 2 },
        { x: x + 22, y: -4 + i * 3, z: 1 },
      ],
      closed: false,
      stroke: 3,
      color: branchDark,
    })
  }

  // Small side twigs
  const twig = (x, y, rotY) => {
    const t = new Zdog.Anchor({
      addTo: branch,
      translate: { x, y },
      rotate: { y: rotY },
    })
    new Zdog.Shape({
      addTo: t,
      path: [
        { x: 0, y: 0, z: 0 },
        { x: 28, y: -22, z: 8 },
      ],
      closed: false,
      stroke: 5,
      color: branchDark,
    })
    // tiny leaf on twig
    new Zdog.Ellipse({
      addTo: t,
      translate: { x: 26, y: -20, z: 9 },
      diameter: 18,
      stroke: 2,
      color: '#2E7D32',
      fill: true,
      rotate: { x: 0.8 },
    })
  }
  twig(-90, -8, 0.6)
  twig(40, 4, -0.8)
  twig(110, 10, 0.4)

  // === Ant factory (3D-ish, round, expressive) ===
  function makeAnt(x, y, z, scale = 1, rotY = 0, legPhase = 0) {
    const ant = new Zdog.Anchor({
      addTo: scene,
      translate: { x, y, z },
      rotate: { y: rotY },
      scale,
    })

    const red = '#C41E3A'
    const darkRed = '#8B1C2E'
    const legColor = '#5A0012'

    // Abdomen (rear, bigger, slightly flattened)
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 38,
      stroke: 10,
      color: red,
      fill: true,
      translate: { x: -8, z: 2 },
    })
    // Abdomen highlight
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 28,
      stroke: 4,
      color: '#E35A6F',
      translate: { x: -6, z: 6 },
    })

    // Waist
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 18,
      stroke: 8,
      color: darkRed,
      translate: { x: 8 },
    })

    // Thorax
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 24,
      stroke: 9,
      color: '#D32F2F',
      fill: true,
      translate: { x: 18, z: 1 },
    })

    // Head
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 20,
      stroke: 7,
      color: darkRed,
      fill: true,
      translate: { x: 30 },
    })

    // Eyes (yellow, 3D pop)
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 6,
      stroke: 1,
      color: '#FFEB3B',
      fill: true,
      translate: { x: 36, y: -5, z: 6 },
    })
    new Zdog.Ellipse({
      addTo: ant,
      diameter: 6,
      stroke: 1,
      color: '#FFEB3B',
      fill: true,
      translate: { x: 36, y: 5, z: 6 },
    })

    // Antennae (curved using Shape)
    const antL = new Zdog.Anchor({ addTo: ant, translate: { x: 38, y: -3 } })
    new Zdog.Shape({
      addTo: antL,
      path: [
        { x: 0, y: 0, z: 0 },
        { x: 12, y: -16, z: 4 },
        { x: 18, y: -20, z: 8 },
      ],
      closed: false,
      stroke: 3,
      color: legColor,
    })

    const antR = new Zdog.Anchor({ addTo: ant, translate: { x: 38, y: 3 } })
    new Zdog.Shape({
      addTo: antR,
      path: [
        { x: 0, y: 0, z: 0 },
        { x: 12, y: 16, z: 4 },
        { x: 18, y: 20, z: 8 },
      ],
      closed: false,
      stroke: 3,
      color: legColor,
    })

    // Legs — 6 legs, 3 per side, with knee bend using phase for life
    const leg = (sideY, baseX, kneeY, footY, phaseOffset) => {
      const phase = legPhase + phaseOffset
      const k = Math.sin(phase) * 4
      const anchor = new Zdog.Anchor({ addTo: ant, translate: { x: baseX, y: sideY * 0.6 } })

      // upper leg
      new Zdog.Shape({
        addTo: anchor,
        path: [
          { x: 0, y: 0, z: 0 },
          { x: -10, y: kneeY + k, z: -4 },
        ],
        closed: false,
        stroke: 3.5,
        color: legColor,
      })
      // lower leg
      new Zdog.Shape({
        addTo: anchor,
        translate: { x: -10, y: kneeY + k, z: -4 },
        path: [
          { x: 0, y: 0, z: 0 },
          { x: -12, y: footY - k * 0.6, z: 2 },
        ],
        closed: false,
        stroke: 3,
        color: legColor,
      })
    }

    // Left side legs
    leg(-1, 2, 12, 18, 0)
    leg(-1, 14, 10, 16, 0.8)
    leg(-1, 24, 8, 14, 1.6)

    // Right side legs
    leg(1, 2, -12, -18, 0.4)
    leg(1, 14, -10, -16, 1.2)
    leg(1, 24, -8, -14, 2.0)

    // Small mandibles
    new Zdog.Shape({
      addTo: ant,
      path: [
        { x: 40, y: -2, z: 0 },
        { x: 46, y: -5, z: 2 },
      ],
      closed: false,
      stroke: 2,
      color: darkRed,
    })
    new Zdog.Shape({
      addTo: ant,
      path: [
        { x: 40, y: 2, z: 0 },
        { x: 46, y: 5, z: 2 },
      ],
      closed: false,
      stroke: 2,
      color: darkRed,
    })
  }

  // === Place a trail of varied ants ===
  makeAnt(-110, -22, 8, 0.82, 0.05, 0.2)
  makeAnt(-55, -18, 5, 0.95, -0.02, 1.1)
  makeAnt(5, -9, 2, 1.0, 0.08, 0.0)
  makeAnt(65, 2, -1, 0.88, -0.04, 2.3)
  makeAnt(120, 14, -4, 1.05, 0.03, 0.7)

  // One carrying a leaf (slightly offset position)
  makeAnt(32, -4, 4, 0.96, 0.1, 1.4)

  // Carried leaf
  new Zdog.Ellipse({
    addTo: scene,
    translate: { x: 48, y: -16, z: 11 },
    diameter: 22,
    stroke: 3,
    color: '#2E7D32',
    fill: true,
    rotate: { x: 1.2, y: 0.4 },
  })

  // Small pink flower at the tip (for personality)
  const flower = new Zdog.Anchor({
    addTo: scene,
    translate: { x: -165, y: -32, z: 10 },
  })
  new Zdog.Ellipse({
    addTo: flower,
    diameter: 22,
    stroke: 2,
    color: '#F48FB1',
    fill: true,
  })
  new Zdog.Ellipse({
    addTo: flower,
    diameter: 10,
    stroke: 1,
    color: '#FFF59D',
    fill: true,
  })

  // Ground plane (simple but nice)
  new Zdog.Shape({
    addTo: scene,
    path: [
      { x: -220, y: 48, z: -20 },
      { x: 210, y: 58, z: -20 },
    ],
    closed: false,
    stroke: 18,
    color: '#3A4A1C',
  })

  // Grass tufts
  for (let i = 0; i < 11; i++) {
    const gx = -190 + i * 38
    const gy = 44 + (i % 3) * 2
    new Zdog.Shape({
      addTo: scene,
      path: [
        { x: gx, y: gy, z: -8 },
        { x: gx - 4, y: gy - 18, z: 0 },
      ],
      closed: false,
      stroke: 2.5,
      color: '#4A5D23',
    })
    new Zdog.Shape({
      addTo: scene,
      path: [
        { x: gx + 3, y: gy, z: -6 },
        { x: gx + 6, y: gy - 14, z: 2 },
      ],
      closed: false,
      stroke: 2,
      color: '#4A5D23',
    })
  }

  // Final render call is handled by the component loop
}
