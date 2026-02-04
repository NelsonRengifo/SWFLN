# ======================================================
# VALIDATE LOGIN CREDENTIALS EXCEPTION
# ======================================================


class InvalidCredentials(Exception):
    pass


class InvalidRole(Exception):
    pass


# ======================================================
# SESSION TOKEN EXCEPTION
# ======================================================


class InvalidToken(Exception):
    pass


# ======================================================
# REGISTER A NEW USER EXCEPTIONS
# ======================================================


class InvalidUsername(Exception):
    pass


class UsernameTaken(Exception):
    pass


class InvalidPassword(Exception):
    pass


class EmailTaken(Exception):
    pass


class FailedToHash(Exception):
    pass


class InvalidUserRole(Exception):
    pass
