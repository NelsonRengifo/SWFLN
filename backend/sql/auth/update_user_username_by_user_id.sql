/*
 * Returns CursorResult object
 */

UPDATE users
SET username = :username
WHERE user_id = :user_id
RETURNING user_id;