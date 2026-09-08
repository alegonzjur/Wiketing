import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login, cargando } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const destino = location.state?.from?.pathname || '/dashboard'

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await login(username, password)
      navigate(destino, { replace: true })
    } catch (err) {
      setError('Usuario o contraseña incorrectos')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-80">
        <h1 className="text-xl font-semibold mb-6 text-gray-800">Plataforma de Tickets</h1>

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

        <label className="block text-sm text-gray-600 mb-1" htmlFor="username">Usuario</label>
        <input
          id="username"
          className="w-full border rounded px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoFocus
        />

        <label className="block text-sm text-gray-600 mb-1" htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          className="w-full border rounded px-3 py-2 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          type="submit"
          disabled={cargando}
          className="w-full bg-blue-600 text-white rounded py-2 font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {cargando ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
