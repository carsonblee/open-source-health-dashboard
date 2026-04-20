"""
Test script for Open Source Health Dashboard

Testing functionality of app.py

Run with:  pytest tests/ -v
"""
import pytest
from app import app, parse_repo


def test_parse_repo_full_url():
    assert parse_repo("https://github.com/EbookFoundation/free-programming-books") == (
        "Free Ebook Foundation",
        "free-programming-books",
    )
