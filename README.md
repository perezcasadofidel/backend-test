# Backend API Local - Pincha

API local construida con FastAPI que actua como intermediario entre React y la API oficial de Innovasoft.

Arquitectura:
React -> FastAPI local -> API Innovasoft / MongoDB

## Requisitos

- Python 3.10+
- MongoDB local en ejecucion

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Ejecucion

```bash
uvicorn app.main:app --reload
```

Base local por defecto:

- http://127.0.0.1:8000
- Swagger local: http://127.0.0.1:8000/docs

## Endpoints locales

Prefijo base: `/api/local`

- `GET /health`
- `POST /auth/login`
- `POST /auth/logout`
- `POST /clientes/listado`
- `GET /clientes/{cliente_id}`
- `POST /clientes`
- `PUT /clientes/{cliente_id}`
- `DELETE /clientes/{cliente_id}`
- `GET /clientes/intereses/listado`

## Comportamiento de MongoDB

Coleccion `sesiones`:

- Se crea/actualiza al hacer login exitoso.
- Se elimina al hacer logout.

Coleccion `operaciones`:

- Se registra en cada accion CRUD de cliente:
  - CREAR
  - ACTUALIZAR
  - ELIMINAR
- Incluye:
  - `accion`
  - `usuario`
  - `cliente_id`
  - `timestamp` (ISO 8601)
  - `resultado` (status HTTP de Innovasoft)

## Nota

La API local no expone ni delega consumo directo desde frontend a Innovasoft. Todo acceso pasa por FastAPI y `httpx` asíncrono.
