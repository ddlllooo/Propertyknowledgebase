import request from '../utils/request'

export const getVectorStatus = () => request.get('/admin/vector/status')

export const rebuildVector = () => request.post('/admin/vector/rebuild', null, { timeout: 0 })
