class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.__name = name
        self.__age = age
        self.__email = email

    def get_user_info(self) -> tuple:
        return (self.__name, self.__age, self.__email)

    def is_adult(self) -> bool:
        return self.__age >= 18    

    def save_to_database(self) -> None:
        # Simulating saving user data to a database
        print(f"Saving {self.__name}'s data to the database.")

    def delete_user(self) -> None:
        # Simulating deleting user data from a database
        print(f"Deleting {self.__name}'s data from the database.")    