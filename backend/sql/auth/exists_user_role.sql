/*
 * Returns true/false literal
 */

SELECT EXISTS (
    SELECT 1
    FROM sessions
    JOIN users ON sessions.user_id = users.user_id
    WHERE sessions.token_hash = :token_hash AND users.user_role = ANY(:valid_roles)
);