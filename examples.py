#!/usr/bin/env python3
"""
Example usage of QuickQL query builder.

This script demonstrates various features of the QuickQL library.
"""

from quickql import Query


def example_basic_queries():
    """Demonstrate basic query building."""
    print("=" * 60)
    print("BASIC QUERY EXAMPLES")
    print("=" * 60)

    # Simple SELECT query
    print("1. Simple SELECT:")
    query = Query().SELECT("name", "email").FROM("users").WHERE("active = 1")
    print(query)
    print()

    # SELECT with aliases
    print("2. SELECT with aliases:")
    query = (
        Query()
        .SELECT(("full_name", "name"), ("user_email", "email"))
        .FROM(("u", "users"))
        .WHERE("u.active = 1")
    )
    print(query)
    print()

    # SELECT DISTINCT
    print("3. SELECT DISTINCT:")
    query = Query()
    query.add("SELECT DISTINCT", "department").FROM("employees")
    print(query)
    print()


def example_join_queries():
    """Demonstrate JOIN operations."""
    print("=" * 60)
    print("JOIN QUERY EXAMPLES")
    print("=" * 60)

    # INNER JOIN
    print("1. INNER JOIN:")
    query = (
        Query()
        .SELECT("u.name", "p.title")
        .FROM("users u")
        .add("INNER JOIN", "posts p ON u.id = p.user_id")
        .WHERE("u.active = 1")
    )
    print(query)
    print()

    # Multiple JOINs
    print("2. Multiple JOINs:")
    query = (
        Query()
        .SELECT("u.name", "p.title", "c.content")
        .FROM("users u")
        .add("LEFT JOIN", "posts p ON u.id = p.user_id")
        .add("LEFT JOIN", "comments c ON p.id = c.post_id")
        .WHERE("u.active = 1")
        .ORDER_BY("u.name", "p.created_at DESC")
    )
    print(query)
    print()


def example_aggregate_queries():
    """Demonstrate aggregate queries."""
    print("=" * 60)
    print("AGGREGATE QUERY EXAMPLES")
    print("=" * 60)

    # GROUP BY with HAVING
    print("1. GROUP BY with HAVING:")
    query = (
        Query()
        .SELECT("department", "COUNT(*) as employee_count", "AVG(salary) as avg_salary")
        .FROM("employees")
        .WHERE("active = 1")
        .GROUP_BY("department")
        .HAVING("COUNT(*) > 5")
        .HAVING("AVG(salary) > 50000")
        .ORDER_BY("avg_salary DESC")
    )
    print(query)
    print()

    # Sales report example
    print("2. Sales report:")
    query = (
        Query()
        .SELECT(
            "p.category",
            "SUM(oi.quantity) as total_sold",
            "SUM(oi.price * oi.quantity) as revenue",
        )
        .FROM("products p")
        .add("INNER JOIN", "order_items oi ON p.id = oi.product_id")
        .add("INNER JOIN", "orders o ON oi.order_id = o.id")
        .WHERE("o.status = 'completed'")
        .WHERE("o.created_at >= '2023-01-01'")
        .GROUP_BY("p.category")
        .ORDER_BY("revenue DESC")
        .LIMIT("10")
    )
    print(query)
    print()


def example_cte_queries():
    """Demonstrate Common Table Expressions (CTEs)."""
    print("=" * 60)
    print("CTE (WITH CLAUSE) EXAMPLES")
    print("=" * 60)

    # Basic CTE
    print("1. Basic CTE:")
    cte_query = """
    SELECT user_id, COUNT(*) as post_count
    FROM posts
    WHERE created_at > '2023-01-01'
    GROUP BY user_id
    """

    query = (
        Query()
        .WITH(("active_posters", cte_query))
        .SELECT("u.name", "u.email", "ap.post_count")
        .FROM("users u")
        .add("INNER JOIN", "active_posters ap ON u.id = ap.user_id")
        .WHERE("u.active = 1")
        .ORDER_BY("ap.post_count DESC")
        .LIMIT("20")
    )
    print(query)

    # Multiple CTEs
    print("2. Multiple CTEs:")
    user_stats_cte = """
    SELECT
        user_id,
        COUNT(*) as login_count,
        MAX(login_date) as last_login
    FROM user_logins
    WHERE login_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    GROUP BY user_id
    """

    post_stats_cte = """
    SELECT
        author_id,
        COUNT(*) as post_count,
        MAX(created_at) as last_post
    FROM posts
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    GROUP BY author_id
    """

    query = (
        Query()
        .WITH(("user_stats", user_stats_cte))
        .WITH(("post_stats", post_stats_cte))
        .SELECT(
            "u.username",
            "us.login_count",
            "us.last_login",
            "ps.post_count",
            "ps.last_post",
        )
        .FROM("users u")
        .add("LEFT JOIN", "user_stats us ON u.id = us.user_id")
        .add("LEFT JOIN", "post_stats ps ON u.id = ps.author_id")
        .WHERE("u.active = 1")
        .WHERE("(us.login_count > 0 OR ps.post_count > 0)")
        .ORDER_BY("us.login_count DESC", "ps.post_count DESC")
    )
    print(query)
    print()


def example_complex_analytics():
    """Demonstrate complex analytics queries."""
    print("=" * 60)
    print("COMPLEX ANALYTICS EXAMPLES")
    print("=" * 60)

    # Monthly sales with year-over-year comparison
    print("1. Monthly sales analysis:")
    monthly_sales = """
    SELECT
        DATE_FORMAT(created_at, '%Y-%m') as month,
        SUM(total_amount) as monthly_total,
        COUNT(*) as order_count,
        AVG(total_amount) as avg_order_value
    FROM orders
    WHERE status = 'completed'
    AND created_at >= DATE_SUB(NOW(), INTERVAL 24 MONTH)
    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
    """

    query = (
        Query()
        .WITH(("monthly_sales", monthly_sales))
        .SELECT("ms.month", "ms.monthly_total", "ms.order_count", "ms.avg_order_value")
        .SELECT("LAG(ms.monthly_total, 12) OVER (ORDER BY ms.month) as prev_year_total")
        .SELECT(
            """ROUND(((ms.monthly_total - LAG(ms.monthly_total, 12)
            OVER (ORDER BY ms.month)) / LAG(ms.monthly_total, 12)
            OVER (ORDER BY ms.month)) * 100, 2) as yoy_growth_pct"""
        )
        .FROM("monthly_sales ms")
        .ORDER_BY("ms.month DESC")
        .LIMIT("12")
    )
    print(query)
    print()


def main():
    """Run all examples."""
    print("QuickQL Query Builder Examples")
    print("Generated SQL queries are formatted for readability.")
    print()

    example_basic_queries()
    example_join_queries()
    example_aggregate_queries()
    example_cte_queries()
    example_complex_analytics()

    print("=" * 60)
    print("All examples completed!")
    print("Try modifying these examples to explore QuickQL features.")
    print("=" * 60)


if __name__ == "__main__":
    main()
