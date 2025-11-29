"""
Tests for SQL query building and formatting.
"""

from quickql import Query


class TestSelectQueries:
    """Test cases for SELECT queries."""

    def test_simple_select_all(self):
        """Test SELECT * query."""
        query = Query().SELECT("*").FROM("users")

        expected = "SELECT\n    *\nFROM\n    users"
        assert str(query) == expected

    def test_select_multiple_columns(self):
        """Test SELECT with multiple columns."""
        query = Query().SELECT("name", "email", "age").FROM("users")

        sql = str(query)
        assert "SELECT" in sql
        assert "name, email, age" in sql
        assert "FROM" in sql
        assert "users" in sql

    def test_select_with_aliases(self):
        """Test SELECT with column aliases."""
        query = (
            Query().SELECT(("full_name", "name"), ("user_email", "email")).FROM("users")
        )

        sql = str(query)
        assert "name AS full_name" in sql
        assert "email AS user_email" in sql

    def test_select_distinct(self):
        """Test SELECT DISTINCT."""
        query = Query()
        query.add("SELECT DISTINCT", "department").FROM("employees")

        sql = str(query)
        assert "SELECT DISTINCT" in sql
        assert "department" in sql


class TestFromQueries:
    """Test cases for FROM clauses."""

    def test_simple_from(self):
        """Test basic FROM clause."""
        query = Query().SELECT("*").FROM("users")

        sql = str(query)
        assert "FROM\n    users" in sql

    def test_from_with_alias(self):
        """Test FROM with table alias."""
        query = Query().SELECT("*").FROM(("u", "users"))

        sql = str(query)
        assert "users AS u" in sql

    def test_multiple_tables(self):
        """Test FROM with multiple tables (cross join)."""
        query = Query().SELECT("*").FROM("users", "posts")

        sql = str(query)
        assert "users, posts" in sql


class TestWhereQueries:
    """Test cases for WHERE clauses."""

    def test_simple_where(self):
        """Test basic WHERE clause."""
        query = Query().SELECT("*").FROM("users").WHERE("active = 1")

        sql = str(query)
        assert "WHERE\n    active = 1" in sql

    def test_multiple_where_conditions(self):
        """Test WHERE with multiple conditions."""
        query = Query().SELECT("*").FROM("users").WHERE("active = 1").WHERE("age > 18")

        sql = str(query)
        assert "WHERE" in sql
        assert "active = 1 AND age > 18" in sql

    def test_complex_where_conditions(self):
        """Test WHERE with complex conditions."""
        query = (
            Query()
            .SELECT("name", "email")
            .FROM("users")
            .WHERE("active = 1")
            .WHERE("(age > 18 OR verified = 1)")
            .WHERE("created_at > '2023-01-01'")
        )

        sql = str(query)
        assert (
            "active = 1 AND (age > 18 OR verified = 1) AND created_at > '2023-01-01'"
            in sql
        )


class TestJoinQueries:
    """Test cases for JOIN clauses."""

    def test_inner_join(self):
        """Test INNER JOIN."""
        query = (
            Query()
            .SELECT("u.name", "p.title")
            .FROM("users u")
            .add("INNER JOIN", "posts p ON u.id = p.user_id")
        )

        sql = str(query)
        assert "INNER JOIN" in sql
        assert "posts p ON u.id = p.user_id" in sql

    def test_left_join(self):
        """Test LEFT JOIN."""
        query = (
            Query()
            .SELECT("u.name", "p.title")
            .FROM("users u")
            .add("LEFT JOIN", "posts p ON u.id = p.user_id")
        )

        sql = str(query)
        assert "LEFT JOIN" in sql
        assert "posts p ON u.id = p.user_id" in sql

    def test_multiple_joins(self):
        """Test multiple JOINs."""
        query = (
            Query()
            .SELECT("u.name", "p.title", "c.content")
            .FROM("users u")
            .add("INNER JOIN", "posts p ON u.id = p.user_id")
            .add("LEFT JOIN", "comments c ON p.id = c.post_id")
        )

        sql = str(query)
        assert "INNER JOIN" in sql
        assert "LEFT JOIN" in sql
        assert "posts p ON u.id = p.user_id" in sql
        assert "comments c ON p.id = c.post_id" in sql

    def test_right_join(self):
        """Test RIGHT JOIN."""
        query = (
            Query()
            .SELECT("u.name", "p.title")
            .FROM("users u")
            .add("RIGHT JOIN", "posts p ON u.id = p.user_id")
        )

        sql = str(query)
        assert "RIGHT JOIN" in sql

    def test_full_join(self):
        """Test FULL JOIN."""
        query = (
            Query()
            .SELECT("u.name", "p.title")
            .FROM("users u")
            .add("FULL JOIN", "posts p ON u.id = p.user_id")
        )

        sql = str(query)
        assert "FULL JOIN" in sql

    def test_cross_join(self):
        """Test CROSS JOIN."""
        query = (
            Query()
            .SELECT("u.name", "p.title")
            .FROM("users u")
            .add("CROSS JOIN", "posts p")
        )

        sql = str(query)
        assert "CROSS JOIN" in sql


class TestOrderByQueries:
    """Test cases for ORDER BY clauses."""

    def test_simple_order_by(self):
        """Test basic ORDER BY."""
        query = Query().SELECT("*").FROM("users").ORDER_BY("name")

        sql = str(query)
        assert "ORDER BY\n    name" in sql

    def test_multiple_order_by(self):
        """Test ORDER BY with multiple columns."""
        query = Query().SELECT("*").FROM("users").ORDER_BY("name", "age DESC")

        sql = str(query)
        assert "ORDER BY\n    name, age DESC" in sql

    def test_order_by_with_aliases(self):
        """Test ORDER BY with column aliases."""
        query = Query().SELECT("*").FROM("users").ORDER_BY(("sort_name", "name"))

        sql = str(query)
        assert "name AS sort_name" in sql


class TestGroupByHaving:
    """Test cases for GROUP BY and HAVING clauses."""

    def test_group_by(self):
        """Test GROUP BY clause."""
        query = (
            Query()
            .SELECT("department", "COUNT(*) as count")
            .FROM("employees")
            .GROUP_BY("department")
        )

        sql = str(query)
        assert "GROUP BY\n    department" in sql

    def test_group_by_with_having(self):
        """Test GROUP BY with HAVING."""
        query = (
            Query()
            .SELECT("department", "COUNT(*) as count")
            .FROM("employees")
            .GROUP_BY("department")
            .HAVING("COUNT(*) > 5")
        )

        sql = str(query)
        assert "GROUP BY\n    department" in sql
        assert "HAVING\n    COUNT(*) > 5" in sql

    def test_multiple_having_conditions(self):
        """Test HAVING with multiple conditions."""
        query = (
            Query()
            .SELECT("department", "COUNT(*) as count", "AVG(salary) as avg_salary")
            .FROM("employees")
            .GROUP_BY("department")
            .HAVING("COUNT(*) > 5")
            .HAVING("AVG(salary) > 50000")
        )

        sql = str(query)
        assert "COUNT(*) > 5 AND AVG(salary) > 50000" in sql


class TestLimitQueries:
    """Test cases for LIMIT clauses."""

    def test_simple_limit(self):
        """Test basic LIMIT clause."""
        query = Query().SELECT("*").FROM("users").LIMIT("10")

        sql = str(query)
        assert "LIMIT\n    10" in sql

    def test_limit_with_offset(self):
        """Test LIMIT with offset."""
        query = Query().SELECT("*").FROM("users").LIMIT("10 OFFSET 20")

        sql = str(query)
        assert "LIMIT\n    10 OFFSET 20" in sql


class TestWithQueries:
    """Test cases for WITH (CTE) clauses."""

    def test_simple_with_clause(self):
        """Test basic WITH clause."""
        cte_query = "SELECT id, name FROM users WHERE active = 1"
        query = (
            Query().WITH(("active_users", cte_query)).SELECT("*").FROM("active_users")
        )

        sql = str(query)
        assert "WITH" in sql
        assert "active_users AS" in sql
        assert cte_query in sql

    def test_multiple_with_clauses(self):
        """Test WITH with multiple CTEs."""
        cte1 = "SELECT id, name FROM users WHERE active = 1"
        cte2 = "SELECT user_id, COUNT(*) as post_count FROM posts GROUP BY user_id"

        query = (
            Query()
            .WITH(("active_users", cte1))
            .WITH(("user_posts", cte2))
            .SELECT("au.name", "up.post_count")
            .FROM("active_users au")
            .add("JOIN", "user_posts up ON au.id = up.user_id")
        )

        sql = str(query)
        assert "active_users AS" in sql
        assert "user_posts AS" in sql
        assert cte1 in sql
        assert cte2 in sql


class TestComplexQueries:
    """Test cases for complex multi-clause queries."""

    def test_full_complex_query(self):
        """Test a complex query with all major clauses."""
        query = (
            Query()
            .SELECT("u.name", "u.email", "COUNT(p.id) as post_count")
            .FROM("users u")
            .add("LEFT JOIN", "posts p ON u.id = p.user_id")
            .WHERE("u.active = 1")
            .WHERE("u.created_at > '2023-01-01'")
            .GROUP_BY("u.id", "u.name", "u.email")
            .HAVING("COUNT(p.id) > 0")
            .ORDER_BY("post_count DESC", "u.name")
            .LIMIT("50")
        )

        sql = str(query)

        # Check all major clauses are present
        assert "SELECT" in sql
        assert "FROM" in sql
        assert "LEFT JOIN" in sql
        assert "WHERE" in sql
        assert "GROUP BY" in sql
        assert "HAVING" in sql
        assert "ORDER BY" in sql
        assert "LIMIT" in sql

        # Check proper formatting
        assert "u.active = 1 AND u.created_at > '2023-01-01'" in sql
        assert "post_count DESC, u.name" in sql

    def test_query_with_subquery_in_with(self):
        """Test complex query with subquery in WITH clause."""
        subquery = """
        SELECT
            user_id,
            COUNT(*) as comment_count,
            MAX(created_at) as last_comment
        FROM comments
        WHERE created_at > '2023-01-01'
        GROUP BY user_id
        """

        query = (
            Query()
            .WITH(("recent_commenters", subquery))
            .SELECT("u.name", "rc.comment_count", "rc.last_comment")
            .FROM("users u")
            .add("INNER JOIN", "recent_commenters rc ON u.id = rc.user_id")
            .WHERE("u.active = 1")
            .ORDER_BY("rc.comment_count DESC")
        )

        sql = str(query)
        assert "WITH" in sql
        assert "recent_commenters AS" in sql
        assert "COUNT(*) as comment_count" in sql
