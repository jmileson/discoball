# Lesson 1: Meet your data

You have a local database. Now you need to find out what is in it—and what you can
reasonably say about it.

In this lesson, you will connect to DuckDB with DBeaver, explore the Olist marketplace
data, and answer your first questions with SQL. You will also practice an important
analytical habit: separating what a result shows from what you assume it means.

Allow about 45–60 minutes. You do not need previous SQL experience.

## Before you start

Complete the [project setup](../../../README.md), including installing DBeaver Community
and running `uv run setup`. You should have a database file at `.data/dev.duckdb` inside
your project folder.

For this lesson, you will only read data. You do not need to edit tables, import files
through DBeaver, or run the setup again.

## 1. Connect to your database

There are three different things involved:

- **DuckDB** is the database engine that executes your queries.
- **`.data/dev.duckdb`** is the file containing your local tables.
- **DBeaver** is the application you will use to browse those tables and write SQL.

DuckDB runs locally inside the application using it. You do not need to start a database
server or enter a host, port, username, or password for this local connection. Later,
you will use Python as another way to work with DuckDB.

1. Open DBeaver and choose **Database → New Database Connection** (or the new connection
button).
2. Search for **DuckDB**, select it, and continue.
3. In the database file/path field, browse to the **existing** `.data/dev.duckdb` in
your project folder. Field labels can vary by DBeaver version. Use an absolute path,
such as `C:\Users\YourName\discoball\.data\dev.duckdb`, rather than just `dev.duckdb`.
4. If prompted to download the DuckDB driver, allow DBeaver to download it through your
organization's approved process.
5. Test the connection and finish. Give it a recognizable name, such as **Discoball
local**.
6. Expand the connection in **Database Navigator**. Look under the database/schema nodes
for the tables, usually in the `main` schema.
7. Select your connection and open a new **SQL Editor / SQL Script** from its context
menu or the SQL Editor menu.

Make sure the editor is attached to **Discoball local**. Paste this statement and
execute it using the SQL editor's execute-statement action (usually `Ctrl+Enter`):

```sql
SELECT 'Hello, DuckDB!' AS message;
```

You should see one row with a column named `message`. `AS` gives a result column a
readable name; it does not rename anything in your database.

Now run:

```sql
SHOW TABLES;
```

You should see these nine tables:

```text
customers
geolocation
order_items
order_payments
order_reviews
orders
product_categories
products sellers
```

**If something goes wrong:**

- **No tables:** check the full database path against your project folder. DuckDB can
  create a new empty database if you supply a different filename. Disconnect, select the
  correct existing file, and refresh the navigator.
- **The file does not exist:** return to the project terminal and run `uv run setup`
  from the repository root.
- **Driver download fails:** check your network or proxy requirements with IT. Do not
  disable certificate verification.
- **File lock or access-mode error:** close other processes using the database and
  disconnect other database sessions before retrying. Before running Python or setup
  code that opens this file for writing, disconnect DBeaver. DuckDB is not a shared
  database server; separate applications cannot freely mix readers and writers on the
  same file.

## 2. Understand the marketplace

The Olist dataset describes historical orders from a Brazilian e-commerce marketplace. A
customer places an order; that order can contain multiple items supplied by sellers.
Payments, delivery milestones, and reviews describe other parts of the experience.

You might use this data to investigate questions such as:

- How many orders reached each status?
- How long did delivery take, and how often did it miss the estimate?
- Which product categories account for the most item sales value?
- Are delivery delays associated with lower review scores?

Those are useful questions, but they need definitions. Does “sales” include freight? Do
you include canceled orders? Does an association between delays and scores establish
that one caused the other? A query alone cannot settle those choices.

Before calculating anything, ask: **what does one row represent?** This is often called
a table's *grain*.

| Table | What you will find | A detail to watch |
| --- | --- | --- |
| `orders` | Orders, their statuses, and timestamps | Delivery events can be missing. |
| `customers` | Customer identifiers and locations | `customer_id` and `customer_unique_id` serve different purposes. |
| `order_items` | Items within an order, with price and freight | One order can have multiple items. |
| `products` | Product categories and descriptive attributes | Some attributes or categories may be missing. |
| `sellers` | Seller identifiers and locations | An order can involve more than one seller. |
| `order_payments` | Payment records associated with orders | One order can have multiple payment records. |
| `order_reviews` | Review scores, comments, and timestamps | Check the number of reviews per order before assuming one. |
| `product_categories` | Category names and English translations | Not every product necessarily has a usable category. |
| `geolocation` | Coordinates and place names for postal-code prefixes | A prefix is not necessarily unique. |

The project uses shorter column names than the original source CSVs. Use the names you
see in this database and in the examples below.

## 3. Look at a few orders

Run:

```sql
SELECT
    order_id
    , customer_id
    , status
    , ordered_at
    , customer_delivered_at
FROM orders
LIMIT 10
;
```

Read this as: “Select these columns from the orders table, and return at most ten rows.”

- `SELECT` chooses the columns to display.
- `FROM` chooses the table to read.
- `LIMIT` keeps the preview small.
- The semicolon ends the statement.

You are looking at a preview, not a random sample or the first ten orders
chronologically. Without `ORDER BY`, the order of the results is not guaranteed.

To inspect the available columns and their types, run:

```sql
DESCRIBE orders;
```

Notice the difference between an identifier, a status, and a timestamp. An identifier
connects records; it is not a number you should add or average.

**Pause and explain:** what does a row in `orders` represent? Could you use the number
of rows in `order_items` as the number of orders? Why or why not?

## 4. Find the time period you actually have

Before interpreting a dataset, check its coverage:

```sql
SELECT
    count(*) AS order_count
   , min(ordered_at) AS earliest_order
   , max(ordered_at) AS latest_order
FROM orders
;
```

`count(*)` counts rows. `min` and `max` find the smallest and largest non-null values—in
this case, the earliest and latest recorded purchase timestamps.

You should get 99,441 orders with the supplied data. Record the date range you see.
These are historical records, not a live view of the marketplace. A first or last month
may cover only part of that month, and these bounds alone do not prove that every
intervening period is complete.

**Your turn:** why would it be misleading to label a chart from this database “Our sales
this month”?

## 5. Summarize order statuses

Your first business question is:

> What order statuses appear in this data, and how many orders have each status?

```sql
SELECT
    status
  , count(*) AS order_count
FROM
    orders
GROUP BY
    status
ORDER BY
    order_count DESC
;
```

`GROUP BY status` collects rows with the same status together. `count(*)` counts the
rows in each group. `ORDER BY ... DESC` puts the largest count first.

The result has one row per **status**, not one row per order. A query can change the
grain of your result even though it leaves the source table untouched.

What can we conclude from this data? What can't we conclude from this?

**Your turn:** change `DESC` to `ASC`. What changes? Do the counts change, or only their
presentation?

## 6. Investigate a missing delivery timestamp

A missing value is represented in SQL as `NULL`. It means there is no recorded value,
not automatically zero, an empty string, or an error.

A canceled order might reasonably have no delivery timestamp. A delivered order with no
delivery timestamp would deserve a closer look. You can check that narrower question:

```sql
SELECT
    count(*)                                AS delivered_orders
  , count(customer_delivered_at)            AS
                                               orders_with_delivery_timestamp
  , count(*) - count(customer_delivered_at) AS
                                               orders_missing_delivery_timestamp
FROM
    orders
WHERE
    status = 'delivered'
;
```

`WHERE` filters the input rows before the counts are calculated. Here, it keeps only
orders whose status is `delivered`.

There is an important distinction:

- `count(*)` counts all rows that passed the filter.
- `count(customer_delivered_at)` counts only rows with a non-null value in that column.

The difference tells you how many delivered orders lack that timestamp. A zero result is
still useful evidence; not every investigation must uncover a defect.

To inspect any matching orders, run:

```sql
SELECT order_id, status, ordered_at, customer_delivered_at
FROM
    orders
WHERE
    status = 'delivered' AND customer_delivered_at IS NULL
LIMIT 20
;
```

Use `IS NULL`, not `= NULL`, to test for a missing value. `AND` requires both conditions
to be true.

**Record your finding:**

1. How many delivered orders did you check?
2. How many lack a delivery timestamp?
3. What does that establish about the records?
4. What does it leave unknown about the real deliveries or the data pipeline?
5. What would you ask the platform team before excluding or changing these records?

Do not fill in a timestamp just to make the data complete. An invented value can make an
analysis look more certain while making it less trustworthy.

## 7. Notice the questions you will need to resolve next

### What counts as a customer?

Try:

```sql
SELECT
    count(*)                           AS customer_rows
  , count(DISTINCT customer_id)        AS customer_ids
  , count(DISTINCT customer_unique_id) AS unique_customer_ids
FROM
    customers
;
```

`DISTINCT` counts different non-null values rather than every occurrence. In this
dataset, `customer_id` is the identifier used to connect an order to its customer
record; `customer_unique_id` lets you recognize the same customer across different
orders.

Which count would you investigate for a repeat-customer analysis? Which identifier would
you need to link an order to its customer record? “Number of customers” is not a
sufficiently precise metric definition on its own.

### What counts as sales value?

`order_items` has `price` and `freight_price`; `order_payments` has `payment_value`.
These are not interchangeable definitions of revenue. Decide whether you mean item
value, customer payments, freight-inclusive value, or something else—and which order
statuses to include—before writing a total.

### Why not join every table immediately?

Imagine an order with two items and two payment records. Joining both sets directly on
the order identifier can produce four rows: every item paired with every payment.
Summing item prices or payments afterwards can double-count them.

This is a row-multiplication problem, not necessarily bad source data. In a later
lesson, you will check relationships and aggregate tables to a suitable grain before
combining them.

## 8. Save a short analytical note

Save your queries in DBeaver as a SQL script, and write a short note alongside your work
using this structure:

```text
Question:
Dataset and date coverage:
What one input row represents:
Query used:
Result:
What the result supports:
Limitations and unanswered questions:
Next check or question for the platform team:
```

Use your delivered-order timestamp investigation as the example. Include the actual
counts you found, not just “some values were missing.”

You have completed the lesson when you can:

- Reconnect DBeaver to the correct local DuckDB file.
- Find the nine tables and explain why their row counts need not match.
- Preview rows, inspect columns, filter records, and count groups.
- Explain the difference between `COUNT(*)` and `COUNT(column)`.
- Describe a finding without inventing a cause or silently repairing data.

Next, you can build on these habits to define metrics and combine tables safely. Python
will give you a way to run the same SQL repeatedly as part of an analysis—not a
replacement for understanding what your query means.
