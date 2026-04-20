"""
Test script for Open Source Health Dashboard

Testing functionality of app.py

Run with:  pytest tests/ -v
"""
import pytest
from app import app, parse_repo

# Placeholder Functionality Testing
def test_parse_repo_full_url():
    assert parse_repo("https://github.com/EbookFoundation/free-programming-books") == (
        "Free Ebook Foundation",
        "free-programming-books",
    )


# Placeholder Integration Testing
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
