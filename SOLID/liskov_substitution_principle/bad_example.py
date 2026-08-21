from abc import ABC, abstractmethod

class BankAccount(ABC):
    def __init__(self, account_name: str, account_number: str, balance: float = 0.0):
        self._account_name = account_name
        self._account_number = account_number
        self._balance = balance

    def get_account_info(self) -> tuple:
        return (self._account_name, self._account_number, self._balance)

    @abstractmethod
    def deposit(self, amount: float) -> None:
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        pass


class SavingsAccount(BankAccount):
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
            print(f"Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        if 0 < amount <= self._balance:
            self._balance -= amount
            print(f"Withdrew ${amount:.2f}. New balance: ${self._balance:.2f}")
        else:
            print("Invalid withdrawal amount or insufficient funds.")

saving = SavingsAccount("John Doe", "123456789", 1000.0)
print(saving.get_account_info())  # Output: ('John Doe', '123456789', 1000.0)
saving.deposit(500.0)  # Output: Deposited $500.00. New balance: $1500.00
saving.withdraw(200.0)  # Output: Withdrew $200.00. New balance: $1300.00
print(saving.get_account_info())  # Output: ('John Doe', '123456

class FixedDepositAccount(BankAccount):
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
            print(f"Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        # Fixed deposit accounts typically do not allow withdrawals before maturity.
        print("Withdrawals are not allowed from a fixed deposit account before maturity.")

fixed_deposit = FixedDepositAccount("Alice Smith", "987654321", 5000.0)
print(fixed_deposit.get_account_info())  # Output: ('Alice Smith', '987654321', 5000.0)
fixed_deposit.deposit(1000.0)  # Output: Deposited $1000.00. New balance: $6000.00
fixed_deposit.withdraw(2000.0)  # Output: Withdrawals are not allowed from a fixed deposit account before maturity.
print(fixed_deposit.get_account_info())  # Output: ('Alice Smith', '987654321', 6000.0)