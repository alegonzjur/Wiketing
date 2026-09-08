import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // necesario para exponer el puerto fuera del contenedor Docker
    proxy: {
      // Reenvía /api al backend en desarrollo (npm run dev), evitando
      // problemas de CORS y replicando el mismo comportamiento que Nginx
      // en producción (mismo origen para frontend y API).
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})