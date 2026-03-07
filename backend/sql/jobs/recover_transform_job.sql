/*
 * Returns CursorResult object
 */

UPDATE uploaded_files
SET transform_status = 'pending', processing_started_at = NULL
WHERE transform_status = 'processing' AND NOW() > transform_started_at + INTERVAL '5 minutes';