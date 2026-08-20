from user import User
from user_repository import UserRepository

# Depedency is used here, earlier we made association between User and UserRepository, now we are using dependency injection to pass the user object to the UserRepository class.
user1 = User("Alice", 25, "alice@example.com")
repo1 = UserRepository("db1", "password1")
print(user1.get_user_info())  # This will return the user's information as a tuple.
repo1.save_to_database(user1)  # This will save the user's data to the database.
repo1.delete_user(user1)  # This will delete the user's data from the database.      