"""Tests for Scrapy settings configuration."""

from jobsearchtools.job_scraper.job_scraper import settings


class TestScrapySettings:
    """Test Scrapy settings are correctly configured."""

    def test_bot_name(self):
        """Test bot name is configured."""
        assert hasattr(settings, "BOT_NAME")
        assert settings.BOT_NAME == "job_scraper"

    def test_spider_modules(self):
        """Test spider modules are configured."""
        assert hasattr(settings, "SPIDER_MODULES")
        assert isinstance(settings.SPIDER_MODULES, list)
        assert len(settings.SPIDER_MODULES) > 0

    def test_robotstxt_obey(self):
        """Test robots.txt setting exists."""
        assert hasattr(settings, "ROBOTSTXT_OBEY")
        assert isinstance(settings.ROBOTSTXT_OBEY, bool)

    def test_download_delay(self):
        """Test download delay is configured."""
        assert hasattr(settings, "DOWNLOAD_DELAY")
        assert settings.DOWNLOAD_DELAY >= 1.0

    def test_concurrent_requests(self):
        """Test concurrent requests per domain is limited."""
        assert hasattr(settings, "CONCURRENT_REQUESTS_PER_DOMAIN")
        assert settings.CONCURRENT_REQUESTS_PER_DOMAIN >= 1

    def test_user_agent_middleware(self):
        """Test random user agent middleware is configured."""
        assert hasattr(settings, "DOWNLOADER_MIDDLEWARES")
        middlewares = settings.DOWNLOADER_MIDDLEWARES
        assert any("SetRandomUserAgentMiddleware" in key for key in middlewares)

    def test_pipeline_configured(self):
        """Test PostgreSQL pipeline is configured."""
        assert hasattr(settings, "ITEM_PIPELINES")
        pipelines = settings.ITEM_PIPELINES
        assert any("PostgreSQLPipeline" in key for key in pipelines)

    def test_extensions_configured(self):
        """Test extensions are configured."""
        assert hasattr(settings, "EXTENSIONS")
        extensions = settings.EXTENSIONS
        assert any("EmailNotificationExtension" in key for key in extensions)
        assert any("SpiderHealthMonitorExtension" in key for key in extensions)
