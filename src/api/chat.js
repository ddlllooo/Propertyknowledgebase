import request from '../utils/request'

export const sendQuestion = (data) => request.post('/chat', data, { timeout: 60000 })

export const sendGuestQuestion = (data) => request.post('/chat/guest', data, { timeout: 60000 })

export const getMyHistory = () => request.get('/chat/my-history')
