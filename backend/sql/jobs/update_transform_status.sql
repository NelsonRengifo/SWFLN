/*
 * Returns CursorObject result
 */

UPDATE uploaded_files
SET transform_status = :transform_status, transform_completed_at = NOW(), transform_error_message = :transform_error_message
WHERE uploaded_file_id = :uploaded_file_id
RETURNING uploaded_file_id;