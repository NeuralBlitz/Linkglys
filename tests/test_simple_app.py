"""Tests for src/simple_app.py - Flask-based simple web app."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def flask_app():
    """Create the Flask test app."""
    # Clear any cached import
    if "simple_app" in sys.modules:
        del sys.modules["simple_app"]

    from simple_app import app
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(flask_app):
    """Create a test client."""
    return flask_app.test_client()


class TestHomePage:
    """Test the home page."""

    def test_home_returns_200(self, client):
        """Test home page returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_title(self, client):
        """Test home page contains the title."""
        response = client.get("/")
        assert b"OpenCode LRS" in response.data

    def test_home_contains_tailwind(self, client):
        """Test home page includes Tailwind CSS."""
        response = client.get("/")
        assert b"tailwindcss" in response.data

    def test_home_contains_code_textarea(self, client):
        """Test home page has code input textarea."""
        response = client.get("/")
        assert b"codeInput" in response.data or b"textarea" in response.data

    def test_home_contains_analyze_button(self, client):
        """Test home page has analyze button."""
        response = client.get("/")
        assert b"analyzeCode" in response.data or b"Analyze" in response.data


class TestAnalyzeEndpoint:
    """Test the /api/analyze endpoint."""

    def test_analyze_with_python_code(self, client):
        """Test analysis of Python code."""
        response = client.post("/api/analyze", json={
            "code": "def hello():\n    print('world')\n\nif True:\n    pass"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["lines_analyzed"] > 0
        assert "functions" in data["insights"]
        assert "conditionals" in data["insights"]

    def test_analyze_with_class_definition(self, client):
        """Test analysis detects class definitions."""
        response = client.post("/api/analyze", json={
            "code": "class MyClass:\n    def __init__(self):\n        pass\n\n    def method(self):\n        pass"
        })
        data = response.get_json()
        assert data["insights"]["classes"] >= 1
        assert data["insights"]["functions"] >= 2

    def test_analyze_with_loops(self, client):
        """Test analysis detects loops."""
        response = client.post("/api/analyze", json={
            "code": "for i in range(10):\n    while i > 0:\n        i -= 1"
        })
        data = response.get_json()
        assert data["insights"]["loops"] >= 2

    def test_analyze_empty_code(self, client):
        """Test analysis of empty code."""
        response = client.post("/api/analyze", json={"code": ""})
        data = response.get_json()
        assert data["success"] is True
        assert data["lines_analyzed"] == 0
        assert data["patterns_found"] == 0

    def test_analyze_multiline_code(self, client):
        """Test analysis of multi-line code."""
        code = "\n".join([f"def func_{i}(): pass" for i in range(20)])
        response = client.post("/api/analyze", json={"code": code})
        data = response.get_json()
        assert data["insights"]["functions"] == 20
        assert data["lines_analyzed"] == 20

    def test_analyze_returns_timing(self, client):
        """Test analysis returns timing information."""
        response = client.post("/api/analyze", json={"code": "x = 1"})
        data = response.get_json()
        assert "analysis_time" in data
        assert isinstance(data["analysis_time"], (int, float))

    def test_analyze_returns_cognitive_score(self, client):
        """Test analysis returns cognitive score."""
        response = client.post("/api/analyze", json={"code": "x = 1"})
        data = response.get_json()
        assert "cognitive_score" in data
        assert isinstance(data["cognitive_score"], (int, float))

    def test_analyze_returns_recommendations(self, client):
        """Test analysis returns recommendations."""
        response = client.post("/api/analyze", json={"code": "x = 1"})
        data = response.get_json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0

    def test_analyze_missing_json_body(self, client):
        """Test analyze returns 400 when no JSON body provided."""
        response = client.post("/api/analyze")
        assert response.status_code == 400

    def test_analyze_invalid_content_type(self, client):
        """Test analyze handles invalid content type."""
        response = client.post(
            "/api/analyze",
            data="not json",
            content_type="text/plain"
        )
        assert response.status_code == 400

    def test_analyze_missing_code_key(self, client):
        """Test analyze handles JSON without code key."""
        response = client.post("/api/analyze", json={"other": "value"})
        data = response.get_json()
        assert data["success"] is True
        assert data["lines_analyzed"] == 0

    def test_analyze_with_comments(self, client):
        """Test analysis handles code with comments."""
        code = "# This is a comment\ndef foo():\n    # Another comment\n    return 42"
        response = client.post("/api/analyze", json={"code": code})
        data = response.get_json()
        assert data["success"] is True
        assert data["insights"]["functions"] == 1


class TestComplexCodeAnalysis:
    """Test analysis of complex code patterns."""

    def test_fibonacci_function(self, client):
        """Test analysis of recursive fibonacci."""
        code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        response = client.post("/api/analyze", json={"code": code})
        data = response.get_json()
        assert data["insights"]["functions"] == 1
        assert data["insights"]["conditionals"] == 1

    def test_task_manager_class(self, client):
        """Test analysis of a class with methods."""
        code = """class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_tasks(self):
        return self.tasks"""
        response = client.post("/api/analyze", json={"code": code})
        data = response.get_json()
        assert data["insights"]["classes"] == 1
        assert data["insights"]["functions"] == 3

    def test_mixed_patterns(self, client):
        """Test analysis of mixed code patterns."""
        code = """for i in range(10):
    if i % 2 == 0:
        print(i)
    elif i % 3 == 0:
        print(i * 2)

while True:
    if condition:
        break"""
        response = client.post("/api/analyze", json={"code": code})
        data = response.get_json()
        assert data["insights"]["loops"] >= 2
        assert data["insights"]["conditionals"] >= 3
