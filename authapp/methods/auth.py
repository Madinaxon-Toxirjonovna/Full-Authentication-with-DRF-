import datetime
import random
import uuid
from methodism import custom_response, MESSAGE
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from authapp.models import CustomUser, OTP
from authapp.serializers import LoginSerializer, UserSerializer, RegisterSerializer


def register(request, params):
    serializer = RegisterSerializer(data=params)
    if serializer.is_valid():
        serializer.save()
        return custom_response({"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz"})
    return {
        "bu register": "register"}

def login(request, params):
    user = CustomUser.objects.filter(phone=params['phone']).first()
    if not user:
        return custom_response(False, message=MESSAGE['UserPasswordError'])
    if not user.check_password(params['password']):
        return ({
           "Error": "Xato password kiritingiz"
        })

    serializer = LoginSerializer(data=params)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Muvaffaqiyatli kirildi!",
            "token": token.key
        })

def logout(request, params):
    token = Token.objects.filter(user=request.user).first()
    if token:
        token.delete()
        return custom_response(True, message=MESSAGE['LogOut'])

def get_profile(request, params):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

def profile_update(request, params):
    user = request.user
    serializer = UserSerializer(user, data=params)
    if serializer.is_valid():
        serializer.save()
        return custom_response({"message": "Ma'lumotlar to'liq yangilandi"})

def profile_delete(request, params):
    user = request.user
    user.delete()
    return custom_response({"message": "Akkount o'chirildi"})

def change_password(request, params):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    user = request.user
    old = request.data.get("old")
    new = request.data.get("new")
    confirm = request.data.get("confirm")

    if not user.check_password(old):
        return custom_response({"error": "Hozirgi parolni to'g'ri kiriting."})

    if new != confirm:
        return custom_response({"error": "New password va confirm password mos kelmadi."})
    if old == new:
        return custom_response({"error": "hozirgi password va yangi password bir xil bolishi mumkin emas."})

    user.set_password(new)
    user.save()

    return custom_response({"success": "Password muvaffaqiyatli o'zgartirildi."})

def authone(request, params):
    data = params
    if not data['phone']:
        return custom_response({
            'error': "To'g'ri malumot kiritilmagan"
        })

    if len(str(data['phone'])) != 12 or not isinstance(data['phone'], int) or str(data['phone'])[:3] != '998':
        return custom_response({
            'error': "Telefon raqami noto'g'ri kiritildi"
        })

    code = ''.join([str(random.randint(1, 9999))[-1] for _ in range(4)])
    key = uuid.uuid4().__str__() + code
    otp = OTP.objects.create(phone=data['phone'], key=key)

    return Response({
        'otp': code,
        'token': otp.key
    })

def authtwo(request, params):
    data = params
    if not data['code'] or not data['key']:
        return custom_response({
            "error": "Siz to'liq malumot kiritmadingiz"
        })
    otp = OTP.objects.filter(key=data['key']).first()
    if not otp:
        return custom_response({
            "Error": "Xato key"
        })

    now = datetime.datetime.now()
    return Response({
        "message": True
    })