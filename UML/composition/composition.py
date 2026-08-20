from typing import Optional

class Engine:
    def __init__(self, engine_type: str, horsepower: int) -> None:
        self.__engine_type = engine_type  # private attribute
        self.__horsepower = horsepower  # private attribute

    def get_details(self) -> str:
        return f"Engine Type: {self.__engine_type}, Horsepower: {self.__horsepower} HP"

    def start(self) -> None:
        print(f"{self.__engine_type} engine started.")


class Car:
    def __init__(self, brand: str, model: str, engine: str, horsepowere: int) -> None:             
        self.__brand = brand # private attribute
        self.__model = model  # private attribute
        self.__engine = Engine(engine, horsepowere)  # composition relationship

    def get_car_details(self) -> str:
        engine_details = self.__engine.get_details()
        return f"Car Brand: {self.__brand}, Model: {self.__model}, {engine_details}"    

    def start_car(self) -> None:
        self.__engine.start()
        print(f"{self.__brand} {self.__model} is ready to drive.") 


car = Car("Toyota", "Camry", "V6", 301)
print(car.get_car_details())
car.start_car()