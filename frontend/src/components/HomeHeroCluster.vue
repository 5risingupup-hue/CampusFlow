<template>
  <div class="hero-cluster" :class="side">
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

    <div class="scene-card scene-top">
      <div class="scene-block" />
      <div class="scene-shadow" />
      <div class="character character-top">
        <div class="character-hair" />
        <div class="character-head" />
        <div class="character-face">
          <span class="eye" />
          <span class="eye" />
        </div>
        <div class="character-body" />
        <div class="character-arm arm-left" />
        <div class="character-arm arm-right" />
        <div class="character-leg leg-left" />
        <div class="character-leg leg-right" />
        <div class="character-prop" />
      </div>
    </div>

    <div class="scene-card scene-bottom">
      <div class="scene-block" />
      <div class="scene-shadow" />
      <div class="character character-bottom">
        <div class="character-hair" />
        <div class="character-head" />
        <div class="character-face">
          <span class="eye" />
          <span class="eye" />
        </div>
        <div class="character-body" />
        <div class="character-arm arm-left" />
        <div class="character-arm arm-right" />
        <div class="character-leg leg-left" />
        <div class="character-leg leg-right" />
        <div class="character-prop" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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
</script>

<style scoped>
.hero-cluster {
  position: relative;
  width: min(100%, 420px);
  min-height: 520px;
}

.scene-card {
  position: absolute;
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
  position: absolute;
  inset: 0;
  border-radius: 24px;
  background: linear-gradient(180deg, #e7c4a2, #e0b88f);
}

:root[data-theme='dark'] .scene-block {
  background: linear-gradient(180deg, #d0a67f, #b78b63);
}

.scene-shadow {
  position: absolute;
  inset: auto 14px 10px;
  height: 18px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--cf-ink) 16%, transparent);
  filter: blur(10px);
}

.character {
  position: absolute;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
}

.character-head {
  position: absolute;
  left: 50%;
  top: 26px;
  width: 52px;
  height: 52px;
  margin-left: -26px;
  border-radius: 50%;
  background: #f2ccaa;
  z-index: 3;
}

.character-face {
  position: absolute;
  left: 50%;
  top: 48px;
  display: flex;
  gap: 10px;
  margin-left: -15px;
  z-index: 4;
}

.eye {
  width: 5px;
  height: 7px;
  border-radius: 999px;
  background: #1f2d3d;
}

.character-hair {
  position: absolute;
  left: 50%;
  top: 12px;
  width: 72px;
  height: 58px;
  margin-left: -36px;
  border-radius: 40px 40px 28px 28px;
  z-index: 2;
}

.character-body {
  position: absolute;
  left: 50%;
  top: 72px;
  width: 84px;
  height: 86px;
  margin-left: -42px;
  border-radius: 28px 28px 20px 20px;
  z-index: 1;
}

.character-arm,
.character-leg {
  position: absolute;
  border-radius: 999px;
  z-index: 0;
}

.character-arm {
  top: 84px;
  width: 18px;
  height: 70px;
  background: #f0c7a7;
}

.arm-left {
  left: 8px;
  transform: rotate(14deg);
}

.arm-right {
  right: 8px;
  transform: rotate(-18deg);
}

.character-leg {
  top: 148px;
  width: 24px;
  height: 64px;
  background: #2b3143;
}

.leg-left {
  left: 40px;
}

.leg-right {
  right: 40px;
}

.character-prop {
  position: absolute;
  z-index: 4;
}

.hero-cluster.left .character-top {
  width: 122px;
  height: 208px;
}

.hero-cluster.left .character-top .character-hair {
  background: #d96929;
  box-shadow: inset 0 -8px 0 rgba(120, 44, 10, 0.2);
}

.hero-cluster.left .character-top .character-body {
  background: #8a7463;
}

.hero-cluster.left .character-top .character-prop {
  left: 24px;
  top: 112px;
  width: 74px;
  height: 48px;
  border-radius: 14px;
  background: #f0e7d8;
  border: 3px solid #3d372f;
  box-shadow: inset 0 0 0 6px #f8f1e4;
}

.hero-cluster.left .character-top .character-prop::before,
.hero-cluster.left .character-top .character-prop::after {
  content: "";
  position: absolute;
  top: 16px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 3px solid #3d372f;
}

.hero-cluster.left .character-top .character-prop::before {
  left: 14px;
}

.hero-cluster.left .character-top .character-prop::after {
  right: 14px;
}

.hero-cluster.left .character-bottom {
  width: 128px;
  height: 224px;
}

.hero-cluster.left .character-bottom .character-hair {
  background: #463f39;
  width: 82px;
  height: 72px;
  margin-left: -41px;
}

.hero-cluster.left .character-bottom .character-body {
  background: #2f2d2f;
  top: 76px;
  height: 92px;
}

.hero-cluster.left .character-bottom .character-prop {
  left: 40px;
  top: 126px;
  width: 48px;
  height: 58px;
  border-radius: 10px;
  background: #2a66d1;
  box-shadow: inset 0 -8px 0 rgba(10, 43, 102, 0.2);
}

.hero-cluster.right .character-top {
  width: 124px;
  height: 206px;
}

.hero-cluster.right .character-top .character-hair {
  background: #24272e;
  width: 80px;
  height: 62px;
  margin-left: -40px;
}

.hero-cluster.right .character-top .character-body {
  background: #21242c;
  border: 6px solid #d24444;
  top: 76px;
  height: 96px;
}

.hero-cluster.right .character-top .character-prop {
  right: 8px;
  top: 102px;
  width: 26px;
  height: 48px;
  border-radius: 12px;
  background: #2f3744;
}

.hero-cluster.right .character-bottom {
  width: 138px;
  height: 226px;
}

.hero-cluster.right .character-bottom .character-hair {
  background: #cc7a3b;
  box-shadow: inset 0 -8px 0 rgba(99, 50, 18, 0.16);
}

.hero-cluster.right .character-bottom .character-body {
  background: #224fa0;
  width: 96px;
  margin-left: -48px;
  height: 92px;
}

.hero-cluster.right .character-bottom .character-prop {
  right: 10px;
  top: 114px;
  width: 26px;
  height: 34px;
  border-radius: 8px;
  background: #f8f6f0;
  box-shadow: inset 0 -8px 0 rgba(216, 178, 121, 0.28);
}

.badge,
.pixel {
  position: absolute;
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
