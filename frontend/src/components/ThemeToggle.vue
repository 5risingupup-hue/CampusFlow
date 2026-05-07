<template>
  <div class="theme-toggle" role="group" aria-label="主题模式切换">
    <button
      type="button"
      class="theme-toggle-btn"
      :class="{ active: themeStore.theme === 'light' }"
      @click="themeStore.setTheme('light')"
    >
      日间
    </button>
    <button
      type="button"
      class="theme-toggle-btn"
      :class="{ active: themeStore.theme === 'dark' }"
      @click="themeStore.setTheme('dark')"
    >
      夜间
    </button>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  padding: 4px;
  border: 1px solid var(--cf-line);
  border-radius: 999px;
  background: var(--cf-surface-strong);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.theme-toggle-btn {
  min-width: 68px;
  padding: 8px 12px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--cf-ink-soft);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.theme-toggle-btn.active {
  background: var(--cf-paper-strong);
  color: var(--cf-ink);
  box-shadow: var(--cf-shadow-sm);
}
</style>
