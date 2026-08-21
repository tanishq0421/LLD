
from abc import ABC, abstractmethod


class BankAccount(ABC):
    def __init__(self, account_name: str, account_number: str, balance: float = 0.0):
        self._account_name = account_name
        self._account_number = account_number
        self._balance = balance

    @abstractmethod
    def deposit(self, amount: float) -> None:
        pass

    def get_account_info(self) -> tuple:
        return (self._account_name, self._account_number, self._balance)

class WithdrawableAccount(BankAccount):
    @abstractmethod
    def withdraw(self, amount: float) -> None:
        pass


class SavingsAccount(WithdrawableAccount):
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

class FixedDepositAccount(BankAccount):
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
            print(f"Deposited ${amount:.2f}. New balance: ${self._balance:.2f}")
        else:
            print("Deposit amount must be positive.")

    # FixedDepositAccount does not implement withdraw method, as withdrawals are not allowed before maturity.       

savingsAccount = SavingsAccount("John Doe", "123456789", 1000.0)
print(savingsAccount.get_account_info())  # Output: ('John Doe', '123456789', 1000.0)
savingsAccount.deposit(500.0)  # Output: Deposited $500.00. New balance: $1500.00
savingsAccount.withdraw(200.0)  # Output: Withdrew $200.00. New balance: $1300.00
print(savingsAccount.get_account_info())  # Output: ('John Doe', '123456789', 1300.0)

fixedDepositAccount = FixedDepositAccount("Alice Smith", "987654321", 5000.0)
print(fixedDepositAccount.get_account_info())  # Output: ('Alice Smith', '987654321', 5000.0)
fixedDepositAccount.deposit(1000.0)  # Output: Deposited $1000.00. New balance: $6000.00