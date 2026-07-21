<script setup>
import { computed } from 'vue'

const props = defineProps({
  stage: { type: Number, default: 0 }, // 0: leaving nest, faint trails; 1: some return; 2: reinforced
  width: { type: Number, default: 820 },
  height: { type: Number, default: 240 },
})

const ants = computed(() => {
  if (props.stage === 0) {
    return [
      { x: 160, y: 128, rot: 15 },
      { x: 195, y: 135, rot: 8 },
      { x: 235, y: 142, rot: -3 },
      { x: 270, y: 138, rot: 12 },
      { x: 310, y: 125, rot: 5 },
      { x: 175, y: 152, rot: -8 },
      { x: 220, y: 158, rot: 18 },
    ]
  }
  if (props.stage === 1) {
    return [
      { x: 160, y: 128, rot: 15 },
      { x: 220, y: 132, rot: 6 },
      { x: 290, y: 125, rot: 10 },
      { x: 360, y: 108, rot: 2 },
      { x: 420, y: 102, rot: -4 },
      { x: 195, y: 150, rot: -6 },
      { x: 280, y: 145, rot: 9 },
    ]
  }
  // stage 2
  return [
    { x: 180, y: 128, rot: 12 },
    { x: 260, y: 120, rot: 5 },
    { x: 340, y: 112, rot: 3 },
    { x: 420, y: 105, rot: -2 },
    { x: 500, y: 100, rot: 4 },
    { x: 220, y: 148, rot: -5 },
    { x: 310, y: 140, rot: 7 },
    { x: 390, y: 108, rot: 1 },
  ]
})
</script>

<template>
  <svg
    :width="width"
    :height="height"
    viewBox="0 0 820 240"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style="max-width: 100%; height: auto; display: block;"
  >
    <!-- Ground -->
    <rect x="0" y="170" width="820" height="70" fill="#2a3a18" opacity="0.55" />

    <!-- Nest -->
    <ellipse cx="80" cy="148" rx="36" ry="20" fill="#5C4033" />
    <ellipse cx="80" cy="142" rx="26" ry="12" fill="#8B5A2B" />
    <circle cx="80" cy="152" r="6" fill="#3D2914" />

    <!-- Paths -->
    <!-- Path A (will be reinforced) -->
    <path 
      d="M115 122 Q 200 98, 320 108 Q 480 90, 650 98" 
      :stroke="stage >= 2 ? '#3a5a1a' : '#5C4033'" 
      :stroke-width="stage >= 2 ? 8 : 3.5" 
      :stroke-dasharray="stage === 0 ? '5 4' : '0'" 
      stroke-linecap="round" 
      opacity="0.85" 
    />
    <!-- Path B -->
    <path 
      d="M115 138 Q 195 145, 310 140 Q 470 148, 680 145" 
      :stroke="stage >= 2 ? '#3a5a1a' : '#5C4033'" 
      :stroke-width="stage >= 2 ? 5 : 2.5" 
      :stroke-dasharray="stage === 0 ? '4 3' : '0'" 
      stroke-linecap="round" 
      opacity="0.65" 
    />
    <!-- Path C -->
    <path 
      d="M115 152 Q 205 170, 340 162 Q 500 175, 700 168" 
      :stroke="stage >= 2 ? '#3a5a1a' : '#5C4033'" 
      :stroke-width="stage >= 2 ? 3.5 : 2" 
      :stroke-dasharray="stage === 0 ? '3 3' : '0'" 
      stroke-linecap="round" 
      opacity="0.55" 
    />

    <!-- Intensified smell marks -->
    <template v-if="stage >= 1">
      <circle cx="190" cy="108" r="2.8" fill="#3a5a1a" />
      <circle cx="290" cy="100" r="2.8" fill="#3a5a1a" />
      <circle cx="400" cy="95" r="3" fill="#3a5a1a" />
      <circle cx="510" cy="93" r="3" fill="#3a5a1a" />
    </template>
    <template v-if="stage >= 2">
      <circle cx="160" cy="115" r="2" fill="#2e4a14" />
      <circle cx="350" cy="102" r="2.5" fill="#2e4a14" />
      <circle cx="450" cy="97" r="2.5" fill="#2e4a14" />
    </template>

    <!-- Ants -->
    <g v-for="(ant, index) in ants" :key="index">
      <g :transform="`translate(${ant.x} ${ant.y}) rotate(${ant.rot})`">
        <!-- Body -->
        <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#C41E3A" />
        <!-- Head -->
        <circle cx="6" cy="0" r="3.8" fill="#8B1C2E" />
        <!-- Eyes -->
        <circle cx="7.5" cy="-1.3" r="1.1" fill="#FFEB3B" />
        <circle cx="7.5" cy="1.3" r="1.1" fill="#FFEB3B" />
        <!-- Legs - thicker and more visible -->
        <line x1="-1" y1="-2.5" x2="-7" y2="-5.5" stroke="#3A0000" stroke-width="2.2" />
        <line x1="-1" y1="2.5" x2="-7" y2="5.5" stroke="#3A0000" stroke-width="2.2" />
        <line x1="2" y1="-2" x2="-3" y2="-5" stroke="#3A0000" stroke-width="2" />
        <line x1="2" y1="2" x2="-3" y2="5" stroke="#3A0000" stroke-width="2" />
        <line x1="4" y1="-1.5" x2="0" y2="-4" stroke="#3A0000" stroke-width="1.8" />
        <line x1="4" y1="1.5" x2="0" y2="4" stroke="#3A0000" stroke-width="1.8" />
        <!-- Antennae -->
        <line x1="8" y1="-1" x2="12" y2="-4" stroke="#4A0000" stroke-width="1.2" />
        <line x1="8" y1="1" x2="12" y2="4" stroke="#4A0000" stroke-width="1.2" />
      </g>
    </g>

    <!-- Food source -->
    <ellipse cx="720" cy="102" rx="11" ry="6" fill="#2E7D32" />
    <circle cx="720" cy="102" r="3.5" fill="#1B5E20" />

    <!-- Returning ants on reinforced path (stage 1+) -->
    <template v-if="stage >= 1">
      <g transform="translate(380 105) rotate(175)">
        <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#C41E3A" />
        <circle cx="-6" cy="0" r="3.8" fill="#8B1C2E" />
        <line x1="3" y1="-2" x2="8" y2="-5" stroke="#4A0000" stroke-width="1.8" />
        <line x1="3" y1="2" x2="8" y2="5" stroke="#4A0000" stroke-width="1.8" />
      </g>
    </template>
    <template v-if="stage >= 2">
      <g transform="translate(470 98) rotate(172)">
        <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#C41E3A" />
        <circle cx="-6" cy="0" r="3.8" fill="#8B1C2E" />
      </g>
    </template>
  </svg>
</template>
