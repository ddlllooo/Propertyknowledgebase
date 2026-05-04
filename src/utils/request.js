import axios from 'axios'
import {
  categoryList,
  chatHistory,
  chatLogs,
  dashboardData,
  feedbackList,
  qaList,
  vectorStatus
} from '../mock/mockData'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 8000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error)
)

export const mockApi = {
  login({ username, password }) {
    if (username === 'user' && password === '123456') {
      return Promise.resolve({
        token: 'mock-user-token',
        role: 'user',
        username: 'user'
      })
    }
    if (username === 'admin' && password === '123456') {
      return Promise.resolve({
        token: 'mock-admin-token',
        role: 'admin',
        username: 'admin'
      })
    }
    return Promise.reject(new Error('账号或密码错误'))
  },
  getKnowledgeList() {
    return Promise.resolve(qaList)
  },
  getChatHistory() {
    return Promise.resolve(chatHistory)
  },
  getFeedbackList() {
    return Promise.resolve(feedbackList)
  },
  getCategoryList() {
    return Promise.resolve(categoryList)
  },
  getChatLogs() {
    return Promise.resolve(chatLogs)
  },
  getDashboardData() {
    return Promise.resolve(dashboardData)
  },
  getVectorStatus() {
    return Promise.resolve(vectorStatus)
  },
  createQa(payload) {
    return Promise.resolve({ ...payload, id: Date.now() })
  },
  updateQa(payload) {
    return Promise.resolve(payload)
  },
  deleteQa(id) {
    return Promise.resolve({ id })
  },
  rebuildVectorStore() {
    return Promise.resolve({ success: true, message: '向量库重建成功' })
  }
}

export default request
