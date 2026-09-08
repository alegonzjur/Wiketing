import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { crearTicket, actualizarTicket, obtenerTicket } from '../api/tickets'
import CategoriaSelect from '../components/CategoriaSelect'
import { TIPOS, PRIORIDADES } from '../constants/tickets'

export default function TicketForm() {
  const { id } = useParams()
  const editando = Boolean(id)
  const navigate = useNavigate()

  const [form, setForm] = useState({
    titulo: '', descripcion: '', tipo: 'incidencia', prioridad: 'media', categoria: null,
  })
  const [cargando, setCargando] = useState(editando)
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!editando) return
    obtenerTicket(id).then(({ data }) => {
      setForm({
        titulo: data.titulo,
        descripcion: data.descripcion,
        tipo: data.tipo,
        prioridad: data.prioridad,
        categoria: data.categoria?.id ?? null,
      })
      setCargando(false)
    })
  }, [id, editando])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!form.categoria) {
      setError('Selecciona una categoría')
      return
    }
    setGuardando(true)
    try {
      if (editando) {
        await actualizarTicket(id, form)
        navigate(`/tickets/${id}`)
      } else {
        const { data } = await crearTicket(form)
        navigate(`/tickets/${data.id}`)
      }
    } catch {
      setError('No se pudo guardar. Revisa los datos.')
    } finally {
      setGuardando(false)
    }
  }

  if (cargando) return <p className="p-8 text-gray-500">Cargando...</p>

  return (
    <div className="p-8 max-w-xl">
      <h1 className="text-2xl font-semibold text-gray-800 mb-6">
        {editando ? 'Editar ticket' : 'Nuevo ticket'}
      </h1>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div>
          <label className="block text-sm text-gray-600 mb-1" htmlFor="titulo">Título</label>
          <input
            id="titulo"
            className="w-full border rounded px-3 py-2"
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
            required
          />
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1" htmlFor="descripcion">Descripción</label>
          <textarea
            id="descripcion"
            className="w-full border rounded px-3 py-2"
            rows={4}
            value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1" htmlFor="tipo">Tipo</label>
            <select
              id="tipo"
              className="w-full border rounded px-3 py-2"
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value })}
            >
              {TIPOS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1" htmlFor="prioridad">Prioridad</label>
            <select
              id="prioridad"
              className="w-full border rounded px-3 py-2"
              value={form.prioridad}
              onChange={(e) => setForm({ ...form, prioridad: e.target.value })}
            >
              {PRIORIDADES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm text-gray-600 mb-1">Categoría</label>
          <CategoriaSelect
            value={form.categoria}
            onChange={(nuevoId) => setForm({ ...form, categoria: nuevoId })}
          />
        </div>

        <button
          type="submit"
          disabled={guardando}
          className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {guardando ? 'Guardando...' : 'Guardar'}
        </button>
      </form>
    </div>
  )
}