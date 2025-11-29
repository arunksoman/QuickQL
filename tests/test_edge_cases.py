"""
Tests for edge cases and error handling.
"""

import pytest

from quickql import Query
from quickql.builder import QueryElement


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions."""

    def test_empty_query(self):
        """Test building an empty query."""
        query = Query()
        sql = str(query)

        # Should return empty string or minimal valid SQL
        assert sql == ""  # No clauses added

    def test_query_with_only_select(self):
        """Test query with only SELECT clause."""
        query = Query().SELECT("*")
        sql = str(query)

        assert "SELECT" in sql
        assert "*" in sql
        # Should not contain FROM, WHERE, etc.
        assert "FROM" not in sql
        assert "WHERE" not in sql

    def test_whitespace_handling_in_sql(self):
        """Test handling of whitespace in SQL strings."""
        query = Query().SELECT("  name  ", "  email  ").FROM("  users  ")
        sql = str(query)

        # Whitespace should be normalized
        assert "name" in sql
        assert "email" in sql
        assert "users" in sql

    def test_multiline_sql_strings(self):
        """Test handling of multiline SQL strings."""
        multiline_condition = """
        user_id IN (
            SELECT id FROM active_users 
            WHERE last_login > '2023-01-01'
        )
        """

        query = Query().SELECT("*").FROM("posts").WHERE(multiline_condition)
        sql = str(query)

        assert "user_id IN" in sql
        assert "SELECT id FROM active_users" in sql

    def test_very_long_query(self):
        """Test building a very long query with many elements."""
        query = Query()

        # Add many SELECT columns
        columns = [f"col{i}" for i in range(50)]
        query.SELECT(*columns)
        query.FROM("big_table")

        # Add many WHERE conditions
        conditions = [f"col{i} > {i}" for i in range(20)]
        for condition in conditions:
            query.WHERE(condition)

        sql = str(query)
        assert "col0, col1, col2" in sql  # First few columns
        assert "col48, col49" in sql  # Last few columns
        assert "col0 > 0 AND col1 > 1" in sql  # First few conditions

    def test_special_characters_in_strings(self):
        """Test handling of special characters in SQL strings."""
        query = (
            Query()
            .SELECT("name", "description")
            .FROM("products")
            .WHERE("description LIKE '%special & chars%'")
            .WHERE("name != 'O''Reilly'")
        )  # Single quote handling

        sql = str(query)
        assert "special & chars" in sql
        assert "O''Reilly" in sql

    def test_case_sensitivity(self):
        """Test case sensitivity handling."""
        query = Query()

        # Only uppercase methods should work
        query.SELECT("name").FROM("users")  # uppercase methods
        query.WHERE("Active = 1")  # Mixed case in SQL

        # Should not raise errors and should preserve case in SQL strings
        sql = str(query)
        assert "Active = 1" in sql


class TestErrorHandling:
    """Test cases for error conditions and exception handling."""

    def test_invalid_tuple_length_in_query_element(self):
        """Test QueryElement with invalid tuple length."""
        with pytest.raises(ValueError, match="Invalid argument format"):
            QueryElement.create((1, 2, 3, 4))  # Too many elements

        with pytest.raises(ValueError, match="Invalid argument format"):
            QueryElement.create(tuple())  # Empty tuple

    def test_unsupported_sql_clause(self):
        """Test adding unsupported SQL clauses."""
        query = Query()

        with pytest.raises(ValueError, match="Unsupported SQL clause"):
            query.add("MERGE", "INTO target")

        with pytest.raises(ValueError, match="Unsupported SQL clause"):
            query.add("UPSERT", "users")

    def test_invalid_flag_for_clause(self):
        """Test invalid flags for SQL clauses."""
        query = Query()

        # DISTINCT should work with SELECT
        query.add("SELECT DISTINCT", "name")  # Should work

        # But invalid combinations should raise errors
        with pytest.raises(ValueError, match="Unsupported SQL clause"):
            query.add("FROM DISTINCT", "users")  # Should raise error

        # Valid query should still work
        sql = str(query)
        assert "SELECT DISTINCT" in sql

    def test_method_name_edge_cases(self):
        """Test edge cases in method name handling."""
        query = Query()

        # Valid uppercase methods
        query.SELECT_DISTINCT("name")  # Should work (converts _ to space)

        # Invalid method names
        with pytest.raises(AttributeError):
            query.lowercase_method()  # Should fail (not uppercase)

        with pytest.raises(AttributeError):
            query.Mixed_Case()  # Should fail (not all uppercase)

    def test_none_values_handling(self):
        """Test handling of None values in queries."""
        query = Query()

        # These should handle None gracefully or raise appropriate errors
        with pytest.raises(Exception):  # Should raise some form of error
            query.SELECT(None)

        with pytest.raises(Exception):
            query.FROM(None)

    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        query = Query()

        # Empty strings should be handled gracefully
        query.SELECT("")  # Might be valid in some contexts
        query.FROM("users")

        sql = str(query)
        # Should not crash, though result might not be meaningful
        assert isinstance(sql, str)


class TestMemoryAndPerformance:
    """Test cases for memory usage and performance characteristics."""

    def test_query_reuse(self):
        """Test reusing the same Query instance."""
        query = Query()

        # Build first query
        query.SELECT("name").FROM("users")
        sql1 = str(query)

        # Add more to the same query
        query.WHERE("active = 1")
        sql2 = str(query)

        # sql2 should include everything from sql1 plus the WHERE clause
        assert "SELECT" in sql1 and "SELECT" in sql2
        assert "FROM" in sql1 and "FROM" in sql2
        assert "WHERE" not in sql1 and "WHERE" in sql2

    def test_multiple_builds(self):
        """Test calling build() multiple times."""
        query = Query().SELECT("*").FROM("users").WHERE("active = 1")

        # Multiple calls to build() should return the same result
        sql1 = query.build()
        sql2 = query.build()
        sql3 = str(query)

        assert sql1 == sql2 == sql3

    def test_deep_copy_behavior(self):
        """Test that queries don't interfere with each other."""
        base_query = Query().SELECT("*").FROM("users")

        # Create two "branches" from the base
        query1 = Query().SELECT("*").FROM("users").WHERE("active = 1")
        query2 = Query().SELECT("*").FROM("users").WHERE("deleted = 0")

        sql1 = str(query1)
        sql2 = str(query2)

        # They should be different
        assert "active = 1" in sql1 and "active = 1" not in sql2
        assert "deleted = 0" in sql2 and "deleted = 0" not in sql1


class TestDataTypeHandling:
    """Test cases for different data types in queries."""

    def test_numeric_values(self):
        """Test handling of numeric values."""
        query = (
            Query()
            .SELECT("*")
            .FROM("products")
            .WHERE("price > 100")
            .WHERE("quantity < 50")
        )

        sql = str(query)
        assert "price > 100" in sql
        assert "quantity < 50" in sql

    def test_string_values_with_quotes(self):
        """Test handling of quoted string values."""
        query = (
            Query()
            .SELECT("*")
            .FROM("users")
            .WHERE("name = 'John Doe'")
            .WHERE("email LIKE '%@example.com'")
        )

        sql = str(query)
        assert "name = 'John Doe'" in sql
        assert "email LIKE '%@example.com'" in sql

    def test_boolean_like_values(self):
        """Test handling of boolean-like values."""
        query = (
            Query()
            .SELECT("*")
            .FROM("users")
            .WHERE("active = TRUE")
            .WHERE("deleted = FALSE")
            .WHERE("verified IS NOT NULL")
        )

        sql = str(query)
        assert "active = TRUE" in sql
        assert "deleted = FALSE" in sql
        assert "verified IS NOT NULL" in sql
