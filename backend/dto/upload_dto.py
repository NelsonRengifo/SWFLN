from dataclasses import dataclass
from uuid import UUID

@dataclass
class FilePathResult:
    file_id: UUID
    file_path: str