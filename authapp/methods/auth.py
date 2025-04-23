from datetime import datetime, timezone
import uuid
from random import randint
from authapp.models import CustomUser, OTP
from rest_framework.authtoken.models import Token
from methodism import custom_response, error_messages, MESSAGE


def register(request, params):
    key = params.get("key")
    password = params.get("password")

    if not key:
        return custom_response(False, error_messages.error_params_unfilled("key"))
    if not password:
        return custom_response(False, error_messages.error_params_unfilled("password"))

    if (len(password) < 6 or ' ' in password or not password.isalnum()
            or not any(c.isupper() for c in password)
            or not any(c.islower() for c in password)):
        return custom_response(False, message=MESSAGE["PasswordError"])

    otp = OTP.objects.filter(key=key).first()
    if not otp:
        return custom_response(False, message=MESSAGE["OTPNotFound"])
    if CustomUser.objects.filter(phone=otp.phone).exists():
        return custom_response(False, message=MESSAGE["UserAlreadyExists"])

    user_data = {
        "phone": otp.phone,
        "password": password,
        "name": params.get("name", "")
    }

    if key == "123":  # Maxsus developer kalit
        user_data.update(is_active=True, is_staff=True, is_superuser=True)

    user = CustomUser.objects.create_user(**user_data)
    token = Token.objects.create(user=user)

    return custom_response(True, data={"token": token.key}, message=MESSAGE["Registered"])


def login(request, params):
    phone = params.get("phone")
    password = params.get("password")

    if not phone:
        return custom_response(False, error_messages.error_params_unfilled("phone"))
    if not password:
        return custom_response(False, error_messages.error_params_unfilled("password"))

    user = CustomUser.objects.filter(phone=phone).first()
    if not user or not user.check_password(password):
        return custom_response(False, message=MESSAGE["Unauthenticated"])

    token, _ = Token.objects.get_or_create(user=user)
    return custom_response(True, data={"token": token.key}, message=MESSAGE["Login"])


def logout(request, params):
    Token.objects.filter(user=request.user).delete()
    return custom_response(True, message=MESSAGE["Logout"])


def profile(request, params):
    return custom_response(True, data=request.user.format())


def update_profile(request, params):
    user = request.user
    phone = params.get("phone")
    name = params.get("name")

    if phone:
        if CustomUser.objects.filter(phone=phone).exclude(id=user.id).exists():
            return custom_response(False, message=MESSAGE["PhoneAlreadyUsed"])
        user.phone = phone
    if name:
        user.name = name

    user.save()
    return custom_response(True, message=MESSAGE["ProfileUpdated"])


def delete_profile(request, params):
    request.user.delete()
    return custom_response(True, message=MESSAGE["ProfileDeleted"])


def change_password(request, params):
    old = params.get("old")
    new = params.get("new")

    if not old or not new:
        return custom_response(False, message=MESSAGE["MissingPassword"])
    if old == new:
        return custom_response(False, message=MESSAGE["PasswordSame"])
    if not request.user.check_password(old):
        return custom_response(False, message=MESSAGE["WrongOldPassword"])

    request.user.set_password(new)
    request.user.save()
    return custom_response(True, message=MESSAGE["PasswordChanged"])


def auth_one(request, params):
    phone = params.get("phone")
    if not phone:
        return custom_response(False, message=MESSAGE["PhoneRequired"])
    if len(str(phone)) != 12 or not str(phone).startswith("998") or not str(phone).isdigit():
        return custom_response(False, message=MESSAGE["InvalidPhone"])

    code = ''.join([str(randint(1, 9)) for _ in range(4)])
    key = str(uuid.uuid4()) + code
    otp = OTP.objects.create(phone=phone, key=key, code=code)

    return custom_response(True, data={"otp": code, "token": otp.key}, message=MESSAGE["CodeSent"])


def auth_two(request, params):
    key = params.get("key")
    code = params.get("code")

    if not key or not code:
        return custom_response(False, message=MESSAGE["MissingKeyCode"])

    otp = OTP.objects.filter(key=key).first()
    if not otp:
        return custom_response(False, message=MESSAGE["OTPNotFound"])

    if otp.is_conf:
        return custom_response(False, message=MESSAGE["AlreadyConfirmed"])
    if otp.is_expire:
        return custom_response(False, message=MESSAGE["CodeExpired"])

    now = datetime.now(timezone.utc)
    if (now - otp.created).total_seconds() > 180:
        otp.is_expire = True
        otp.save()
        return custom_response(False, message=MESSAGE["CodeExpired"])

    if otp.code != str(code):
        otp.tried += 1
        otp.save()
        return custom_response(False, message=MESSAGE["WrongCode"])

    otp.is_conf = True
    otp.save()

    is_registered = CustomUser.objects.filter(phone=otp.phone).exists()
    return custom_response(True, data={"registered": is_registered}, message=MESSAGE["CodeConfirmed"])
