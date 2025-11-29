"""
Integration tests for the QuickQL package.
"""

from quickql import Query


class TestIntegration:
    """Integration tests that test the full workflow."""

    def test_import_from_package(self):
        """Test that Query can be imported from the main package."""
        # This should not raise ImportError
        from quickql import Query

        query = Query()
        assert query is not None

    def test_realistic_user_management_queries(self):
        """Test realistic queries for user management system."""

        # Get all active users with their profile info
        query1 = (
            Query()
            .SELECT("u.id", "u.username", "u.email", "p.first_name", "p.last_name")
            .FROM("users u")
            .add("LEFT JOIN", "user_profiles p ON u.id = p.user_id")
            .WHERE("u.active = 1")
            .WHERE("u.email_verified = 1")
            .ORDER_BY("u.username")
        )

        sql1 = str(query1)
        assert all(
            clause in sql1
            for clause in ["SELECT", "FROM", "LEFT JOIN", "WHERE", "ORDER BY"]
        )
        assert "u.active = 1 AND u.email_verified = 1" in sql1

        # Get users with post counts
        query2 = (
            Query()
            .SELECT("u.username", "u.email", "COUNT(p.id) as post_count")
            .FROM("users u")
            .add("LEFT JOIN", "posts p ON u.id = p.author_id")
            .WHERE("u.active = 1")
            .GROUP_BY("u.id", "u.username", "u.email")
            .HAVING("COUNT(p.id) >= 5")
            .ORDER_BY("post_count DESC")
            .LIMIT("20")
        )

        sql2 = str(query2)
        assert "GROUP BY" in sql2
        assert "HAVING" in sql2
        assert "COUNT(p.id) >= 5" in sql2

    def test_realistic_ecommerce_queries(self):
        """Test realistic queries for e-commerce system."""

        # Get product sales report
        query = (
            Query()
            .SELECT(
                "p.name",
                "p.category",
                "SUM(oi.quantity) as total_sold",
                "SUM(oi.price * oi.quantity) as revenue",
            )
            .FROM("products p")
            .add("INNER JOIN", "order_items oi ON p.id = oi.product_id")
            .add("INNER JOIN", "orders o ON oi.order_id = o.id")
            .WHERE("o.status = 'completed'")
            .WHERE("o.created_at >= '2023-01-01'")
            .WHERE("o.created_at < '2024-01-01'")
            .GROUP_BY("p.id", "p.name", "p.category")
            .HAVING("SUM(oi.quantity) > 10")
            .ORDER_BY("revenue DESC", "total_sold DESC")
            .LIMIT("100")
        )

        sql = str(query)
        assert "SUM(oi.quantity) as total_sold" in sql
        assert "SUM(oi.price * oi.quantity) as revenue" in sql
        assert "o.status = 'completed'" in sql
        assert "o.created_at >= '2023-01-01' AND o.created_at < '2024-01-01'" in sql

    def test_complex_reporting_with_cte(self):
        """Test complex reporting query with Common Table Expression."""

        # Monthly sales summary with year-over-year comparison
        monthly_sales_cte = """
        SELECT
            DATE_FORMAT(created_at, '%Y-%m') as month,
            SUM(total_amount) as monthly_total,
            COUNT(*) as order_count
        FROM orders
        WHERE status = 'completed'
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        """

        query = (
            Query()
            .WITH(("monthly_sales", monthly_sales_cte))
            .SELECT(
                "ms.month",
                "ms.monthly_total",
                "ms.order_count",
                "LAG(ms.monthly_total, 12) OVER (ORDER BY ms.month) as prev_year_total",
            )
            .FROM("monthly_sales ms")
            .ORDER_BY("ms.month DESC")
            .LIMIT("24")
        )

        sql = str(query)
        assert "WITH" in sql
        assert "monthly_sales AS" in sql
        assert "DATE_FORMAT(created_at, '%Y-%m') as month" in sql
        assert "LAG(ms.monthly_total, 12)" in sql

    def test_data_analytics_queries(self):
        """Test data analytics style queries."""

        # User engagement metrics
        user_activity_cte = """
        SELECT
            user_id,
            COUNT(*) as login_count,
            MAX(created_at) as last_login,
            MIN(created_at) as first_login,
            DATEDIFF(MAX(created_at), MIN(created_at)) as days_active
        FROM user_sessions
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY user_id
        """

        query = (
            Query()
            .WITH(("user_activity", user_activity_cte))
            .SELECT(
                "u.username",
                "u.email",
                "ua.login_count",
                "ua.last_login",
                "ua.days_active",
                "CASE WHEN ua.login_count >= 20 THEN 'High' "
                + "WHEN ua.login_count >= 5 THEN 'Medium' ELSE 'Low' "
                + "END as engagement_level",
            )
            .FROM("users u")
            .add("INNER JOIN", "user_activity ua ON u.id = ua.user_id")
            .WHERE("u.active = 1")
            .ORDER_BY("ua.login_count DESC", "ua.last_login DESC")
        )

        sql = str(query)
        assert "CASE WHEN ua.login_count >= 20" in sql
        assert "DATEDIFF(MAX(created_at), MIN(created_at))" in sql
        assert "DATE_SUB(NOW(), INTERVAL 30 DAY)" in sql

    def test_migration_and_maintenance_queries(self):
        """Test queries typically used for data migration and maintenance."""

        # Find duplicate records
        query1 = (
            Query()
            .SELECT("email", "COUNT(*) as duplicate_count")
            .FROM("users")
            .GROUP_BY("email")
            .HAVING("COUNT(*) > 1")
            .ORDER_BY("duplicate_count DESC")
        )

        sql1 = str(query1)
        assert "COUNT(*) > 1" in sql1

        # Find orphaned records
        query2 = (
            Query()
            .SELECT("p.id", "p.title", "p.author_id")
            .FROM("posts p")
            .add("LEFT JOIN", "users u ON p.author_id = u.id")
            .WHERE("u.id IS NULL")
        )

        sql2 = str(query2)
        assert "LEFT JOIN" in sql2
        assert "u.id IS NULL" in sql2

    def test_query_builder_fluency(self):
        """Test the fluent interface feels natural to use."""

        # Should be able to build queries in a readable, natural way
        query = (
            Query()
            .SELECT("customers.name", "customers.email")
            .SELECT(
                "COUNT(orders.id) as order_count"
            )  # Additional SELECT calls should work
            .SELECT("SUM(orders.total) as lifetime_value")
            .FROM("customers")
            .add("LEFT JOIN", "orders ON customers.id = orders.customer_id")
            .WHERE("customers.active = 1")
            .WHERE("customers.created_at >= '2023-01-01'")
            .GROUP_BY("customers.id", "customers.name", "customers.email")
            .HAVING("COUNT(orders.id) >= 3")
            .ORDER_BY("lifetime_value DESC")
            .ORDER_BY("order_count DESC")  # Multiple ORDER BY calls should work
            .LIMIT("50")
        )

        sql = str(query)

        # Should contain all the expected parts
        expected_parts = [
            "customers.name, customers.email, COUNT(orders.id) as order_count, SUM(orders.total) as lifetime_value", #noqa
            "FROM\n    customers",
            "LEFT JOIN",
            "customers.active = 1 AND customers.created_at >= '2023-01-01'",
            "GROUP BY",
            "HAVING\n    COUNT(orders.id) >= 3",
            "ORDER BY\n    lifetime_value DESC, order_count DESC",
            "LIMIT\n    50",
        ]

        for part in expected_parts:
            assert part in sql, f"Expected '{part}' not found in:\n{sql}"

    def test_real_world_performance_query(self):
        """Test a real-world performance monitoring query."""

        slow_queries_cte = """
        SELECT
            query_hash,
            COUNT(*) as execution_count,
            AVG(execution_time_ms) as avg_time,
            MAX(execution_time_ms) as max_time,
            SUM(execution_time_ms) as total_time
        FROM query_performance_log
        WHERE logged_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
        AND execution_time_ms > 1000
        GROUP BY query_hash
        """

        query = (
            Query()
            .WITH(("slow_queries", slow_queries_cte))
            .SELECT(
                "sq.query_hash",
                "sq.execution_count",
                "sq.avg_time",
                "sq.max_time",
                "sq.total_time",
            )
            .SELECT("qd.query_text", "qd.database_name", "qd.table_names")
            .FROM("slow_queries sq")
            .add("LEFT JOIN", "query_definitions qd ON sq.query_hash = qd.hash")
            .WHERE("sq.avg_time > 5000")  # Queries averaging > 5 seconds
            .ORDER_BY("sq.total_time DESC")  # Order by total impact
            .LIMIT("20")
        )

        sql = str(query)
        assert "DATE_SUB(NOW(), INTERVAL 1 HOUR)" in sql
        assert "execution_time_ms > 1000" in sql
        assert "sq.avg_time > 5000" in sql
