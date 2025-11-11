"""Common tests for all spiders."""

import pytest


class SpiderTestBase:
    """Base class for common spider tests."""

    spider_class = None
    expected_name = None
    expected_domains = None
    expected_company = None

    @pytest.fixture
    def spider(self):
        """Create spider instance."""
        if self.spider_class is None:
            pytest.skip("Spider class not defined")
        return self.spider_class()

    def test_spider_name(self, spider):
        """Test spider has correct name."""
        if self.expected_name:
            assert spider.name == self.expected_name

    def test_spider_domains(self, spider):
        """Test spider has correct allowed domains."""
        if self.expected_domains:
            assert spider.allowed_domains == self.expected_domains

    def test_spider_has_start_urls(self, spider):
        """Test spider has start URLs."""
        assert hasattr(spider, "start_urls")
        assert len(spider.start_urls) > 0

    def test_spider_has_parse_method(self, spider):
        """Test spider has parse method."""
        assert hasattr(spider, "parse")
        assert callable(spider.parse)

    def test_company_name_in_items(self, spider):
        """Test spider sets correct company name."""
        if self.expected_company:
            # This would need actual parsing test
            pass


def test_all_spiders_importable():
    """Test that all spiders can be imported."""
    from jobsearchtools.job_scraper.job_scraper.spiders.dynamic import bbva, visa
    from jobsearchtools.job_scraper.job_scraper.spiders.static import (
        avianca,
        bancolombia,
        citi,
        ecopetrol,
        mastercard,
        nequi,
        scotiabank,
        sura,
    )

    # Check all modules are imported
    assert avianca.AviancaSpider
    assert bancolombia.BancolombiaSpider
    assert citi.CitiSpider
    assert ecopetrol.EcopetrolSpider
    assert mastercard.MastercardSpider
    assert nequi.NequiSpider
    assert scotiabank.ScotiabankSpider
    assert sura.SuraSpider
    assert bbva.BbvaSpider
    assert visa.VisaSpider


def test_all_spider_names_unique():
    """Test that all spider names are unique."""
    from jobsearchtools.job_scraper.job_scraper.spiders.dynamic import bbva, visa
    from jobsearchtools.job_scraper.job_scraper.spiders.static import (
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
        avianca.AviancaSpider(),
        bancolombia.BancolombiaSpider(),
        citi.CitiSpider(),
        ecopetrol.EcopetrolSpider(),
        mastercard.MastercardSpider(),
        nequi.NequiSpider(),
        scotiabank.ScotiabankSpider(),
        sura.SuraSpider(),
        bbva.BbvaSpider(),
        visa.VisaSpider(),
    ]

    names = [spider.name for spider in spiders]
    assert len(names) == len(set(names)), "Spider names must be unique"


def test_all_spiders_have_required_attributes():
    """Test all spiders have required attributes."""
    from jobsearchtools.job_scraper.job_scraper.spiders.dynamic import bbva, visa
    from jobsearchtools.job_scraper.job_scraper.spiders.static import (
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
        avianca.AviancaSpider(),
        bancolombia.BancolombiaSpider(),
        citi.CitiSpider(),
        ecopetrol.EcopetrolSpider(),
        mastercard.MastercardSpider(),
        nequi.NequiSpider(),
        scotiabank.ScotiabankSpider(),
        sura.SuraSpider(),
        bbva.BbvaSpider(),
        visa.VisaSpider(),
    ]

    for spider in spiders:
        assert hasattr(spider, "name")
        assert hasattr(spider, "allowed_domains")
        assert hasattr(spider, "start_urls")
        assert hasattr(spider, "parse")
        assert spider.name
        assert len(spider.allowed_domains) > 0
        assert len(spider.start_urls) > 0
