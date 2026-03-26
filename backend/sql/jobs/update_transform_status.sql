/*
 * Returns CursorObject result
 */

UPDATE uploaded_files
SET transform_status = :transform_status
WHERE uploaded_file_id = :uploaded_file_id
RETURNING uploaded_file_id;