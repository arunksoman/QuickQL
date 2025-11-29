from dataclasses import dataclass
from enum import Enum
import textwrap
from typing import Dict, List, Optional, Union


class SQLKeyword(Enum):
    """SQL keywords supported by the query builder."""

    WITH = "WITH"
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    GROUP_BY = "GROUP BY"
    HAVING = "HAVING"
    ORDER_BY = "ORDER BY"
    LIMIT = "LIMIT"


class SQLFlag(Enum):
    """SQL flags that can modify keywords."""

    DISTINCT = "DISTINCT"
    ALL = "ALL"


@dataclass
class QueryElement:
    """Represents a single element in a SQL query (column, table, condition, etc.)."""

    value: str
    alias: str = ""
    join_keyword: str = ""  # For JOIN clauses like INNER JOIN, LEFT JOIN
    is_subquery: bool = False

    @classmethod
    def create(cls, arg: Union[str, tuple], **kwargs) -> "QueryElement":
        """Create a QueryElement from various input formats."""
        if isinstance(arg, str):
            return cls(value=_normalize_sql(arg), **kwargs)
        elif isinstance(arg, (list, tuple)) and len(arg) == 2:
            alias, value = arg
            return cls(
                value=_normalize_sql(value), alias=_normalize_sql(alias), **kwargs
            )
        else:
            raise ValueError(f"Invalid argument format: {arg!r}")


class ClauseCollection:
    """Manages a collection of query elements for a specific SQL clause."""

    def __init__(self):
        self.elements: List[QueryElement] = []
        self.flag: Optional[str] = None

    def add_element(self, element: QueryElement) -> None:
        """Add a query element to this clause."""
        self.elements.append(element)

    def set_flag(self, flag: str) -> None:
        """Set a flag for this clause (e.g., DISTINCT for SELECT)."""
        if self.flag:
            raise ValueError(f"Flag already set to '{self.flag}', cannot set '{flag}'")
        self.flag = flag

    def is_empty(self) -> bool:
        """Check if this clause has any elements."""
        return len(self.elements) == 0

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)


class Query:
    """
    A fluent SQL query builder that constructs queries through method chaining.

    Usage:
        query = QueryBuilder()
        query.SELECT("name", "email").FROM("users").WHERE("active = 1")
        print(str(query))  # Outputs formatted SQL
    """

    # Configuration for how different clauses are formatted and separated
    CLAUSE_SEPARATORS = {
        SQLKeyword.WHERE: " AND ",
        SQLKeyword.HAVING: " AND ",
    }

    DEFAULT_SEPARATOR = ", "

    # Keywords that support flags
    FLAGGABLE_KEYWORDS = {SQLKeyword.SELECT: {SQLFlag.DISTINCT, SQLFlag.ALL}}

    # Keywords that support subqueries
    SUBQUERY_KEYWORDS = {SQLKeyword.WITH}

    # JOIN aliases that map to FROM clause
    JOIN_ALIASES = {
        "JOIN": "FROM",
        "INNER JOIN": "FROM",
        "LEFT JOIN": "FROM",
        "RIGHT JOIN": "FROM",
        "FULL JOIN": "FROM",
        "CROSS JOIN": "FROM",
    }

    def __init__(self):
        """Initialize a new query builder."""
        self._clauses: Dict[SQLKeyword, ClauseCollection] = {
            keyword: ClauseCollection() for keyword in SQLKeyword
        }

    def add(self, clause_name: str, *args) -> "Query":
        """
        Add elements to a SQL clause.

        Args:
            clause_name: The SQL clause name (e.g., "SELECT", "WHERE")
            *args: Elements to add to the clause

        Returns:
            Self for method chaining
        """
        # Handle JOIN aliases
        actual_clause, join_keyword = self._resolve_join_alias(clause_name)

        # Handle flags (e.g., "SELECT DISTINCT")
        actual_clause, flag = self._parse_flag(actual_clause)

        # Get the SQL keyword enum
        try:
            keyword = SQLKeyword(actual_clause)
        except ValueError as e:
            raise ValueError(f"Unsupported SQL clause: {actual_clause}") from e

        clause_collection = self._clauses[keyword]

        # Set flag if present
        if flag:
            clause_collection.set_flag(flag)

        # Add elements to the clause
        for arg in args:
            kwargs = {}
            if join_keyword:
                kwargs["join_keyword"] = join_keyword
            if keyword in self.SUBQUERY_KEYWORDS:
                kwargs["is_subquery"] = True

            element = QueryElement.create(arg, **kwargs)
            clause_collection.add_element(element)

        return self

    def _resolve_join_alias(self, clause_name: str) -> tuple[str, str]:
        """Resolve JOIN aliases to their actual clause and extract join type."""
        for join_type, actual_clause in self.JOIN_ALIASES.items():
            if join_type in clause_name:
                return actual_clause, clause_name
        return clause_name, ""

    def _parse_flag(self, clause_name: str) -> tuple[str, str]:
        """Parse flags from clause names.
        Example: 'SELECT DISTINCT' -> 'SELECT', 'DISTINCT'
        """
        parts = clause_name.split()
        if len(parts) == 1:
            return clause_name, ""

        base_clause, potential_flag = parts[0], parts[1]

        try:
            keyword = SQLKeyword(base_clause)
            if keyword in self.FLAGGABLE_KEYWORDS:
                try:
                    flag = SQLFlag(potential_flag)
                    if flag in self.FLAGGABLE_KEYWORDS[keyword]:
                        return base_clause, potential_flag
                except ValueError:
                    pass
        except ValueError:
            pass

        return clause_name, ""

    def __getattr__(self, name: str):
        """Enable fluent interface for SQL clauses (e.g., query.SELECT(...))."""
        if name.isupper():
            clause_name = name.replace("_", " ")
            return lambda *args: self.add(clause_name, *args)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def build(self) -> str:
        """Build and return the complete SQL query string."""
        sql_parts = []

        for keyword in SQLKeyword:
            clause = self._clauses[keyword]
            if clause.is_empty():
                continue

            # Add the keyword and optional flag
            if clause.flag:
                sql_parts.append(f"{keyword.value} {clause.flag}")
            else:
                sql_parts.append(keyword.value)

            # Group elements by join type for proper formatting
            join_groups = self._group_elements_by_join(clause.elements)

            for join_keyword, elements in join_groups.items():
                if join_keyword:
                    sql_parts.append(join_keyword)

                # Format elements in this group
                formatted_elements = []
                for element in elements:
                    formatted = self._format_element(keyword, element)
                    formatted_elements.append(formatted)

                # Join elements with appropriate separator
                separator = self.CLAUSE_SEPARATORS.get(keyword, self.DEFAULT_SEPARATOR)
                joined_elements = separator.join(formatted_elements)
                sql_parts.append(_indent_text(joined_elements))

        return "\n".join(sql_parts)

    def _group_elements_by_join(
        self, elements: List[QueryElement]
    ) -> Dict[str, List[QueryElement]]:
        """Group elements by their join keywords for proper formatting."""
        groups = {"": []}  # Default group for non-JOIN elements

        for element in elements:
            join_key = element.join_keyword
            if join_key not in groups:
                groups[join_key] = []
            groups[join_key].append(element)

        return groups

    def _format_element(self, keyword: SQLKeyword, element: QueryElement) -> str:
        """Format a single query element based on the clause type."""
        value = element.value

        # Handle subqueries
        if element.is_subquery:
            value = f"(\n{_indent_text(value)}\n)"

        # Handle aliases
        if element.alias:
            if keyword == SQLKeyword.WITH:
                return f"{element.alias} AS {value}"
            else:
                return f"{value} AS {element.alias}"

        return value

    def __str__(self) -> str:
        """Return the built SQL query."""
        return self.build()


def _normalize_sql(text: str) -> str:
    """Normalize SQL text by removing extra whitespace and formatting."""
    return textwrap.dedent(str(text).rstrip()).strip()


def _indent_text(text: str, spaces: int = 4) -> str:
    """Indent text with the specified number of spaces."""
    return textwrap.indent(text, " " * spaces)
