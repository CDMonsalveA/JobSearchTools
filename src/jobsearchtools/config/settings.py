"""
Enhanced configuration system using Pydantic Settings for environment management.

This module provides type-safe configuration management with support for:
- Environment variables (.env file)
- PostgreSQL database configuration
- Email notification settings
- Scheduler configuration
- Scrapy settings integration
"""

import logging
from pathlib import Path
from typing import Any

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""

    model_config = SettingsConfigDict(env_prefix="DB_")

    type: str = Field(default="postgresql", description="Database type")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="jobsearchtools", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="", description="Database password")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max pool overflow")

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class EmailSettings(BaseSettings):
    """Email notification configuration."""

    model_config = SettingsConfigDict(env_prefix="EMAIL_")

    enabled: bool = Field(default=True, description="Enable email notifications")
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    from_address: EmailStr = Field(
        default="noreply@jobsearchtools.com", description="From email address"
    )
    to_address: EmailStr = Field(
        default="recipient@example.com", description="Recipient email address"
    )
    use_tls: bool = Field(default=True, description="Use TLS for SMTP")


class SchedulerSettings(BaseSettings):
    """Scheduler configuration."""

    model_config = SettingsConfigDict(env_prefix="SCHEDULER_")

    enabled: bool = Field(default=True, description="Enable scheduler")
    interval_hours: int = Field(
        default=4, description="Interval between spider runs (hours)"
    )
    timezone: str = Field(default="America/Bogota", description="Scheduler timezone")
    max_instances: int = Field(default=1, description="Max concurrent spider instances")


class ScrapySettings(BaseSettings):
    """Scrapy-specific configuration."""

    model_config = SettingsConfigDict(env_prefix="SCRAPY_")

    bot_name: str = Field(default="job_scraper", description="Scrapy bot name")
    concurrent_requests_per_domain: int = Field(
        default=1, description="Concurrent requests per domain"
    )
    download_delay: float = Field(default=1.0, description="Download delay in seconds")
    robotstxt_obey: bool = Field(default=True, description="Obey robots.txt")
    log_level: str = Field(default="INFO", description="Scrapy log level")


class AppSettings(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Application metadata
    project_name: str = Field(default="JobSearchTools", description="Project name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")

    # Directories
    base_dir: Path = Field(
        default=Path("src/jobsearchtools"), description="Base directory"
    )
    logs_dir: Path = Field(default=Path("logs"), description="Logs directory")
    data_dir: Path = Field(default=Path("data"), description="Data directory")
    cache_dir: Path = Field(default=Path("cache"), description="Cache directory")

    # Sub-configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    scrapy: ScrapySettings = Field(default_factory=ScrapySettings)

    @field_validator("base_dir", "logs_dir", "data_dir", "cache_dir", mode="before")
    @classmethod
    def ensure_path(cls, v: Any) -> Path:
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    def model_post_init(self, __context: Any) -> None:
        """Create necessary directories after initialization."""
        for dir_path in [self.logs_dir, self.data_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Configuration initialized: {self.model_dump()}")


# Global settings instance
settings = AppSettings()
