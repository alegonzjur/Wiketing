import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import client, { configurarClienteAuth } from '../api/client'

const AuthContext = createContext(null)
const CLAVE_REFRESH = 'ticketing_refresh_token'

export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState({ access: null, refresh: null })
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(false)

  // Distinto de `cargando` (una petición de login en curso): esto cubre
  // el arranque de la app, mientras se intenta restaurar sesión a partir
  // del refresh token guardado. Mientras es true, las rutas protegidas
  // no deben redirigir a /login todavía, o se vería un parpadeo a login
  // incluso cuando sí había sesión guardada.
  const [inicializando, setInicializando] = useState(true)

  useEffect(() => {
    configurarClienteAuth({
      getTokens: () => tokens,
      setAccessToken: (access) => setTokens((t) => ({ ...t, access })),
      onSesionExpirada: () => {
        localStorage.removeItem(CLAVE_REFRESH)
        setTokens({ access: null, refresh: null })
        setUsuario(null)
      },
    })
  }, [tokens])

  // Al montar la app: si hay un refresh token de una sesión anterior,
  // se usa para pedir un access token nuevo y recuperar el usuario.
  // Decisión de seguridad asumida: el refresh token vive en localStorage
  // (persiste entre recargas), el access token vive solo en memoria.
  useEffect(() => {
    async function restaurarSesion() {
      const refresh = localStorage.getItem(CLAVE_REFRESH)
      if (!refresh) {
        setInicializando(false)
        return
      }
      try {
        const { data: tokenData } = await client.post('/token/refresh/', { refresh })
        const { data: usuarioData } = await client.get('/usuarios/me/', {
          headers: { Authorization: `Bearer ${tokenData.access}` },
        })
        setTokens({ access: tokenData.access, refresh })
        setUsuario(usuarioData)
      } catch {
        // Refresh token caducado o inválido: no se puede recuperar la
        // sesión, se limpia y tocará volver a iniciar sesión.
        localStorage.removeItem(CLAVE_REFRESH)
      } finally {
        setInicializando(false)
      }
    }
    restaurarSesion()
  }, [])

  const login = useCallback(async (username, password) => {
    setCargando(true)
    try {
      const { data } = await client.post('/token/', { username, password })
      localStorage.setItem(CLAVE_REFRESH, data.refresh)
      setTokens({ access: data.access, refresh: data.refresh })
      setUsuario(data.user)
    } finally {
      setCargando(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem(CLAVE_REFRESH)
    setTokens({ access: null, refresh: null })
    setUsuario(null)
  }, [])

  const value = {
    usuario,
    estaAutenticado: Boolean(tokens.access),
    cargando,
    inicializando,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  }
  return context
}
