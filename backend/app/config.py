import os


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DATABASE_URL: str = _normalize_database_url(
        os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/docproc",
        )
    )
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/docproc_uploads")
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
    CORS_ORIGINS: list[str] = _parse_origins(os.getenv("CORS_ORIGINS"))
    CORS_ALLOW_CREDENTIALS: bool = _parse_bool(
        os.getenv("CORS_ALLOW_CREDENTIALS"), False
    )

    def validate(self) -> None:
        if self.APP_ENV.lower() not in {"development", "test"} and not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY must be set in non-development environments")


settings = Settings()
settings.validate()
