from argon2 import PasswordHasher
from password_strength import PasswordPolicy


hasher = PasswordHasher()
policy = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1)

# ======================================================
# USERNAME VALIDATION & SANITATION
# ======================================================


def validate_username(username) -> bool:

    # Alphanumeric characters only
    return username.isalnum()


def normalize_username(username) -> str:

    # Remove spaces
    name_list = username.split()
    norm_username = "".join(name_list)

    # Lowercase username
    return norm_username.lower()


# ======================================================
# PASSWORD VERIFICATION & VALIDATION
# ======================================================


def verify_password(plain_password, stored_password) -> None:

    hasher.verify(stored_password, plain_password)


def validate_password(plain_password) -> bool:

    failures_list = policy.test(plain_password)
    return not failures_list

# ======================================================
# EMAIL SANITATION
# ======================================================


def normalize_email(email) -> str:

    return email.strip().lower()

# ======================================================
# FIRST NAME SANITATION
# ======================================================


def normalize_first_name(first_name) -> str:

    # Remove spaces
    first_name_list = first_name.split()
    norm_first_name = "".join(first_name_list)

    # Lowercase username
    return norm_first_name.lower()

# ======================================================
# LAST NAME SANITATION
# ======================================================


def normalize_last_name(last_name) -> str:

    # Remove spaces
    last_name_list = last_name.split()
    norm_last_name = "".join(last_name_list)

    # Lowercase username
    return norm_last_name.lower()
