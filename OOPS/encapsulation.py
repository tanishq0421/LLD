class Bank:
    def __init__(self, account_name: str, account_number: str, balance: float = 0.0):
        self.__account_name = account_name     # Private attribute
        self.__account_number = account_number # Private attribute
        self.__balance = balance               # Private attribute

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self.__balance += amount
            print(f"Deposited ${amount:.2f}. New balance: ${self.__balance:.2f}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        if self.__isServerLive():
            if 0 < amount <= self.__balance:
                self.__balance -= amount
                print(f"Withdrew ${amount:.2f}. New balance: ${self.__balance:.2f}")
            else:
                print("Invalid withdrawal amount or insufficient funds.")
        else:
            print("Server is not live. Please try again later.")

    def get_balance(self) -> float:
        return self.__balance

    def set_account_name(self, name: str) -> None:
        self.__account_name = name

    def get_acount_info(self) -> tuple:
        return (self.__account_name, self.__account_number)

    #private method to simulate server status check
    def __isServerLive(self) -> bool: 
        # Simulating a server check (for demonstration purposes)
        return False
    
acc1 = Bank("John Doe", "123456789", 1000.0)
acc1.deposit(500.0)
#acc1.__balance(10000) This line will raise an AttributeError because __balance is a private attribute and cannot be accessed directly from outside the class.
acc1.withdraw(200.0)
print(f"Current balance: ${acc1.get_balance():.2f}")                 
print(f"Account Info: {acc1.get_acount_info()}")