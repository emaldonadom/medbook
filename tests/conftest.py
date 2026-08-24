import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import Base, get_db
from app.models.role import Role

# Base SQLite en memoria compartida durante todo el proceso de tests.
# StaticPool mantiene siempre la MISMA conexión, algo necesario porque
# ":memory:" por defecto crea una base nueva y vacía por cada conexión.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Crea las tablas y sembra los roles antes de cada test, y limpia después.

    Esto garantiza que cada test arranca desde cero: sin usuarios,
    pacientes ni citas de tests anteriores.
    """
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add_all([
        Role(id=1, name="admin"),
        Role(id=2, name="doctor"),
        Role(id=3, name="patient"),
    ])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient, email: str, password: str, role_id: int) -> dict:
    """Registra un usuario con el rol dado y devuelve sus headers de auth."""
    response = client.post(
        "/users/",
        json={
            "name": f"Usuario {email}",
            "email": email,
            "password": password,
            "role_id": role_id,
        },
    )
    assert response.status_code == 200, response.text

    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    return register_and_login(client, "admin@medbook.example.com", "adminpass123", role_id=1)


@pytest.fixture
def doctor_headers(client):
    return register_and_login(client, "doctor@medbook.example.com", "doctorpass123", role_id=2)


@pytest.fixture
def patient_headers(client):
    return register_and_login(client, "patient@medbook.example.com", "patientpass123", role_id=3)


@pytest.fixture
def another_patient_headers(client):
    return register_and_login(client, "patient2@medbook.example.com", "patientpass123", role_id=3)
