import client from './client'

export function listarTickets(params) {
  return client.get('/tickets/', { params })
}

export function obtenerTicket(id) {
  return client.get(`/tickets/${id}/`)
}

export function crearTicket(datos) {
  return client.post('/tickets/', datos)
}

export function actualizarTicket(id, datos) {
  return client.patch(`/tickets/${id}/`, datos)
}

export function listarCategorias(params = {}) {
  return client.get('/categorias/', { params })
}

export function crearCategoria(datos) {
  return client.post('/categorias/', datos)
}

export function crearComentario(ticketId, texto) {
  return client.post('/comentarios/', { ticket: ticketId, texto })
}