import request from '../utils/request'

export const getFeedbackList = (params) => request.get('/admin/feedback/list', { params })

export const updateFeedbackStatus = (id, data) => request.put(`/admin/feedback/status/${id}`, data)

export const feedbackToKnowledge = (id, data) => request.post(`/admin/feedback/to-knowledge/${id}`, data)

export const deleteFeedback = (id) => request.delete(`/admin/feedback/delete/${id}`)

export const batchUpdateFeedbackStatus = (ids, status) => request.post('/admin/feedback/batch-status', { ids, status })

