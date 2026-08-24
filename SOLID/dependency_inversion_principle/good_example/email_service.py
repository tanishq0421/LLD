from notification_channel import NotificationChannel

class EmailService(NotificationChannel):
    def send_notification(self, message: str) -> None:
        # Simulating sending an email
        print(f"Sending email: {message}")