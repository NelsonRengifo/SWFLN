/*
 * Returns CursorResult object
 */


DELETE FROM password_reset_tokens
WHERE expires_at < NOW();
