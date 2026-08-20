"""
STEP 2 of 3 - Liskov Substitution Principle (LSP)

ABC guarantees a subclass has the right METHOD NAMES.
It cannot guarantee the subclass HONOURS WHAT THOSE METHODS PROMISE.

LSP:  anywhere the code expects a Parent, you must be able to hand it a Child
      and have nothing break.

The trap: inheritance feels right whenever you can say "X is a Y" in English.
"A square IS A rectangle." True in geometry, false in code. LSP is about
substitutable BEHAVIOUR, not about vocabulary.
"""


# =========================================================== VIOLATION 1
# "A penguin IS A bird" - but the Bird class promised every bird can fly.
class Bird:
    def __init__(self, name: str):
        self.name = name

    def fly(self) -> None:
        print(f"{self.name} is flying.")


class Sparrow(Bird):
    pass


class Penguin(Bird):
    def fly(self) -> None:
        # Three bad ways out, all LSP violations:
        #   raise      -> caller crashes on a valid Bird
        #   pass       -> caller silently gets nothing (worse)
        #   print(...) -> lies about what happened
        raise NotImplementedError("Penguins can't fly!")


def migrate(birds: list[Bird]) -> None:
    """Written against Bird. Has no idea Penguin exists. Should never break."""
    for bird in birds:
        bird.fly()


# =========================================================== THE FIX 1
# Push the capability DOWN to the subset that actually has it.
# The hierarchy now describes what things CAN DO, not what they are called.
class BirdFixed:
    def __init__(self, name: str):
        self.name = name

    def eat(self) -> None:
        print(f"{self.name} is eating.")


class FlyingBird(BirdFixed):
    def fly(self) -> None:
        print(f"{self.name} is flying.")


class SparrowFixed(FlyingBird):
    pass


class PenguinFixed(BirdFixed):      # simply never claims it can fly
    def swim(self) -> None:
        print(f"{self.name} is swimming.")


def migrate_fixed(birds: list[FlyingBird]) -> None:
    for bird in birds:
        bird.fly()                  # every FlyingBird really can. No exceptions.


# =========================================================== VIOLATION 2
# The classic. Square passes every "is-a" test and still breaks callers.
class Rectangle:
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    def set_width(self, width: int) -> None:
        self._width = width

    def set_height(self, height: int) -> None:
        self._height = height

    def area(self) -> int:
        return self._width * self._height


class Square(Rectangle):
    # A square must keep its sides equal, so it is forced to break the
    # implied contract of set_width: "changes width and NOTHING else".
    def set_width(self, width: int) -> None:
        self._width = self._height = width

    def set_height(self, height: int) -> None:
        self._width = self._height = height


def resize_and_check(rect: Rectangle) -> None:
    """Any honest Rectangle satisfies this. Square cannot."""
    rect.set_width(5)
    rect.set_height(4)
    print(f"  {type(rect).__name__}: expected area 20, got {rect.area()}")


# =========================================================== THE FIX 2
# Squares and rectangles are siblings, not parent and child. Neither is
# mutable, so there is no set_width contract left to violate.
class Shape:
    def area(self) -> int:
        raise NotImplementedError


class RectangleFixed(Shape):
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height

    def area(self) -> int:
        return self.width * self.height


class SquareFixed(Shape):
    def __init__(self, side: int):
        self.side = side

    def area(self) -> int:
        return self.side ** 2


if __name__ == "__main__":
    print("--- violation 1: Penguin is a Bird, but breaks every Bird caller ---")
    try:
        migrate([Sparrow("Jack"), Penguin("Pingu")])
    except NotImplementedError as e:
        print("  crashed:", e)

    print("\n--- fix 1: only birds that can fly are asked to fly ---")
    migrate_fixed([SparrowFixed("Jack")])
    PenguinFixed("Pingu").swim()      # keeps its own ability, breaks no contract

    print("\n--- violation 2: Square silently returns the wrong answer ---")
    resize_and_check(Rectangle(1, 1))
    resize_and_check(Square(1, 1))    # no crash, no warning, just wrong

    print("\n--- fix 2: siblings, not parent/child ---")
    for shape in (RectangleFixed(5, 4), SquareFixed(4)):
        print(f"  {type(shape).__name__} area = {shape.area()}")

    print("""
Rule of thumb - your subclass probably violates LSP if it:
  * raises NotImplementedError on an inherited method
  * overrides a method to do nothing
  * strengthens what the caller must provide (narrower argument types)
  * weakens what the caller gets back (broader/None return, new exceptions)
  * changes state the parent's method promised not to touch
""")
