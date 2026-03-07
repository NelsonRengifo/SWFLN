/*
 Returns true/false literal
 */

SELECT EXISTS (
    SELECT 1
    FROM uploaded_files
    WHERE checksum_sha256 = :checksum_sha256
);