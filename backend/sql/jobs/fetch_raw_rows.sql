/*
 * Returns CursorResult object
 */

SELECT raw_data
FROM raw_rows
WHERE uploaded_file_id = :uploaded_file_id;

