import client from './client'

export function obtenerResumenDashboard(params = {}) {
  return client.get('/dashboard/resumen/', { params })
}