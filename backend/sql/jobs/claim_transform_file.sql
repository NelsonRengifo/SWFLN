/*
 * Returns CursorResult object
 */

UPDATE uploaded_files
SET transform_status = 'processing', transform_started_at = NOW()
WHERE uploaded_file_id = (
    SELECT uploaded_file_id
    FROM uploaded_files
    WHERE ingestion_status = 'completed' AND transform_status = 'pending' AND source = :source
    ORDER BY uploaded_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
    )
RETURNING uploaded_file_id;