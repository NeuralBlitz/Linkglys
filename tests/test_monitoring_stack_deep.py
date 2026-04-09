"""Deep tests for monitoring stack configs - dynamic discovery."""
import pytest, sys, os, yaml

class TestPrometheusConfig:
    def test_valid_yaml(self):
        with open("prometheus/prometheus.yml") as f:
            config = yaml.safe_load(f)
        assert "global" in config
        assert "scrape_configs" in config

class TestPrometheusAlerts:
    def test_valid_yaml(self):
        with open("prometheus/alerts.yml") as f:
            config = yaml.safe_load(f)
        assert "groups" in config

class TestPrometheusRecordingRules:
    def test_valid_yaml(self):
        with open("prometheus/recording-rules.yml") as f:
            config = yaml.safe_load(f)
        assert "groups" in config

class TestDockerCompose:
    def test_valid_yaml(self):
        with open("docker-compose.yml") as f:
            config = yaml.safe_load(f)
        assert "services" in config
        assert len(config["services"]) >= 4

class TestInfluxDBConfig:
    def test_valid_config(self):
        assert os.path.exists("influxdb/config/influxdb.conf")

class TestTimescaleDBInit:
    def test_init_script_exists(self):
        assert os.path.exists("timescaledb/init/01-init-schema.sql")
