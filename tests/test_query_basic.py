"""
Tests for the basic Query class functionality.
"""

import pytest

from quickql import Query
from quickql.builder import ClauseCollection, QueryElement, SQLKeyword


class TestQueryElement:
    """Test cases for QueryElement class."""

    def test_create_from_string(self):
        """Test creating QueryElement from a string."""
        element = QueryElement.create("name")
        assert element.value == "name"
        assert element.alias == ""
        assert element.join_keyword == ""
        assert element.is_subquery is False

    def test_create_from_tuple(self):
        """Test creating QueryElement from a tuple (alias, value)."""
        element = QueryElement.create(("user_name", "name"))
        assert element.value == "name"
        assert element.alias == "user_name"

    def test_create_with_kwargs(self):
        """Test creating QueryElement with additional kwargs."""
        element = QueryElement.create(
            "name", join_keyword="INNER JOIN", is_subquery=True
        )
        assert element.value == "name"
        assert element.join_keyword == "INNER JOIN"
        assert element.is_subquery is True

    def test_invalid_argument_format(self):
        """Test that invalid argument formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid argument format"):
            QueryElement.create([1, 2, 3])  # Too many elements in list


class TestClauseCollection:
    """Test cases for ClauseCollection class."""

    def test_initial_state(self):
        """Test ClauseCollection initial state."""
        clause = ClauseCollection()
        assert clause.is_empty()
        assert len(clause) == 0
        assert clause.flag is None

    def test_add_element(self):
        """Test adding elements to ClauseCollection."""
        clause = ClauseCollection()
        element = QueryElement.create("name")

        clause.add_element(element)
        assert not clause.is_empty()
        assert len(clause) == 1
        assert element in clause

    def test_set_flag(self):
        """Test setting flags on ClauseCollection."""
        clause = ClauseCollection()
        clause.set_flag("DISTINCT")
        assert clause.flag == "DISTINCT"

    def test_set_flag_twice_raises_error(self):
        """Test that setting a flag twice raises ValueError."""
        clause = ClauseCollection()
        clause.set_flag("DISTINCT")

        with pytest.raises(ValueError, match="Flag already set"):
            clause.set_flag("ALL")

    def test_iteration(self):
        """Test iterating over ClauseCollection elements."""
        clause = ClauseCollection()
        elements = [QueryElement.create(f"col{i}") for i in range(3)]

        for element in elements:
            clause.add_element(element)

        result = list(clause)
        assert result == elements


class TestQueryBasic:
    """Test cases for basic Query functionality."""

    def test_query_initialization(self):
        """Test Query class initialization."""
        query = Query()
        assert isinstance(query, Query)
        assert all(keyword in query._clauses for keyword in SQLKeyword)

    def test_simple_select(self):
        """Test basic SELECT query."""
        query = Query()
        query.SELECT("name", "email")

        sql = query.build()
        assert "SELECT" in sql
        assert "name" in sql
        assert "email" in sql

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        query = Query()
        result = query.SELECT("*").FROM("users").WHERE("active = 1")

        assert result is query  # Should return same instance

    def test_build_vs_str(self):
        """Test that build() and __str__() return the same result."""
        query = Query().SELECT("*").FROM("users")

        assert query.build() == str(query)

    def test_uppercase_method_names(self):
        """Test that uppercase method names work correctly."""
        query = Query()

        # These should all work without AttributeError
        query.SELECT("*")
        query.FROM("users")
        query.WHERE("id = 1")
        query.ORDER_BY("name")

        sql = str(query)
        assert "SELECT" in sql
        assert "FROM" in sql
        assert "WHERE" in sql
        assert "ORDER BY" in sql

    def test_invalid_method_name_raises_error(self):
        """Test that invalid method names raise AttributeError."""
        query = Query()

        with pytest.raises(AttributeError):
            query.invalid_method()

    def test_add_method_directly(self):
        """Test using the add() method directly."""
        query = Query()
        query.add("SELECT", "name", "email")
        query.add("FROM", "users")

        sql = str(query)
        assert "SELECT" in sql
        assert "name" in sql
        assert "email" in sql
        assert "FROM" in sql
        assert "users" in sql


class TestQueryFlags:
    """Test cases for SQL flags (DISTINCT, ALL, etc.)."""

    def test_select_distinct(self):
        """Test SELECT DISTINCT functionality."""
        query = Query()
        query.add("SELECT DISTINCT", "name")

        sql = str(query)
        assert "SELECT DISTINCT" in sql
        assert "name" in sql

    def test_select_all(self):
        """Test SELECT ALL functionality."""
        query = Query()
        query.add("SELECT ALL", "name")

        sql = str(query)
        assert "SELECT ALL" in sql

    def test_multiple_flags_on_same_clause_raises_error(self):
        """Test that setting multiple flags on the same clause raises error."""
        query = Query()
        query.add("SELECT DISTINCT", "name")

        # This should raise an error since DISTINCT is already set
        with pytest.raises(ValueError, match="Flag already set"):
            query.add("SELECT ALL", "email")


class TestQueryUnsupportedClauses:
    """Test cases for unsupported SQL clauses."""

    def test_unsupported_clause_raises_error(self):
        """Test that unsupported SQL clauses raise ValueError."""
        query = Query()

        with pytest.raises(ValueError, match="Unsupported SQL clause"):
            query.add("INVALID_CLAUSE", "something")
