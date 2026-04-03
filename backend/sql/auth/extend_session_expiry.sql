/*
 * Returns CursorResult Object
 */

UPDATE sessions
SET expires_at = expires_at + INTERVAL '8 hours'
WHERE user_id = :user_id AND token_hash = :token_hash;