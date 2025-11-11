"""Pytest fixtures for spider tests."""

import pytest
from scrapy.http import HtmlResponse, Request


@pytest.fixture
def fake_response():
    """Create a fake Scrapy response for testing."""

    def _make_response(url="http://test.com", body=b"<html></html>", status=200):
        request = Request(url=url)
        return HtmlResponse(
            url=url, request=request, body=body, encoding="utf-8", status=status
        )

    return _make_response


@pytest.fixture
def sample_job_item():
    """Sample job item structure for testing."""
    return {
        "job_id": "test_12345",
        "title": "Software Engineer",
        "company": "Test Company",
        "location": "Bogotá",
        "description": "Test job description",
        "salary": "5000 USD",
        "url": "https://test.com/jobs/12345",
        "date_posted": "2025-11-10",
        "date_extracted": "2025-11-10T10:00:00",
        "was_opened": False,
    }
