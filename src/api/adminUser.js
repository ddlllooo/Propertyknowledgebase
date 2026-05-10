import request from '../utils/request'

export const getUserList = (params) => request.get('/admin/user/list', { params })

export const createUser = (data) => request.post('/admin/user/create', data)

export const updateUser = (id, data) => request.put(`/admin/user/update/${id}`, data)

export const deleteUser = (id) => request.delete(`/admin/user/delete/${id}`)

export const batchUpdateUserStatus = (ids, status) => request.put('/admin/user/batch-status', { ids, status })
