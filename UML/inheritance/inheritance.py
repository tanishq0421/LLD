from typing import Any


class Animal:
    def __init__(self, name: str, age: int):
        self.__name = name
        self.__age = age

    def get_name(self) -> str:
        return self.__name

    def get_age(self) -> int:
        return self.__age

    def eat(self) -> None:
        print(f"{self.__name} is eating.")


class Dog(Animal):
    def __init__(self, name: str, age: int, breed: str) -> None:
        super().__init__(name, age)
        self.__breed = breed

    def get_breed(self) -> str:
        return self.__breed

    def bark(self) -> None:
        print(f"{self.get_name()} is barking.")

    def play_fetch(self) -> None:
        print(f"{self.get_name()} is playing fetch.")

dog = Dog("Buddy", 3, "Golden Retriever")
print(f"Dog's Name: {dog.get_name()}")
print(f"Dog's Age: {dog.get_age()}")
print(f"Dog's Breed: {dog.get_breed()}")
dog.eat()  # Inherited method from Animal class
dog.bark()  # Method specific to Dog class
dog.play_fetch()  # Method specific to Dog class