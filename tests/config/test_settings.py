"""Tests for the new Pydantic settings configuration."""

import pytest
from pydantic import ValidationError

from jobsearchtools.config.settings import (
    AppSettings,
    DatabaseSettings,
    EmailSettings,
    SchedulerSettings,
    ScrapySettings,
)


class TestDatabaseSettings:
    """Test database configuration settings."""

    def test_default_values(self):
        """Test default database settings."""
        db_settings = DatabaseSettings()
        assert db_settings.type == "postgresql"
        assert db_settings.host == "localhost"
        assert db_settings.port == 5432
        assert db_settings.name == "jobsearchtools"
        assert db_settings.user == "postgres"
        assert db_settings.pool_size == 5

    def test_connection_string_generation(self):
        """Test connection string generation."""
        db_settings = DatabaseSettings(
            user="testuser",
            password="testpass",  # noqa: S106
            host="testhost",
            name="testdb",
        )
        expected = "postgresql://testuser:testpass@testhost:5432/testdb"
        assert db_settings.connection_string == expected

    def test_custom_values(self):
        """Test custom database configuration."""
        db_settings = DatabaseSettings(
            host="customhost", port=5433, name="customdb", pool_size=10
        )
        assert db_settings.host == "customhost"
        assert db_settings.port == 5433
        assert db_settings.name == "customdb"
        assert db_settings.pool_size == 10


class TestEmailSettings:
    """Test email notification settings."""

    def test_default_values(self):
        """Test default email settings."""
        email_settings = EmailSettings()
        assert email_settings.enabled is True
        assert email_settings.smtp_host == "smtp.gmail.com"
        assert email_settings.smtp_port == 587
        assert email_settings.use_tls is True

    def test_email_validation(self):
        """Test email address validation."""
        # Valid email
        email_settings = EmailSettings(
            from_address="test@example.com", to_address="recipient@example.com"
        )
        assert str(email_settings.from_address) == "test@example.com"

        # Invalid email should raise validation error
        with pytest.raises(ValidationError):
            EmailSettings(from_address="invalid-email")


class TestSchedulerSettings:
    """Test scheduler configuration settings."""

    def test_default_values(self):
        """Test default scheduler settings."""
        scheduler_settings = SchedulerSettings()
        assert scheduler_settings.enabled is True
        assert scheduler_settings.interval_hours == 4
        assert scheduler_settings.timezone == "America/Bogota"
        assert scheduler_settings.max_instances == 1

    def test_custom_interval(self):
        """Test custom scheduler interval."""
        scheduler_settings = SchedulerSettings(interval_hours=2)
        assert scheduler_settings.interval_hours == 2


class TestScrapySettings:
    """Test Scrapy-specific settings."""

    def test_default_values(self):
        """Test Scrapy settings from environment."""
        scrapy_settings = ScrapySettings()
        assert scrapy_settings.bot_name == "job_scraper"
        assert scrapy_settings.concurrent_requests_per_domain == 1
        assert scrapy_settings.download_delay == 1.0
        # This is False in .env for testing purposes
        assert scrapy_settings.robotstxt_obey is False
        assert scrapy_settings.log_level == "INFO"


class TestAppSettings:
    """Test main application settings."""

    def test_default_values(self):
        """Test application settings from environment."""
        app_settings = AppSettings()
        assert app_settings.project_name == "JobSearchTools"
        # This is 'production' in .env
        assert app_settings.environment == "production"
        assert app_settings.debug is False

    def test_nested_settings(self):
        """Test nested configuration objects."""
        app_settings = AppSettings()
        assert isinstance(app_settings.database, DatabaseSettings)
        assert isinstance(app_settings.email, EmailSettings)
        assert isinstance(app_settings.scheduler, SchedulerSettings)
        assert isinstance(app_settings.scrapy, ScrapySettings)

    def test_directory_creation(self):
        """Test that necessary directories are created."""
        app_settings = AppSettings()
        # Directories should exist after initialization
        assert app_settings.logs_dir.exists()
        assert app_settings.data_dir.exists()
        assert app_settings.cache_dir.exists()

    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("DB_HOST", "custom-host")
        monkeypatch.setenv("DB_PORT", "5433")
        monkeypatch.setenv("SCHEDULER_INTERVAL_HOURS", "2")

        app_settings = AppSettings()
        assert app_settings.database.host == "custom-host"
        assert app_settings.database.port == 5433
        assert app_settings.scheduler.interval_hours == 2
