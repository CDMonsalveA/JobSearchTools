"""Tests for static HTML spiders (Avianca, Bancolombia, Citi, etc)."""

import pytest

from jobsearchtools.job_scraper.job_scraper.spiders.static.avianca import (
    AviancaSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.bancolombia import (
    BancolombiaSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.citi import CitiSpider
from jobsearchtools.job_scraper.job_scraper.spiders.static.ecopetrol import (
    EcopetrolSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.mastercard import (
    MastercardSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.nequi import NequiSpider
from jobsearchtools.job_scraper.job_scraper.spiders.static.scotiabank import (
    ScotiabankSpider,
)
from jobsearchtools.job_scraper.job_scraper.spiders.static.sura import SuraSpider


class TestStaticSpiders:
    """Test all static spiders basic functionality."""

    @pytest.mark.parametrize(
        "spider_class,expected_name,expected_domain",
        [
            (AviancaSpider, "avianca", "jobs.avianca.com"),
            (BancolombiaSpider, "bancolombia", "empleo.grupobancolombia.com"),
            (CitiSpider, "citi", "jobs.citi.com"),
            (EcopetrolSpider, "ecopetrol", "jobs.ecopetrol.com.co"),
            (MastercardSpider, "mastercard", "careers.mastercard.com"),
            (NequiSpider, "nequi", "lapipolnequi.buk.co"),
            (ScotiabankSpider, "scotiabank", "jobs.scotiabank.com"),
            (SuraSpider, "sura", "trabajaconnosotros.sura.com"),
        ],
    )
    def test_spider_configuration(self, spider_class, expected_name, expected_domain):
        """Test spider has correct name and domain configuration."""
        spider = spider_class()
        assert spider.name == expected_name
        assert expected_domain in spider.allowed_domains
        assert len(spider.start_urls) > 0

    @pytest.mark.parametrize(
        "spider_class",
        [
            AviancaSpider,
            BancolombiaSpider,
            CitiSpider,
            EcopetrolSpider,
            MastercardSpider,
            NequiSpider,
            ScotiabankSpider,
            SuraSpider,
        ],
    )
    def test_parse_method_exists(self, spider_class):
        """Test all spiders have a parse method."""
        spider = spider_class()
        assert hasattr(spider, "parse")
        assert callable(spider.parse)


class TestAviancaSpider:
    """Test Avianca-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create Avianca spider instance."""
        return AviancaSpider()

    def test_has_spanish_months_constant(self, spider):
        """Test spider has Spanish month mapping for date parsing."""
        assert hasattr(spider, "SPANISH_MONTHS")
        assert isinstance(spider.SPANISH_MONTHS, dict)
        assert "ene" in spider.SPANISH_MONTHS
        assert spider.SPANISH_MONTHS["ene"] == "Jan"

    def test_has_parse_detail_method(self, spider):
        """Test Avianca spider has detail page parser."""
        assert hasattr(spider, "parse_detail")
        assert callable(spider.parse_detail)


class TestMastercardSpider:
    """Test Mastercard-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create Mastercard spider instance."""
        return MastercardSpider()

    def test_has_parse_detail_method(self, spider):
        """Test Mastercard spider has detail page parser."""
        assert hasattr(spider, "parse_detail")
        assert callable(spider.parse_detail)

    def test_targets_bogota_colombia(self, spider):
        """Test Mastercard spider targets Bogotá, Colombia jobs."""
        assert any("bogota" in url.lower() for url in spider.start_urls)


class TestEcopetrolSpider:
    """Test Ecopetrol-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create Ecopetrol spider instance."""
        return EcopetrolSpider()

    def test_targets_colombia(self, spider):
        """Test Ecopetrol spider targets Colombian jobs."""
        assert any("Colombia" in url for url in spider.start_urls)


class TestNequiSpider:
    """Test Nequi-specific functionality."""

    @pytest.fixture
    def spider(self):
        """Create Nequi spider instance."""
        return NequiSpider()

    def test_targets_colombia(self, spider):
        """Test Nequi spider is configured for Colombian jobs."""
        assert "lapipolnequi.buk.co" in spider.allowed_domains
