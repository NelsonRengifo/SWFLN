/*
 * Returns CursorResult object
 */

SELECT item_id, item_name, COUNT(*) as total
FROM loans
GROUP BY item_name, item_id
ORDER BY total DESC
LIMIT :limit;