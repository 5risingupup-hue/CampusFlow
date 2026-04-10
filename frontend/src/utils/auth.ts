const stripTokenQuotes = (value: string) => {
  let token = value.trim()
  while (token.length >= 2 && token[0] === token[token.length - 1] && ['"', "'"].includes(token[0])) {
    token = token.slice(1, -1).trim()
  }
  return token
}

const tokenJsonKeys = ['token', 'accessToken', 'access_token', 'jwt', 'idToken', 'id_token']
const storageKey = 'campusflow_token'
const profileStorageKey = 'campusflow_profile'

export interface AuthProfile {
  id?: number
  username?: string
  nickname?: string
  role?: string
}

const readStorageToken = (storage: Storage) => normalizeAuthToken(storage.getItem(storageKey))

export const normalizeAuthToken = (value: string | null | undefined): string => {
  let token = stripTokenQuotes(value || '')
  for (let index = 0; index < 4; index += 1) {
    const match = token.match(/^(bearer|token)\s+(.+)$/i)
    if (!match) break
    token = stripTokenQuotes(match[2])
  }
  if (token.startsWith('{')) {
    try {
      const data = JSON.parse(token) as Record<string, unknown>
      const nested = tokenJsonKeys.map((key) => data[key]).find(Boolean)
      if (nested) {
        return normalizeAuthToken(String(nested))
      }
    } catch {
      // Keep the original token when old storage data is not valid JSON.
    }
  }
  return token
}

let activeAuthToken =
  readStorageToken(window.sessionStorage) || readStorageToken(window.localStorage)
let activeAuthProfile: AuthProfile | null = null

export const getAuthToken = () => {
  const token =
    readStorageToken(window.sessionStorage) || activeAuthToken || readStorageToken(window.localStorage)
  if (token && token !== activeAuthToken) {
    activeAuthToken = token
  }
  if (token && !readStorageToken(window.sessionStorage)) {
    window.sessionStorage.setItem(storageKey, token)
  }
  return token
}

export const setAuthToken = (value: string | null | undefined) => {
  activeAuthToken = normalizeAuthToken(value)
  if (activeAuthToken) {
    window.sessionStorage.setItem(storageKey, activeAuthToken)
    window.localStorage.setItem(storageKey, activeAuthToken)
  } else {
    window.sessionStorage.removeItem(storageKey)
    window.localStorage.removeItem(storageKey)
  }
  return activeAuthToken
}

export const clearAuthToken = () => {
  activeAuthToken = ''
  window.sessionStorage.removeItem(storageKey)
  window.localStorage.removeItem(storageKey)
}

export const getAuthProfile = () => {
  if (activeAuthProfile?.username) return activeAuthProfile
  const raw = window.sessionStorage.getItem(profileStorageKey) || window.localStorage.getItem(profileStorageKey)
  if (!raw) return null
  try {
    const data = JSON.parse(raw) as AuthProfile
    activeAuthProfile = data
    return data
  } catch {
    return null
  }
}

export const setAuthProfile = (profile: AuthProfile | null | undefined) => {
  activeAuthProfile = profile || null
  if (activeAuthProfile) {
    const raw = JSON.stringify(activeAuthProfile)
    window.sessionStorage.setItem(profileStorageKey, raw)
    window.localStorage.setItem(profileStorageKey, raw)
  } else {
    window.sessionStorage.removeItem(profileStorageKey)
    window.localStorage.removeItem(profileStorageKey)
  }
  return activeAuthProfile
}

export const clearAuthProfile = () => {
  activeAuthProfile = null
  window.sessionStorage.removeItem(profileStorageKey)
  window.localStorage.removeItem(profileStorageKey)
}
