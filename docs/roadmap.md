# Plataforma de Tickets — Roadmap por fases

**Stack:** Django + DRF · React · PostgreSQL · Docker Compose · JWT · 100% gratuito
**Alcance:** Single-user ahora, preparado para multi-usuario · Helpdesk + seguimiento de tareas/proyectos

---

## Fase 0 — Fundamentos del repositorio

**Objetivo:** dejar el esqueleto del proyecto listo antes de escribir lógica de negocio.

**Decisiones:**
- Monorepo con dos carpetas de primer nivel: `/backend` (Django) y `/frontend` (React) + `docker-compose.yml` en la raíz
- `backend`: proyecto Django con apps separadas desde el inicio: `tickets`, `categorias`, `guias`, `usuarios`, `busqueda` — evita un app monolítico y refleja los dominios ya definidos
- Entorno virtual con `requirements.txt` (no Pipenv/Poetry, por consistencia con tus otros proyectos en conda/venv)
- `.env` + `.env.example` desde el primer commit, con `django-environ` para separar configuración de código (necesario ya que luego habrá secretos de JWT, DB, y futura API key de IA)
- `.gitignore` cubriendo `node_modules`, `__pycache__`, `.env`, `media/`

**Entregable:** repo con estructura vacía pero funcional (`docker-compose up` levanta los 3 servicios y responde "hello world" en ambos extremos).

---

## Fase 1 — Backend core: modelos y base de datos

**Objetivo:** implementar el modelo de datos completo ya cerrado en el diseño.

**Decisiones:**
- Migraciones desde cero con los 5 modelos: `Categoria`, `Ticket`, `HistorialCambios`, `Comentario`, `Guia`
- `AUTH_USER_MODEL` propio desde el día uno (aunque extienda `AbstractUser` sin cambios todavía) — evita el clásico problema de Django de no poder cambiar el modelo de usuario a mitad de proyecto
- Signals de Django para `HistorialCambios`: cualquier cambio de `estado`/`asignado_a`/`prioridad` en `Ticket` genera una entrada automática — así la auditoría no depende de que el código de la vista se acuerde de registrarla
- Soft-delete en `Categoria` (`activa=False`) en vez de borrado real
- Índices explícitos en `Ticket.estado`, `Ticket.fecha_ultima_actividad` (los usará el dashboard y la tarea de abandono constantemente)

**Entregable:** modelos + migraciones aplicadas + Django Admin registrado para poder inspeccionar datos de prueba sin frontend.

---

## Fase 2 — API REST (tickets, categorías, comentarios)

**Objetivo:** CRUD completo vía DRF, sin auth todavía (se añade en Fase 3 para no mezclar dos problemas a la vez).

**Decisiones:**
- `ModelViewSet` de DRF por recurso + `DefaultRouter` — CRUD estándar sin reinventar rutas
- Filtros con `django-filter`: por `estado`, `tipo`, `categoria`, `prioridad`, rango de fechas — el dashboard los reutilizará
- Paginación por defecto (`PageNumberPagination`) desde el inicio, aunque el volumen sea bajo ahora
- Serializers separados para lectura/escritura en `Ticket` (el de lectura anida `categoria` y `historial` resumido; el de escritura solo espera IDs) — evita sobre-fetching y errores de anidación en creación

**Entregable:** API navegable de DRF con CRUD funcional de tickets, categorías y comentarios, probada con datos de ejemplo.

---

## Fase 3 — Autenticación JWT

**Objetivo:** proteger la API y dejar la puerta abierta a multi-usuario.

**Decisiones:**
- `djangorestframework-simplejwt`: endpoints `/api/token/` y `/api/token/refresh/`
- Todos los ViewSets con `IsAuthenticated` por defecto
- `creado_por` se asigna automáticamente del usuario del token (nunca del payload del cliente) — evita que alguien se "asigne" tickets a otro usuario
- Preparado pero no implementado aún: campo `rol` en el modelo de usuario, para cuando llegue el segundo usuario

**Entregable:** login funcional vía API, todos los endpoints anteriores protegidos.

---

## Fase 4 — Frontend base: React + autenticación

**Objetivo:** esqueleto de la SPA conectado a la API.

**Decisiones:**
- Vite en vez de Create React App (mantenido activo, arranque mucho más rápido)
- React Router para las rutas: `/login`, `/tickets`, `/tickets/:id`, `/dashboard`, `/guias`, `/buscar`
- Gestión de estado: Context API + hooks propios para auth (token en memoria + refresh silencioso), sin Redux — el alcance no lo justifica todavía
- Cliente HTTP centralizado (Axios con interceptor que añade el JWT y gestiona el refresh automático)
- Tailwind CSS para estilos — velocidad de desarrollo, sin diseñar un sistema propio para un proyecto de este tamaño

**Entregable:** login funcional desde React contra el backend, ruta protegida mínima tras autenticar.

---

## Fase 5 — Gestión de tickets (frontend)

**Objetivo:** las pantallas que usarás en el día a día.

**Decisiones:**
- Listado con filtros (estado, tipo, categoría, prioridad) reutilizando los query params ya definidos en la API
- Vista de detalle con historial de cambios y comentarios en línea temporal
- Formulario de creación/edición con selector de categoría dinámico (ya gestionable desde la app)
- Marcado manual de "abandonado" como acción explícita en la UI (botón, no solo cambio de estado genérico) — refleja la distinción `abandono_origen='manual'` del modelo

**Entregable:** ciclo completo crear → ver → comentar → cambiar estado → marcar abandonado, funcional de punta a punta.

---

## Fase 6 — Dashboard

**Objetivo:** las métricas ya definidas, visualizadas.

**Decisiones:**
- Endpoint(s) de agregación en backend (`/api/dashboard/resumen/`) que devuelven los números ya calculados — el frontend no debe recalcular agregados sobre datos crudos
- Librería de gráficas: Recharts (ligera, se integra bien con Tailwind, sin coste)
- Tarjetas de conteo (abiertos/en progreso/resueltos/abandonados) + gráfica de tendencia temporal + distribución por categoría y prioridad
- Filtro de rango de fechas también en el dashboard, reutilizando el mismo patrón de query params

**Entregable:** dashboard funcional con datos reales de tus tickets de prueba.

---

## Fase 7 — Guías (base de conocimiento) + búsqueda unificada

**Objetivo:** el apartado de guías propias y el buscador federado tickets+guías.

**Decisiones:**
- Editor Markdown en frontend (`react-markdown` para renderizado; textarea simple o `@uiw/react-md-editor` para edición, ambos gratuitos)
- Backend: `SearchVector`/`SearchQuery` de Postgres (`config='spanish'`) sobre `Ticket` y `Guia` por separado, endpoint único `/api/buscar/?q=` que devuelve `{tickets, guias}` como se diseñó
- Contador `veces_consultada` incrementado en el `retrieve` de la guía (no en cada búsqueda, solo al abrirla)
- Estado `publicada` para poder guardar borradores sin que aparezcan en resultados de búsqueda

**Entregable:** puedes escribir una guía, buscar "MFA" y ver tickets y guías relacionados en la misma pantalla.

---

## Fase 8 — Automatización de abandono

**Objetivo:** la regla de 30 días sin actividad.

**Decisiones:**
- Empezamos con **management command** (`revisar_abandonados`) + tarea programada del SO (Task Scheduler de Windows, ya que el servidor es Windows), **no Celery todavía** — evita meter Redis antes de necesitarlo
- El comando actualiza `fecha_ultima_actividad` como criterio (ya mantenido por los signals de la Fase 1) y marca `estado='abandonado'`, `abandono_origen='automatico'`
- Log propio del comando (fichero o `HistorialCambios` con usuario nulo) para poder auditar qué se marcó y cuándo

**Entregable:** comando ejecutable manualmente primero, luego programado, verificado con tickets de prueba con fecha manipulada.

---

## Fase 9 — Dockerización y despliegue

**Objetivo:** todo el stack corriendo con un solo comando en el servidor real.

**Decisiones:**
- `docker-compose.yml` con 3 servicios: `postgres` (volumen persistente), `backend` (Gunicorn), `frontend` (build de React servido por Nginx, que también actúa de reverse proxy hacia el backend)
- Variables de entorno de producción separadas de las de desarrollo (`.env.prod`)
- Backups: `pg_dump` programado (reutilizas el patrón que ya tienes en otros proyectos con scripts de backup)
- Si más adelante quieres acceso fuera de la red del centro: Cloudflare Tunnel (gratuito, sin abrir puertos) — se documenta pero no se implementa en esta fase

**Entregable:** plataforma accesible de forma persistente en el servidor de trabajo, con datos reales sustituyendo a los de prueba.

---

## Fase 10 (futuro, fuera de este roadmap inicial) — IA

**Objetivo:** dejado deliberadamente abierto, a decidir cuando la base esté en producción y validada.

**Opciones ya compatibles con el diseño actual, sin romper nada de lo anterior:**
- Búsqueda semántica: añadir `pgvector` a Postgres + columna `embedding` en `Guia` (y opcionalmente `Ticket`) — sustituye o complementa el full-text search de la Fase 7 sin cambiar el contrato del endpoint `/api/buscar/`
- Chatbot de soporte: RAG sobre las guías ya existentes (mismo patrón que `laila-rag`), expuesto como nuevo endpoint, con Celery + Redis para no bloquear peticiones en respuestas de LLM
- ML: clasificación automática de categoría/prioridad al crear un ticket, entrenado sobre el histórico ya acumulado en `Ticket` — solo tiene sentido una vez haya volumen real de datos

---

## Resumen de dependencias entre fases

```
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5
                                              ↓
                            Fase 6 ←──────────┤
                            Fase 7 ←──────────┤
                            Fase 8 (independiente, solo depende de Fase 1)
                                              ↓
                                          Fase 9
                                              ↓
                                    Fase 10 (futuro)
```

Las fases 6, 7 y 8 pueden desarrollarse en el orden que prefieras una vez completada la 5 — no tienen dependencia entre sí.