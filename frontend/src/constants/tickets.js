// ATENCIÓN: estos valores deben coincidir exactamente con los TextChoices
// definidos en backend/tickets/models.py (Ticket.Estado, Ticket.Tipo,
// Ticket.Prioridad). Es una duplicación consciente (ver explicación en el
// mensaje que acompaña a esta fase) — si cambias un choice en el backend,
// actualiza también este fichero.

export const ESTADOS = [
  { value: 'abierto', label: 'Abierto', color: 'bg-blue-100 text-blue-800' },
  { value: 'en_progreso', label: 'En progreso', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'resuelto', label: 'Resuelto', color: 'bg-green-100 text-green-800' },
  { value: 'abandonado', label: 'Abandonado', color: 'bg-gray-200 text-gray-700' },
  { value: 'cerrado', label: 'Cerrado', color: 'bg-slate-200 text-slate-700' },
]

export const TIPOS = [
  { value: 'incidencia', label: 'Incidencia' },
  { value: 'tarea', label: 'Tarea' },
]

export const PRIORIDADES = [
  { value: 'baja', label: 'Baja', color: 'bg-gray-100 text-gray-700' },
  { value: 'media', label: 'Media', color: 'bg-blue-100 text-blue-700' },
  { value: 'alta', label: 'Alta', color: 'bg-orange-100 text-orange-700' },
  { value: 'critica', label: 'Crítica', color: 'bg-red-100 text-red-700' },
]