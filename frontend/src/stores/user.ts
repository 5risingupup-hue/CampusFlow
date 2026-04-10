import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'
import type { UserProfile } from '../types'
import { clearAuthProfile, clearAuthToken, getAuthProfile, getAuthToken, setAuthProfile, setAuthToken } from '../utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(setAuthToken(getAuthToken()))
  const profile = ref<UserProfile | null>(getAuthProfile() as UserProfile | null)

  const isLoggedIn = computed(() => Boolean(token.value))
  const role = computed(() => profile.value?.role || '')

  const setSession = (nextToken: string, nextProfile: UserProfile) => {
    token.value = setAuthToken(nextToken)
    profile.value = nextProfile
    setAuthProfile(nextProfile)
  }

  const login = async (payload: { username: string; password: string }) => {
    const response = await api.login(payload)
    setSession(response.data.token, response.data.userInfo)
  }

  const fetchProfile = async () => {
    if (!token.value) return
    const response = await api.getProfile()
    profile.value = response.data
    setAuthProfile(response.data)
  }

  const logout = () => {
    token.value = ''
    profile.value = null
    clearAuthToken()
    clearAuthProfile()
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
