"""Tests for email notification system."""

from unittest.mock import MagicMock, patch

import pytest

from jobsearchtools.notifications.email_notifier import EmailNotifier


class TestEmailNotifier:
    """Test email notification functionality."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        with patch("jobsearchtools.notifications.email_notifier.settings") as mock:
            mock.email.enabled = True
            mock.email.smtp_host = "smtp.test.com"
            mock.email.smtp_port = 587
            mock.email.smtp_user = "test@test.com"
            mock.email.smtp_password = "testpass"  # noqa: S105
            mock.email.from_address = "from@test.com"
            mock.email.to_address = "to@test.com"
            mock.email.use_tls = True
            yield mock

    def test_initialization_enabled(self, mock_settings):
        """Test notifier initializes when enabled."""
        notifier = EmailNotifier()
        assert notifier.enabled is True

    def test_initialization_disabled(self, mock_settings):
        """Test notifier initializes when disabled."""
        mock_settings.email.enabled = False
        notifier = EmailNotifier()
        assert notifier.enabled is False

    def test_no_notification_when_disabled(self, mock_settings):
        """Test no email sent when notifications disabled."""
        mock_settings.email.enabled = False
        notifier = EmailNotifier()

        jobs = [{"title": "Test Job", "company": "TestCorp"}]
        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        # When disabled, returns False without sending
        assert result is False

    @patch("smtplib.SMTP")
    def test_send_notification_success(self, mock_smtp, mock_settings):
        """Test successful email notification."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = EmailNotifier()
        jobs = [
            {
                "title": "Software Engineer",
                "company": "TestCorp",
                "location": "Bogotá",
                "url": "https://example.com/job/1",
            }
        ]

        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_multiple_jobs(self, mock_smtp, mock_settings):
        """Test notification with multiple jobs."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        notifier = EmailNotifier()
        jobs = [
            {"title": "Job 1", "company": "Corp", "url": "http://example.com/1"},
            {"title": "Job 2", "company": "Corp", "url": "http://example.com/2"},
        ]

        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        assert result is True
        mock_server.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_smtp_error_handling(self, mock_smtp, mock_settings):
        """Test email handles SMTP errors gracefully."""
        mock_smtp.side_effect = Exception("SMTP Error")

        notifier = EmailNotifier()
        jobs = [{"title": "Job", "company": "Corp", "url": "http://example.com"}]

        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        assert result is False

    def test_html_email_generation(self, mock_settings):
        """Test HTML email is generated correctly."""
        notifier = EmailNotifier()
        jobs = [
            {
                "title": "Software Engineer",
                "company": "TestCorp",
                "location": "Bogotá",
                "url": "https://example.com/job/1",
            }
        ]

        html = notifier._generate_html_email(jobs, "test_spider")
        assert "Software Engineer" in html
        assert "TestCorp" in html
        assert "https://example.com/job/1" in html

    def test_html_email_with_description(self, mock_settings):
        """Test HTML email includes job description."""
        notifier = EmailNotifier()
        long_desc = "A" * 400  # Description longer than 300 chars
        jobs = [
            {
                "title": "Job",
                "company": "Corp",
                "url": "http://example.com",
                "description": long_desc,
            }
        ]

        html = notifier._generate_html_email(jobs, "test_spider")
        # HTML should contain the description (possibly truncated with "...")
        assert "AAAA" in html  # Part of description should be present
        assert "Description" in html or "description" in html.lower()
