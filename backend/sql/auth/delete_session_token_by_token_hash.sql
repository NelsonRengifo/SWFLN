/*
 * Returns CursorResult object
 */

DELETE FROM sessions
WHERE token_hash = :token_hash
RETURNING id;