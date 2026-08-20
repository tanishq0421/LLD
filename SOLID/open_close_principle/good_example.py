from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None:
        pass

class CreditCardPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing credit card payment of ${amount}.")

class PayPalPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing PayPal payment of ${amount}.")

class BankTransferPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing bank transfer payment of ${amount}.")        

class UPIPayment(PaymentMethod):
    def pay(self, amount: float) -> None:
        print(f"Processing UPI payment of ${amount}.")


class PaymentProcessor:
    def __init__(self, payment_method: PaymentMethod, amount: float) -> None:
        self.__payment_method = payment_method
        self.__amount = amount

    @classmethod
    def with_default_method(cls, amount: float) -> 'PaymentProcessor':
        return cls(CreditCardPayment(), amount)
    
    def process_payment(self) -> None:
        self.__payment_method.pay(self.__amount)

payment1 = PaymentProcessor(CreditCardPayment(), 100.0)
payment1.process_payment()
payment2 = PaymentProcessor(PayPalPayment(), 50.0)
payment2.process_payment()
payment3 = PaymentProcessor(BankTransferPayment(), 200.0)
payment3.process_payment()
payment4 = PaymentProcessor(UPIPayment(), 75.0)
payment4.process_payment()
payment5 = PaymentProcessor.with_default_method(150.0)  # Using the default payment method (Credit Card)
payment5.process_payment()
