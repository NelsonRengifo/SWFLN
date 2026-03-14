/*
 * Returns CursorResult object
 */

SELECT uploaded_file_id, users.first_name, users.last_name, uploaded_at, original_file_name, ingestion_status, transform_status
FROM uploaded_files
JOIN users ON uploaded_files.uploaded_by = users.user_id
WHERE source = :source
ORDER BY uploaded_at DESC
LIMIT 26
OFFSET :OFFSET;