import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { usuario, logout } = useAuth()
  const location = useLocation()

  function claseEnlace(ruta) {
    return location.pathname.startsWith(ruta)
      ? 'text-blue-600 font-medium'
      : 'text-gray-500 hover:text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-8 py-3 flex justify-between items-center">
        <div className="flex gap-6">
          <Link to="/dashboard" className={claseEnlace('/dashboard')}>Dashboard</Link>
          <Link to="/tickets" className={claseEnlace('/tickets')}>Tickets</Link>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">{usuario?.first_name || usuario?.username}</span>
          <button onClick={logout} className="text-sm text-gray-500 hover:text-gray-800">
            Cerrar sesión
          </button>
        </div>
      </nav>
      <Outlet />
    </div>
  )
}