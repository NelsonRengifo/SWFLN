/*
 * Returns CursorResult object
 */

INSERT INTO users (username, password_hash, email, first_name, last_name, user_role)
VALUES            (:username, :password_hash, :email, :first_name, :last_name, :user_role)
RETURNING user_id;