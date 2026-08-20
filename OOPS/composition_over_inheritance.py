"""
STEP 3 of 3 - Composition over Inheritance

LSP told you when inheritance is WRONG.
This file is about when inheritance is merely a BAD DEAL.

Inheritance gives a class exactly one axis of variation: its parent chain.
Real objects vary along several axes at once. Model each axis with inheritance
and the class count multiplies instead of adding.

    inheritance:  2 ways to move x 3 ways to speak  = 6 classes
    composition:  2 movers       + 3 speakers       = 5 small parts,
                  and ANY combination is free

"Favor object composition over class inheritance."  - Gang of Four, 1994
"""

from abc import ABC, abstractmethod


# ============================================================ the explosion
# Animals vary by how they MOVE and what SOUND they make. Model both with
# inheritance and you must write one class per combination.
class Animal:
    def __init__(self, name: str):
        self.name = name


class WalkingAnimal(Animal):
    def move(self): print(f"{self.name} walks.")


class SwimmingAnimal(Animal):
    def move(self): print(f"{self.name} swims.")


class WalkingBarkingAnimal(WalkingAnimal):
    def speak(self): print(f"{self.name} barks.")


class WalkingMeowingAnimal(WalkingAnimal):
    def speak(self): print(f"{self.name} meows.")


class SwimmingBarkingAnimal(SwimmingAnimal):
    # A seal barks and swims. Note the barking code is now duplicated,
    # because it cannot be shared with WalkingBarkingAnimal.
    def speak(self): print(f"{self.name} barks.")


# ...and adding "flies" or "hisses" means writing every combination again.
# Worse: a dog that learns to swim cannot change class at runtime.


# ============================================================ composition
# Each axis of variation becomes its own small, swappable object.
class MoveBehaviour(ABC):
    @abstractmethod
    def move(self, name: str) -> None: ...


class Walk(MoveBehaviour):
    def move(self, name: str) -> None: print(f"{name} walks on 4 legs.")


class Swim(MoveBehaviour):
    def move(self, name: str) -> None: print(f"{name} swims.")


class Fly(MoveBehaviour):
    def move(self, name: str) -> None: print(f"{name} flies.")


class SoundBehaviour(ABC):
    @abstractmethod
    def speak(self, name: str) -> None: ...


class Bark(SoundBehaviour):
    def speak(self, name: str) -> None: print(f"{name} barks.")


class Meow(SoundBehaviour):
    def speak(self, name: str) -> None: print(f"{name} meows.")


class Silent(SoundBehaviour):
    def speak(self, name: str) -> None: print(f"{name} says nothing.")


class ComposedAnimal:
    """HAS-A movement, HAS-A sound - instead of IS-A walking barking thing."""

    def __init__(self, name: str, mover: MoveBehaviour, speaker: SoundBehaviour):
        self.name = name
        self._mover = mover              # injected, not inherited
        self._speaker = speaker

    def move(self) -> None:
        self._mover.move(self.name)      # delegation: forward to the part

    def speak(self) -> None:
        self._speaker.speak(self.name)

    def set_mover(self, mover: MoveBehaviour) -> None:
        self._mover = mover              # behaviour can change at RUNTIME


if __name__ == "__main__":
    print("--- inheritance: one class per combination ---")
    for animal in (WalkingBarkingAnimal("Buddy"),
                   WalkingMeowingAnimal("Whiskers"),
                   SwimmingBarkingAnimal("Sealy")):
        animal.move()
        animal.speak()
    print("  3 combinations used so far -> 6 classes written, bark() duplicated.")

    print("\n--- composition: mix and match, no new classes ---")
    zoo = [
        ComposedAnimal("Buddy",    Walk(), Bark()),
        ComposedAnimal("Whiskers", Walk(), Meow()),
        ComposedAnimal("Sealy",    Swim(), Bark()),   # combination is free
        ComposedAnimal("Tweety",   Fly(),  Silent()), # so is this one
    ]
    for animal in zoo:
        animal.move()
        animal.speak()

    print("\n--- the thing inheritance simply cannot do: change at runtime ---")
    buddy = zoo[0]
    buddy.move()
    buddy.set_mover(Swim())              # Buddy learns to swim; no new class,
    buddy.move()                         # no reconstruction, same object

    print("""
How to choose:
  IS-A, and every parent method makes sense on the child  -> inheritance
  HAS-A, or behaviour varies independently, or may change -> composition

Signals you should have composed instead:
  * a class name that is a list of adjectives (WalkingBarkingAnimal)
  * a subclass that overrides most of its parent
  * needing an object to change category while it is alive
  * copy-pasting a method between two sibling classes

This exact pattern - swappable behaviour objects injected into a context -
is the Strategy pattern, and it is what dependency injection injects.
""")
