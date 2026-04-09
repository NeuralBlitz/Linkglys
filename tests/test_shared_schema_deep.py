"""Deep tests for shared schema - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

class TestSharedSchema:
    def test_module_loads(self):
        # TypeScript file - just verify it exists and has content
        with open("shared/schema.ts") as f:
            content = f.read()
        assert "pgTable" in content
        assert "conversations" in content
        assert "messages" in content

    def test_chat_model_exists(self):
        with open("shared/models/chat.ts") as f:
            content = f.read()
        assert "pgTable" in content
