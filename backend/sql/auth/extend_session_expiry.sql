/*
 * Returns CursorResult object
 */

UPDATE sessions
SET expires_at = now() + INTERVAL '24 hours'
WHERE token_hash = :token_hash;