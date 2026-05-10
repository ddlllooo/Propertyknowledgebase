import request from '../utils/request'

export const getAdminQaList = (params) => request.get('/admin/qa/list', { params })

export const getAdminQaStats = () => request.get('/admin/qa/stats')

export const createQa = (data) => request.post('/admin/qa/create', data)

export const batchCreateQa = (items) => request.post('/admin/qa/batch-create', { items })

export const updateQa = (id, data) => request.put(`/admin/qa/update/${id}`, data)

export const deleteQa = (id, hard = false) => request.delete(`/admin/qa/delete/${id}`, { params: { hard } })

export const batchDeleteQa = (ids, hard = false) => request.post('/admin/qa/batch-delete', { ids, hard })

export const batchUpdateQaStatus = (ids, status) => request.post('/admin/qa/batch-status', { ids, status })

