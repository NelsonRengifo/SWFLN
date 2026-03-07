/*
 * Returns CursorResult object
 */

UPDATE uploaded_files
SET ingestion_status = 'pending', processing_started_at = NULL
WHERE ingestion_status = 'processing' AND NOW() > processing_started_at + INTERVAL '5 minutes';
