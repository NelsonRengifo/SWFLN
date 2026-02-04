/*
 * Returns true/false literal
 */

SELECT EXISTS(
    SELECT 1
    FROM users
    WHERE email = :email
);