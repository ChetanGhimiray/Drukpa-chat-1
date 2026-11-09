"""Streamlit dashboard checks with a fake engine and no model/network calls."""
import sys
from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dzongkha_bot import engine as engine_module, strings  # noqa: E402
from dzongkha_bot.engine import Reply  # noqa: E402

ANSWER = "ཨིན། འདི་ཡིག་ཆ་ཨིན།"


class FakeEngine:
    def __init__(self):
        self.seen = []

    def reply(self, messages):
        self.seen.append([dict(message) for message in messages])
        return Reply(ANSWER, provider="fake")


def open_app(monkeypatch, engine):
    monkeypatch.setattr(engine_module, "build_engine", lambda: engine)

    def no_ollama(*args, **kwargs):
        raise requests.ConnectionError("test mode")

    monkeypatch.setattr(requests, "get", no_ollama)
    import streamlit as st

    st.cache_resource.clear()
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    app.run()
    return app


def markdown_text(app):
    return "\n".join(item.value for item in app.markdown)


def test_dashboard_renders_and_shows_welcome(monkeypatch):
    app = open_app(monkeypatch, FakeEngine())
    assert not app.exception
    assert "Drukpa Chat" in markdown_text(app)
    assert strings.WELCOME in markdown_text(app)
    assert len(app.chat_input) == 1
    assert any("Download conversation" in button.label for button in app.button) is False


def test_chat_keeps_conversation_context(monkeypatch):
    fake = FakeEngine()
    app = open_app(monkeypatch, fake)
    app.chat_input[0].set_value("What is Bhutan known for?").run()
    app.chat_input[0].set_value("Tell me one more fact").run()
    assert not app.exception
    assert len(fake.seen) == 2
    assert [item["role"] for item in fake.seen[1]] == ["user", "assistant", "user"]
    assert fake.seen[1][-1]["content"] == "Tell me one more fact"


def test_failed_exchange_does_not_pollute_next_request(monkeypatch):
    class FailingOnce(FakeEngine):
        def reply(self, messages):
            self.seen.append([dict(message) for message in messages])
            if len(self.seen) == 1:
                return Reply(strings.ERR_RATE_LIMIT, error="rate_limit")
            return Reply(ANSWER)

    fake = FailingOnce()
    app = open_app(monkeypatch, fake)
    app.chat_input[0].set_value("first question").run()
    app.chat_input[0].set_value("second question").run()
    assert not app.exception
    assert [item["content"] for item in fake.seen[1]] == ["second question"]
