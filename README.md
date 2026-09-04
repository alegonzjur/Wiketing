# Plataforma de Tickets

Django + DRF · React (Vite) · PostgreSQL · Docker Compose

## Estado

**Fase 0 completada** — esqueleto del monorepo, backend y frontend
arrancando correctamente por separado y vía Docker Compose. Sin modelos de
negocio todavía (llegan en la Fase 1).

## Estructura

```
.
├── backend/          Django + DRF
│   ├── config/        settings, urls, wsgi/asgi
│   ├── usuarios/       modelo de usuario personalizado (AUTH_USER_MODEL)
│   ├── categorias/     (vacío, Fase 1)
│   ├── tickets/        (vacío, Fase 1)
│   ├── guias/           (vacío, Fase 7)
│   └── busqueda/        (vacío, Fase 7)
├── frontend/         React + Vite + Tailwind
└── docker-compose.yml
```

## Puesta en marcha (Docker Compose — recomendado)

```bash
cp .env.example .env
cp backend/.env.example backend/.env
# Edita ambos .env si quieres credenciales distintas a las de ejemplo

docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:80
- Postgres expuesto en localhost:5432 (para inspección con un cliente SQL)

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
npm run dev
```

## Decisiones de la Fase 0

Ver el roadmap completo del proyecto para el detalle de cada fase y sus
decisiones técnicas.
