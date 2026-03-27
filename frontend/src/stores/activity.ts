import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { api } from '../api'
import type { ActivityCard, ActivityDetail, PageResult } from '../types'

export const useActivityStore = defineStore('activity', () => {
  const filters = reactive({
    keyword: '',
    type: '',
    requireTeam: undefined as boolean | undefined,
    pageNum: 1,
    pageSize: 8
  })
  const pageResult = ref<PageResult<ActivityCard>>({ total: 0, records: [] })
  const currentDetail = ref<ActivityDetail | null>(null)

  const fetchActivities = async () => {
    const response = await api.getActivities(filters)
    pageResult.value = response.data
  }

  const fetchDetail = async (id: number) => {
    const response = await api.getActivityDetail(id)
    currentDetail.value = response.data
  }

  return {
    filters,
    pageResult,
    currentDetail,
    fetchActivities,
    fetchDetail
  }
})
