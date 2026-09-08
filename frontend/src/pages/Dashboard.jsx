import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend, PieChart, Pie, Cell,
} from 'recharts'
import { obtenerResumenDashboard } from '../api/dashboard'
import { PRIORIDADES } from '../constants/tickets'

const COLOR_PRIORIDAD = { baja: '#9ca3af', media: '#3b82f6', alta: '#f97316', critica: '#ef4444' }

function TarjetaMetrica({ etiqueta, valor, colorClase }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-xs text-gray-500 mb-1">{etiqueta}</p>
      <p className={`text-2xl font-semibold ${colorClase ?? 'text-gray-800'}`}>{valor}</p>
    </div>
  )
}

export default function Dashboard() {
  const [rango, setRango] = useState({ fecha_desde: '', fecha_hasta: '' })
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    async function cargar() {
      setCargando(true)
      const params = {}
      if (rango.fecha_desde) params.fecha_desde = rango.fecha_desde
      if (rango.fecha_hasta) params.fecha_hasta = rango.fecha_hasta
      const { data } = await obtenerResumenDashboard(params)
      setDatos(data)
      setCargando(false)
    }
    cargar()
  }, [rango])

  if (cargando || !datos) return <p className="p-8 text-gray-500">Cargando métricas...</p>

  const datosCategoria = datos.por_categoria.map((c) => ({ nombre: c.categoria, total: c.total }))
  const datosPrioridad = Object.entries(datos.por_prioridad).map(([valor, total]) => ({
    nombre: PRIORIDADES.find((p) => p.value === valor)?.label ?? valor,
    valor,
    total,
  }))
  const hayDatosPrioridad = datosPrioridad.some((d) => d.total > 0)

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
        <h1 className="text-2xl font-semibold text-gray-800">Dashboard</h1>
        <div className="flex gap-2 items-center text-sm">
          <label className="text-gray-500" htmlFor="fecha_desde">Desde</label>
          <input
            id="fecha_desde"
            type="date"
            className="border rounded px-2 py-1"
            value={rango.fecha_desde}
            onChange={(e) => setRango((r) => ({ ...r, fecha_desde: e.target.value }))}
          />
          <label className="text-gray-500" htmlFor="fecha_hasta">Hasta</label>
          <input
            id="fecha_hasta"
            type="date"
            className="border rounded px-2 py-1"
            value={rango.fecha_hasta}
            onChange={(e) => setRango((r) => ({ ...r, fecha_hasta: e.target.value }))}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <TarjetaMetrica etiqueta="Total" valor={datos.total_tickets} />
        <TarjetaMetrica etiqueta="Abiertos" valor={datos.por_estado.abierto} colorClase="text-blue-600" />
        <TarjetaMetrica etiqueta="En progreso" valor={datos.por_estado.en_progreso} colorClase="text-yellow-600" />
        <TarjetaMetrica etiqueta="Resueltos" valor={datos.por_estado.resuelto} colorClase="text-green-600" />
        <TarjetaMetrica etiqueta="Abandonados" valor={datos.por_estado.abandonado} colorClase="text-gray-500" />
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-8">
        <p className="text-xs text-gray-500 mb-1">Tiempo medio de resolución</p>
        <p className="text-2xl font-semibold text-gray-800">
          {datos.tiempo_medio_resolucion_horas != null
            ? `${datos.tiempo_medio_resolucion_horas} h`
            : 'Sin datos todavía'}
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm font-semibold text-gray-600 mb-3">Tickets por categoría</h2>
          {datosCategoria.length === 0 ? (
            <p className="text-sm text-gray-400">Sin datos.</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={datosCategoria}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="nombre" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-sm font-semibold text-gray-600 mb-3">Tickets por prioridad</h2>
          {!hayDatosPrioridad ? (
            <p className="text-sm text-gray-400">Sin datos.</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={datosPrioridad} dataKey="total" nameKey="nombre" outerRadius={90} label>
                  {datosPrioridad.map((entry) => (
                    <Cell key={entry.valor} fill={COLOR_PRIORIDAD[entry.valor] ?? '#9ca3af'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-sm font-semibold text-gray-600 mb-3">Tendencia mensual</h2>
        {datos.tendencia.length === 0 ? (
          <p className="text-sm text-gray-400">Sin datos suficientes todavía.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={datos.tendencia}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="periodo" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="creados" name="Creados" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="resueltos" name="Resueltos" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}