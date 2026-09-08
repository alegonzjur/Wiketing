import axios from 'axios'

const client = axios.create({ baseURL: '/api' })

// Estas funciones las inyecta AuthProvider al montar. Se hace así (en vez
// de importar el contexto directamente aquí) para que este módulo sea un
// cliente HTTP independiente, sin depender de React.
let getTokens = () => ({ access: null, refresh: null })
let setAccessToken = () => {}
let onSesionExpirada = () => {}

export function configurarClienteAuth({ getTokens: getter, setAccessToken: setter, onSesionExpirada: cb }) {
  getTokens = getter
  setAccessToken = setter
  onSesionExpirada = cb
}

client.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

// Evita refrescos duplicados si varias peticiones reciben 401 a la vez:
// todas esperan la misma promesa de refresco en vez de disparar una cada una.
let refrescoEnCurso = null

async function refrescarAccessToken() {
  const { refresh } = getTokens()
  if (!refresh) throw new Error('No hay refresh token disponible')

  // axios "pelado" (sin los interceptores de arriba) para no entrar en
  // bucle si esta misma llamada devolviera 401.
  const respuesta = await axios.post('/api/token/refresh/', { refresh })
  const nuevoAccess = respuesta.data.access
  setAccessToken(nuevoAccess)
  return nuevoAccess
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    if (response?.status === 401 && config && !config._reintentado) {
      config._reintentado = true
      try {
        if (!refrescoEnCurso) {
          refrescoEnCurso = refrescarAccessToken().finally(() => {
            refrescoEnCurso = null
          })
        }
        const nuevoAccess = await refrescoEnCurso
        config.headers.Authorization = `Bearer ${nuevoAccess}`
        return client(config)
      } catch (errorRefresco) {
        onSesionExpirada()
        return Promise.reject(errorRefresco)
      }
    }
    return Promise.reject(error)
  }
)

export default client