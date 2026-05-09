import request from '../utils/request'

export const getPasswordResetList = (params) => request.get('/admin/password-reset/list', { params })

export const adminResetPassword = (id) => request.post(`/admin/password-reset/reset/${id}`)

export const ignorePasswordReset = (id) => request.put(`/admin/password-reset/ignore/${id}`)
