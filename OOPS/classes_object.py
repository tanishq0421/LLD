
from typing import Optional

class Student:
    def __init__(self):
        self.name = None
        self.age = 0
        self.gender = None

    def display(self) -> None:
        print(f"Name: {self.name}, Age: {self.age}, Gender: {self.gender}")

    def set_info(self, name : str, age: int, gender: str) -> None:
        self.name = name
        self.age = age
        self.gender = gender

    def get_info(self) -> Optional[tuple]:
        if self.name is not None and self.age is not None and self.gender is not None:
            return (self.name, self.age, self.gender)
        else:
            return None

    def get_age(self) -> int:
        return self.age    
    
s1 = Student()
s1.set_info("Alice", 20, "Female")
s1.display()
print(s1.get_info())
print(s1.get_age())
