# Backend API + Authentication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI backend with Firebase Auth, Cloud SQL PostgreSQL, and GCS model loading, and update the React frontend with a login page and real API calls.

**Architecture:** FastAPI runs on Cloud Run, verifies Firebase ID tokens from the frontend, loads a `.pkl` model from GCS at startup, and persists user data to Cloud SQL PostgreSQL via the Cloud SQL connector. The frontend gains a login page (email/password + Google) and wires the classify flow to the real API. For local development, a direct `DATABASE_URL` bypasses the Cloud SQL connector.

**Tech Stack:** FastAPI, SQLAlchemy (async), asyncpg, cloud-sql-python-connector, firebase-admin, google-cloud-storage, psutil, Alembic, pytest, React + Firebase JS SDK

---

## File Map

### Backend (new `backend/` directory)

| File | Responsibility |
|---|---|
| `backend/main.py` | App entry point: CORS, routers, lifespan (model load) |
| `backend/requirements.txt` | All Python dependencies pinned |
| `backend/.env.example` | Template for required env vars |
| `backend/app/config.py` | pydantic-settings: all env vars with validation |
| `backend/app/database.py` | Cloud SQL connector + async SQLAlchemy engine + `get_db()` |
| `backend/app/models/user.py` | SQLAlchemy `User` ORM model |
| `backend/app/models/request_log.py` | SQLAlchemy `RequestLog` ORM model |
| `backend/app/schemas/user.py` | Pydantic: `UserSync`, `UserResponse` |
| `backend/app/schemas/classify.py` | Pydantic: `Metrics`, `ClassifyResponse` |
| `backend/app/services/firebase.py` | Firebase Admin SDK init + `verify_token()` dependency |
| `backend/app/services/model.py` | GCS model download + `run_inference()` |
| `backend/app/data/species_data.py` | Class-label → species info lookup dict |
| `backend/app/routers/auth.py` | `POST /auth/sync` |
| `backend/app/routers/classify.py` | `POST /classify` |
| `backend/tests/conftest.py` | pytest fixtures: test client, mocked Firebase, mocked model |
| `backend/tests/test_health.py` | `GET /health` tests |
| `backend/tests/test_auth.py` | `POST /auth/sync` tests |

### Frontend (additions to existing `src/`)

| File | Responsibility |
|---|---|
| `src/services/firebase.js` | Firebase client SDK init, `auth`, `googleProvider` |
| `src/services/api.js` | `syncUser()`, `classify(file)` — attaches Bearer token |
| `src/hooks/useAuth.js` | `onAuthStateChanged` wrapper → `{ user, loading }` |
| `src/pages/LoginPage.jsx` | Email/password form + Google Sign-In button |
| `src/App.jsx` | Updated: auth check, real classify call, error handling |
| `src/components/Header.jsx` | Updated: optional `onSignOut` prop → "Salir" button |
| `src/components/UploadZone.jsx` | Unchanged (onUpload prop still works) |

---

## Task 1: Backend Scaffold + Config

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`

- [ ] **Step 1: Create `backend/` directory structure**

```bash
cd /Users/mymac/Desktop/Ing-sistemas/2026-1/REDES-NEURONALES/reconocimiento-aves
mkdir -p backend/app/models backend/app/schemas backend/app/services backend/app/routers backend/app/data backend/tests
touch backend/app/__init__.py backend/app/models/__init__.py backend/app/schemas/__init__.py
touch backend/app/services/__init__.py backend/app/routers/__init__.py backend/app/data/__init__.py
touch backend/tests/__init__.py
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy[asyncio]==2.0.36
asyncpg==0.29.0
cloud-sql-python-connector[asyncpg]==1.12.1
google-cloud-storage==2.18.2
firebase-admin==6.5.0
python-multipart==0.0.12
pydantic-settings==2.5.2
alembic==1.13.3
psutil==6.0.0
Pillow==10.4.0
numpy==1.26.4
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

- [ ] **Step 3: Create `backend/.env.example`**

```
# Local dev — use this instead of Cloud SQL connector
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/avevision

# Cloud Run (leave empty for local dev)
CLOUD_SQL_CONNECTION_NAME=
DB_USER=
DB_PASSWORD=
DB_NAME=

# Google Cloud Storage
GCS_BUCKET_NAME=avevision-models
MODEL_BLOB_NAME=model.pkl

# Firebase
FIREBASE_PROJECT_ID=your-firebase-project-id

# CORS — set to your Vercel URL in production
FRONTEND_URL=http://localhost:5173
```

- [ ] **Step 4: Create `backend/app/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Local dev: direct PostgreSQL URL (overrides Cloud SQL connector)
    database_url: str | None = None

    # Cloud Run: Cloud SQL connector
    cloud_sql_connection_name: str | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_name: str | None = None

    # GCS
    gcs_bucket_name: str = "avevision-models"
    model_blob_name: str = "model.pkl"

    # Firebase
    firebase_project_id: str = "your-project-id"

    # CORS
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Install dependencies in a virtual environment**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Expected: all packages install without errors.

- [ ] **Step 6: Copy `.env.example` to `.env` and fill in local values**

```bash
cp .env.example .env
```

For local dev, set `DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/avevision` and leave the Cloud SQL fields empty. Create the local database:

```bash
createdb avevision   # or use psql: CREATE DATABASE avevision;
```

- [ ] **Step 7: Commit**

```bash
cd /Users/mymac/Desktop/Ing-sistemas/2026-1/REDES-NEURONALES/reconocimiento-aves
git add backend/
git commit -m "chore: scaffold FastAPI backend with config and requirements"
```

---

## Task 2: Database Layer

**Files:**
- Create: `backend/app/database.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_db.py`:

```python
import pytest
from app.database import Base


def test_base_exists():
    # Verify the declarative base is importable and has the expected interface
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && source venv/bin/activate
pytest tests/test_db.py -v
```

Expected: `ImportError: cannot import name 'Base' from 'app.database'`

- [ ] **Step 3: Create `backend/app/database.py`**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


_engine = None


async def _get_engine():
    global _engine
    if _engine is not None:
        return _engine

    from app.config import settings

    if settings.database_url:
        # Local development: direct connection
        _engine = create_async_engine(settings.database_url, echo=False)
    else:
        # Cloud Run: Cloud SQL connector
        from google.cloud.sql.connector import create_async_connector
        connector = await create_async_connector()

        async def get_conn():
            return await connector.connect_async(
                settings.cloud_sql_connection_name,
                "asyncpg",
                user=settings.db_user,
                password=settings.db_password,
                db=settings.db_name,
            )

        _engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=get_conn,
            echo=False,
        )

    return _engine


async def get_db() -> AsyncSession:
    engine = await _get_engine()
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_db.py -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add backend/app/database.py backend/tests/test_db.py
git commit -m "feat: add async database layer with Cloud SQL connector support"
```

---

## Task 3: ORM Models

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/request_log.py`

- [ ] **Step 1: Create `backend/app/models/user.py`**

```python
from sqlalchemy import Column, Text, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    firebase_uid = Column(Text, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    display_name = Column(Text)
    role = Column(Text, nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: Create `backend/app/models/request_log.py`**

```python
from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey, func
from app.database import Base


class RequestLog(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, ForeignKey("users.firebase_uid"), nullable=False)
    image_filename = Column(Text)
    predicted_class = Column(Text)
    confidence = Column(Float)
    latency_ms = Column(Integer)
    ram_mb = Column(Float)
    cpu_percent = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 3: Write and run import test**

Add to `backend/tests/test_db.py`:

```python
def test_models_importable():
    from app.models.user import User
    from app.models.request_log import RequestLog
    assert User.__tablename__ == "users"
    assert RequestLog.__tablename__ == "requests"
```

```bash
pytest tests/test_db.py -v
```

Expected: both tests PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add User and RequestLog ORM models"
```

---

## Task 4: Alembic Migrations

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`

- [ ] **Step 1: Initialize Alembic**

```bash
cd backend && source venv/bin/activate
alembic init alembic
```

Expected: `alembic/` directory created with `env.py` and `versions/`.

- [ ] **Step 2: Replace `backend/alembic/env.py`**

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.config import settings
from app.database import Base
import app.models.user  # noqa: F401 — register models with Base
import app.models.request_log  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    if settings.database_url:
        return settings.database_url
    # Cloud SQL (sync URL for Alembic)
    return (
        f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
        f"@/{settings.db_name}?host=/cloudsql/{settings.cloud_sql_connection_name}"
    )


def run_migrations_offline() -> None:
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(get_url())
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] **Step 3: Update `backend/alembic.ini` — set script_location**

In `alembic.ini`, find and update:
```
script_location = alembic
```
(This is already the default — just verify it is set correctly.)

- [ ] **Step 4: Generate initial migration**

```bash
cd backend && source venv/bin/activate
alembic revision --autogenerate -m "initial_schema"
```

Expected: file created in `alembic/versions/` like `xxxx_initial_schema.py` containing `create_table("users", ...)` and `create_table("requests", ...)`.

- [ ] **Step 5: Run migration against local database**

```bash
alembic upgrade head
```

Expected:
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, initial_schema
```

Verify tables exist:
```bash
psql avevision -c "\dt"
```

Expected output includes `users` and `requests`.

- [ ] **Step 6: Commit**

```bash
git add backend/alembic/ backend/alembic.ini
git commit -m "feat: add Alembic migrations for users and requests tables"
```

---

## Task 5: Firebase Service

**Files:**
- Create: `backend/app/services/firebase.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_firebase.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_verify_token_raises_on_invalid():
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("invalid")):
        with patch("firebase_admin.initialize_app"):
            from app.services.firebase import verify_token
            with pytest.raises(HTTPException) as exc:
                await verify_token("bad-token")
            assert exc.value.status_code == 401
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_firebase.py -v
```

Expected: `ImportError` or `ModuleNotFoundError`

- [ ] **Step 3: Create `backend/app/services/firebase.py`**

```python
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

_firebase_app = None
_bearer = HTTPBearer()


def _get_app():
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(
            cred, {"projectId": settings.firebase_project_id}
        )
    return _firebase_app


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> dict:
    _get_app()
    try:
        decoded = auth.verify_id_token(credentials.credentials)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_firebase.py -v
```

Expected: `PASSED`

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/firebase.py backend/tests/test_firebase.py
git commit -m "feat: add Firebase token verification dependency"
```

---

## Task 6: Species Data + Model Service

**Files:**
- Create: `backend/app/data/species_data.py`
- Create: `backend/app/services/model.py`

- [ ] **Step 1: Create `backend/app/data/species_data.py`**

```python
# Map model output class labels → species display info.
# Populate this dict with your actual classes once the model is trained.
# Keys must exactly match what model.predict() returns.
SPECIES_DATA: dict[str, dict] = {
    "mirlo_comun": {
        "especie": "Mirlo Común",
        "nombre_cientifico": "Turdus merula",
        "descripcion": (
            "El mirlo común es un ave paseriforme de la familia Turdidae, "
            "conocida por su plumaje negro brillante en los machos y su melodioso canto."
        ),
        "datos_curiosos": [
            "El macho adulto tiene un pico y anillo orbital de color amarillo-naranja intenso.",
            "Es capaz de imitar los sonidos de otras aves e incluso sonidos artificiales.",
            "Puede vivir hasta 5 años en estado salvaje y más de 20 en cautividad.",
        ],
    },
    # Add more species here matching your model's class labels
}

_FALLBACK = {
    "especie": "Ave no identificada",
    "nombre_cientifico": "Especie desconocida",
    "descripcion": "Esta especie no se encuentra en la base de datos actual.",
    "datos_curiosos": ["Agrega esta especie al diccionario SPECIES_DATA."],
}


def get_species_info(class_label: str) -> dict:
    return SPECIES_DATA.get(class_label, _FALLBACK)
```

- [ ] **Step 2: Write the failing test**

Create `backend/tests/test_model.py`:

```python
from app.data.species_data import get_species_info


def test_get_species_info_known():
    info = get_species_info("mirlo_comun")
    assert info["especie"] == "Mirlo Común"
    assert info["nombre_cientifico"] == "Turdus merula"
    assert len(info["datos_curiosos"]) == 3


def test_get_species_info_unknown_returns_fallback():
    info = get_species_info("nonexistent_bird")
    assert "no identificada" in info["especie"]
```

- [ ] **Step 3: Run test to verify it passes**

```bash
pytest tests/test_model.py::test_get_species_info_known tests/test_model.py::test_get_species_info_unknown_returns_fallback -v
```

Expected: both PASS.

- [ ] **Step 4: Create `backend/app/services/model.py`**

```python
import io
import os
import pickle
import time

import numpy as np
import psutil
from PIL import Image

_model = None


def load_model_from_gcs() -> None:
    """Download model.pkl from GCS and hold in memory. Called once at startup."""
    global _model
    from google.cloud import storage
    from app.config import settings

    client = storage.Client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob = bucket.blob(settings.model_blob_name)
    model_bytes = blob.download_as_bytes()
    _model = pickle.loads(model_bytes)
    print(f"[model] Loaded from gs://{settings.gcs_bucket_name}/{settings.model_blob_name}")


def is_model_loaded() -> bool:
    return _model is not None


def run_inference(image_bytes: bytes) -> dict:
    """
    Run classification on raw image bytes.
    Adapt the preprocessing and prediction call to match your model's expected input.
    Returns: { predicted_class, confidence, latency_ms, ram_mb, cpu_percent }
    """
    if _model is None:
        raise RuntimeError("Model not loaded")

    process = psutil.Process(os.getpid())
    ram_before = process.memory_info().rss / 1024 / 1024

    start = time.perf_counter()

    # --- Preprocessing (adapt to your model) ---
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # shape: (1, 224, 224, 3)

    # --- Inference ---
    # For sklearn: prediction = _model.predict(img_array)[0]
    # For Keras/TF: probabilities = _model.predict(img_array)[0]; prediction = classes[np.argmax(probabilities)]
    # Adjust the lines below to match your model's output format:
    probabilities = _model.predict(img_array)
    if hasattr(probabilities, '__len__') and len(probabilities.shape) > 1:
        # Multi-class output (Keras-style)
        class_idx = int(np.argmax(probabilities[0]))
        confidence = float(probabilities[0][class_idx])
        # Map index to label if model has classes_ attribute, else use str(class_idx)
        classes = getattr(_model, "classes_", None)
        predicted_class = str(classes[class_idx]) if classes is not None else str(class_idx)
    else:
        # Direct label output (sklearn-style)
        predicted_class = str(probabilities[0])
        confidence = 1.0  # sklearn classifiers don't return confidence by default

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    ram_after = process.memory_info().rss / 1024 / 1024

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "latency_ms": elapsed_ms,
        "ram_mb": round(max(ram_after - ram_before, 0.0), 2),
        "cpu_percent": round(psutil.cpu_percent(interval=None), 1),
    }
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/species_data.py backend/app/services/model.py backend/tests/test_model.py
git commit -m "feat: add species data lookup and model inference service"
```

---

## Task 7: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/classify.py`

- [ ] **Step 1: Create `backend/app/schemas/user.py`**

```python
from pydantic import BaseModel


class UserSync(BaseModel):
    firebase_uid: str
    email: str
    display_name: str | None = None


class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str
```

- [ ] **Step 2: Create `backend/app/schemas/classify.py`**

```python
from pydantic import BaseModel


class Metrics(BaseModel):
    latency_ms: int
    ram_mb: float
    cpu_percent: float


class ClassifyResponse(BaseModel):
    especie: str
    nombre_cientifico: str
    confianza: float
    descripcion: str
    datos_curiosos: list[str]
    metrics: Metrics
```

- [ ] **Step 3: Write and run schema test**

Add to `backend/tests/test_model.py`:

```python
def test_classify_response_schema():
    from app.schemas.classify import ClassifyResponse, Metrics
    resp = ClassifyResponse(
        especie="Mirlo Común",
        nombre_cientifico="Turdus merula",
        confianza=0.91,
        descripcion="Descripción de prueba.",
        datos_curiosos=["Hecho 1", "Hecho 2"],
        metrics=Metrics(latency_ms=142, ram_mb=48.2, cpu_percent=12.4),
    )
    assert resp.confianza == 0.91
    assert resp.metrics.latency_ms == 142
```

```bash
pytest tests/test_model.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas for auth and classify endpoints"
```

---

## Task 8: Auth Router

**Files:**
- Create: `backend/app/routers/auth.py`

- [ ] **Step 1: Create `backend/app/routers/auth.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserSync, UserResponse
from app.services.firebase import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync", response_model=UserResponse)
async def sync_user(
    body: UserSync,
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Upsert Firebase user into Cloud SQL. Call once after every login."""
    result = await db.execute(select(User).where(User.firebase_uid == body.firebase_uid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            firebase_uid=body.firebase_uid,
            email=body.email,
            display_name=body.display_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return UserResponse(user_id=user.firebase_uid, email=user.email, role=user.role)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/routers/auth.py
git commit -m "feat: add POST /auth/sync endpoint"
```

---

## Task 9: Classify Router

**Files:**
- Create: `backend/app/routers/classify.py`

- [ ] **Step 1: Create `backend/app/routers/classify.py`**

```python
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.classify import ClassifyResponse, Metrics
from app.services.firebase import verify_token
from app.services.model import run_inference
from app.data.species_data import get_species_info

router = APIRouter(tags=["classify"])


@router.post("/classify", response_model=ClassifyResponse)
async def classify_image(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> ClassifyResponse:
    image_bytes = await file.read()
    inference = run_inference(image_bytes)
    species = get_species_info(inference["predicted_class"])

    return ClassifyResponse(
        especie=species["especie"],
        nombre_cientifico=species["nombre_cientifico"],
        confianza=inference["confidence"],
        descripcion=species["descripcion"],
        datos_curiosos=species["datos_curiosos"],
        metrics=Metrics(
            latency_ms=inference["latency_ms"],
            ram_mb=inference["ram_mb"],
            cpu_percent=inference["cpu_percent"],
        ),
    )
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/routers/classify.py
git commit -m "feat: add POST /classify endpoint"
```

---

## Task 10: main.py + Tests

**Files:**
- Create: `backend/main.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Create `backend/main.py`**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, classify


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model at startup (skip in test mode)
    import os
    if os.getenv("TESTING") != "1":
        from app.services.model import load_model_from_gcs
        load_model_from_gcs()
    yield


app = FastAPI(title="AveVision API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classify.router)


@app.get("/health")
async def health():
    from app.services.model import is_model_loaded
    return {"status": "ok", "model_loaded": is_model_loaded()}
```

- [ ] **Step 2: Create `backend/tests/conftest.py`**

```python
import os
os.environ["TESTING"] = "1"

import pytest
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.database import get_db
from app.services.firebase import verify_token


def make_mock_session():
    session = MagicMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_session():
    return make_mock_session()


@pytest.fixture
def client_with_auth(mock_session):
    """Test client with Firebase auth and DB both overridden."""
    async def override_get_db():
        yield mock_session

    def override_verify_token():
        return {"uid": "test-uid-123", "email": "test@example.com"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[verify_token] = override_verify_token
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Test client with no auth override (tests unauthenticated paths)."""
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
```

- [ ] **Step 3: Create `backend/tests/test_health.py`**

```python
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client_no_auth):
    async with client_no_auth as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data
```

- [ ] **Step 4: Create `backend/tests/test_auth.py`**

```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_sync_user_requires_auth(client_no_auth):
    """Request with no Authorization header must return 403."""
    async with client_no_auth as client:
        response = await client.post("/auth/sync", json={
            "firebase_uid": "uid-123",
            "email": "test@example.com",
        })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sync_user_creates_user(client_with_auth, mock_session):
    """Valid token + new user → 200 with user data."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    async def set_role(user):
        user.role = "user"

    mock_session.refresh.side_effect = set_role

    async with client_with_auth as client:
        response = await client.post(
            "/auth/sync",
            json={"firebase_uid": "test-uid-123", "email": "test@example.com"},
            headers={"Authorization": "Bearer fake-token"},
        )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

- [ ] **Step 5: Add `pytest.ini` for asyncio mode**

Create `backend/pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
```

- [ ] **Step 6: Run all backend tests**

```bash
cd backend && source venv/bin/activate
pytest tests/ -v
```

Expected: all tests PASS (health, auth, db, firebase, model).

- [ ] **Step 7: Start dev server and verify `/health`**

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000/health`. Expected: `{"status":"ok","model_loaded":false}` (model_loaded is false because no GCS in local dev).

- [ ] **Step 8: Commit**

```bash
git add backend/main.py backend/tests/ backend/pytest.ini
git commit -m "feat: add FastAPI main app with CORS, lifespan, and backend tests"
```

---

## Task 11: Frontend Firebase Setup

**Files:**
- Modify: `package.json` (add firebase)
- Create: `src/services/firebase.js`
- Create: `.env.local` (gitignored)

- [ ] **Step 1: Install Firebase client SDK**

```bash
cd /Users/mymac/Desktop/Ing-sistemas/2026-1/REDES-NEURONALES/reconocimiento-aves
npm install firebase
```

Expected: firebase added to `node_modules`.

- [ ] **Step 2: Add `.env.local` to `.gitignore`**

Verify `.gitignore` already contains `.env.local` (Vite's default gitignore includes it). If not, add it:

```bash
echo ".env.local" >> .gitignore
```

- [ ] **Step 3: Create `.env.local` with Firebase config**

```
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_API_URL=http://localhost:8000
```

Get these values from the Firebase console → Project Settings → Web app config.

- [ ] **Step 4: Create `src/services/firebase.js`**

```js
import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()
```

- [ ] **Step 5: Verify Vite compiles**

```bash
npm run dev
```

Expected: dev server starts without errors. Stop server.

- [ ] **Step 6: Commit**

```bash
git add src/services/firebase.js .gitignore
git commit -m "feat: add Firebase client SDK setup"
```

---

## Task 12: Frontend API Service + Auth Hook

**Files:**
- Create: `src/services/api.js`
- Create: `src/hooks/useAuth.js`

- [ ] **Step 1: Create `src/services/api.js`**

```js
import { auth } from './firebase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getToken() {
  const user = auth.currentUser
  if (!user) throw new Error('No autenticado')
  return user.getIdToken()
}

export async function syncUser() {
  const user = auth.currentUser
  const token = await getToken()
  const res = await fetch(`${API_URL}/auth/sync`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      firebase_uid: user.uid,
      email: user.email,
      display_name: user.displayName ?? null,
    }),
  })
  if (!res.ok) throw new Error('Error al sincronizar usuario')
  return res.json()
}

export async function classify(file) {
  const token = await getToken()
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_URL}/classify`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  })
  if (!res.ok) throw new Error('Error al clasificar la imagen')
  return res.json()
}
```

- [ ] **Step 2: Create `src/hooks/useAuth.js`**

```js
import { useState, useEffect } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../services/firebase'

export function useAuth() {
  const [user, setUser] = useState(undefined) // undefined = still loading

  useEffect(() => {
    return onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser ?? null) // null = definitely not logged in
    })
  }, [])

  return { user, loading: user === undefined }
}
```

- [ ] **Step 3: Verify Vite compiles**

```bash
npm run dev
```

Expected: no errors. Stop server.

- [ ] **Step 4: Commit**

```bash
git add src/services/api.js src/hooks/useAuth.js
git commit -m "feat: add API service and useAuth hook"
```

---

## Task 13: Login Page

**Files:**
- Create: `src/pages/LoginPage.jsx`

- [ ] **Step 1: Create `src/pages/LoginPage.jsx`**

```jsx
import { useState } from 'react'
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
} from 'firebase/auth'
import { auth, googleProvider } from '../services/firebase'
import { syncUser } from '../services/api'
import BlackbirdIcon from '../assets/BlackbirdIcon'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleEmailAuth(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (isRegister) {
        await createUserWithEmailAndPassword(auth, email, password)
      } else {
        await signInWithEmailAndPassword(auth, email, password)
      }
      await syncUser()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogle() {
    setError(null)
    setLoading(true)
    try {
      await signInWithPopup(auth, googleProvider)
      await syncUser()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center justify-center px-4">
      <div className="animate-bob inline-block text-forest mb-4">
        <BlackbirdIcon className="w-16 h-16" />
      </div>
      <h1 className="text-4xl font-bold text-forest mb-1">AveVision</h1>
      <p className="text-muted text-sm mb-8">Identificación Automática de Aves</p>

      <div className="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm flex flex-col gap-4">
        <form onSubmit={handleEmailAuth} className="flex flex-col gap-3">
          <input
            type="email"
            placeholder="Correo electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-primary focus:outline-none focus:border-forest"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-primary focus:outline-none focus:border-forest"
          />
          {error && <p className="text-red-500 text-xs leading-snug">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="bg-forest text-white rounded-xl py-2.5 font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? 'Cargando...' : isRegister ? 'Registrarse' : 'Iniciar sesión'}
          </button>
        </form>

        <button
          type="button"
          onClick={() => setIsRegister(!isRegister)}
          className="text-muted text-xs text-center hover:text-forest transition-colors"
        >
          {isRegister ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate'}
        </button>

        <div className="flex items-center gap-2">
          <div className="flex-1 h-px bg-gray-100" />
          <span className="text-muted text-xs">o</span>
          <div className="flex-1 h-px bg-gray-100" />
        </div>

        <button
          type="button"
          onClick={handleGoogle}
          disabled={loading}
          className="border-2 border-coffee text-coffee rounded-xl py-2.5 font-semibold text-sm hover:bg-coffee/5 transition-colors disabled:opacity-50"
        >
          Continuar con Google
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify Vite compiles**

```bash
npm run dev
```

Expected: no errors. Stop server.

- [ ] **Step 3: Commit**

```bash
git add src/pages/LoginPage.jsx
git commit -m "feat: add LoginPage with email/password and Google Sign-In"
```

---

## Task 14: Wire Frontend to Real API

**Files:**
- Modify: `src/App.jsx`
- Modify: `src/components/Header.jsx`

- [ ] **Step 1: Replace `src/App.jsx`**

```jsx
import { useState, useRef } from 'react'
import { signOut } from 'firebase/auth'
import { auth } from './services/firebase'
import { useAuth } from './hooks/useAuth'
import { classify } from './services/api'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import LoadingView from './components/LoadingView'
import ResultCard from './components/ResultCard'
import Footer from './components/Footer'
import LoginPage from './pages/LoginPage'
import BlackbirdIcon from './assets/BlackbirdIcon'

export default function App() {
  const { user, loading } = useAuth()
  const [phase, setPhase] = useState('idle')
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  async function handleUpload(file) {
    setPreview(URL.createObjectURL(file))
    setPhase('loading')
    setError(null)
    try {
      const data = await classify(file)
      setResult(data)
      setPhase('result')
    } catch {
      setError('Error al clasificar la imagen. Intenta de nuevo.')
      if (preview) URL.revokeObjectURL(preview)
      setPreview(null)
      setPhase('idle')
    }
  }

  function handleReset() {
    clearTimeout(timerRef.current)
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setResult(null)
    setError(null)
    setPhase('idle')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="animate-bob text-forest">
          <BlackbirdIcon className="w-12 h-12" />
        </div>
      </div>
    )
  }

  if (!user) return <LoginPage />

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center px-4 py-8">
      <Header onSignOut={() => signOut(auth)} />
      <main className="w-full max-w-2xl mt-8 flex-1">
        {error && (
          <p className="text-red-500 text-sm text-center mb-4">{error}</p>
        )}
        {phase === 'idle' && <UploadZone onUpload={handleUpload} />}
        {phase === 'loading' && <LoadingView />}
        {phase === 'result' && result && (
          <ResultCard result={result} preview={preview} onReset={handleReset} />
        )}
      </main>
      <Footer />
    </div>
  )
}
```

- [ ] **Step 2: Update `src/components/Header.jsx` — add optional sign-out button**

```jsx
import BlackbirdIcon from '../assets/BlackbirdIcon'

const BADGES = ['CNN', 'CLASIFICACIÓN', 'DEEP LEARNING', 'UNIAGUSTINIANA']

export default function Header({ onSignOut }) {
  return (
    <header className="text-center w-full max-w-2xl relative">
      {onSignOut && (
        <button
          type="button"
          onClick={onSignOut}
          className="absolute right-0 top-0 text-xs text-muted hover:text-coffee transition-colors"
        >
          Salir
        </button>
      )}
      <div className="animate-bob inline-block text-forest">
        <BlackbirdIcon className="w-16 h-16 mx-auto" />
      </div>
      <h1 className="text-5xl font-bold text-forest mt-3 tracking-tight">AveVision</h1>
      <p className="text-muted mt-2 text-sm max-w-md mx-auto leading-relaxed">
        Identificación Automática de Aves mediante Aprendizaje Profundo
      </p>
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {BADGES.map((badge) => (
          <span
            key={badge}
            className="px-3 py-1 text-xs font-semibold border border-coffee text-coffee rounded-full"
          >
            {badge}
          </span>
        ))}
      </div>
    </header>
  )
}
```

- [ ] **Step 3: Verify Vite compiles without errors**

```bash
npm run dev
```

Expected: dev server starts. Opening `http://localhost:5173` shows LoginPage (since Firebase is not configured yet or user is not logged in).

- [ ] **Step 4: End-to-end test (requires Firebase + backend running)**

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173`
4. Register with email/password → redirected to main app
5. Upload any image → loading animation → result card with mock species data
6. Click "Salir" → redirected back to login page

- [ ] **Step 5: Commit**

```bash
git add src/App.jsx src/components/Header.jsx
git commit -m "feat: wire frontend to real FastAPI backend with Firebase auth"
```

---

## Verification Checklist

| Check | Command / Action | Expected |
|---|---|---|
| Backend tests pass | `cd backend && pytest tests/ -v` | All green |
| Dev server starts | `uvicorn main:app --reload` | "Application startup complete" |
| Health endpoint | `GET http://localhost:8000/health` | `{"status":"ok","model_loaded":false}` |
| OpenAPI docs | `http://localhost:8000/docs` | 3 endpoints listed |
| DB tables exist | `psql avevision -c "\dt"` | users, requests |
| Frontend compiles | `npm run dev` | No errors at localhost:5173 |
| Login page shows | Open localhost:5173 (logged out) | Login form + Google button |
| Auth redirect | Login → main page | Upload zone visible |
| Sign out | Click "Salir" | Back to login page |
| Full classify flow | Login → upload image → wait | ResultCard with species + metrics |
