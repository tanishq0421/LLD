
from user import User

class UserRepository:
    def __init__(self, db: str, password: str) -> None:
        self.__db = db
        self.__password = password

    def save_to_database(self, user: User) -> None:
        # Simulating saving user data to a database
        print(f"Saving {user.get_name()}'s data to the database.")

    def delete_user(self, user: User) -> None:
        # Simulating deleting user data from a database
        print(f"Deleting {user.get_name()}'s data from the database.")    