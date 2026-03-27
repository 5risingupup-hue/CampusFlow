import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'
import type { UserProfile } from '../types'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('campusflow_token') || '')
  const profile = ref<UserProfile | null>(null)

  const isLoggedIn = computed(() => Boolean(token.value))
  const role = computed(() => profile.value?.role || '')

  const setSession = (nextToken: string, nextProfile: UserProfile) => {
    token.value = nextToken
    profile.value = nextProfile
    localStorage.setItem('campusflow_token', nextToken)
  }

  const login = async (payload: { username: string; password: string }) => {
    const response = await api.login(payload)
    setSession(response.data.token, response.data.userInfo)
  }

  const fetchProfile = async () => {
    if (!token.value) return
    const response = await api.getProfile()
    profile.value = response.data
  }

  const logout = () => {
    token.value = ''
    profile.value = null
    localStorage.removeItem('campusflow_token')
  }

  return {
    token,
    profile,
    role,
    isLoggedIn,
    setSession,
    login,
    fetchProfile,
    logout
  }
})
