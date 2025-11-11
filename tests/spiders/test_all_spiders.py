"""Common tests for all spiders - import validation and uniqueness."""

import pytest


def test_all_spiders_importable():
    """Test that all spiders can be imported without errors."""
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

    # Verify all spider classes exist
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
    """Test that all spider names are unique to avoid conflicts."""
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


@pytest.mark.parametrize(
    "spider_module,spider_class",
    [
        ("avianca", "AviancaSpider"),
        ("bancolombia", "BancolombiaSpider"),
        ("citi", "CitiSpider"),
        ("ecopetrol", "EcopetrolSpider"),
        ("mastercard", "MastercardSpider"),
        ("nequi", "NequiSpider"),
        ("scotiabank", "ScotiabankSpider"),
        ("sura", "SuraSpider"),
    ],
)
def test_static_spider_attributes(spider_module, spider_class):
    """Test static spiders have all required attributes."""
    from importlib import import_module

    module = import_module(
        f"jobsearchtools.job_scraper.job_scraper.spiders.static.{spider_module}"
    )
    spider_cls = getattr(module, spider_class)
    spider = spider_cls()

    assert hasattr(spider, "name")
    assert hasattr(spider, "allowed_domains")
    assert hasattr(spider, "start_urls")
    assert hasattr(spider, "parse")

    assert isinstance(spider.name, str)
    assert len(spider.name) > 0
    assert isinstance(spider.allowed_domains, list)
    assert len(spider.allowed_domains) > 0
    assert isinstance(spider.start_urls, list)
    assert len(spider.start_urls) > 0
    assert callable(spider.parse)


@pytest.mark.parametrize(
    "spider_module,spider_class",
    [
        ("bbva", "BbvaSpider"),
        ("visa", "VisaSpider"),
    ],
)
def test_dynamic_spider_attributes(spider_module, spider_class):
    """Test dynamic (Playwright) spiders have all required attributes."""
    from importlib import import_module

    module = import_module(
        f"jobsearchtools.job_scraper.job_scraper.spiders.dynamic.{spider_module}"
    )
    spider_cls = getattr(module, spider_class)
    spider = spider_cls()

    assert hasattr(spider, "name")
    assert hasattr(spider, "allowed_domains")
    assert hasattr(spider, "start_requests")
    assert hasattr(spider, "parse")

    assert isinstance(spider.name, str)
    assert len(spider.name) > 0
    assert isinstance(spider.allowed_domains, list)
    assert len(spider.allowed_domains) > 0
    assert callable(spider.start_requests)
    assert callable(spider.parse)
