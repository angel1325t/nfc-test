# Sistema de Asistencia NFC (Flask + PostgreSQL)

## Estructura

```text
.
|-- app
|   |-- __init__.py
|   |-- config.py
|   |-- extensions.py
|   |-- models.py
|   `-- routes.py
|-- scripts
|   `-- init_db.py
|-- .dockerignore
|-- .env.example
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- wsgi.py
```

## Ejecutar con Docker

1. Crear archivo de entorno:

```bash
cp .env.example .env
```

2. Levantar servicios:

```bash
docker compose up --build
```

La API quedara disponible en:

```text
http://localhost:8000
```

## Endpoints

- `GET /asistencia?user_id=123`
- `GET /asistencia?tarjeta_uid=ABC123`
- `GET /usuarios`
- `POST /usuarios`
- `GET /registro-usuario?tarjeta_uid=ABC123&nombre=Angel`
- `GET /asistencias`
- `GET /health`

## Ejemplos

Crear usuario:

```bash
curl -X POST http://localhost:8000/usuarios \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Angel\"}"
```

Crear usuario con tarjeta NFC:

```bash
curl "http://localhost:8000/registro-usuario?tarjeta_uid=ABC123&nombre=Angel%20Perez"
```

Registrar asistencia NFC:

```bash
curl "http://localhost:8000/asistencia?user_id=1"
```

Registrar asistencia por tarjeta NFC:

```bash
curl "http://localhost:8000/asistencia?tarjeta_uid=ABC123"
```
