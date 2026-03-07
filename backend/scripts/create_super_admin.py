# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from dotenv import load_dotenv
from pathlib import Path
from argon2 import exceptions, PasswordHasher
from email_validator import validate_email, EmailNotValidError
from getpass import getpass


# ======================================================
# LOAD .env
# ======================================================


backend = Path(__file__).resolve().parent.parent
env_path = backend / ".env"
load_dotenv(env_path, override=True)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend import validators, queries
from backend.core.database_config import SessionLocal


# ======================================================
# SUPER ADMIN CREDENTIALS
# ======================================================


hasher = PasswordHasher()


def super_admin():

    param = dict()

    # username
    username = input("Enter username: ")
    if not validators.validate_username(username):
        print("Invalid username")
        return
    norm_username = validators.normalize_username(username)
    param["username"] = norm_username

    # password
    MAX_ATTEMPTS = 3
    for attempt in range(MAX_ATTEMPTS):
        plain_password = getpass("Enter password: ")
        confirm_password = getpass("Confirm password: ")

        if plain_password != confirm_password:
            print("Passwords do not match. Try again")
            continue

        if not validators.validate_password(plain_password):
            print("Password does not meet requirements")
            continue

        password_hash = ""
        try:
            password_hash = hasher.hash(plain_password)
            param["password_hash"] = password_hash
            break
        except exceptions.HashingError as e:
            print(f"Failed to hash password: {e}")
            return
    else:
        print("Too many failed attempts. Aborting")
        return

    # email
    email = input("Enter email: ")
    try:
        emailinfo = validate_email(email, check_deliverability=True)
        email = emailinfo.normalized
        param["email"] = email
    except EmailNotValidError:
        print("invalid email")
        return

    # first name
    first_name = input("Enter first name: ")
    norm_first_name = validators.normalize_first_name(first_name)
    param["first_name"] = norm_first_name

    # last name
    last_name = input("Enter last name: ")
    norm_last_name = validators.normalize_last_name(last_name)
    param["last_name"] = norm_last_name

    db = SessionLocal()

    try:
        queries.create_super_admin(db, param)
        db.commit()
        print(f"super admin created")
    
    except Exception as e:
        db.rollback()
        print(f"failed to generate super admin")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    super_admin()
