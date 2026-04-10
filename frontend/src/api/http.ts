import axios from 'axios'
import { getAuthProfile, getAuthToken, setAuthProfile, setAuthToken } from '../utils/auth'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
const http = axios.create({
  baseURL,
  timeout: 12000
})

const attachAuthHeaders = (config: any) => {
  const token = getAuthToken()
  const profile = getAuthProfile()
  config.headers ||= {}
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    config.headers['X-Access-Token'] = token
  }
  if (profile?.username) {
    config.headers['X-Demo-Username'] = profile.username
  }
  if (profile?.id) {
    config.headers['X-Demo-User-Id'] = String(profile.id)
  }
  return config
}

http.interceptors.request.use((config) => {
  return attachAuthHeaders(config)
})

http.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const message = error.response?.data?.message || error.message || '请求失败'
    const config = error.config
    const profile = getAuthProfile()
    if (message === '请先登录' && profile?.username && config && !config.__authRetry && config.url !== '/api/auth/login') {
      config.__authRetry = true
      const response = await axios.post(`${baseURL}/api/auth/login`, {
        username: profile.username,
        password: '123456'
      })
      const data = response.data?.data
      if (data?.token) {
        setAuthToken(data.token)
        setAuthProfile(data.userInfo || profile)
        return http(attachAuthHeaders(config))
      }
    }
    return Promise.reject(new Error(message))
  }
)

export default http
