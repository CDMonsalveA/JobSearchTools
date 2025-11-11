# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from scrapy import Spider
from scrapy.exceptions import NotConfigured

from jobsearchtools.config.settings import settings

logger = logging.getLogger(__name__)


class PostgreSQLPipeline:
    """
    PostgreSQL pipeline with connection pooling and duplicate detection.

    Features:
    - Connection pooling for efficient database access
    - Automatic duplicate detection by job_id
    - Tracks new job insertions for notifications
    - Robust error handling with rollback
    - Schema auto-creation with indexes
    """

    def __init__(self):
        """Initialize the PostgreSQL connection pool."""
        if not settings.database.password:
            raise NotConfigured(
                "PostgreSQL password not configured. "
                "Set DB_PASSWORD environment variable."
            )

        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=settings.database.pool_size,
                host=settings.database.host,
                port=settings.database.port,
                database=settings.database.name,
                user=settings.database.user,
                password=settings.database.password,
            )
            logger.info("PostgreSQL connection pool created successfully")
            self.new_jobs_count = 0
            self.new_jobs = []  # Store new jobs for email notification
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise NotConfigured(f"PostgreSQL connection failed: {e}") from e

    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for database connections.

        Yields:
            Connection object from the pool.
        """
        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def open_spider(self, spider: Spider) -> None:
        """
        Called when spider opens. Creates tables and indexes if needed.

        Args:
            spider: The spider instance.
        """
        logger.info(f"Opening PostgreSQL pipeline for spider: {spider.name}")
        self.new_jobs_count = 0
        self.new_jobs = []
        self._create_schema()

    def _create_schema(self) -> None:
        """Create database schema with tables and indexes."""
        with self.get_connection() as conn, conn.cursor() as cursor:
            # Create jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    company VARCHAR(255) NOT NULL,
                    location VARCHAR(255),
                    description TEXT,
                    salary VARCHAR(255),
                    url TEXT NOT NULL,
                    date_posted TIMESTAMP,
                    date_extracted TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    was_opened BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_job_id
                ON jobs(job_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_company
                ON jobs(company)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_date_extracted
                ON jobs(date_extracted DESC)
            """)

            # Create spider_runs table for health monitoring
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spider_runs (
                    id SERIAL PRIMARY KEY,
                    spider_name VARCHAR(255) NOT NULL,
                    run_start TIMESTAMP NOT NULL,
                    run_end TIMESTAMP,
                    status VARCHAR(50) NOT NULL,
                    items_scraped INTEGER DEFAULT 0,
                    items_saved INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spider_runs_spider_name
                ON spider_runs(spider_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spider_runs_run_start
                ON spider_runs(run_start DESC)
            """)

            conn.commit()
            logger.info("Database schema created/verified successfully")

    def process_item(
        self, item: dict[str, Any], spider: Spider
    ) -> dict[str, Any] | None:
        """
        Process scraped item and store in database if not duplicate.

        Args:
            item: Scraped item dictionary.
            spider: Spider instance.

        Returns:
            The processed item or None if duplicate.
        """
        job_id = item.get("job_id")
        if not job_id:
            logger.warning("Item missing job_id, skipping")
            return None

        try:
            with (
                self.get_connection() as conn,
                conn.cursor(cursor_factory=RealDictCursor) as cursor,
            ):
                # Check for duplicate
                cursor.execute("SELECT id FROM jobs WHERE job_id = %s", (job_id,))
                if cursor.fetchone():
                    spider.logger.debug(f"Duplicate job skipped: {job_id}")
                    return None

                # Parse date_posted if it's a string
                date_posted = item.get("date_posted")
                if isinstance(date_posted, str):
                    try:
                        date_posted = datetime.fromisoformat(date_posted)
                    except (ValueError, TypeError):
                        date_posted = None

                # Parse date_extracted
                date_extracted = item.get("date_extracted")
                if isinstance(date_extracted, str):
                    try:
                        date_extracted = datetime.fromisoformat(date_extracted)
                    except (ValueError, TypeError):
                        date_extracted = datetime.utcnow()
                elif not date_extracted:
                    date_extracted = datetime.utcnow()

                # Insert new job
                cursor.execute(
                    """
                    INSERT INTO jobs (
                        job_id, title, company, location, description,
                        salary, url, date_posted, date_extracted, was_opened
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        job_id,
                        item.get("title"),
                        item.get("company"),
                        item.get("location"),
                        item.get("description"),
                        item.get("salary"),
                        item.get("url"),
                        date_posted,
                        date_extracted,
                        item.get("was_opened", False),
                    ),
                )
                conn.commit()
                self.new_jobs_count += 1
                self.new_jobs.append(item)
                spider.logger.info(f"New job stored: {job_id}")
                return item

        except Exception as e:
            logger.error(f"Error processing item {job_id}: {e}")
            spider.logger.error(f"Database error for {job_id}: {e}")
            return None

    def close_spider(self, spider: Spider) -> None:
        """
        Called when spider closes. Logs statistics and closes connections.

        Args:
            spider: The spider instance.
        """
        logger.info(
            f"Closing PostgreSQL pipeline for {spider.name}. "
            f"New jobs: {self.new_jobs_count}"
        )

        # Store the new jobs list in spider stats for email notification
        if hasattr(spider, "crawler") and spider.crawler.stats:
            spider.crawler.stats.set_value("new_jobs", self.new_jobs)
            spider.crawler.stats.set_value("new_jobs_count", self.new_jobs_count)

        # Close all connections in the pool
        if hasattr(self, "connection_pool"):
            self.connection_pool.closeall()
            logger.info("PostgreSQL connection pool closed")
