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


# ======================================================
# PASSWORD EXCEPTIONS
# ======================================================


class PasswordsMatch(Exception):
    pass


# ======================================================
# SENDGRID EXCEPTIONS
# ======================================================


class FailedToSend(Exception):
    pass


# ======================================================
# EMAIL EXCEPTIONS
# ======================================================


class EmailNotFound(Exception):
    pass
