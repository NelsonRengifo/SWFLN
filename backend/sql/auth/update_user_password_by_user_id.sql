/*
 * Returns CursorResult object
 */

UPDATE users
SET password_hash = :password_hash
WHERE user_id = :user_id
RETURNING user_id;