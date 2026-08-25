from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api import patients
from app.api import appointments


app = FastAPI(
    title="MEDBOOK",
    version="1.0.0"
)

# Permite que el frontend de React (Vite, puerto 5173) llame a la API
# desde el navegador. Sin esto, el navegador bloquea las peticiones
# aunque el backend funcione perfecto (error de CORS, no de la API).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(patients.router)
app.include_router(appointments.router)


@app.get("/")
def root():
    return {
        "message": "HELLOWORLD",
        "version": "1.0.0"
    }