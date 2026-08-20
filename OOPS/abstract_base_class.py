"""
STEP 1 of 3 - Abstract Base Classes (ABC)

Problem with plain inheritance:  nothing forces a subclass to implement the
methods the rest of your code depends on.  The failure shows up late, at the
call site, as an AttributeError or a silently wrong result.

ABC moves that failure to the earliest possible moment - object creation.
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------- the problem
class LooseAnimal:
    def speak(self):
        pass  # subclasses are "supposed to" override this... but nothing checks


class LooseSnake(LooseAnimal):
    pass  # forgot to implement speak()


# ---------------------------------------------------------------- the fix
class Animal(ABC):                      # ABC = this class cannot be instantiated
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def speak(self) -> None:
        """Every animal must define this. No default is possible."""

    # Concrete methods live happily alongside abstract ones - an ABC is NOT
    # an interface, it can carry shared implementation too.
    def eat(self) -> None:
        print(f"{self.name} is eating.")

    def introduce(self) -> None:
        # Template Method pattern: a concrete method built on abstract steps.
        print(f"I am {self.name}, and ", end="")
        self.speak()


class Dog(Animal):
    def speak(self) -> None:
        print("I bark.")


class Cat(Animal):
    def speak(self) -> None:
        print("I meow.")


class Snake(Animal):
    pass  # deliberately forgot speak() - watch what happens below


if __name__ == "__main__":
    print("--- without ABC: the bug hides until someone calls speak() ---")
    snake = LooseSnake()        # constructed happily
    print("LooseSnake() constructed fine, speak() returns:", snake.speak())
    print("...silently does nothing. Bug ships to production.\n")

    print("--- with ABC: subclasses that keep the contract ---")
    for animal in (Dog("Buddy"), Cat("Whiskers")):
        animal.eat()
        animal.introduce()

    print("\n--- with ABC: you cannot instantiate the abstract class itself ---")
    try:
        Animal("Generic")
    except TypeError as e:
        print("TypeError:", e)

    print("\n--- with ABC: an incomplete subclass fails at construction ---")
    try:
        Snake("Kaa")
    except TypeError as e:
        print("TypeError:", e)
