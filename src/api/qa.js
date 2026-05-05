import request from '../utils/request'

export const getQaList = (params) => request.get('/qa/list', { params })

export const getQaDetail = (id) => request.get(`/qa/detail/${id}`)

export const getCategories = () => request.get('/qa/categories')

export const getHomeSummary = () => request.get('/qa/home-summary')
