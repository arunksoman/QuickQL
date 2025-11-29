# QuickQL

A fluent SQL query builder for Python that makes it easy to construct complex SQL queries programmatically.

## Features

- 🚀 **Fluent Interface**: Build queries using method chaining
- 📋 **Comprehensive SQL Support**: SELECT, FROM, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT, WITH (CTEs)
- 🎯 **Type-Safe**: Built with type hints for better IDE support
- 🧪 **Well Tested**: Comprehensive test suite with >95% coverage
- 🔧 **Python 3.7+**: Supports Python 3.7 and above
- 📦 **Zero Dependencies**: No external dependencies in production

## Installation

```bash
# Using uv (recommended)
uv add quickql

# Using pip
pip install quickql
```

## Quick Start

```python
from quickql import Query

# Simple SELECT query
query = Query().SELECT("name", "email").FROM("users").WHERE("active = 1")
print(query)
```

Output:
```sql
SELECT
    name, email
FROM
    users
WHERE
    active = 1
```

## Advanced Usage

### Complex Queries with JOINs

```python
query = (Query()
    .SELECT("u.name", "u.email", "p.title")
    .FROM("users u")
    .add("LEFT JOIN", "posts p ON u.id = p.user_id")
    .WHERE("u.active = 1")
    .WHERE("p.published = 1")
    .ORDER_BY("u.name")
    .LIMIT("10"))
```

### Using Common Table Expressions (CTEs)

```python
cte_query = """
SELECT user_id, COUNT(*) as post_count
FROM posts 
WHERE created_at > '2023-01-01'
GROUP BY user_id
"""

query = (Query()
    .WITH(("active_posters", cte_query))
    .SELECT("u.name", "ap.post_count")
    .FROM("users u")
    .add("JOIN", "active_posters ap ON u.id = ap.user_id")
    .ORDER_BY("ap.post_count DESC"))
```

### Aggregate Queries

```python
query = (Query()
    .SELECT("department", "COUNT(*) as employee_count", "AVG(salary) as avg_salary")
    .FROM("employees")
    .WHERE("active = 1")
    .GROUP_BY("department")
    .HAVING("COUNT(*) > 5")
    .ORDER_BY("avg_salary DESC"))
```

## Development

### Prerequisites

- Python 3.7+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/quickql.git
cd quickql

# Run the setup script (installs dependencies and runs tests)
python setup_dev.py

# Or manually with uv
uv venv
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python run_tests.py basic      # Basic functionality tests
python run_tests.py building   # Query building tests
python run_tests.py edge       # Edge case tests
python run_tests.py integration # Integration tests
python run_tests.py coverage   # Tests with coverage report
```

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Check formatting without changing files
uv run ruff format --check .
```

### Project Structure

```
quickql/
├── src/
│   └── quickql/
│       ├── __init__.py          # Package exports
│       └── builder.py           # Main Query builder
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   ├── test_query_basic.py     # Basic functionality tests
│   ├── test_query_building.py  # Query building tests
│   ├── test_edge_cases.py      # Edge cases and error handling
│   └── test_integration.py     # Integration tests
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── pyproject.toml              # Project configuration
├── setup_dev.py               # Development setup script
├── run_tests.py               # Test runner script
└── README.md
```

## API Reference

### Query Class

The main `Query` class provides a fluent interface for building SQL queries.

#### Methods

- `SELECT(*columns)` - Add columns to SELECT clause
- `FROM(*tables)` - Add tables to FROM clause  
- `WHERE(condition)` - Add WHERE conditions (chained with AND)
- `GROUP_BY(*columns)` - Add GROUP BY columns
- `HAVING(condition)` - Add HAVING conditions (chained with AND)
- `ORDER_BY(*columns)` - Add ORDER BY columns
- `LIMIT(limit)` - Add LIMIT clause
- `WITH((name, query))` - Add Common Table Expression
- `add(clause, *args)` - Generic method to add any clause

#### JOIN Operations

Use the `add()` method for JOINs:

```python
query.add("INNER JOIN", "table2 ON table1.id = table2.foreign_id")
query.add("LEFT JOIN", "table3 ON table1.id = table3.foreign_id")
query.add("RIGHT JOIN", "table4 ON table1.id = table4.foreign_id")
query.add("FULL JOIN", "table5 ON table1.id = table5.foreign_id")
```

#### Flags

Some clauses support flags:

```python
query.add("SELECT DISTINCT", "column")  # SELECT DISTINCT
query.add("SELECT ALL", "column")       # SELECT ALL
```

## Releasing

### Creating Releases

This project uses automated PyPI publishing via GitHub Actions. To create a release:

```bash
# Verify the build works
python verify_build.py

# Create a release (this will trigger PyPI publishing)
python release.py 0.1.1

# Or create a release candidate (publishes to TestPyPI)
python release.py 0.2.0rc1
```

The release process:
1. Updates version in `pyproject.toml`
2. Creates a git tag
3. Pushes the tag to GitHub
4. GitHub Actions automatically builds and publishes to PyPI
5. Creates a GitHub release with signed artifacts

For detailed setup instructions, see [PUBLISHING.md](PUBLISHING.md).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python run_tests.py all`)
5. Run code quality checks (`uv run ruff check . && uv run ruff format --check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0 (Initial Release)

- Fluent query builder interface
- Support for all major SQL clauses
- JOIN operations support
- Common Table Expressions (WITH)
- Comprehensive test suite
- Python 3.7+ support