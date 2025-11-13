"""
Scheduler service for running spiders at regular intervals.

Uses APScheduler to run all configured spiders every N hours.
Supports graceful shutdown and error handling.
Implements persistent scheduling to handle container restarts and PC shutdowns.
"""

import contextlib
import logging
import sys
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scrapy.crawler import CrawlerProcess

from jobsearchtools.config.settings import settings

logger = logging.getLogger(__name__)


class SpiderScheduler:
    """
    Scheduler for running Scrapy spiders at regular intervals.

    Uses APScheduler to trigger spider runs and monitors execution.
    Implements persistent state tracking to ensure spiders run at least
    every N hours even after container restarts or PC shutdowns.
    """

    def __init__(self):
        """Initialize the scheduler with configuration."""
        self.scheduler = BlockingScheduler(timezone=settings.scheduler.timezone)
        self.spider_names = self._discover_spiders()
        self.db_connection = None
        logger.info(f"Discovered {len(self.spider_names)} spiders: {self.spider_names}")

    def _get_db_connection(self):
        """
        Get or create a database connection for state persistence.

        Returns:
            psycopg2 connection object.
        """
        if self.db_connection is None or self.db_connection.closed:
            import psycopg2

            self.db_connection = psycopg2.connect(
                host=settings.database.host,
                port=settings.database.port,
                dbname=settings.database.name,
                user=settings.database.user,
                password=settings.database.password,
            )
        return self.db_connection

    def _get_last_run_time(self) -> datetime | None:
        """
        Get the timestamp of the last successful spider run from database.

        Returns:
            DateTime of last run, or None if never run before.
        """
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT last_run_at
                    FROM scheduler_state
                    WHERE status = 'completed'
                    ORDER BY last_run_at DESC
                    LIMIT 1
                    """
                )
                result = cursor.fetchone()
                if result:
                    last_run = result[0]
                    # Ensure timezone-aware datetime
                    if last_run.tzinfo is None:
                        last_run = last_run.replace(tzinfo=UTC)
                    return last_run
                return None
        except Exception as e:
            logger.error(f"Failed to get last run time from database: {e}")
            return None

    def _update_last_run_time(self, spider_count: int, status: str = "completed"):
        """
        Update the last run timestamp in the database.

        Args:
            spider_count: Number of spiders that were run.
            status: Status of the run (completed, failed, running).
        """
        conn = None
        try:
            conn = self._get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO scheduler_state
                    (last_run_at, spider_count, status, updated_at)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        datetime.now(UTC),
                        spider_count,
                        status,
                        datetime.now(UTC),
                    ),
                )
                conn.commit()
                logger.debug(f"Updated last run time in database with status: {status}")
        except Exception as e:
            logger.error(f"Failed to update last run time in database: {e}")
            if conn:
                conn.rollback()

    def _should_run_now(self) -> bool:
        """
        Determine if spiders should run immediately based on last run time.

        Checks if more than the configured interval has passed since the
        last successful run. This handles cases where the container was
        stopped for extended periods.

        Returns:
            True if spiders should run now, False otherwise.
        """
        last_run = self._get_last_run_time()

        if last_run is None:
            logger.info("No previous run found in database, should run immediately")
            return True

        now = datetime.now(UTC)
        time_since_last_run = now - last_run
        required_interval = timedelta(hours=settings.scheduler.interval_hours)

        logger.info(
            f"Last run was {time_since_last_run.total_seconds() / 3600:.2f} hours ago "
            f"(required: {settings.scheduler.interval_hours} hours)"
        )

        if time_since_last_run >= required_interval:
            logger.info("Time threshold exceeded, should run immediately")
            return True

        hours_remaining = (
            required_interval - time_since_last_run
        ).total_seconds() / 3600
        logger.info(
            f"Time threshold not met, will wait {hours_remaining:.2f} more hours"
        )
        return False

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
        Updates the database with run status for persistent tracking.
        """
        if not self.spider_names:
            logger.warning("No spiders configured to run")
            return

        logger.info(f"Starting spider run for {len(self.spider_names)} spider(s)")

        # Update status to running
        self._update_last_run_time(len(self.spider_names), status="running")

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

            # Update status to completed
            self._update_last_run_time(len(self.spider_names), status="completed")

        except Exception as e:
            logger.error(f"Error during spider run: {e}", exc_info=True)
            # Update status to failed
            self._update_last_run_time(len(self.spider_names), status="failed")

    def start(self):
        """
        Start the scheduler.

        Schedules spider runs at configured intervals and starts the scheduler.
        Uses persistent state to determine if spiders should run immediately
        based on time elapsed since last successful run.
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

        # Check if we should run immediately based on last run time
        if self._should_run_now():
            logger.info("Time threshold met or exceeded, running spiders immediately")
            self.run_spiders()
        else:
            logger.info(
                "Recent run detected, skipping immediate execution. "
                "Next run will occur according to schedule."
            )

        # Start the scheduler
        try:
            logger.info("Scheduler started. Press Ctrl+C to exit.")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown the scheduler and close database connections."""
        logger.info("Shutting down scheduler...")
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)

        # Close database connection
        if self.db_connection and not self.db_connection.closed:
            self.db_connection.close()
            logger.debug("Database connection closed")

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
