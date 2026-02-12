/*
 * Returns CursorResult object
 */

SELECT password_hash, user_id
FROM users
WHERE username = :username;