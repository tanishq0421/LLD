from email_service import EmailService
from sms_service import SMSService

class NotificationService:
    def __init__(self) -> None:
        self.email_service = EmailService()
        self.sms_service = SMSService()

    def notify_by_email(self, message: str) -> None:
        self.email_service.send_email(message)

    def notify_by_sms(self, message: str) -> None:
        self.sms_service.send_sms(message)    


ns = NotificationService()
ns.notify_by_email("Hello via Email!")  # Output: Sending email: Hello via Email
ns.notify_by_sms("Hello via SMS!")      # Output: Sending SMS: Hello via SMS