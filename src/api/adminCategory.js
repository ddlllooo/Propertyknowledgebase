import request from '../utils/request'

export const getCategoryList = () => request.get('/admin/category/list')

export const createCategory = (data) => request.post('/admin/category/create', data)

export const updateCategory = (id, data) => request.put(`/admin/category/update/${id}`, data)

export const deleteCategory = (id) => request.delete(`/admin/category/delete/${id}`)

