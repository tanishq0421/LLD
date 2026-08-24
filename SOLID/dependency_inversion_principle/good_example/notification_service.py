from notification_channel import NotificationChannel

class NotificationService:
    def __init__(self, notification_channel: NotificationChannel) -> None:
        self.notification_channel = notification_channel

    def notify(self, message: str) -> None:
        self.notification_channel.send_notification(message)


from email_service import EmailService
email_service = EmailService()
notification_service_email = NotificationService(email_service)
notification_service_email.notify("Hello via Email!")  # Output: Sending email: Hello via Email

from sms_service import SMSService
sms_service = SMSService()  
notification_service_sms = NotificationService(sms_service)
notification_service_sms.notify("Hello via SMS!")  # Output: Sending SMS: Hello via SMS