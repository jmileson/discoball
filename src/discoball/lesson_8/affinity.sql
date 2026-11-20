WITH basket_categories AS (
    SELECT DISTINCT
        o.order_id
      , p.category_name
    FROM orders AS o
    INNER JOIN order_items AS i ON o.order_id = i.order_id
    INNER JOIN products AS p ON i.product_id = p.product_id
    WHERE o.status = 'delivered'
      AND p.category_name IS NOT NULL
      AND trim(p.category_name) <> ''
), category_counts AS (
    SELECT category_name, count(*) AS category_baskets
    FROM basket_categories
    GROUP BY category_name
), pair_counts AS (
    SELECT
        a.category_name AS category_a
      , b.category_name AS category_b
      , count(*) AS pair_baskets
    FROM basket_categories AS a
    INNER JOIN basket_categories AS b
        ON a.order_id = b.order_id
       AND a.category_name < b.category_name
    GROUP BY a.category_name, b.category_name
), population AS (
    SELECT count(DISTINCT order_id) AS eligible_baskets
    FROM basket_categories
), counts AS (
    SELECT
        p.*
      , a.category_baskets AS a_baskets
      , b.category_baskets AS b_baskets
      , n.eligible_baskets
    FROM pair_counts AS p
    INNER JOIN category_counts AS a ON p.category_a = a.category_name
    INNER JOIN category_counts AS b ON p.category_b = b.category_name
    CROSS JOIN population AS n
)
SELECT
    *
  , pair_baskets / nullif(eligible_baskets, 0) AS support
  , pair_baskets / nullif(a_baskets, 0) AS confidence_a_to_b
  , pair_baskets / nullif(b_baskets, 0) AS confidence_b_to_a
  , (pair_baskets / nullif(a_baskets, 0))
        / nullif(b_baskets / nullif(eligible_baskets, 0), 0) AS lift
FROM counts
ORDER BY pair_baskets DESC, category_a, category_b;
