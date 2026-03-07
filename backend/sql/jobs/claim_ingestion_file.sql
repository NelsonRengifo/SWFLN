/*
 * Returns CursorResult object
 */

UPDATE uploaded_files
SET ingestion_status = 'processing', processing_started_at = now()
WHERE uploaded_file_id = (
    SELECT uploaded_file_id
    FROM uploaded_files
    WHERE ingestion_status = 'pending'
    ORDER BY uploaded_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
    )
RETURNING uploaded_file_id, storage_path;
