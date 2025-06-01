class InvalidVersionError(Exception):
    """Raised when the requested file version does not exist"""
    file_version: int

    def __init__(self, file_version: int):
        self.file_version = file_version
        super().__init__(f"Requested file version not found: {file_version}")