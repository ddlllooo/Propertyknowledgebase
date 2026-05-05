import request from '../utils/request'

export const getOverview = () => request.get('/admin/dashboard/overview')

export const getDailyTrend = () => request.get('/admin/dashboard/daily-trend')

export const getHotQuestions = () => request.get('/admin/dashboard/hot-questions')

export const getHitRateTrend = () => request.get('/admin/dashboard/hit-rate-trend')

export const getCategoryRatio = () => request.get('/admin/dashboard/category-ratio')

export const getFeedbackStatus = () => request.get('/admin/dashboard/feedback-status')

export const getUnmatched = () => request.get('/admin/dashboard/unmatched')
