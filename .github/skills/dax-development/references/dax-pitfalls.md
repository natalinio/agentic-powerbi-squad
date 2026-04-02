# DAX Pitfalls: Deprecated, Not Recommended, and Non-Existent Functions

Reference for avoiding common DAX mistakes; particularly those that AI agents generate from training data in other languages (SQL, Python, Excel, M).

> **Anti-hallucination guard**: Cross-reference this file before generating any DAX function call you are not 100% certain about.

## Functions Marked "Not Recommended" on dax.guide

These exist and execute without error but should be replaced with modern alternatives.

| Function | Status | Alternative | Why |
|---|---|---|---|
| `EARLIER(col)` | Not recommended | `VAR` | Confusing row context semantics. Capture the value in a variable before entering a nested row context |
| `EARLIEST(col)` | Not recommended | `VAR` | Same as EARLIER but retrieves from the outermost row context. Even more confusing |
| `SUMMARIZE` Name/Expression params | Deprecated | `SUMMARIZECOLUMNS` or `ADDCOLUMNS(SUMMARIZE(...))` | Extension columns in SUMMARIZE use clustering semantics that differ from what most users expect. Use SUMMARIZE only for grouping (no added columns) |

## Functions That Do Not Exist in DAX

Agents frequently hallucinate these from SQL, Python, Excel VBA, or M training data. They will cause immediate syntax errors.

| Hallucinated Function | Language Source | DAX Equivalent |
|---|---|---|
| `TRY ... CATCH` | Python, C#, JavaScript | `IFERROR(expr, fallback)` |
| `TRY ... OTHERWISE` | Power Query M | `IFERROR(expr, fallback)` |
| `ISNULL(expr)` | SQL Server | `ISBLANK(expr)` ; DAX has no null concept, only BLANK |
| `IIF(cond, true, false)` | SQL Server, VBA | `IF(cond, true, false)` |
| `NZ(expr, default)` | Access VBA | `IF(ISBLANK(expr), default, expr)` or `COALESCE(expr, default)` |
| `COALESCE(a, b, ...)` | SQL | `COALESCE(a, b, ...)` actually exists in DAX (added ~2020). But agents sometimes use SQL-style `ISNULL` or `IFNULL` instead |
| `IFNULL(expr, default)` | MySQL, SQLite | `COALESCE(expr, default)` or `IF(ISBLANK(expr), default, expr)` |
| `NVL(expr, default)` | Oracle | `COALESCE(expr, default)` |
| `CAST(expr AS type)` | SQL | `CONVERT(expr, type)` or implicit conversion |
| `SUBSTRING(text, start, len)` | SQL | `MID(text, start, len)` |
| `CONCAT(a, b)` | SQL | `a & b` (ampersand operator) or `CONCATENATE(a, b)` |
| `LEN(text)` | Excel, SQL | `LEN(text)` actually exists in DAX |
| `TRIM(text)` | Excel, SQL | `TRIM(text)` actually exists in DAX |
| `GETDATE()` | SQL Server | `TODAY()` or `NOW()` |
| `CURDATE()` | MySQL | `TODAY()` |
| `DATEDIFF(start, end, unit)` | SQL | `DATEDIFF(date1, date2, interval)` exists but parameter order and interval names differ from SQL |
| `GROUP BY` | SQL | Not a function; DAX has no GROUP BY clause. Use `SUMMARIZECOLUMNS` or `GROUPBY` |
| `HAVING` | SQL | Not a function; use `FILTER` on a summarized table |
| `JOIN` / `LEFT JOIN` | SQL | Not a function; DAX uses relationships + `RELATED`/`RELATEDTABLE`, or `NATURALINNERJOIN`/`NATURALLEFTOUTERJOIN` |
| `PIVOT` / `UNPIVOT` | SQL | Not functions; do reshaping in Power Query (M), not DAX |
| `COLLECT` / `REDUCE` | Python, JavaScript | Not functions; use iterators like `SUMX`, `MAXX`, `CONCATENATEX` |
| `MAP` / `APPLY` | Python, R | Not functions; use `ADDCOLUMNS` or iterator functions |
| `LAMBDA` | Excel, Python | Not a function; use `VAR` for intermediate expressions |
| `STRING(expr)` | Various | `FORMAT(expr, format_string)` or `CONVERT(expr, STRING)` |
| `TOSTRING(expr)` | JavaScript | `FORMAT(expr, format_string)` or `CONVERT(expr, STRING)` |
| `TOINT(expr)` / `TOFLOAT(expr)` | Python | `INT(expr)` or `CONVERT(expr, INTEGER)` / `CONVERT(expr, DOUBLE)` |
| `POWER(base, exp)` | Excel | `POWER(base, exp)` actually exists in DAX |
| `ROUND(num, digits)` | Various | `ROUND(num, digits)` actually exists in DAX |
| `ARRAY(...)` | Various | Not a function; use table constructors `{(val1, val2), ...}` |
| `PRINT` / `CONSOLE.LOG` | Various | Not functions; DAX has no output/debug statements |

## Common DAX Syntax Mistakes from Other Languages

| Mistake | Correct DAX |
|---|---|
| `-- comment` | `// comment` (double dash is not a comment in DAX) |
| `= 'text'` (single-quoted string) | `= "text"` (double-quoted; single quotes are for table names) |
| `table.column` (dot notation) | `'Table'[Column]` (bracket notation with single-quoted table) |
| `[Column]` without table (in measures) | `'Table'[Column]` (always fully qualify column references) |
| `variable = value` (assignment) | `VAR variable = value RETURN ...` (VAR/RETURN pattern required) |
| `SELECT ... FROM` | `EVALUATE ...` (DAX queries use EVALUATE, not SELECT; SELECT is for DMV only) |
| `WHERE condition` | `CALCULATETABLE(table, condition)` or `FILTER(table, condition)` |
| `ORDER BY col ASC` outside EVALUATE | `ORDER BY` must follow an `EVALUATE` expression in a DAX query |
| `!=` (not equal) | `<>` (DAX uses diamond operator for not-equal) |
| `&&` / `||` (logical) | `&&` and `||` actually work in DAX, but `AND()`/`OR()` are also valid |
| `true` / `false` (lowercase) | `TRUE()` / `FALSE()` (function syntax with parens) |
| `null` | `BLANK()` (DAX has no null literal) |

## BLANK vs NULL

DAX has no concept of NULL. The equivalent is BLANK, which behaves differently from SQL NULL:

- `BLANK() + 1` returns `1` (not BLANK); SQL NULL + 1 returns NULL
- `BLANK() & "text"` returns `"text"`; SQL NULL || 'text' returns NULL
- `IF(BLANK(), "yes", "no")` returns `"no"` (BLANK is falsy)
- `BLANK() = BLANK()` returns `TRUE`; SQL NULL = NULL returns NULL (unknown)

Use `ISBLANK()` to test, not `ISNULL()` (which does not exist).
