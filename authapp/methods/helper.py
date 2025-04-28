from django.core.mail import send_mail
from blog import settings
import re
import threading
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
PHONE_REGEX = re.compile(r'^\+?\d{9,15}$')


# def send_to_mail(request, address, message):
#     message = f"Salom, {address}.\n\n Code: {message}"
#     subject = "Confirmation code"
#     address = address
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [address])


def send_email_in_thread(to_email: str, code: str):
    subject = "Confirmation code"
    message = f"Salom, {to_email}.\n\nTasdiqlash kodingiz: {code}"
    email = settings.EMAIL_HOST_USER
    recipient_list = [to_email]
    send_mail(subject, message, email, recipient_list)

def send_code(address, code: str):
    addr_str = str(address)
    if EMAIL_REGEX.match(addr_str):
        thread = threading.Thread(
            target=send_email_in_thread,
            args=(addr_str, code),
            daemon=True
        )
        thread.start()
    elif PHONE_REGEX.match(addr_str):
        print(f"Telefon raqamga kod yuborish: {addr_str} -> {code}")
    else:
        raise ValueError("Nimadir xato.")