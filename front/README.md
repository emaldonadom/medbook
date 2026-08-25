# MedBook Frontend

Frontend en React (Vite) para probar la API de MedBook. Cubre el flujo de
paciente: registro, login, crear/editar perfil de paciente, agendar citas y
ver/cancelar tus citas.

## Requisitos

- Node.js 18+
- El backend de MedBook corriendo en `http://localhost:8000` (con el fix de
  CORS aplicado — ver más abajo)

## Instalación

```bash
npm install
cp .env.example .env
npm run dev
```

Abrí `http://localhost:5173`.

## Importante: CORS en el backend

Este frontend corre en `http://localhost:5173`. El backend necesita permitir
ese origen o el navegador va a bloquear las peticiones. Si todavía no
aplicaste el cambio, agregá esto en `app/main.py` (antes de los
`include_router`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Flujo para probar

1. `/register` — crear una cuenta (siempre se registra como paciente)
2. `/perfil` — completar fecha de nacimiento, teléfono y dirección
3. `/agendar` — elegir un doctor (necesitás tener al menos un doctor creado
   en el backend, con `role_id: 2`) y agendar una cita
4. `/citas` — ver el estado de tus citas y cancelarlas

Si iniciás sesión con una cuenta que no es de rol "patient" (doctor o
admin), vas a ver una pantalla de acceso restringido — este frontend todavía
solo cubre la vista de paciente.
