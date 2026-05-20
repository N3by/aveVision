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

    model_config = {"env_file": ".env", "protected_namespaces": ("settings_",)}


settings = Settings()
