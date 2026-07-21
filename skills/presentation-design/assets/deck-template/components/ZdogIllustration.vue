<script setup>
import { onMounted, ref, watch } from 'vue'
import Zdog from 'zdog'

const props = defineProps({
  illustration: { type: String, required: true },
  width: { type: Number, default: 620 },
  height: { type: Number, default: 260 },
  // Pass through any scene options
})

const canvasRef = ref(null)
let illo = null
let raf = null

async function loadIllustration(name) {
  // Dynamic import the scene factory
  const mod = await import(`./illustrations/${name}.js`)
  return mod.default || mod.create
}

async function mountIllustration() {
  if (!canvasRef.value) return

  const create = await loadIllustration(props.illustration)

  // Clean previous
  if (illo) {
    cancelAnimationFrame(raf)
    canvasRef.value.width = props.width
    canvasRef.value.height = props.height
  }

  illo = new Zdog.Illustration({
    element: canvasRef.value,
    dragRotate: false,
    resize: false,
    scale: 1,
  })

  create(illo, { width: props.width, height: props.height })

  function animate() {
    illo.updateRenderGraph()
    raf = requestAnimationFrame(animate)
  }
  animate()
}

onMounted(mountIllustration)
watch(() => props.illustration, mountIllustration)
</script>

<template>
  <canvas
    ref="canvasRef"
    :width="width"
    :height="height"
    class="zdog-canvas"
  />
</template>

<style scoped>
.zdog-canvas {
  width: 100%;
  height: auto;
  display: block;
  image-rendering: crisp-edges;
}
</style>
