"""
Test fixtures and utilities for QuickQL tests.
"""

import pytest

from quickql import Query


@pytest.fixture
def query():
    """Create a fresh Query instance for testing."""
    return Query()


@pytest.fixture
def basic_query(query):
    """Create a Query with basic SELECT * FROM users setup."""
    return query.SELECT("*").FROM("users")


@pytest.fixture
def complex_query(query):
    """Create a more complex query for testing advanced features."""
    return (
        query.SELECT("u.name", "u.email", "p.title")
        .FROM("users u")
        .JOIN("posts p ON u.id = p.user_id")
        .WHERE("u.active = 1")
        .WHERE("p.published = 1")
        .ORDER_BY("u.name")
        .LIMIT("10")
    )
