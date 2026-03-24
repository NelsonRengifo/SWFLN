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


class FileIsEmpty(Exception):
    pass


class FailedToDeleteTutorials(Exception):
    pass


class InvalidDateRange(Exception):
    pass

class InvalidFileType(Exception):
    pass