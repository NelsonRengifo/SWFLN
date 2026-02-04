/*
 * Returns CursorResult object
 */

INSERT INTO users (username, email, first_name, last_name, password_hash, user_role)
VALUES            (:username, :email, :first_name, :last_name, :password_hash, 'super admin')
RETURNING user_id;