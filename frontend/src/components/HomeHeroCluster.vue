<template>
  <div class="hero-cluster" :class="side" aria-hidden="true">
    <span
      v-for="pixel in pixels"
      :key="pixel.name"
      class="pixel"
      :class="pixel.name"
      :style="{ width: `${pixel.size}px`, height: `${pixel.size}px` }"
    />

    <span
      v-for="badge in badges"
      :key="badge.name"
      class="badge"
      :class="badge.name"
      :style="{ background: badge.bg }"
    >
      {{ badge.emoji }}
    </span>

    <div
      v-for="figure in figures"
      :key="figure.name"
      class="scene-card"
      :class="figure.sceneClass"
    >
      <div class="scene-block" />
      <div class="scene-shadow" />
      <img class="figure-media" :class="figure.imageClass" :src="figure.src" alt="" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import heroFigureFeedback from '../assets/hero/hero-figure-feedback.png'
import heroFigureOrganizer from '../assets/hero/hero-figure-organizer.png'
import heroFigureReview from '../assets/hero/hero-figure-review.png'
import heroFigureTeam from '../assets/hero/hero-figure-team.png'

const props = defineProps<{
  side: 'left' | 'right'
}>()

const badges = computed(() =>
  props.side === 'left'
    ? [
        { name: 'badge-a', emoji: '📣', bg: '#d8f22c' },
        { name: 'badge-b', emoji: '👥', bg: '#1f63ea' },
        { name: 'badge-c', emoji: '🤝', bg: '#ff4d4d' },
        { name: 'badge-d', emoji: '🧭', bg: '#1f5a47' },
        { name: 'badge-e', emoji: '🎓', bg: '#78d600' },
        { name: 'badge-f', emoji: '✨', bg: '#ffeb4f' }
      ]
    : [
        { name: 'badge-a', emoji: '✅', bg: '#7a22e2' },
        { name: 'badge-b', emoji: '🔔', bg: '#ff4f6b' },
        { name: 'badge-c', emoji: '📊', bg: '#1fb8c8' },
        { name: 'badge-d', emoji: '🎫', bg: '#0a0f1a' },
        { name: 'badge-e', emoji: '💬', bg: '#d92137' },
        { name: 'badge-f', emoji: '📅', bg: '#1f63ea' }
      ]
)

const pixels = computed(() =>
  props.side === 'left'
    ? [
        { name: 'pixel-a', size: 14 },
        { name: 'pixel-b', size: 8 },
        { name: 'pixel-c', size: 10 },
        { name: 'pixel-d', size: 16 },
        { name: 'pixel-e', size: 8 },
        { name: 'pixel-f', size: 12 },
        { name: 'pixel-g', size: 9 },
        { name: 'pixel-h', size: 12 }
      ]
    : [
        { name: 'pixel-a', size: 16 },
        { name: 'pixel-b', size: 8 },
        { name: 'pixel-c', size: 10 },
        { name: 'pixel-d', size: 14 },
        { name: 'pixel-e', size: 8 },
        { name: 'pixel-f', size: 12 },
        { name: 'pixel-g', size: 10 },
        { name: 'pixel-h', size: 14 }
      ]
)

const figures = computed(() =>
  props.side === 'left'
    ? [
        {
          name: 'organizer',
          src: heroFigureOrganizer,
          sceneClass: 'scene-top',
          imageClass: 'image-organizer'
        },
        {
          name: 'team',
          src: heroFigureTeam,
          sceneClass: 'scene-bottom',
          imageClass: 'image-team'
        }
      ]
    : [
        {
          name: 'feedback',
          src: heroFigureFeedback,
          sceneClass: 'scene-top',
          imageClass: 'image-feedback'
        },
        {
          name: 'review',
          src: heroFigureReview,
          sceneClass: 'scene-bottom',
          imageClass: 'image-review'
        }
      ]
)
</script>

<style scoped>
.hero-cluster {
  position: relative;
  width: min(100%, 420px);
  min-height: 520px;
}

.scene-card,
.badge,
.pixel {
  position: absolute;
}

.scene-card {
  overflow: visible;
}

.scene-top {
  top: 44px;
  width: 168px;
  height: 212px;
}

.scene-bottom {
  width: 188px;
  height: 240px;
}

.hero-cluster.left .scene-top {
  left: 44px;
}

.hero-cluster.left .scene-bottom {
  left: 170px;
  top: 218px;
}

.hero-cluster.right .scene-top {
  right: 60px;
  top: 28px;
}

.hero-cluster.right .scene-bottom {
  right: 190px;
  top: 262px;
}

.scene-block {
  display: none;
}

.scene-shadow {
  position: absolute;
  inset: auto 14px 10px;
  height: 18px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cf-ink) 16%, transparent);
  filter: blur(10px);
}

.figure-media {
  position: absolute;
  left: 50%;
  bottom: 10px;
  height: auto;
  transform: translateX(-50%);
  filter: drop-shadow(0 10px 18px rgba(26, 33, 49, 0.18));
  user-select: none;
  pointer-events: none;
}

.image-organizer {
  width: auto;
  height: 255px;
}

.image-team {
  width: auto;
  height: 291px;
  bottom: 6px;
}

.image-feedback {
  width: auto;
  height: 255px;
}

.image-review {
  width: auto;
  height: 297px;
  bottom: 4px;
}

.badge {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  font-size: 26px;
  line-height: 1;
  box-shadow: 0 12px 24px rgba(27, 24, 29, 0.14);
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
}

.pixel {
  border-radius: 4px;
  background: #d6ab81;
  opacity: 0.9;
}

.hero-cluster.left .badge-a {
  left: 8px;
  top: 58px;
}

.hero-cluster.left .badge-b {
  left: 314px;
  top: 78px;
}

.hero-cluster.left .badge-c {
  left: 166px;
  top: 118px;
}

.hero-cluster.left .badge-d {
  left: 286px;
  top: 172px;
}

.hero-cluster.left .badge-e {
  left: 206px;
  top: 266px;
}

.hero-cluster.left .badge-f {
  left: 328px;
  top: 414px;
}

.hero-cluster.right .badge-a {
  left: 36px;
  top: 42px;
}

.hero-cluster.right .badge-b {
  left: 164px;
  top: 90px;
}

.hero-cluster.right .badge-c {
  right: 8px;
  top: 10px;
}

.hero-cluster.right .badge-d {
  right: 0;
  top: 278px;
}

.hero-cluster.right .badge-e {
  right: 84px;
  top: 402px;
}

.hero-cluster.right .badge-f {
  left: -8px;
  top: 208px;
}

.hero-cluster.left .pixel-a {
  left: 56px;
  top: 42px;
}

.hero-cluster.left .pixel-b {
  left: 96px;
  top: 20px;
}

.hero-cluster.left .pixel-c {
  left: 228px;
  top: 64px;
}

.hero-cluster.left .pixel-d {
  left: 286px;
  top: 44px;
}

.hero-cluster.left .pixel-e {
  left: 340px;
  top: 158px;
}

.hero-cluster.left .pixel-f {
  left: 116px;
  top: 470px;
}

.hero-cluster.left .pixel-g {
  left: 262px;
  top: 492px;
}

.hero-cluster.left .pixel-h {
  left: 304px;
  top: 446px;
}

.hero-cluster.right .pixel-a {
  right: 108px;
  top: 8px;
}

.hero-cluster.right .pixel-b {
  left: 4px;
  top: 22px;
}

.hero-cluster.right .pixel-c {
  left: 8px;
  top: 96px;
}

.hero-cluster.right .pixel-d {
  right: 150px;
  top: 182px;
}

.hero-cluster.right .pixel-e {
  right: 20px;
  top: 188px;
}

.hero-cluster.right .pixel-f {
  right: 8px;
  top: 354px;
}

.hero-cluster.right .pixel-g {
  left: 42px;
  top: 440px;
}

.hero-cluster.right .pixel-h {
  left: 224px;
  top: 472px;
}

@media (max-width: 1180px) {
  .hero-cluster {
    min-height: 430px;
    transform: scale(0.84);
    transform-origin: center top;
  }
}

@media (max-width: 760px) {
  .hero-cluster {
    min-height: 310px;
    width: min(100%, 320px);
    transform: scale(0.64);
  }
}
</style>
