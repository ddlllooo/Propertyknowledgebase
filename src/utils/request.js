import axios from 'axios'
import { ElMessage } from 'element-plus'
import { clearCache, getCache, setCache } from './cache'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 8000,
  withCredentials: true
})

const redirectToLogin = () => {
  const remember = localStorage.getItem('rememberMe') === '1'
  sessionStorage.clear()
  if (!remember) {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('username')
  }
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

export function isTokenExpired(token) {
  if (!token) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

request.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token') || localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  if (config.method === 'get' && !config._noCache) {
    const cached = getCache(config)
    if (cached) {
      config.adapter = () => Promise.resolve({
        data: cached,
        status: 200,
        statusText: 'OK',
        headers: {},
        config,
      })
    }
  }

  return config
})

request.interceptors.response.use(
  (response) => {
    const { config } = response

    if (config.method === 'get' && !config._noCache && response.status === 200) {
      setCache(config, response.data)
    }

    if (config.method !== 'get') {
      const basePath = config.url?.split('?')[0]?.split('/').slice(0, 4).join('/')
      if (basePath) clearCache(basePath)
    }

    const result = response.data
    if (result?.code && result.code !== 200) {
      ElMessage.error(result.message || '请求失败')
      if (result.code === 423) {
        window.location.href = '/change-password'
        return Promise.reject(result)
      }
      if (result.code === 401 || result.code === 403) {
        redirectToLogin()
      }
      return Promise.reject(result)
    }
    return result
  },
  (error) => {
    if (error.config?.method !== 'get') {
      clearCache()
    }
    const status = error?.response?.status
    const message = error?.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)
    if (status === 423) {
      window.location.href = '/change-password'
      return Promise.reject(error)
    }
    if (status === 401 || status === 403) {
      redirectToLogin()
    }
    return Promise.reject(error)
  }
)

export default request
