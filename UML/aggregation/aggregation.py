from typing import List

# Student class can exist independently of the Department class, demonstrating aggregation.
class Student:
    def __init__(self, name: str, roll_number: int):
        self.__name = name  # private attribute
        self.__roll_number = roll_number  # private attribute

    def get_name(self) -> str:
        return self.__name

    def get_roll_number(self) -> int:
        return self.__roll_number

# Department class demonstrating aggregation with Student class
class Department:
    def __init__(self, department_name: str):
        self.__department_name = department_name  # private attribute
        self.__students: List[Student] = []  # private attribute

    def add_student(self, student: Student) -> None:
        self.__students.append(student)

    def get_students(self) -> List[Student]:
        return self.__students

    def get_department_name(self) -> str:
        return self.__department_name

    def display_students(self) -> None:
        print(f"Department: {self.__department_name}")
        for student in self.__students:
            print(f"Student Name: {student.get_name()}, Roll Number: {student.get_roll_number()}")

student1 : Student = Student("Alice", 1)
student2 : Student = Student("Bob", 2)
department : Department = Department("Computer Science")
department.add_student(student1)
department.add_student(student2)
department.display_students()
del department  # Deleting the department object, but student objects still exist
department : Department = Department("Mathematics")
department.add_student(student1)  # Adding existing student to a new department
department.display_students()   