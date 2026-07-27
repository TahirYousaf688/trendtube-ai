"""Application configuration with all environment variables."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    # App
    app_name: str = os.getenv("APP_NAME", "TrendTube AI")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    env: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    allowed_hosts: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_HOSTS", "*").split(","))

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/trendtube",
    )
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_cache_ttl: int = int(os.getenv("REDIS_CACHE_TTL", "300"))

    # Celery / RabbitMQ
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "development-secret-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # OAuth / Google
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    google_redirect_uri: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

    # YouTube API
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    youtube_client_id: str = os.getenv("YOUTUBE_CLIENT_ID", "")
    youtube_client_secret: str = os.getenv("YOUTUBE_CLIENT_SECRET", "")

    # OpenAI / AI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ElevenLabs
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")

    # Azure Speech
    azure_speech_key: str = os.getenv("AZURE_SPEECH_KEY", "")
    azure_speech_region: str = os.getenv("AZURE_SPEECH_REGION", "eastus")

    # AWS
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "trendtube-assets")

    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_price_monthly: str = os.getenv("STRIPE_PRICE_MONTHLY", "")
    stripe_price_yearly: str = os.getenv("STRIPE_PRICE_YEARLY", "")

    # PayPal
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")

    # ChromaDB / Pinecone
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "trendtube")

    # CORS
    cors_origins: List[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    )

    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Storage
    storage_provider: str = os.getenv("STORAGE_PROVIDER", "s3")  # s3 or local
    local_storage_path: str = os.getenv("LOCAL_STORAGE_PATH", "./storage")

    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

