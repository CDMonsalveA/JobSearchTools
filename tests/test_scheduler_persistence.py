"""
Unit tests for the persistent scheduler with state tracking.

Tests the new functionality that ensures spiders run at least every N hours
even after container restarts or PC shutdowns.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from jobsearchtools.scheduler import SpiderScheduler


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    conn = MagicMock()
    conn.closed = False
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


@pytest.fixture
def scheduler():
    """Create a SpiderScheduler instance with mocked dependencies."""
    with patch("jobsearchtools.scheduler.settings") as mock_settings:
        mock_settings.scheduler.enabled = True
        mock_settings.scheduler.interval_hours = 4
        mock_settings.scheduler.timezone = "America/Bogota"
        mock_settings.scheduler.max_instances = 1

        with patch.object(
            SpiderScheduler, "_discover_spiders", return_value=["test_spider"]
        ):
            scheduler = SpiderScheduler()
            yield scheduler


class TestSchedulerStatePersistence:
    """Test suite for scheduler state persistence functionality."""

    def test_should_run_now_no_previous_run(self, scheduler, mock_db_connection):
        """Test that scheduler runs immediately when no previous run exists."""
        conn, cursor = mock_db_connection
        cursor.fetchone.return_value = None

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            assert scheduler._should_run_now() is True

    def test_should_run_now_time_threshold_exceeded(
        self, scheduler, mock_db_connection
    ):
        """Test that scheduler runs when time threshold is exceeded."""
        conn, cursor = mock_db_connection
        # Simulate last run was 5 hours ago (threshold is 4 hours)
        last_run = datetime.now(UTC) - timedelta(hours=5)
        cursor.fetchone.return_value = (last_run,)

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            assert scheduler._should_run_now() is True

    def test_should_run_now_time_threshold_not_met(self, scheduler, mock_db_connection):
        """Test that scheduler waits when time threshold is not met."""
        conn, cursor = mock_db_connection
        # Simulate last run was 2 hours ago (threshold is 4 hours)
        last_run = datetime.now(UTC) - timedelta(hours=2)
        cursor.fetchone.return_value = (last_run,)

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            assert scheduler._should_run_now() is False

    def test_should_run_now_exactly_at_threshold(self, scheduler, mock_db_connection):
        """Test that scheduler runs when exactly at time threshold."""
        conn, cursor = mock_db_connection
        # Simulate last run was exactly 4 hours ago
        last_run = datetime.now(UTC) - timedelta(hours=4)
        cursor.fetchone.return_value = (last_run,)

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            assert scheduler._should_run_now() is True

    def test_update_last_run_time_completed(self, scheduler, mock_db_connection):
        """Test updating last run time with completed status."""
        conn, cursor = mock_db_connection

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            scheduler._update_last_run_time(5, status="completed")

            # Verify INSERT was called
            cursor.execute.assert_called_once()
            call_args = cursor.execute.call_args
            assert "INSERT INTO scheduler_state" in call_args[0][0]
            assert call_args[0][1][1] == 5  # spider_count
            assert call_args[0][1][2] == "completed"  # status

            # Verify commit was called
            conn.commit.assert_called_once()

    def test_update_last_run_time_failed(self, scheduler, mock_db_connection):
        """Test updating last run time with failed status."""
        conn, cursor = mock_db_connection

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            scheduler._update_last_run_time(5, status="failed")

            call_args = cursor.execute.call_args
            assert call_args[0][1][2] == "failed"

    def test_get_last_run_time_with_timezone(self, scheduler, mock_db_connection):
        """Test getting last run time handles timezone-aware datetimes."""
        conn, cursor = mock_db_connection
        last_run = datetime.now(UTC) - timedelta(hours=3)
        cursor.fetchone.return_value = (last_run,)

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            result = scheduler._get_last_run_time()
            assert result is not None
            assert result.tzinfo is not None

    def test_get_last_run_time_without_timezone(self, scheduler, mock_db_connection):
        """Test getting last run time converts naive datetimes to UTC."""
        conn, cursor = mock_db_connection
        # Create naive datetime (no timezone)
        last_run = datetime.now() - timedelta(hours=3)
        cursor.fetchone.return_value = (last_run,)

        with patch.object(scheduler, "_get_db_connection", return_value=conn):
            result = scheduler._get_last_run_time()
            assert result is not None
            assert result.tzinfo is not None

    def test_run_spiders_updates_state_on_success(self, scheduler, mock_db_connection):
        """Test that run_spiders updates state to completed on success."""
        conn, cursor = mock_db_connection

        with (
            patch.object(scheduler, "_get_db_connection", return_value=conn),
            patch("jobsearchtools.scheduler.CrawlerProcess") as mock_process,
            patch.object(scheduler, "_update_last_run_time") as mock_update,
        ):
            mock_process.return_value.start.return_value = None
            scheduler.run_spiders()

            # Check that status was updated to running and completed
            assert mock_update.call_count == 2
            # First call: (spider_count, status='running')
            assert mock_update.call_args_list[0][1]["status"] == "running"
            # Second call: (spider_count, status='completed')
            assert mock_update.call_args_list[1][1]["status"] == "completed"

    def test_run_spiders_updates_state_on_failure(self, scheduler, mock_db_connection):
        """Test that run_spiders updates state to failed on exception."""
        conn, cursor = mock_db_connection

        with (
            patch.object(scheduler, "_get_db_connection", return_value=conn),
            patch("jobsearchtools.scheduler.CrawlerProcess") as mock_process,
            patch.object(scheduler, "_update_last_run_time") as mock_update,
        ):
            mock_process.return_value.start.side_effect = Exception("Test error")
            scheduler.run_spiders()

            # Check that status was updated to running and failed
            assert mock_update.call_count == 2
            # First call: (spider_count, status='running')
            assert mock_update.call_args_list[0][1]["status"] == "running"
            # Second call: (spider_count, status='failed')
            assert mock_update.call_args_list[1][1]["status"] == "failed"

    def test_start_runs_immediately_when_threshold_met(
        self, scheduler, mock_db_connection
    ):
        """Test that start() runs spiders immediately when time threshold is met."""
        conn, cursor = mock_db_connection

        with (
            patch.object(scheduler, "_get_db_connection", return_value=conn),
            patch.object(scheduler, "_should_run_now", return_value=True),
            patch.object(scheduler, "run_spiders") as mock_run,
            patch.object(scheduler.scheduler, "start"),
            pytest.raises(SystemExit),
        ):
            scheduler.start()
            raise SystemExit()

        # Verify spiders were run immediately
        mock_run.assert_called_once()

    def test_start_skips_immediate_run_when_threshold_not_met(
        self, scheduler, mock_db_connection
    ):
        """Test that start() skips immediate run when time threshold not met."""
        conn, cursor = mock_db_connection

        with (
            patch.object(scheduler, "_get_db_connection", return_value=conn),
            patch.object(scheduler, "_should_run_now", return_value=False),
            patch.object(scheduler, "run_spiders") as mock_run,
            patch.object(scheduler.scheduler, "start"),
            pytest.raises(SystemExit),
        ):
            scheduler.start()
            raise SystemExit()

        # Verify spiders were NOT run immediately
        mock_run.assert_not_called()

    def test_shutdown_closes_db_connection(self, scheduler):
        """Test that shutdown properly closes database connection."""
        mock_conn = MagicMock()
        mock_conn.closed = False
        scheduler.db_connection = mock_conn

        # Mock the scheduler.running property
        with patch.object(
            type(scheduler.scheduler),
            "running",
            new_callable=lambda: property(lambda self: False),
        ):
            scheduler.shutdown()

            # Verify connection was closed
            mock_conn.close.assert_called_once()

    def test_db_connection_reuse(self, scheduler, mock_db_connection):
        """Test that database connection is reused when not closed."""
        conn, cursor = mock_db_connection
        scheduler.db_connection = conn

        result = scheduler._get_db_connection()

        # Should return existing connection
        assert result is conn

    def test_db_connection_recreate_when_closed(self, scheduler):
        """Test that database connection is recreated when closed."""
        import psycopg2

        mock_closed_conn = MagicMock()
        mock_closed_conn.closed = True
        scheduler.db_connection = mock_closed_conn

        with patch.object(psycopg2, "connect") as mock_connect:
            new_conn = MagicMock()
            mock_connect.return_value = new_conn

            result = scheduler._get_db_connection()

            # Should create new connection
            mock_connect.assert_called_once()
            assert result is new_conn
