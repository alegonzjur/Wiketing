import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { usuario, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-semibold text-gray-800">
          Hola, {usuario?.first_name || usuario?.username}
        </h1>
        <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-800">
          Cerrar sesión
        </button>
      </div>
      <p className="text-gray-500">
        Fase 4 — login JWT funcionando de punta a punta. El dashboard real
        con métricas llega en la Fase 6.
      </p>
    </div>
  )
}
