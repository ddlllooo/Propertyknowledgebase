import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 8000
})

const redirectToLogin = () => {
  sessionStorage.clear()
  if (window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

request.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const result = response.data
    if (result?.code && result.code !== 200) {
      ElMessage.error(result.message || '请求失败')
      if (result.code === 401 || result.code === 403) {
        redirectToLogin()
      }
      return Promise.reject(result)
    }
    return result
  },
  (error) => {
    const status = error?.response?.status
    const message = error?.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)
    if (status === 401 || status === 403) {
      redirectToLogin()
    }
    return Promise.reject(error)
  }
)

export default request
