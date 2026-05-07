<template>
  <div class="metric-card glass-card">
    <div class="metric-label">{{ label }}</div>
    <div class="metric-value">{{ value }}</div>
    <div class="metric-caption">{{ caption }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  caption: string
}>()
</script>

<style scoped>
.metric-card {
  padding: 24px;
  border-radius: 24px;
}

.metric-label {
  color: var(--cf-ink-soft);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.metric-value {
  margin-top: 18px;
  font-size: 42px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.06em;
}

.metric-caption {
  margin-top: 12px;
  color: var(--cf-ink-soft);
  font-size: 13px;
  line-height: 1.7;
}
</style>
