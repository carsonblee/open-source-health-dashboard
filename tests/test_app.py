"""
Test script for Open Source Health Dashboard
    - Testing functionality of app.py
    - Called to run on pushes to main via CI pipeline
Run with:  pytest tests/ -v
"""
import pytest
from app import app, parse_repo


# %%%%%%%%%%%%%%% 1: FUNCTIONALITY TESTING - parse_repo() %%%%%%%%%%%%%%%
# 1A: Testing parsing from full GH URL
def test_parse_repo_full_url():
    assert parse_repo("https://github.com/EbookFoundation/free-programming-books") == (
        "EbookFoundation",
        "free-programming-books",
    )


# 1B: Testing parsing from GH owner and repo shorthand
def test_parse_repo_shorthand():
    assert parse_repo("EbookFoundation/free-programming-books") == (
        "EbookFoundation",
        "free-programming-books",
    )


# 1C: Same test as 1A but this time with trailing slash to be trimmed
def test_parse_repo_trailing_slash():
    assert parse_repo("https://github.com/EbookFoundation/free-programming-books/") == (
        "EbookFoundation",
        "free-programming-books",
    )


# 1D: Test to validate can find error in invalid input
def test_parse_repo_not_valid():
    assert parse_repo("not valid url") is None


# 1E: Test to validate can catch error for empty input
def test_parse_repo_empty():
    assert parse_repo("") is None


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
