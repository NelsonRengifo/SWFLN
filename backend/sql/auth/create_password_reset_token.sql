/*
 * Returns CursorResult object
 */

INSERT INTO password_reset_tokens (user_id, token_hash)
VALUES                            (:user_id, :token_hash)
RETURNING id;