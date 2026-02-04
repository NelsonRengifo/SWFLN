/*
 * Returns CursorResult object
 */
 
INSERT INTO sessions (user_id, token_hash)
VALUES               (:user_id, :token_hash)
RETURNING id;