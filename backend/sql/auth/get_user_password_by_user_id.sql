/*
 * Returns CursorResult object
 */

SELECT password_hash
FROM users
WHERE user_id = :user_id;