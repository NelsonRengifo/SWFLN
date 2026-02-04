from argon2 import PasswordHasher


hasher = PasswordHasher()

# ======================================================
# USERNAME VALIDATION
# ======================================================


def validate_username(username) -> bool:

    # Alphanumeric characters only
    if not username.isalnum():
        return False

    # length of at least 3 characters
    if len(username) < 3:
        return False

# ======================================================
# USERNAME SANITATION
# ======================================================


def normalize_username(username) -> str:
    return username.strip()


# ======================================================
# PASSWORD VERIFICATION
# ======================================================

def verify_password(plain_password, stored_password) -> None:
    hasher.verify(stored_password, plain_password)
