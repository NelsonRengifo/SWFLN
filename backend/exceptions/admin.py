# ======================================================
# UPLOADED FILE EXCEPTIONS
# ======================================================

class NoFileWasUploaded(Exception):
    pass


class InvalidFileFormat(Exception):
    pass


class DuplicateFile(Exception):
    pass


class StorageUploadFailError(Exception):
    pass


class FailedToUploadMetaData(Exception):
    pass