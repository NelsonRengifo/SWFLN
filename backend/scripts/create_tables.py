from backend.queries import generate_schema


def create_tables():
    generate_schema()


if __name__ == "__main__":
    create_tables()
