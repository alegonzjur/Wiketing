import { useEffect, useState } from 'react'
import { listarCategorias, crearCategoria } from '../api/tickets'

/**
 * Desplegable de categoría con creación inline: cumple el requisito de
 * "categorías gestionables desde la propia app" sin necesitar una
 * pantalla de administración aparte para el caso más común (añadir una
 * categoría nueva mientras creas un ticket).
 */
export default function CategoriaSelect({ value, onChange }) {
  const [categorias, setCategorias] = useState([])
  const [creando, setCreando] = useState(false)
  const [nombreNueva, setNombreNueva] = useState('')
  const [error, setError] = useState('')

  async function cargar() {
    const { data } = await listarCategorias()
    setCategorias(data)
  }

  useEffect(() => {
    cargar()
  }, [])

  async function handleCrear(e) {
    e.preventDefault()
    setError('')
    if (!nombreNueva.trim()) return
    try {
      const { data } = await crearCategoria({ nombre: nombreNueva.trim() })
      await cargar()
      onChange(data.id)
      setNombreNueva('')
      setCreando(false)
    } catch {
      setError('No se pudo crear (¿nombre repetido?)')
    }
  }

  return (
    <div>
      <div className="flex gap-2">
        <select
          className="flex-1 border rounded px-3 py-2"
          value={value ?? ''}
          onChange={(e) => onChange(Number(e.target.value))}
        >
          <option value="" disabled>Selecciona una categoría</option>
          {categorias.map((c) => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => setCreando((v) => !v)}
          className="px-3 py-2 border rounded text-gray-600 hover:bg-gray-50"
          title="Nueva categoría"
        >
          +
        </button>
      </div>

      {creando && (
        <div className="mt-2 flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-1 text-sm"
            placeholder="Nombre de la categoría"
            value={nombreNueva}
            onChange={(e) => setNombreNueva(e.target.value)}
            autoFocus
          />
          <button onClick={handleCrear} className="text-sm bg-blue-600 text-white px-3 rounded">
            Crear
          </button>
        </div>
      )}

      {error && <p className="text-red-600 text-xs mt-1">{error}</p>}
    </div>
  )
}