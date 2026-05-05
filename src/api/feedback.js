import request from '../utils/request'

export const createFeedback = (data) => request.post('/feedback/create', data)

export const getMyFeedback = () => request.get('/feedback/my')

