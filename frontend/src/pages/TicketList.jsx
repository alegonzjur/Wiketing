import { useEffect, useState, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listarTickets } from '../api/tickets'
import { ESTADOS, TIPOS, PRIORIDADES } from '../constants/tickets'

function Badge({ valor, opciones }) {
  const opcion = opciones.find((o) => o.value === valor)
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${opcion?.color ?? 'bg-gray-100 text-gray-700'}`}>
      {opcion?.label ?? valor}
    </span>
  )
}

export default function TicketList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [datos, setDatos] = useState({ results: [], count: 0, next: null, previous: null })
  const [cargando, setCargando] = useState(true)

  const params = Object.fromEntries(searchParams.entries())

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const { data } = await listarTickets(params)
      setDatos(data)
    } finally {
      setCargando(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  useEffect(() => {
    cargar()
  }, [cargar])

  function actualizarFiltro(clave, valor) {
    const nuevos = new URLSearchParams(searchParams)
    if (valor) {
      nuevos.set(clave, valor)
    } else {
      nuevos.delete(clave)
    }
    nuevos.delete('page') // cualquier cambio de filtro reinicia la paginación
    setSearchParams(nuevos)
  }

  function irAPagina(url) {
    if (!url) return
    const pagina = new URL(url).searchParams.get('page')
    const nuevos = new URLSearchParams(searchParams)
    nuevos.set('page', pagina)
    setSearchParams(nuevos)
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-gray-800">Tickets</h1>
        <Link
          to="/tickets/nuevo"
          className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700"
        >
          Nuevo ticket
        </Link>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <input
          className="border rounded px-3 py-2 text-sm"
          placeholder="Buscar..."
          defaultValue={params.search ?? ''}
          onKeyDown={(e) => {
            if (e.key === 'Enter') actualizarFiltro('search', e.target.value)
          }}
        />
        <select
          className="border rounded px-3 py-2 text-sm"
          value={params.estado ?? ''}
          onChange={(e) => actualizarFiltro('estado', e.target.value)}
        >
          <option value="">Todos los estados</option>
          {ESTADOS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select
          className="border rounded px-3 py-2 text-sm"
          value={params.tipo ?? ''}
          onChange={(e) => actualizarFiltro('tipo', e.target.value)}
        >
          <option value="">Todos los tipos</option>
          {TIPOS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select
          className="border rounded px-3 py-2 text-sm"
          value={params.prioridad ?? ''}
          onChange={(e) => actualizarFiltro('prioridad', e.target.value)}
        >
          <option value="">Todas las prioridades</option>
          {PRIORIDADES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      {cargando ? (
        <p className="text-gray-500">Cargando...</p>
      ) : datos.results.length === 0 ? (
        <p className="text-gray-500">No hay tickets con estos filtros.</p>
      ) : (
        <div className="bg-white rounded-lg shadow divide-y">
          {datos.results.map((t) => (
            <Link
              key={t.id}
              to={`/tickets/${t.id}`}
              className="flex items-center justify-between px-4 py-3 hover:bg-gray-50"
            >
              <div>
                <p className="font-medium text-gray-800">{t.titulo}</p>
                <p className="text-xs text-gray-500">
                  {t.categoria?.nombre} · {new Date(t.fecha_creacion).toLocaleDateString('es-ES')}
                </p>
              </div>
              <div className="flex gap-2">
                <Badge valor={t.prioridad} opciones={PRIORIDADES} />
                <Badge valor={t.estado} opciones={ESTADOS} />
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="flex justify-between items-center mt-4 text-sm text-gray-500">
        <span>{datos.count} resultado{datos.count === 1 ? '' : 's'}</span>
        <div className="flex gap-2">
          <button
            disabled={!datos.previous}
            onClick={() => irAPagina(datos.previous)}
            className="px-3 py-1 border rounded disabled:opacity-40"
          >
            Anterior
          </button>
          <button
            disabled={!datos.next}
            onClick={() => irAPagina(datos.next)}
            className="px-3 py-1 border rounded disabled:opacity-40"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  )
}