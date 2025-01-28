import threading
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import datetime

# Function to send email notification using Mailjet
def send_email_to_client(email, f_email, f_password):
    subject = " Test Credentials"
    login_url = "http://127.0.0.1:8000/custom_login/"  # Local URL for login page.

    message = f"""
    Hello, your account has been created successfully.
              
    Your login credentials are:
    Username is {f_email}
    Password is: {f_password}
    
    To log in, click the following link:
    {login_url}
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    def send_email():
        try:
            result=send_mail(subject, message, from_email, [email])
            if result ==1:
                print(f"Email sent successfully to {email}")
            else:
                print(f"Failed to send email to {email}")

        except Exception as e:
            print(f"Error sending email: {e}")

    # Run the email sending in a separate thread
    email_thread = threading.Thread(target=send_email)
    email_thread.start()
    
# Function to send reminder email 5 minutes before the test:
def schedule_reminder(candidate):
    # Calculate reminder time (5 minutes before the scheduled time)
    reminder_time = candidate.time_slot - timedelta(minutes=5)
    # Ensure we only send reminders when the reminder time is within the current date
    if reminder_time.date() == datetime.datetime.today().date():
    
        # Prepare the reminder message
        reminder_message = f"Reminder: Your test is scheduled in 5 minutes. Please be ready."
    
        # Send email reminder
        send_email_to_client(candidate.c_email, candidate.c_id, "FakePassword")


from django import template

register = template.Library()


@register.filter
def split_option(option):
    return option.split(')')[0]
