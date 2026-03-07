/*
 * Returns CursorObject result
 */

INSERT INTO uploaded_files (
uploaded_file_id, 
uploaded_by, 
original_file_name, 
original_file_size_in_bytes, 
source, 
storage_path, 
checksum_sha256)

VALUES (
:uploaded_file_id, 
:uploaded_by, 
:original_file_name, 
:original_file_size_in_bytes, 
:source, 
:storage_path, 
:checksum_sha256
)

RETURNING uploaded_file_id;