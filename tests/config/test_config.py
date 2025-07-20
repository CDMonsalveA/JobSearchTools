import tempfile
from copy import deepcopy

from jobsearchtools.config.config import Config, config


class TestConfig:
    def test_default_config_values(self):
        cfg = Config()
        assert cfg.get("project_name") == "JobSearchTools"
        assert cfg.get("version") == "0.0.1"
        assert cfg.get("db")["type"] == "sqlite"
        assert isinstance(cfg.get("scrapy"), dict)
        assert cfg.get("log_level") == "DEBUG"

    def test_set_and_get_value(self):
        cfg = Config()
        cfg.set("custom_key", "custom_value")
        assert cfg.get("custom_key") == "custom_value"

    def test_set_and_get_db_type(self):
        cfg = Config()
        with tempfile.NamedTemporaryFile() as tmpfile:
            cfg.set("db", {"type": "postgresql", "name": "jobs", "path": tmpfile.name})
            db_cfg = cfg.get("db")
            assert db_cfg["type"] == "postgresql"
            assert db_cfg["name"] == "jobs"
            assert db_cfg["path"] == tmpfile.name

    def test_get_nonexistent_key_returns_default(self):
        cfg = Config()
        assert cfg.get("nonexistent", "default") == "default"

    def test_config_is_independent_between_instances(self):
        cfg1 = Config()
        cfg2 = Config()
        cfg1.set("db", {"type": "mysql"})
        assert cfg2.get("db")["type"] == "sqlite"
        assert cfg1.get("db")["type"] == "mysql"

    def test_config_property_returns_internal_dict(self):
        cfg = Config()
        assert isinstance(cfg.config, dict)
        assert cfg.config["project_name"] == "JobSearchTools"

    def test_default_config_not_modified(self):
        original = deepcopy(Config.default_config)
        cfg = Config()
        cfg.set("project_name", "ChangedName")
        assert Config.default_config == original

    def test_set_none_value(self):
        cfg = Config()
        cfg.set("nullable", None)
        assert cfg.get("nullable") is None

    def test_scrapy_settings_structure(self):
        cfg = Config()
        scrapy = cfg.get("scrapy")
        assert "settings" in scrapy
        assert scrapy["settings"]["BOT_NAME"] == "jobsearchtools"

    def test_change_db_type_for_mvp(self):
        cfg = Config()
        # Simulate MVP switch to PostgreSQL
        new_db = {
            "type": "postgresql",
            "name": "jobsearchtools",
            "path": "/var/lib/postgresql/jobsearchtools.db",
        }
        cfg.set("db", new_db)
        db_cfg = cfg.get("db")
        assert db_cfg["type"] == "postgresql"
        assert db_cfg["name"] == "jobsearchtools"
        assert db_cfg["path"] == "/var/lib/postgresql/jobsearchtools.db"

    def test_global_config_instance(self):
        assert isinstance(config, Config)
        assert config.get("project_name") == "JobSearchTools"

    def test_overwrite_entire_config(self):
        cfg = Config()
        new_cfg = {"foo": "bar"}
        cfg._config = new_cfg
        assert cfg.get("foo") == "bar"
        assert cfg.config == new_cfg

    def test_config_init_with_custom_dict(self):
        custom = {"custom_key": "custom_value"}
        cfg = Config(custom)
        assert cfg.get("custom_key") == "custom_value"
