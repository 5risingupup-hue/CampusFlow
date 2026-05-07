import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NotificationItem } from '../types'
import { api } from '../api'

export const useNoticeStore = defineStore('notice', () => {
  const unreadCount = ref(0)
  const latest = ref<NotificationItem | null>(null)
  const connected = ref(false)
  let client: { activate: () => void; deactivate: () => void; subscribe?: (destination: string, cb: (frame: { body: string }) => void) => void } | null = null

  const fetchUnreadCount = async () => {
    try {
      const response = await api.getUnreadCount()
      unreadCount.value = response.data.count
    } catch {
      unreadCount.value = 0
    }
  }

  const connect = async (userId?: number) => {
    if (!userId || client) return
    const [{ Client }, sockjsModule] = await Promise.all([
      import('@stomp/stompjs'),
      import('sockjs-client')
    ])
    const SockJS = sockjsModule.default
    client = new Client({
      webSocketFactory: () => new SockJS(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'}/ws`),
      reconnectDelay: 3000,
      onConnect: () => {
        connected.value = true
        if (client?.subscribe) {
          client.subscribe(`/topic/notifications/${userId}`, (frame) => {
            const payload: NotificationItem = JSON.parse(frame.body)
            latest.value = payload
            unreadCount.value += 1
          })
        }
      },
      onDisconnect: () => {
        connected.value = false
      }
    })
    client.activate()
  }

  const disconnect = () => {
    client?.deactivate()
    client = null
    connected.value = false
  }

  return {
    unreadCount,
    latest,
    connected,
    fetchUnreadCount,
    connect,
    disconnect
  }
})
