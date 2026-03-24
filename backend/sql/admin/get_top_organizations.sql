/*
 * Returns CursorResult object
 */

SELECT organization, COUNT(*) as borrowed_items
FROM loans
GROUP BY organization
ORDER BY borrowed_items DESC
LIMIT :limit;