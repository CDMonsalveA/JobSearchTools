import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Config:
    """
    Configuration class for the job search tools project.
    """

    # Class variables for configuration settings

    default_config: ClassVar[dict[str, Any]] = {
        "project_name": "JobSearchTools",
        "version": "0.0.1",
        "description": "A set of tools for job searching and scraping job listings.",
        "cache_dir": "cache",
        "base_dir": "src/jobsearchtools",
        "logs_dir": "logs",
        "log_level": "DEBUG",
        "data_dir": "data",
        # Database configuration
        "db": {
            "type": "sqlite",
            "name": "jobsearchtools.db",
            "path": "src/jobsearchtools/db/jobsearchtools.db",
        },
        # Scrapy configuration
        "scrapy": {
            "bot_name": "job_scraper",
            "project_dir": str(Path("src/jobsearchtools/job_scraper").resolve()),
            "spiders_dir": str(
                Path("src/jobsearchtools/job_scraper/spiders").resolve()
            ),
            "spiders_list": [],  # If not specified, will be auto-discovered
            "settings": {
                "BOT_NAME": "jobsearchtools",
                "SPIDER_MODULES": ["jobsearchtools.job_scraper.spiders"],
                "NEWSPIDER_MODULE": "jobsearchtools.job_scraper.spiders",
                "LOG_LEVEL": "DEBUG",
            },
        },
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the configuration with default values or provided config.

        Args:
            config (dict[str, Any], optional): A dictionary containing settings.
                If None, the default configuration will be used.
        """
        self._config = deepcopy(self.default_config)
        if config is not None:
            # Shallow update: custom keys/values will overwrite defaults
            self._config.update(config)
        logger.debug(f"Configuration initialized: {self._config}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key (str): The key for the configuration setting.
            default (Any, optional): The default value to return if key not found.
        Returns:
            Any: The value of the configuration setting or the default value.
        """
        value = self.config.get(key, default)
        logger.debug(f"Retrieved config value for '{key}': {value}")
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.

        Args:
            key (str): The key for the configuration setting.
            value (Any): The value to set for the configuration setting.
        """
        self.config[key] = value
        logger.debug(f"Set config value for '{key}': {value}")

    @property
    def config(self) -> dict[str, Any]:
        return self._config


# Define a global configuration instance
config = Config()
