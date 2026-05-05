import request from '../utils/request'

export const getAdminQaList = (params) => request.get('/admin/qa/list', { params })

export const createQa = (data) => request.post('/admin/qa/create', data)

export const updateQa = (id, data) => request.put(`/admin/qa/update/${id}`, data)

export const deleteQa = (id) => request.delete(`/admin/qa/delete/${id}`)

