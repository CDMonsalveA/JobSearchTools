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
        """Test notifier initialization when enabled."""
        notifier = EmailNotifier()
        assert notifier.enabled is True

    def test_initialization_disabled(self, mock_settings):
        """Test notifier initialization when disabled."""
        mock_settings.email.enabled = False
        notifier = EmailNotifier()
        assert notifier.enabled is False

    def test_initialization_no_password(self, mock_settings):
        """Test notifier initialization without password."""
        mock_settings.email.smtp_password = ""
        notifier = EmailNotifier()
        assert notifier.enabled is False

    @patch("smtplib.SMTP")
    def test_send_notification_success(self, mock_smtp, mock_settings):
        """Test successful email sending."""
        # Setup
        notifier = EmailNotifier()
        jobs = [
            {
                "title": "Software Engineer",
                "company": "TestCorp",
                "location": "Bogotá",
                "url": "https://test.com/job1",
                "salary": "$50,000",
                "date_posted": "2024-01-01",
                "description": "Test job description",
            }
        ]

        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Test
        result = notifier.send_new_jobs_notification(jobs, "test_spider")

        # Verify
        assert result is True
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@test.com", "testpass")
        mock_server.sendmail.assert_called_once()

    def test_send_notification_disabled(self, mock_settings):
        """Test email sending when disabled."""
        mock_settings.email.enabled = False
        notifier = EmailNotifier()
        jobs = [{"title": "Test Job"}]

        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        assert result is False

    def test_send_notification_empty_jobs(self, mock_settings):
        """Test email sending with no jobs."""
        notifier = EmailNotifier()
        result = notifier.send_new_jobs_notification([], "test_spider")
        assert result is False

    @patch("smtplib.SMTP")
    def test_send_notification_smtp_error(self, mock_smtp, mock_settings):
        """Test email sending with SMTP error."""
        notifier = EmailNotifier()
        jobs = [{"title": "Test Job", "company": "TestCorp"}]

        # Mock SMTP to raise error
        mock_smtp.side_effect = Exception("SMTP Error")

        result = notifier.send_new_jobs_notification(jobs, "test_spider")
        assert result is False

    def test_generate_html_email(self, mock_settings):
        """Test HTML email generation."""
        notifier = EmailNotifier()
        jobs = [
            {
                "title": "Software Engineer",
                "company": "TestCorp",
                "location": "Bogotá",
                "url": "https://test.com/job",
                "salary": "$50,000",
                "date_posted": "2024-01-01",
                "description": "Test description",
            }
        ]

        html = notifier._generate_html_email(jobs, "test_spider")

        # Verify HTML contains key elements
        assert "Software Engineer" in html
        assert "TestCorp" in html
        assert "Bogotá" in html
        assert "$50,000" in html
        assert "https://test.com/job" in html
        assert "<!DOCTYPE html>" in html
        assert "<body>" in html
