"""
Test script for Open Source Health Dashboard

Testing functionality of app.py

Run with:  pytest tests/ -v
"""
import pytest
from app import app, parse_repo


# # %%%%%%%%%%%%%%% 2: FUNCTIONALITY TESTING %%%%%%%%%%%%%%%
def test_parse_repo_full_url():
    assert parse_repo("https://github.com/EbookFoundation/free-programming-books") == (
        "Free Ebook Foundation",
        "free-programming-books",
    )


# %%%%%%%%%%%%%%% 2: INTEGRATION TESTING %%%%%%%%%%%%%%%
@pytest.fixture
def client():  # Adds client object to test with
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Analyzer" in resp.data
