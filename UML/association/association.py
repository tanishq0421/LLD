class Teacher:
    def __init__(self, name: str, student: 'Student'):
        self.__name = name  #private attribute
        self.__student : 'Student' = student  #private attribute to hold associated students

    def teach(self) -> None:   
        print(f"{self.__name} is teaching {self.__student.get_name()}.")

    def get_name(self) -> str:
        return self.__name
    
class Student:
    def __init__(self, name: str):
        self.__name = name  #private attribute

    def get_name(self) -> str:
        return self.__name
    
    def learn(self, teacher: Teacher) -> None:
        print(f"{self.__name} is learning from {teacher.get_name()}.")

student = Student("Alice")
teacher = Teacher("Mr. Smith", student)
teacher.teach()
del teacher  # Deleting the teacher object, but student object still exists
print(student.get_name())  # This will raise an error because teacher object is deleted