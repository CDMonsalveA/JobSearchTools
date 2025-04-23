"""Script to scrape job postings from Mastercard's career page."""

import json
import logging
from typing import NamedTuple

import httpx
import jmespath
import parsel

logger = logging.getLogger(__name__)

URL = "https://amadeus.wd3.myworkdayjobs.com/jobs?locationCountry=e8106cd6a3534f2dba6fdee2d41db89d"


class LastJobPosting(NamedTuple):
    title: str
    jobId: str
    postedDate: str
    applyUrl: str


# add headers to the request to make it look like a browser
def VisaLastJobPosting():
    """Scrape the last job posting from Visa."""
    headers = {
        "Accept": "application/json,application/xml",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",  # noqa: E501
    }
    request = httpx.get(URL, headers=headers)
    # Save the response to a file
    with open("visa.html", "w", encoding="utf-8") as f:
        f.write(request.text)

if __name__ == "__main__":
    VisaLastJobPosting()
