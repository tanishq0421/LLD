class PaymentProcessor:
    def __init__(self, payment_method: str, amount: float) -> None:
        self.__payment_method = payment_method
        self.__amount = amount

    def process_payment(self) -> None:
        if self.__payment_method == "credit_card":
            print(f"Processing credit card payment of ${self.__amount}.")
        elif self.__payment_method == "paypal":
            print(f"Processing PayPal payment of ${self.__amount}.")
        elif self.__payment_method == "bank_transfer":
            print(f"Processing bank transfer payment of ${self.__amount}.")
        elif self.__payment_method == "upi":
            print(f"Processing UPI payment of ${self.__amount}.")
        else:
            raise ValueError("Unsupported payment method")    

payment1 = PaymentProcessor("credit_card", 100.0)
payment1.process_payment()
payment2 = PaymentProcessor("paypal", 50.0)
payment2.process_payment()
payment3 = PaymentProcessor("bank_transfer", 200.0)
payment3.process_payment()
payment4 = PaymentProcessor("upi", 75.0)
payment4.process_payment()        