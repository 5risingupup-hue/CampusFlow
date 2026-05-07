import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'campusflow-theme'

const applyTheme = (theme: ThemeMode) => {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.theme = theme
  document.documentElement.style.colorScheme = theme
}

const getPreferredTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'light'
  const saved = window.localStorage.getItem(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') {
    return saved
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<ThemeMode>('light')

  const initTheme = () => {
    theme.value = getPreferredTheme()
    applyTheme(theme.value)
  }

  const setTheme = (mode: ThemeMode) => {
    theme.value = mode
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, mode)
    }
    applyTheme(mode)
  }

  const isDark = computed(() => theme.value === 'dark')

  return {
    theme,
    isDark,
    initTheme,
    setTheme
  }
})
