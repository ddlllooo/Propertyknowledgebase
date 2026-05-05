import request from '../utils/request'

export const getChatLogs = (params) => request.get('/admin/chat-logs', { params })

