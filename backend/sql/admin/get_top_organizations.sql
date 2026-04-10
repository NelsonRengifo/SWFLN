/*
 * Returns CursorResult object
 */

-- < end_date to ensure we cover the entire last month due to timestamz column

-- SELECT organization, COUNT(*) as borrowed_items
-- FROM loans
-- INNER JOIN uploaded_files ON loans.uploaded_file_id = uploaded_files.uploaded_file_id
-- WHERE (:start_date IS NULL OR uploaded_files.uploaded_at >= :start_date)
--       AND
--       (:end_date IS NULL OR uploaded_files.uploaded_at < :end_date)
-- GROUP BY organization
-- ORDER BY borrowed_items DESC
-- LIMIT :limit;

SELECT organization, COUNT(*) as borrowed_items
FROM loans
WHERE (:start_date IS NULL OR checkout_at >= :start_date)
      AND
      (:end_date IS NULL OR checkout_at < :end_date)
GROUP BY organization
ORDER BY borrowed_items DESC
LIMIT :limit;