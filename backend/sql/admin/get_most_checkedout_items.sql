/*
 * Returns CursorResult object
 */

SELECT item_id, item_name, COUNT(*) as total
FROM loans
INNER JOIN uploaded_files ON loans.uploaded_file_id = uploaded_files.uploaded_file_id
WHERE (:start_date IS NULL OR uploaded_files.uploaded_at >= :start_date)
      AND
      (:end_date IS NULL OR uploaded_files.uploaded_at < :end_date)
GROUP BY item_name, item_id
ORDER BY total DESC
LIMIT :limit;