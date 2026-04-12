import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Officers
export const officerService = {
  list: () => api.get('/officers/'),
  get: (id) => api.get(`/officers/${id}`),
  create: (data) => api.post('/officers/', data),
  update: (id, data) => api.put(`/officers/${id}`, data),
  delete: (id) => api.delete(`/officers/${id}`),
  listDutyTypes: () => api.get('/officers/duty-types'),
}

// Schedules
export const scheduleService = {
  list: () => api.get('/schedules/'),
  get: (year, month) => api.get(`/schedules/${year}/${month}`),
  create: (data) => api.post('/schedules/', data),
  update: (year, month, data) => api.put(`/schedules/${year}/${month}`, data),
  delete: (year, month) => api.delete(`/schedules/${year}/${month}`),
}

// Exchanges
export const exchangeService = {
  list: () => api.get('/exchanges/'),
  get: (id) => api.get(`/exchanges/${id}`),
  create: (data) => api.post('/exchanges/', data),
  updateStatus: (id, status, admin_note) =>
    api.put(`/exchanges/${id}`, { status, admin_note }),
  delete: (id) => api.delete(`/exchanges/${id}`),
}

// Absences
export const absenceService = {
  list: (year, month) => api.get('/absences/', { params: { year, month } }),
  get: (id) => api.get(`/absences/${id}`),
  create: (data) => api.post('/absences/', data),
  update: (id, data) => api.put(`/absences/${id}`, data),
  delete: (id) => api.delete(`/absences/${id}`),
}

export default api
