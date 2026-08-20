class User:
    def __init__(self, name: str, age: int, email: str) -> None:
        self.__name = name
        self.__age = age
        self.__email = email

    def get_user_info(self) -> tuple:
        return (self.__name, self.__age, self.__email)

    def is_adult(self) -> bool:
        return self.__age >= 18    

    def get_name(self) -> str:
        return self.__name