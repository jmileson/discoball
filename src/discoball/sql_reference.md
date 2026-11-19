# SQL reference: Working with DuckDB

Use this page when a lesson raises a SQL question. You do not need to read it from start
to finish before continuing.

If you already use SQL Server, much will look familiar. Some differences are database
behavior; others are just how this project formats SQL. The labels below distinguish
**General SQL**, **DuckDB**, and **Project style**.

Run the examples in DBeaver against your local `.data/dev.duckdb`. Each example is
independent except the explicitly marked temporary-object script. The examples read
source tables; they do not update them.

## Find what you need

- [Query structure and execution order](#1-query-structure-and-execution-order)
- [SQL Server translation guide](#2-sql-server-translation-guide)
- [Names, strings, and formatting](#3-names-strings-and-formatting)
- [Types, arithmetic, and conditional expressions](#4-types-arithmetic-and-conditional-expressions)
- [Missing values and filtering](#5-missing-values-and-filtering)
- [Aggregation and grain](#6-aggregation-and-grain)
- [Joins and row multiplication](#7-joins-and-row-multiplication)
- [Dates and timestamps](#8-dates-and-timestamps)
- [CTEs, views, and tables](#9-ctes-views-and-tables)
- [Useful DuckDB additions](#10-useful-duckdb-additions)

## 1. Query structure and execution order

**General SQL:** choose columns, read rows, filter, summarize, and order the result.

```sql
SELECT
    status
  , count(*) AS order_count
FROM orders
WHERE ordered_at >= TIMESTAMPTZ '2017-01-01 00:00:00+00'
GROUP BY status
HAVING count(*) >= 100
ORDER BY order_count DESC, status
LIMIT 10;
```

| Clause | What it does |
| --- | --- |
| `SELECT` | Chooses output columns and expressions. |
| `FROM` / `JOIN` | Identifies and combines input rows. |
| `WHERE` | Filters individual input rows. |
| `GROUP BY` | Forms groups for aggregation. |
| `HAVING` | Filters groups after aggregation. |
| `ORDER BY` | Sorts the output. |
| `LIMIT` | Restricts the number of output rows. |

A useful logical model is: **FROM/JOIN → WHERE → GROUP BY/aggregation → HAVING → SELECT
→ DISTINCT → ORDER BY → LIMIT**. This explains why filtering rows and filtering groups
are different operations. It is not a description of the physical execution plan; the
engine can optimize how it does the work.

Without `ORDER BY`, results have no guaranteed order. `LIMIT 10` alone is a preview, not
the earliest ten rows or a random sample. Add tie-breakers to the sort when you need a
stable selection.

**DuckDB:** some alias rules are more permissive than in other databases, including SQL
Server. The logical model above is useful, but not a complete guide to which aliases a
dialect permits. A CTE is often a clearer way to reuse a calculated expression across
query stages.

## 2. SQL Server translation guide

**DuckDB:** use these patterns rather than copying T-SQL unchanged. These are starting
points, not a complete compatibility specification.

| Task | Familiar SQL Server pattern | DuckDB pattern |
| --- | --- | --- |
| Preview rows | `SELECT TOP (10) ...` | `SELECT ... LIMIT 10` |
| Quote an identifier | `[column_name]` | `"column_name"` |
| Write a string | `'delivered'` | `'delivered'` |
| Separate batches | `GO` in client scripts | No `GO`; end statements with `;` |
| Substitute for null | `ISNULL(x, y)` | Prefer `coalesce(x, y)`; check the resulting type |
| Fractional division | Integer operands can truncate: `1 / 2` gives `0` | `/` gives fractional division: `1 / 2` gives `0.5` |
| Integer division | `/` with integer operands | `//` with integer operands |
| Current date/time | `GETDATE()` | `CURRENT_DATE` or `CURRENT_TIMESTAMP`, depending on the need |
| Date difference | `DATEDIFF(day, start, finish)` | `date_diff('day', start, finish)` |
| Add time | `DATEADD(day, 7, value)` | `value + INTERVAL '7 days'` |
| Temporary table | `#name` | `CREATE TEMP TABLE name AS SELECT ...` |
| Session-local view | No direct temporary-view equivalent | `CREATE TEMP VIEW name AS SELECT ...` |

`GO` is a SQL Server client batch separator, not a SQL statement. It is not needed in
your DuckDB scripts.

Date/time functions are not all exact substitutes. Return types, time zones, and
boundary-counting behavior matter; see [dates and timestamps](#8-dates-and-timestamps).

## 3. Names, strings, and formatting

**General SQL:** single quotes denote string values; double quotes quote identifiers
such as column names.

```sql
SELECT
    o.status AS "Order status"
FROM orders AS o
WHERE o.status = 'delivered'
LIMIT 10;
```

`o` is a table alias. `o.status` identifies a column from that table. `AS "Order
status"` names the output column without renaming the stored column.

Do not write `status = "delivered"`: that asks for an identifier named `delivered`, not
a text value. Write an apostrophe inside a string by doubling it: `'customer''s
basket'`.

**DuckDB:** identifiers are case-insensitive, including quoted identifiers. Quoting is
useful for spaces or reserved words, not for creating separate columns distinguished
only by case. Text-value comparisons are case-sensitive by default; identifier matching
and value matching are different rules.

**Project style:** uppercase keywords, lowercase function names, leading commas,
indentation, and the position of the semicolon are formatting choices. They do not
change the calculation. Follow the surrounding lesson style rather than treating it as a
DuckDB requirement.

Use a semicolon to end a statement. Execute the current statement or select the intended
block in DBeaver. Do not paste Markdown fence markers into the SQL editor.

### Naming and capitalization: convention versus behavior

**Project style:** use `snake_case` for table names, column names, and aliases, such as
`order_items`, `customer_unique_id`, and `pair_baskets`. Use uppercase SQL keywords
such as `SELECT`, `FROM`, and `GROUP BY`, and lowercase function names such as
`count(*)` and `date_trunc(...)`.

If you come from SQL Server, you may be used to names such as `OrderItems` and
`CustomerUniqueId` (**PascalCase**). PascalCase is common in some SQL Server teams;
`snake_case` is common in DuckDB examples and many other SQL environments. Neither
is a universal rule: SQL Server can use snake_case, and DuckDB can use PascalCase.
Follow the existing schema and your team's conventions rather than assuming a
particular database requires a naming style.

| Purpose | This project's convention | Another style you might encounter |
| --- | --- | --- |
| Table name | `order_items` | `OrderItems` |
| Column name | `customer_unique_id` | `CustomerUniqueId` |
| Calculated output alias | `order_count` | `OrderCount` |
| SQL keywords | `SELECT`, `GROUP BY` | `select`, `group by` |
| Function call | `count(*)` | `COUNT(*)` |

Uppercase keywords help distinguish the structure of a query from its data names.
This is a common convention across SQL Server, DuckDB, and other databases—not a
SQL Server versus DuckDB difference. Lowercase keywords and uppercase function
names are also valid. The casing choices do not make the query faster or change
its calculation.

**DuckDB behavior:** `OrderItems` and `order_items` are different names because one
contains an underscore, not because of capitalization. `ORDER_ITEMS` and
`order_items` refer to the same identifier in DuckDB. In SQL Server, identifier
case sensitivity depends on collation; do not assume all databases handle it the
same way. These identifier rules also do not tell you whether text values such as
`'delivered'` and `'Delivered'` compare as equal.

Use names that explain the grain or measure: `pair_baskets` is more informative
than `total`. Prefer simple names without spaces so routine queries do not need
quoted identifiers. When querying an existing schema, use its actual names;
changing PascalCase to snake_case is a schema change, not just reformatting.

### Comments: explain decisions and mark experiments

**General SQL:** comments are text the SQL engine ignores. Use them to explain **why**
you made a choice, record an assumption, or flag an unresolved question. A comment
saying “select orders” adds little; a comment explaining why you excluded canceled
orders helps someone interpret the result.

`--` starts a comment that continues to the end of the line. Use it for a short
explanation above a clause, a brief note beside an expression, or temporarily disabling
a complete line:

```sql
SELECT
    order_id
  , ordered_at
FROM orders
-- Match the delivered-order population used in the basket analysis.
WHERE status = 'delivered'
-- Experiment: restrict the period. Remove the comment marker to apply it.
--  AND ordered_at >= TIMESTAMPTZ '2018-01-01 00:00:00+00'
LIMIT 10;
```

`/* ... */` encloses a block comment, which can span multiple lines or sit within a
line. Use it for a query-level explanation or temporarily disabling a section without
adding `--` to every line:

```sql
/*
Purpose: inspect delivered orders before preparing category pairs.
Limitation: delivered status does not guarantee every timestamp is populated.
*/
SELECT order_id, customer_delivered_at
FROM orders
WHERE status = 'delivered'
LIMIT 10;
```

When disabling code, check that the remaining query is still valid and answers the
question you intend. Commenting out a filter can dramatically widen the population. Keep
comments up to date: an old explanation beside changed SQL can be more misleading than
no explanation. Comments are not a safe place for credentials or sensitive records.

### Leading commas: make exploration easier

**Project style:** place the comma at the beginning of each selected expression after
the first. This keeps the separator attached to the expression you are adding or
removing:

```sql
SELECT
    order_id
--  , customer_id
  , status
  , ordered_at
FROM orders
LIMIT 10;
```

You can comment out `customer_id` with its comma without editing the previous line. You
can also append another expression without adding a comma to the expression above it.
This is useful when experimenting with select lists or comparing alternative
calculations.

The first expression is a special case: if you remove `order_id`, also remove the
leading comma from the new first expression. Apply the same care when editing `GROUP BY`
and `ORDER BY` lists. Do not assume that removing a selected expression also removes its
analytical role elsewhere in the query.

Leading commas are a preference, not a DuckDB requirement. Trailing commas are also a
reasonable style. Consistency and readable edits matter more than winning an argument
about comma placement.

**Tip:** Use the DBeaver keybinding **Ctrl+/** to toggle `--` line comments on the
current line or selected lines.                                                                                              

### Format SQL so the structure is visible

**Project style:** formatting makes it easier to review joins, spot a missing condition,
understand grouping, and compare changes. It does not prove a query is correct, but it
makes checking correctness easier.

- Put major clauses on separate lines.
- Use one selected expression per line for longer lists.
- Indent expressions inside `CASE`, CTEs, and subqueries.
- Keep join conditions close to their join and qualify ambiguous column names.
- Use parentheses to make mixed `AND` / `OR` conditions clear.
- Keep keyword casing, comma placement, and indentation consistent within a script.

**In DBeaver:** use the formatter rather than adjusting every space by hand.

1. Open your SQL script and confirm its connection uses the DuckDB dialect.
2. Select the SQL you want to format, or leave the selection empty to format the script.
3. Use **Format → Format SQL** in the SQL editor context menu. The usual shortcut is
   `Ctrl+Shift+F` on Windows/Linux; shortcuts and menu labels can vary by version or
   keymap. If it does not work, find **Format SQL** in the menus or check the key
   bindings.
4. Review the result, especially comments and temporarily disabled expressions.
   Formatting is not query validation; rerun the relevant checks after making analytical
   edits.

To adjust the automatic style, open **Preferences** (on Windows, usually under
**Window**) and look under **Editors → SQL Editor → Formatting**. Choose the built-in
formatter and inspect the available keyword-case, indentation, line-break, and
comma-placement settings. Exact options vary by formatter and DBeaver version; if
leading commas are not offered, keep a consistent supported style rather than manually
fighting every format operation. Keyboard shortcuts can be checked under **General →
Keys**.

For shared scripts, agree on a style and formatter settings with your team. Do not
reformat an entire shared file just to change one condition unless that broader change
is intentional.

## 4. Types, arithmetic, and conditional expressions

**General SQL:** inspect types before deciding how to use a column.

```sql
DESCRIBE order_items;
```

| Type | Typical use in this project |
| --- | --- |
| `VARCHAR` | Text, categories, and postal-code prefixes. |
| `INTEGER` / `BIGINT` | Whole numbers and counts. |
| `DECIMAL(18, 2)` | Fixed-scale values such as item prices. |
| `DOUBLE` | Floating-point values such as coordinates. |
| `UUID` | Identifiers, not quantities to sum or average. |
| `DATE` | Calendar dates. |
| `TIMESTAMP` / `TIMESTAMPTZ` | Date/time values; see the timestamp section. |
| `BOOLEAN` | `TRUE`, `FALSE`, or a missing value. |

Numeric-looking codes are not necessarily numbers. Keeping a postal prefix as text
preserves leading zeros.

**DuckDB:** `CAST` converts a value to another type. `::` is a shorter spelling.
`TRY_CAST` returns `NULL` when conversion fails rather than raising an error for invalid
input.

```sql
SELECT
    CAST('42' AS INTEGER) AS converted
  , '42'::INTEGER AS short_form
  , try_cast('not a number' AS INTEGER) AS invalid_input
  , 1 / 2 AS fractional_division
  , 1 // 2 AS integer_division;
```

`TRY_CAST` is useful for investigation, but silently losing invalid values is not a
complete cleaning policy. Count and report failures. Unlike SQL Server integer division,
DuckDB's `/` does not require multiplying by `1.0` to obtain a fraction. The lessons use
`1.0` to make that intent visible.

Round for presentation, not at every intermediate step. Division can produce approximate
results even when the inputs are decimals; inspect types and requirements when exact
financial arithmetic matters.

**General SQL:** `CASE` gives you conditional expressions:

```sql
SELECT
    order_id
  , CASE
        WHEN customer_delivered_at IS NULL THEN 'No recorded delivery time'
        ELSE 'Delivery time recorded'
    END AS delivery_time_check
FROM orders
LIMIT 10;
```

This labels a record; it does not establish why a timestamp is absent.

## 5. Missing values and filtering

**General SQL:** `NULL` represents a missing or unknown value. It is not automatically
zero or an empty string.

- Test with `IS NULL` or `IS NOT NULL`, not `= NULL`.
- `WHERE` keeps rows whose condition is true. False and unknown conditions are not
  retained.
- `count(*)` counts rows; `count(column)` counts non-null values.
- `coalesce(x, y)` returns the first non-null argument. Substitution changes the
  interpretation; it does not repair the source.

```sql
SELECT
    count(*) AS order_rows
  , count(customer_delivered_at) AS recorded_delivery_times
  , count(*) - count(customer_delivered_at) AS missing_delivery_times
FROM orders;
```

### Combining conditions: say exactly what must be true

`AND` and `OR` connect conditions, but they mean different things:

- `AND`: both conditions must be true for the row to pass.
- `OR`: at least one condition must be true. Both may be true too; SQL's `OR` does
  not mean “one or the other, but not both.”

Suppose your question is:

> Which orders are either delivered or shipped, but have no recorded delivery time?

There are two requirements: an allowed status **and** a missing timestamp. Put the
status alternatives in parentheses to make them one group:

```sql
SELECT order_id, status
FROM orders
WHERE (status = 'delivered' OR status = 'shipped')
  AND customer_delivered_at IS NULL
LIMIT 10;
```

Read this as: “The status is one of these two choices, **and in either case** the
delivery timestamp must be missing.”

Now consider the same conditions without parentheses:

```sql
-- Different question: this also includes delivered orders WITH delivery times.
SELECT order_id, status
FROM orders
WHERE status = 'delivered'
   OR status = 'shipped' AND customer_delivered_at IS NULL
LIMIT 10;
```

SQL does not group these conditions simply by reading left to right. Its rules give
`AND` priority over `OR`, so the second query means:

```text
status = 'delivered'
OR (status = 'shipped' AND customer_delivered_at IS NULL)
```

Every delivered order qualifies, regardless of its timestamp. Only shipped orders
have to meet the missing-timestamp condition. Adding a line break or indentation
does not change that meaning.

Compare how the two filters treat these example rows:

| Status | Delivery timestamp | Grouped status choices AND missing time | No parentheses: AND gets priority |
| --- | --- | --- | --- |
| delivered | Present | Exclude | Include |
| delivered | Missing | Include | Include |
| shipped | Present | Exclude | Exclude |
| shipped | Missing | Include | Include |
| canceled | Missing | Exclude | Exclude |

This priority rule is called **operator precedence**. For these logical operators,
`NOT` has priority over `AND`, which has priority over `OR`. Parentheses let you
explicitly group the conditions you intend. These are rules for interpreting the
expression, not a promise that the engine physically checks conditions in that order.

For the first question, an even shorter way to express the status choices is:

```sql
SELECT order_id, status
FROM orders
WHERE status IN ('delivered', 'shipped')
  AND customer_delivered_at IS NULL
LIMIT 10;
```

**A useful habit:** when mixing `AND` and `OR`, write the groups explicitly even if
SQL's default rules would give the answer you intended. A reviewer should not need
to remember precedence rules to understand your filter.

Remember that missing values introduce an “unknown” result for ordinary comparisons.
The examples use `IS NULL`, which explicitly tests for missingness; `status = NULL`
would not do that. `WHERE` still retains only rows whose complete condition is true.

Be especially careful with `NOT IN` if its list or subquery can contain nulls. For
example, `2 NOT IN (1, NULL)` is unknown, not true. To find rows without a match, a
correlated `NOT EXISTS` is often clearer:

```sql
SELECT p.product_id
FROM products AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM order_items AS i
    WHERE i.product_id = p.product_id
)
LIMIT 10;
```

This finds product records without matching item records. Decide separately how missing
keys should be handled; changing the syntax does not define that policy for you.

## 6. Aggregation and grain

**General SQL:** ask what one input row represents and what one output row represents.

```sql
SELECT
    status
  , count(*) AS orders
  , count(*) FILTER (WHERE customer_delivered_at IS NULL)
        AS orders_without_delivery_time
FROM orders
GROUP BY status
HAVING count(*) >= 100
ORDER BY orders DESC, status;
```

The input grain is one order. The output grain is one status. `WHERE` would filter input
orders; `HAVING` filters the resulting status groups.

**DuckDB:** aggregate `FILTER` applies a condition to one aggregate without filtering
the other aggregates. This syntax is also supported by some other databases, but not by
SQL Server; a familiar alternative is conditional aggregation with `CASE`.

**General SQL:** `DISTINCT` applies to the full selected combination:

```sql
SELECT DISTINCT order_id, product_id
FROM order_items
LIMIT 10;
```

This gives distinct order-product combinations, not distinct orders. `count(DISTINCT
product_id)` counts distinct non-null product identifiers.

Adding `DISTINCT` to a query is not proof that its grain is correct. It can conceal
duplicate lookup records or remove genuinely separate events. Define the intended grain
first.

## 7. Joins and row multiplication

**General SQL:** choose joins according to which records you intend to retain.

| Join | What it retains |
| --- | --- |
| `INNER JOIN` | Matching combinations of rows. |
| `LEFT JOIN` | Every left row, with matching right rows or nulls when unmatched. |
| `CROSS JOIN` | Every combination of left and right rows. |
| Self-join | Not a separate join type: the same dataset is referenced using different aliases. |

**Project style:** prefer `LEFT JOIN` for optional matches. Put the population you
intend to retain on the left, then attach related information on the right. This
keeps a consistent reading direction: “start with these records, then enrich them.”
Use `INNER JOIN` when a match is required.

`RIGHT JOIN` preserves the right-hand input instead. For a simple two-table join,
you can express the same relationship as a left join by swapping the inputs. It is
valid SQL, but you rarely need it in this style. This is a readability preference,
not a DuckDB requirement or a performance optimization. Do not casually rearrange
whole chains of outer joins: changing their grouping can change the result.

Preserving rows does not guarantee the original grain or prevent later filters
from removing rows. A join does not promise one output row per left row. Two items
joined directly to three payments for an order produce six combinations. Summing item
prices afterwards can triple their contribution. Aggregate to compatible grains before
combining independent one-to-many relationships.

### ON decides what matches; WHERE decides what stays

Start with a simple goal: **keep every product and attach its English category
translation when one exists**.

```sql
SELECT
    p.product_id
  , p.category_name
  , t.category_name_english
FROM products AS p
LEFT JOIN product_categories AS t
    ON p.category_name = t.category_name
LIMIT 10;
```

For a product without a matching translation, the product still appears. Its
`category_name_english` is `NULL`.

Now suppose you add this condition to `WHERE`:

```sql
SELECT
    p.product_id
  , p.category_name
  , t.category_name_english
FROM products AS p
LEFT JOIN product_categories AS t
    ON p.category_name = t.category_name
WHERE t.category_name_english = 'health_beauty'
LIMIT 10;
```

You have changed the goal to **keep only products whose English category is
`health_beauty`**. Products without translations cannot satisfy that requirement,
so they no longer appear. Neither do products translated to other categories.

A `LEFT JOIN` preserves unmatched products **at the join step**. It does not exempt
them from a later `WHERE` filter.

Here is an illustrative set of products, not a claim about specific source rows:

| Product | Attached translation | No WHERE filter | WHERE translation = 'health_beauty' |
| --- | --- | --- | --- |
| P1 | health_beauty | Keep | Keep |
| P2 | toys | Keep | Remove |
| P3 | NULL (no match) | Keep | Remove |

What if you want to **keep every product, but attach a translation only when it is
`health_beauty`**? Put that restriction in `ON` instead:

```sql
SELECT
    p.product_id
  , p.category_name
  , t.category_name_english
FROM products AS p
LEFT JOIN product_categories AS t
    ON p.category_name = t.category_name
   AND t.category_name_english = 'health_beauty'
LIMIT 10;
```

All three illustrative products remain. P1 has its translation attached; P2 and P3
have `NULL` in the translation column. P2's translation exists in the source, but
it did not meet this query's matching rule. A null introduced by a join therefore
does not always mean the source data is missing.

**Choose by intent:**

- All products, with any available translation: simple `LEFT JOIN`.
- Only products with the specified translation: use `INNER JOIN` with that
  condition, or the filtered query above.
- All products, with only qualifying translations attached: put the restriction
  in the `LEFT JOIN`'s `ON` clause.

The underlying null rule is that a comparison such as `NULL = 'health_beauty'`
is unknown, not true, and `WHERE` retains only true conditions. The practical
question comes first: **am I restricting the match, or filtering the final rows?**

Check lookup-key uniqueness before relying on these joins. For an extended self-join
example, see [Lesson 2](lesson_2/README.md#5-make-pairs-without-counting-them-twice).

## 8. Dates and timestamps

**General SQL:** use typed literals and explicit boundaries. A half-open range includes
the start and excludes the end, avoiding guesses about the last possible time on the
final day.

```sql
SELECT count(*) AS orders_in_period
FROM orders
WHERE ordered_at >= TIMESTAMPTZ '2018-01-01 00:00:00+00'
  AND ordered_at < TIMESTAMPTZ '2018-02-01 00:00:00+00';
```

These are UTC boundaries, chosen explicitly for the example. Use the agreed business
time zone for a real reporting period. `BETWEEN` includes both endpoints, which can
unintentionally include the next period's midnight.

**DuckDB:** common date operations include:

```sql
SELECT
    DATE '2018-01-01' AS start_date
  , DATE '2018-01-01' + INTERVAL '7 days' AS one_week_later
  , date_trunc('month', DATE '2018-01-17') AS month_start
  , date_diff('day', TIMESTAMP '2018-01-01 23:00:00',
                     TIMESTAMP '2018-01-02 01:00:00') AS day_boundaries
  , TIMESTAMP '2018-01-02 01:00:00'
        - TIMESTAMP '2018-01-01 23:00:00' AS elapsed_time;
```

The last two results are **one day boundary** and **two hours elapsed**. `date_diff`
counts boundaries of the requested unit; it is not a general fractional-duration
calculation. Adding an interval to a date can also change the result type to a
timestamp.

`TIMESTAMP` describes a date and time without time-zone semantics. `TIMESTAMPTZ`
represents an instant; it does not retain the original named time zone. Its display and
calendar operations such as month grouping depend on the session time zone.

The project imports order times as `TIMESTAMPTZ`. That type alone does not establish
that the source times were assigned the correct zone. Confirm source meaning and
ingestion rules before making timezone-sensitive claims. Do not assume the example's UTC
reporting choice establishes the source's business time zone.

For a DuckDB connection, inspect the session setting with:

```sql
SELECT current_setting('TimeZone') AS session_time_zone;
```

DBeaver's display configuration can also affect what you see. Check both when
interpreting timestamps. See the official [timestamp
documentation](https://duckdb.org/docs/stable/sql/data_types/timestamp.html) for the
full behavior.

## 9. CTEs, views, and tables

**General SQL concepts, with DuckDB syntax:** choose an object based on its purpose and
lifetime.

| Object | Lifetime | What it holds |
| --- | --- | --- |
| CTE (`WITH`) | One statement | A named query expression; not a promise of physical storage. |
| Temporary view | Current connection | A query definition, not a stored result snapshot. |
| Temporary table | Current connection | Stored intermediate rows. |
| Persistent view | Survives reconnection | A stored query definition. |
| Persistent table | Survives reconnection | Stored rows. |

This CTE exists only for the following `SELECT`:

```sql
WITH delivered_orders AS (
    SELECT order_id
    FROM orders
    WHERE status = 'delivered'
)
SELECT count(*) AS delivered_order_count
FROM delivered_orders;
```

Run this next script in order, on one connection. It creates two session-local objects
with reference-specific names, reads the stored result, then removes both:

```sql
CREATE OR REPLACE TEMP VIEW sql_reference_status_counts AS
SELECT status, count(*) AS order_count
FROM orders
GROUP BY status;

CREATE OR REPLACE TEMP TABLE sql_reference_status_snapshot AS
SELECT * FROM sql_reference_status_counts;

SELECT *
FROM sql_reference_status_snapshot
ORDER BY order_count DESC, status;

DROP TABLE sql_reference_status_snapshot;
DROP VIEW sql_reference_status_counts;
```

The view reads its underlying data when queried. The table holds the rows captured when
it was created; later changes to the source do not automatically refresh it.

Reconnecting loses temporary objects. Different SQL editors may use different
connections, even when their connection names look the same. If a lesson's temporary
view is missing, rerun its definitions in the active session.

Persistent objects belong in an agreed workspace when you use a shared platform.
Removing `TEMP` is not, by itself, a publishing workflow.

## 10. Useful DuckDB additions

These conveniences shorten queries. Understand their explicit equivalents first,
especially when sharing SQL across database engines.

### GROUP BY ALL

**DuckDB:** group by every non-aggregate expression in the select list:

```sql
SELECT status, count(*) AS order_count
FROM orders
GROUP BY ALL;
```

Here, that means `GROUP BY status`. Adding a non-aggregate select expression can change
the grain automatically, so review edits carefully.

### SELECT * EXCLUDE

**DuckDB:** omit named columns from a wildcard selection:

```sql
SELECT * EXCLUDE (comment_title, comment_message)
FROM order_reviews
LIMIT 10;
```

Wildcards are convenient for exploration. For a dependable output, an explicit column
list makes the schema and exposure of fields easier to control.

### Window functions and QUALIFY

**General SQL:** a window function calculates over related rows without collapsing them
into one group row. **DuckDB:** `QUALIFY` filters window-function results without an
extra outer query.

```sql
SELECT
    order_id
  , order_item_id
  , price
  , row_number() OVER (
        PARTITION BY order_id
        ORDER BY price DESC, order_item_id
    ) AS item_rank
FROM order_items
QUALIFY item_rank = 1
ORDER BY order_id
LIMIT 10;
```

This selects one highest-priced item per order, breaking price ties with the item
identifier. It is not an order-total calculation. SQL Server supports window functions,
but would normally use a CTE or subquery to filter the row number instead of `QUALIFY`.

## Keep exploring deliberately

When a query surprises you, check the database dialect, column types, missing values,
and grain before assuming the source data is wrong. Save a small reproducible example
and explain the result you expected.

For more syntax and behavior, consult the official [DuckDB SQL
introduction](https://duckdb.org/docs/stable/sql/introduction) and [SQL dialect
documentation](https://duckdb.org/docs/stable/sql/dialect/overview.html). Return to
[Lesson 1](lesson_1/README.md) or the [project
roadmap](../../README.md#work-through-the-lessons) when you are ready to continue.
