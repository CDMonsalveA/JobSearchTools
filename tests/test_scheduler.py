"""Tests for SpiderScheduler service."""

from unittest.mock import MagicMock, patch

from jobsearchtools.scheduler import SpiderScheduler


class TestSpiderScheduler:
    """Test cases for SpiderScheduler."""

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    def test_initialization(self, mock_scheduler_class):
        """Test scheduler initializes with correct configuration."""
        mock_scheduler_instance = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler_instance

        scheduler = SpiderScheduler()

        assert scheduler.scheduler == mock_scheduler_instance
        mock_scheduler_class.assert_called_once()

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    def test_discovers_all_spiders(self, mock_scheduler_class):
        """Test scheduler discovers all configured spiders."""
        scheduler = SpiderScheduler()

        # Should discover 10 spiders: 8 static + 2 dynamic
        assert len(scheduler.spider_names) == 10
        assert "mastercard" in scheduler.spider_names
        assert "avianca" in scheduler.spider_names
        assert "bbva" in scheduler.spider_names
        assert "visa" in scheduler.spider_names

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    def test_spider_names_are_unique(self, mock_scheduler_class):
        """Test no duplicate spider names."""
        scheduler = SpiderScheduler()

        assert len(scheduler.spider_names) == len(set(scheduler.spider_names))

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    @patch("jobsearchtools.scheduler.CrawlerProcess")
    def test_run_spiders_creates_crawler_process(
        self, mock_crawler_class, mock_scheduler_class
    ):
        """Test run_spiders creates and starts CrawlerProcess."""
        mock_process = MagicMock()
        mock_crawler_class.return_value = mock_process

        scheduler = SpiderScheduler()
        scheduler.run_spiders()

        mock_crawler_class.assert_called_once()
        mock_process.start.assert_called_once()

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    @patch("jobsearchtools.scheduler.CrawlerProcess")
    def test_run_spiders_crawls_all_discovered_spiders(
        self, mock_crawler_class, mock_scheduler_class
    ):
        """Test all discovered spiders are added to crawler."""
        mock_process = MagicMock()
        mock_crawler_class.return_value = mock_process

        scheduler = SpiderScheduler()
        spider_count = len(scheduler.spider_names)
        scheduler.run_spiders()

        # Each spider should be crawled
        assert mock_process.crawl.call_count == spider_count

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    def test_shutdown_stops_scheduler(self, mock_scheduler_class):
        """Test shutdown() stops scheduler gracefully."""
        mock_scheduler_instance = MagicMock()
        mock_scheduler_instance.running = True
        mock_scheduler_class.return_value = mock_scheduler_instance

        scheduler = SpiderScheduler()
        scheduler.shutdown()

        mock_scheduler_instance.shutdown.assert_called_once_with(wait=True)

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    @patch("jobsearchtools.scheduler.CrawlerProcess")
    def test_handles_crawler_errors_gracefully(
        self, mock_crawler_class, mock_scheduler_class
    ):
        """Test scheduler handles CrawlerProcess errors."""
        mock_process = MagicMock()
        mock_process.start.side_effect = Exception("Crawler error")
        mock_crawler_class.return_value = mock_process

        scheduler = SpiderScheduler()

        # Should not raise exception, just log it
        scheduler.run_spiders()  # Should handle error gracefully

    @patch("jobsearchtools.scheduler.BlockingScheduler")
    def test_scheduler_uses_configured_timezone(self, mock_scheduler_class):
        """Test scheduler uses timezone from settings."""
        from jobsearchtools.config.settings import settings

        SpiderScheduler()

        # Verify scheduler was initialized with correct timezone
        call_kwargs = mock_scheduler_class.call_args[1]
        assert call_kwargs["timezone"] == settings.scheduler.timezone
