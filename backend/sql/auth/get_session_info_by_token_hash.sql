/*
 * Returns CursorResult object
 */

SELECT * 
FROM sessions
WHERE token_hash = :token_hash AND expires_at > now();
