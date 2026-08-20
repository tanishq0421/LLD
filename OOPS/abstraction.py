from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

# s = Shape()  # This will raise an error because Shape is an abstract class and cannot be instantiated directly.    

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * 3.14159 * self.radius    


rectange = Rectangle(5, 10)
print(f"Rectangle Area: {rectange.area()} m^2")
print(f"Rectangle Perimeter: {rectange.perimeter()} m")

circle = Circle(7)
print(f"Circle Area: {circle.area()} m^2")
print(f"Circle Perimeter: {circle.perimeter()} m ")