"""Tests for configuration system."""

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
    """Test database configuration."""

    def test_connection_string_generation(self):
        """Test PostgreSQL connection string is generated correctly."""
        db = DatabaseSettings(
            user="testuser",
            password="testpass",  # noqa: S106
            host="testhost",
            name="testdb",
        )
        assert (
            db.connection_string
            == "postgresql://testuser:testpass@testhost:5432/testdb"
        )

    def test_custom_port(self):
        """Test custom database port."""
        db = DatabaseSettings(port=5433)
        assert db.port == 5433


class TestEmailSettings:
    """Test email notification configuration."""

    def test_email_validation(self):
        """Test email address validation."""
        # Valid email
        email = EmailSettings(
            from_address="test@example.com", to_address="recipient@example.com"
        )
        assert str(email.from_address) == "test@example.com"

        # Invalid email should raise validation error
        with pytest.raises(ValidationError):
            EmailSettings(from_address="invalid-email")

    def test_disabled_email(self):
        """Test email can be disabled."""
        email = EmailSettings(enabled=False)
        assert email.enabled is False


class TestSchedulerSettings:
    """Test scheduler configuration."""

    def test_default_interval(self):
        """Test default scheduler runs every 4 hours."""
        scheduler = SchedulerSettings()
        assert scheduler.interval_hours == 4

    def test_custom_interval(self):
        """Test custom scheduler interval."""
        scheduler = SchedulerSettings(interval_hours=2)
        assert scheduler.interval_hours == 2

    def test_timezone(self):
        """Test scheduler timezone is Bogota."""
        scheduler = SchedulerSettings()
        assert scheduler.timezone == "America/Bogota"


class TestScrapySettings:
    """Test Scrapy-specific settings."""

    def test_bot_name(self):
        """Test Scrapy bot name."""
        scrapy = ScrapySettings()
        assert scrapy.bot_name == "job_scraper"

    def test_download_delay(self):
        """Test default download delay."""
        scrapy = ScrapySettings()
        assert scrapy.download_delay == 1.0

    def test_concurrent_requests(self):
        """Test concurrent requests limit."""
        scrapy = ScrapySettings()
        assert scrapy.concurrent_requests_per_domain == 1


class TestAppSettings:
    """Test main application settings."""

    def test_project_name(self):
        """Test project name is set correctly."""
        app = AppSettings()
        assert app.project_name == "JobSearchTools"

    def test_nested_settings(self):
        """Test all nested configuration objects are initialized."""
        app = AppSettings()
        assert isinstance(app.database, DatabaseSettings)
        assert isinstance(app.email, EmailSettings)
        assert isinstance(app.scheduler, SchedulerSettings)
        assert isinstance(app.scrapy, ScrapySettings)

    def test_directory_creation(self):
        """Test required directories are created on initialization."""
        app = AppSettings()
        assert app.logs_dir.exists()
        assert app.data_dir.exists()
        assert app.cache_dir.exists()

    def test_environment_override(self, monkeypatch):
        """Test environment variables override defaults."""
        monkeypatch.setenv("DB_HOST", "custom-host")
        monkeypatch.setenv("SCHEDULER_INTERVAL_HOURS", "2")

        app = AppSettings()
        assert app.database.host == "custom-host"
        assert app.scheduler.interval_hours == 2
