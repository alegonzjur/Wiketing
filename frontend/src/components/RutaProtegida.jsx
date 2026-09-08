import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Envuelve rutas que requieren sesión iniciada. Si no hay token, redirige
 * a /login guardando la ruta original en location.state para volver allí
 * tras iniciar sesión.
 */
export default function RutaProtegida() {
  const { estaAutenticado, inicializando } = useAuth()
  const location = useLocation()

  if (inicializando) {
    // Evita un parpadeo a /login mientras se comprueba si hay una sesión
    // guardada (refresh token en localStorage) que se pueda restaurar.
    return null
  }

  if (!estaAutenticado) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}