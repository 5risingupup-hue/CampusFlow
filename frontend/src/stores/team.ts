import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'
import type { TeamDetail } from '../types'

export const useTeamStore = defineStore('team', () => {
  const currentTeam = ref<TeamDetail | null>(null)

  const fetchTeam = async (id: number) => {
    const response = await api.getTeamDetail(id)
    currentTeam.value = response.data
  }

  return {
    currentTeam,
    fetchTeam
  }
})
