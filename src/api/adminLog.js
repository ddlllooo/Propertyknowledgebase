import request from '../utils/request'

export const getChatLogs = (params) => request.get('/admin/chat-logs', { params })

export const getChatLogStats = () => request.get('/admin/chat-logs/stats')

export const deleteChatLog = (id) => request.delete(`/admin/chat-logs/${id}`)

export const batchDeleteChatLogs = (ids) => request.post('/admin/chat-logs/batch-delete', { ids })

