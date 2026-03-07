/*
 * Returns CursorResult object
 */


SELECT *
FROM password_reset_tokens
WHERE token_hash = :token_hash AND expires_at > now();