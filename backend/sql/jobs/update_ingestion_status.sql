/*
 * Returns CursorObject result
 */

UPDATE uploaded_files
SET ingestion_status = :ingestion_status, processing_finished_at = NOW(), error_message = :error_message
WHERE uploaded_file_id = :uploaded_file_id
RETURNING uploaded_file_id;