import request from '../utils/request'

export const register = (data) => request.post('/auth/register', data)

export const login = (data) => request.post('/auth/login', data)

export const profile = () => request.get('/auth/profile')

export const requestPasswordReset = (data) => request.post('/auth/password-reset/request', data)

export const getPasswordResetStatus = (params) => request.get('/auth/password-reset/status', { params })

export const changePassword = (data) => request.post('/auth/change-password', data)

