class Animal:
    def __init__(self, name: str, age: int = 0):
        self.name = name
        self.age = age

    def eat(self):
        print(f"{self.name} is eating.")

    def sleep(self):
        print(f"{self.name} is sleeping.")

    def get_age(self) -> int:
        return self.age

    def move(self):
        print(f"{self.name} is moving.")

class Dog(Animal):
    # removed the super().__init__(name, age) call from the constructor for extendability, as the Dog class can inherit the constructor from the Animal class without needing to redefine it.
    def bark(self):
        print(f"{self.name} is barking.")    

    def move(self):
        print(f"{self.name} is running on 4 legs.")  # Overriding the move method from Animal class

class Cat(Animal):
    # removed the super().__init__(name, age) call from the constructor for extendability, as the Cat class can inherit the constructor from the Animal class without needing to redefine it.
    def meow(self):
        print(f"{self.name} is meowing.")

    def move(self):
        print(f"{self.name} is walking gracefully.")  # Overriding the move method from Animal class    

class BullDog(Dog):
    # removed the super().__init__(name, age) call from the constructor for extendability, as the BullDog class can inherit the constructor from the Dog class without needing to redefine it.
    def growl(self):
        print(f"{self.name} is growling.")

dog = Dog("Buddy", 3)
dog.eat()  # Inherited method from Animal class
dog.sleep()  # Inherited method from Animal class
dog.bark()  # Method specific to Dog class     
print(f"{dog.name} is {dog.get_age()} years old.")  # Using inherited method to get age
dog.move()  # Calling the overridden move method from Dog class


cat = Cat("Whiskers", 6)
cat.eat()  # Inherited method from Animal class
cat.sleep()  # Inherited method from Animal class   
cat.meow()  # Method specific to Cat class
print(f"{cat.name} is {cat.get_age()} years old.")  # Using inherited method to get age
cat.move()  # Calling the overridden move method from Cat class

bull_dog = BullDog("Max", 5)
bull_dog.eat()  # Inherited method from Animal class
bull_dog.sleep()  # Inherited method from Animal class
bull_dog.bark()  # Method specific to Dog class
bull_dog.growl()  # Method specific to BullDog class
print(f"{bull_dog.name} is {bull_dog.get_age()} years old.")  # Using inherited method to get age
bull_dog.move()  # Calling the overridden move method from Dog class (inherited by BullDog)