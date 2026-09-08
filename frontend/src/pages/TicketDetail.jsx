import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { obtenerTicket, actualizarTicket, crearComentario } from '../api/tickets'
import { ESTADOS, PRIORIDADES } from '../constants/tickets'

export default function TicketDetail() {
  const { id } = useParams()
  const [ticket, setTicket] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [comentario, setComentario] = useState('')
  const [enviandoComentario, setEnviandoComentario] = useState(false)

  const cargar = useCallback(async () => {
    const { data } = await obtenerTicket(id)
    setTicket(data)
    setCargando(false)
  }, [id])

  useEffect(() => {
    cargar()
  }, [cargar])

  async function cambiarCampo(campo, valor) {
    await actualizarTicket(id, { [campo]: valor })
    cargar()
  }

  async function marcarAbandonado() {
    if (!window.confirm('¿Marcar este ticket como abandonado?')) return
    await cambiarCampo('estado', 'abandonado')
  }

  async function handleComentario(e) {
    e.preventDefault()
    if (!comentario.trim()) return
    setEnviandoComentario(true)
    try {
      await crearComentario(id, comentario.trim())
      setComentario('')
      await cargar()
    } finally {
      setEnviandoComentario(false)
    }
  }

  if (cargando) return <p className="p-8 text-gray-500">Cargando...</p>
  if (!ticket) return <p className="p-8 text-gray-500">Ticket no encontrado.</p>

  const yaCerrado = ['abandonado', 'cerrado'].includes(ticket.estado)

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-gray-800">{ticket.titulo}</h1>
          <p className="text-sm text-gray-500">
            {ticket.categoria?.nombre} · creado por {ticket.creado_por?.username} el{' '}
            {new Date(ticket.fecha_creacion).toLocaleString('es-ES')}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to={`/tickets/${id}/editar`} className="text-sm border px-3 py-1.5 rounded hover:bg-gray-50">
            Editar
          </Link>
          {!yaCerrado && (
            <button
              onClick={marcarAbandonado}
              className="text-sm border border-red-300 text-red-600 px-3 py-1.5 rounded hover:bg-red-50"
            >
              Marcar abandonado
            </button>
          )}
        </div>
      </div>

      <p className="text-gray-700 mb-6 whitespace-pre-wrap">{ticket.descripcion}</p>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div>
          <label className="block text-xs text-gray-500 mb-1" htmlFor="estado">Estado</label>
          <select
            id="estado"
            className="w-full border rounded px-3 py-2 text-sm"
            value={ticket.estado}
            onChange={(e) => cambiarCampo('estado', e.target.value)}
          >
            {ESTADOS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1" htmlFor="prioridad">Prioridad</label>
          <select
            id="prioridad"
            className="w-full border rounded px-3 py-2 text-sm"
            value={ticket.prioridad}
            onChange={(e) => cambiarCampo('prioridad', e.target.value)}
          >
            {PRIORIDADES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      </div>

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Comentarios</h2>
        <div className="space-y-3 mb-4">
          {ticket.comentarios.length === 0 && (
            <p className="text-sm text-gray-400">Sin comentarios todavía.</p>
          )}
          {ticket.comentarios.map((c) => (
            <div key={c.id} className="bg-gray-50 rounded p-3 text-sm">
              <p className="text-gray-800">{c.texto}</p>
              <p className="text-xs text-gray-400 mt-1">
                {c.usuario?.username} · {new Date(c.fecha).toLocaleString('es-ES')}
              </p>
            </div>
          ))}
        </div>
        <form onSubmit={handleComentario} className="flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-2 text-sm"
            placeholder="Añadir un comentario..."
            value={comentario}
            onChange={(e) => setComentario(e.target.value)}
          />
          <button
            type="submit"
            disabled={enviandoComentario}
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50"
          >
            Comentar
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Historial</h2>
        {ticket.historial.length === 0 ? (
          <p className="text-sm text-gray-400">Sin cambios registrados todavía.</p>
        ) : (
          <ul className="space-y-2 border-l-2 border-gray-200 pl-4">
            {ticket.historial.map((h) => (
              <li key={h.id} className="text-sm">
                <span className="text-gray-800">
                  <strong>{h.campo_modificado}</strong>: {h.valor_anterior || '—'} → {h.valor_nuevo || '—'}
                </span>
                <p className="text-xs text-gray-400">
                  {h.usuario ? h.usuario.username : 'Automático'} · {new Date(h.fecha).toLocaleString('es-ES')}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}