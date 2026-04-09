"""Deep tests for JSON schemas - dynamic discovery."""
import pytest, json, os

class TestDeploymentSchema:
    def test_valid_json(self):
        with open("schemas/deployments/deployment_goldendag.json") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

class TestMLPipelineSchema:
    def test_valid_json(self):
        with open("schemas/capabilities/ck_ml_automated_pipeline_schema.json") as f:
            data = json.load(f)
        assert "kernel" in data or "properties" in data

class TestDataQualitySchema:
    def test_valid_json(self):
        with open("schemas/capabilities/ck_data_quality_assessment_schema.json") as f:
            data = json.load(f)
        assert "kernel" in data or "properties" in data

class TestFeatureEngineeringSchema:
    def test_valid_json(self):
        with open("schemas/capabilities/ck_feature_engineering_automation_schema.json") as f:
            data = json.load(f)
        assert "kernel" in data or "properties" in data

class TestBioinformaticsSchema:
    def test_valid_json(self):
        with open("schemas/bioinformatics_ck_contracts.json") as f:
            data = json.load(f)
        assert isinstance(data, dict)

class TestCybersecuritySchema:
    def test_valid_json(self):
        with open("schemas/cybersecurity_ck_registry.json") as f:
            data = json.load(f)
        assert isinstance(data, dict)

class TestVotingReportSchema:
    def test_valid_json(self):
        with open("schemas/voting_systems_report_metadata.json") as f:
            data = json.load(f)
        assert isinstance(data, dict)
