# Wiketing - Plataforma de Tickets

Django + DRF · React (Vite) · PostgreSQL · Docker Compose

Herramienta interna de gestión de tickets (helpdesk + seguimiento de
tareas/proyectos), single-user por ahora, preparada para multi-usuario.

## Estado

**Fases 0 a 6 completadas.**

| Fase | Contenido | Estado |
|---|---|---|
| 0 | Esqueleto del monorepo, Docker Compose, backend/frontend arrancando | ✅ |
| 1 | Modelos (`Ticket`, `Categoria`, `HistorialCambios`, `Comentario`) + auditoría automática por signals | ✅ |
| 2 | API REST completa (tickets, categorías, comentarios) con filtros y búsqueda | ✅ |
| 3 | Autenticación JWT (login, refresh) | ✅ |
| 4 | Frontend React: login, sesión persistente (refresh token en localStorage), rutas protegidas | ✅ |
| 5 | Gestión de tickets: listado con filtros, detalle con historial/comentarios, formulario de creación/edición, categorías gestionables inline | ✅ |
| 6 | Dashboard con métricas (conteos por estado, distribución por categoría/prioridad, tendencia mensual, tiempo medio de resolución) | ✅ |
| 7 | Guías (base de conocimiento) + búsqueda unificada tickets+guías | ⬜ Pendiente |
| 8 | Automatización de abandono (30 días sin actividad) | ⬜ Pendiente |
| 9 | Dockerización de producción y despliegue | ⬜ Parcial (Docker Compose de desarrollo ya funciona) |
| 10 | IA (búsqueda semántica, chatbot, ML) | ⬜ Futuro, fuera de alcance por ahora |

## Estructura

```
.
├── backend/                  Django + DRF
│   ├── config/                 settings, urls, wsgi/asgi
│   ├── usuarios/                AUTH_USER_MODEL propio, login JWT extendido, /usuarios/me/
│   ├── categorias/               CRUD + soft-delete, sin paginación (tabla de referencia)
│   ├── tickets/                   Ticket, HistorialCambios, Comentario, signals de auditoría,
│   │                               endpoint de dashboard
│   ├── guias/                      (vacío, Fase 7)
│   └── busqueda/                    (vacío, Fase 7)
├── frontend/                  React + Vite + Tailwind + React Router + Recharts
│   └── src/
│       ├── api/                  cliente Axios con refresh automático, wrappers por dominio
│       ├── context/                AuthContext (sesión, tokens)
│       ├── components/               Layout, RutaProtegida, CategoriaSelect
│       ├── pages/                     Login, Dashboard, TicketList, TicketDetail, TicketForm
│       └── constants/                  choices duplicados desde los TextChoices del backend
└── docker-compose.yml         postgres + backend + frontend, con healthchecks
```

## Puesta en marcha (Docker Compose — recomendado)

```bash
cp .env.example .env
cp backend/.env.example backend/.env
# Edita ambos .env si quieres credenciales distintas a las de ejemplo

docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

- Frontend: http://localhost (puerto 80, vía Nginx)
- Backend / API navegable: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/
- Postgres expuesto en **localhost:5433** (no 5432 — ver "Decisiones y

  problemas resueltos" más abajo) para inspección con un cliente SQL

## Desarrollo sin Docker (opcional)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate  # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # y cambia el host de DATABASE_URL a localhost
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # con proxy a /api configurado en vite.config.js
```

## API — endpoints principales

| Endpoint | Método(s) | Notas |
|---|---|---|
| `/api/token/` | POST | Login JWT, devuelve `access`, `refresh` y datos del usuario |
| `/api/token/refresh/` | POST | Renueva el `access` token |
| `/api/usuarios/me/` | GET | Usuario autenticado actual (usado para restaurar sesión tras F5) |
| `/api/tickets/` | GET, POST | Filtros: `estado`, `tipo`, `categoria`, `prioridad`, `asignado_a`, `fecha_creacion_desde/hasta`; búsqueda: `?search=` |
| `/api/tickets/{id}/` | GET, PATCH, PUT | Detalle incluye `historial` y `comentarios` anidados |
| `/api/categorias/` | GET, POST, DELETE | Sin paginación; `DELETE` es soft-delete (`activa=False`); `?todas=true` incluye inactivas |
| `/api/comentarios/` | GET, POST | Requiere `ticket` (ID) en el body |
| `/api/dashboard/resumen/` | GET | Filtros opcionales `fecha_desde`/`fecha_hasta` (AAAA-MM-DD) |
| `/api-auth/login/` | — | Puente de sesión para la API navegable (depuración), no lo usa el frontend |

## Decisiones de diseño clave

- **Un único modelo `Ticket`** con campo `tipo` (incidencia/tarea) en vez de dos modelos separados — mismo flujo de estados y dashboard para ambos casos.
- **Auditoría automática vía signals**, no en las vistas: cualquier cambio de `estado`/`prioridad`/`asignado_a` queda en `HistorialCambios` sin que el código de la API tenga que acordarse. Quien guarda el ticket debe asignar `instance._usuario_modificacion` antes de `.save()` para que el cambio no quede como "automático".
- **`fecha_ultima_actividad`** se actualiza con cualquier cambio relevante o comentario, **excepto** cuando el cambio es el propio marcado automático de abandono (evita que el cron de la Fase 8 reinicie su propio contador).
- **`fecha_resolucion`** se autorellena al entrar en estado `resuelto` y se limpia al salir de ese estado — necesario para que el tiempo medio de resolución del dashboard tenga datos.
- **Tokens JWT solo en memoria (`access`) + `localStorage` (`refresh`)**: trade-off de seguridad asumido para una herramienta interna de un único usuario. Ver `frontend/src/context/AuthContext.jsx` para el detalle.
- **Choices duplicados entre backend y frontend** (`backend/tickets/models.py` ↔ `frontend/src/constants/tickets.js`): si cambias un valor en un sitio, hay que actualizar el otro a mano.
- **Categorías sin paginación**: es una tabla de referencia pequeña usada como desplegable, no una lista que crece sin límite.

## Decisiones y problemas resueltos durante el desarrollo

- **Puerto 5432 ocupado**: si tienes otro proyecto con Postgres en Docker usando el 5432 del host, este proyecto expone el suyo en **5433** (`docker-compose.yml`, servicio `postgres`). El backend sigue hablando con Postgres por `postgres:5432` dentro de la red de Docker; el cambio solo afecta a accesos desde fuera de Docker.
- **Healthcheck de Postgres con `-d` explícito**: sin especificar la base de datos, `pg_isready` asume que se llama igual que el usuario y falla en bucle.
- **`.dockerignore` en `backend/` y `frontend/`**: sin él, un `node_modules` local (con binarios nativos de otra plataforma) puede sobreescribir el instalado dentro del contenedor Linux y romper `npm run build`.
- **`LOGIN_REDIRECT_URL`**: Django redirige a `/accounts/profile/` por defecto tras el login de sesión; se sobreescribió a `/api/` porque esa ruta no existe en este proyecto.

## Limitaciones conocidas (no resueltas todavía)

- El endpoint de comentarios no está anidado bajo `/tickets/{id}/comentarios/` — hay que mandar el `ticket` en el body.
- No existe todavía asignación de tickets a otros usuarios desde la UI (el campo `asignado_a` existe en el modelo y la API, pero no hay selector en el frontend — tiene sentido cuando haya multi-usuario real).
- El bundle de producción del frontend pesa ~190KB comprimidos, principalmente por Recharts; no se ha aplicado code-splitting.
- Recharts está en la versión 2.x (mantenimiento), no en la 3.x activa.

## Roadmap completo

Ver el documento de roadmap del proyecto para el detalle de las fases 7-10 y sus decisiones técnicas previstas.