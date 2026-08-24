from notification_channel import NotificationChannel

class SMSService(NotificationChannel):
    def send_notification(self, message: str) -> None:
        # Simulating sending an SMS
        print(f"Sending SMS: {message}")