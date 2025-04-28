import datetime
import random
import re
import uuid
from methodism import METHODISM, custom_response, MESSAGE
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout

from .methods.helper import send_code
from .models import OTP, CustomUser
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from authapp import methods


class Main(METHODISM):
    file = methods
    token_key = "Token"
    not_auth_methods = ['register', 'login']


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Muvaffaqiyatli ro'yxatdan o'tdingiz"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.authtoken.models import Token

class LoginAPIView(APIView):
    def post(self, request):

        data = request.data
        
        user = CustomUser.objects.filter(phone=data['phone']).first()
        if not user:
            return custom_response(False, message=MESSAGE['UserPasswordError'])
        if not user.check_password(data['password']):
            return ({
                "Error": "Xato password kiritingiz"
            })
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Muvaffaqiyatli kirildi!",
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Muvaffaqiyatli chiqildi"}, status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ProfileUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ma'lumotlar to'liq yangilandi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Ma'lumotlar qisman yangilandi"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Akkount o'chirildi"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request):

        user = request.user
        old = request.data.get("old")
        new = request.data.get("new")
        confirm = request.data.get("confirm")

        if not user.check_password(old):
            return Response({"error": "Hozirgi parolni to'g'ri kiriting."}, status=status.HTTP_400_BAD_REQUEST)

        if new != confirm:
            return Response({"error": "New password va confirm password mos kelmadi."}, status=status.HTTP_400_BAD_REQUEST)

        if old == new:
            return Response({"error": "hozirgi password va yangi password bir xil bolishi mumkin emas."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new)
        user.save()

        return Response({"success": "Password muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)

EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

class AuthOne(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        phone = data.get('phone')
        if not email and not phone:
            return Response({'error': "Kamida telefon yoki email kiriting"}, status=400)

        if not data['phone']:
            return Response({
                'error': "To'g'ri malumot kiritilmagan"
            })

        if len(str(data['phone'])) != 12 or not isinstance(data['phone'], int) or str(data['phone'])[:3] != '998':
            return Response({
                'error': "Telefon raqami noto'g'ri kiritildi"
            })

        is_email = isinstance(email, str) and EMAIL_REGEX.match(email)
        is_phone = isinstance(phone, int) or (isinstance(phone, str) and phone.isdigit())

        if email and not is_email:
            return Response({'error': "Email formati noto‘g‘ri"}, status=400)

        code = ''.join([str(random.randint(1,9999))[-1] for _ in range(4)])
        key = uuid.uuid4().__str__() + code
        # send_to_mail(request, 'maxmudovamadinaxon27@gmail.com', int(code))

        if is_email:
            send_code(email, code)

        if is_phone:
            send_code(phone, code)
        otp = OTP.objects.create(phone=data['phone'], key=key)

        return Response({
            'otp': code,
            'token': otp.key
        })


class AuthTwo(APIView):
    def post(self, request):
        data = request.data
        if not data['code'] or not data['key']:
            return Response({
                "error": "Siz to'liq malumot kiritmadingiz"
            })
        otp = OTP.objects.filter(key=data['key']).first()

        if not otp:
            return Response({
                "Error": "Xato key"
            })

        now = datetime.datetime.now()
        return Response({
            "message": True
            })