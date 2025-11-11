"""
Scheduler service for running spiders at regular intervals.

Uses APScheduler to run all configured spiders every N hours.
Supports graceful shutdown and error handling.
"""

import contextlib
import logging
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scrapy.crawler import CrawlerProcess

from jobsearchtools.config.settings import settings

logger = logging.getLogger(__name__)


class SpiderScheduler:
    """
    Scheduler for running Scrapy spiders at regular intervals.

    Uses APScheduler to trigger spider runs and monitors execution.
    """

    def __init__(self):
        """Initialize the scheduler with configuration."""
        self.scheduler = BlockingScheduler(timezone=settings.scheduler.timezone)
        self.spider_names = self._discover_spiders()
        logger.info(f"Discovered {len(self.spider_names)} spiders: {self.spider_names}")

    def _discover_spiders(self) -> list[str]:
        """
        Discover all available spiders in the project.

        Returns:
            List of spider names.
        """
        # Import spider modules to register them
        try:
            # Import static spiders
            from jobsearchtools.job_scraper.job_scraper.spiders.static import (  # noqa: F401
                avianca,
                bancolombia,
                citi,
                ecopetrol,
                mastercard,
                nequi,
                scotiabank,
                sura,
            )

            spiders = [
                "avianca",
                "bancolombia",
                "citi",
                "ecopetrol",
                "mastercard",
                "nequi",
                "scotiabank",
                "sura",
            ]

            # Import dynamic spiders (Playwright)
            with contextlib.suppress(ImportError):
                from jobsearchtools.job_scraper.job_scraper.spiders.dynamic import (  # noqa: F401
                    bbva,
                    visa,
                )

                spiders.extend(["bbva", "visa"])

            return spiders
        except ImportError as e:
            logger.error(f"Failed to discover spiders: {e}")
            return []

    def run_spiders(self):
        """
        Run all discovered spiders.

        This method is called by the scheduler at regular intervals.
        """
        if not self.spider_names:
            logger.warning("No spiders configured to run")
            return

        logger.info(f"Starting spider run for {len(self.spider_names)} spider(s)")

        try:
            # Get Scrapy settings with the correct module
            from scrapy.settings import Settings

            scrapy_settings = Settings()
            scrapy_settings.setmodule(
                "jobsearchtools.job_scraper.job_scraper.settings", priority="project"
            )

            # Create CrawlerProcess
            process = CrawlerProcess(scrapy_settings)

            # Add all spiders to the process
            for spider_name in self.spider_names:
                logger.info(f"Scheduling spider: {spider_name}")
                process.crawl(spider_name)

            # Start the crawling process (blocking)
            process.start()

            logger.info("Spider run completed successfully")

        except Exception as e:
            logger.error(f"Error during spider run: {e}", exc_info=True)

    def start(self):
        """
        Start the scheduler.

        Schedules spider runs at configured intervals and starts the scheduler.
        """
        if not settings.scheduler.enabled:
            logger.info("Scheduler is disabled in configuration")
            return

        interval_hours = settings.scheduler.interval_hours
        logger.info(f"Starting scheduler with {interval_hours} hour interval")

        # Schedule the spider run job
        self.scheduler.add_job(
            self.run_spiders,
            trigger=IntervalTrigger(hours=interval_hours),
            id="spider_run_job",
            name="Run all spiders",
            replace_existing=True,
            max_instances=settings.scheduler.max_instances,
        )

        # Run immediately on startup
        logger.info("Running spiders immediately on startup")
        self.run_spiders()

        # Start the scheduler
        try:
            logger.info("Scheduler started. Press Ctrl+C to exit.")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown the scheduler."""
        logger.info("Shutting down scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down successfully")


def main():
    """Main entry point for the scheduler service."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.logs_dir / "scheduler.log", mode="a"),
        ],
    )

    # Create and start scheduler
    scheduler = SpiderScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
