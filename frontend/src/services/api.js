import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Employees ─────────────────────────────────────────────────────────────────

export const getEmployees = (params = {}) =>
  api.get('/employees/', { params }).then(r => r.data)

export const getEmployee = (id) =>
  api.get(`/employees/${id}/`).then(r => r.data)

export const createEmployee = (data) =>
  api.post('/employees/', data).then(r => r.data)

export const updateEmployee = (id, data) =>
  api.patch(`/employees/${id}/`, data).then(r => r.data)

export const deleteEmployee = (id) =>
  api.delete(`/employees/${id}/`).then(r => r.data)

// ── Insights ──────────────────────────────────────────────────────────────────

export const getCountryInsights = (params = {}) =>
  api.get('/insights/country/', { params }).then(r => r.data)

export const getJobTitleInsights = (params = {}) =>
  api.get('/insights/job-title/', { params }).then(r => r.data)

export const getDepartmentInsights = () =>
  api.get('/insights/department/').then(r => r.data)

export const getOverviewInsights = () =>
  api.get('/insights/overview/').then(r => r.data)
