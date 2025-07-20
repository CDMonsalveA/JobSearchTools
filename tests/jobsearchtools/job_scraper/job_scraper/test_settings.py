import jobsearchtools.job_scraper.job_scraper.settings as settings
from jobsearchtools.config.config import config


def test_bot_name_exists():
    assert hasattr(settings, "BOT_NAME")


def test_bot_name_config():
    expected = config.get("scrapy", {}).get("bot_name", "job_scraper")
    assert expected == settings.BOT_NAME


def test_spider_modules_exists():
    assert hasattr(settings, "SPIDER_MODULES")


def test_newspider_module_exists():
    assert hasattr(settings, "NEWSPIDER_MODULE")


def test_robotstxt_obey_exists():
    assert hasattr(settings, "ROBOTSTXT_OBEY")


def test_feed_export_encoding_exists():
    assert hasattr(settings, "FEED_EXPORT_ENCODING")


def test_concurrent_requests_per_domain_exists():
    assert hasattr(settings, "CONCURRENT_REQUESTS_PER_DOMAIN")


def test_download_delay_exists():
    assert hasattr(settings, "DOWNLOAD_DELAY")
