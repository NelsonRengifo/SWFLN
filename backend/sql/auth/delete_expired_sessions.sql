/*
 * Returns CursorResult object
 */


DELETE FROM sessions
WHERE expires_at < now();