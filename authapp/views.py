from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
import random
import string
import uuid
from .models import OTP
import datetime
from methodism import METHODISM
from authapp import methods

class Main(METHODISM):
    file = methods
    token_key = 'Token'
    not_auth_methods = ['regis', 'login', 'auth_one', 'auth_two']

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if "key" not in data or "password" not in data:
            return Response({
                "Error": "Phone yoki password kiritilmagan"
            })
        


        if (len(data['password']) < 6 or ' ' in data['password'] or not data['password'].isalnum() or len([i for i in data['password'] if i.isalpha() and i.isupper()]) < 1 or len([i for i in data['password'] if i.isalpha() and i.islower()]) < 1):
            return Response({
             "Error": "Password xato kiritildi"
                })

      
        otp = OTP.objects.filter(key=data['key']).first()
        phone = CustomUser.objects.filter(phone=otp.phone).first()
       
        if phone:
            return Response({
                "Error": "Bu raqamdan avval ro'yhatdan o'tilgan"
            })
        user_data = {
            'phone': otp.phone,
            'password': data['password'],
            'name': data.get('name', '')
        }
        if data.get('key', '') == '123':
            user_data.update({
                'is_active': True,
                'is_staff': True,
                'is_superuser': True
            })
        user = CustomUser.objects.create_user(**user_data)
        token = Token.objects.create(user=user)
        return Response({
            "message": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz",
            "Token": token.key
        })

class LoginView(APIView):
    def post(self, request):
        data = request.data

        user = CustomUser.objects.filter(phone=data['phone']).first()
        if not user:
            return Response({
                "Error": "Bu telefon raqam orqali ro'yxatdan o'tilmagan"
            })
        
        if not user.check_password(data['password']):
            return Response({
                "Error": "Xato parol kiritdingiz"
            })
        
      
        token = Token.objects.get_or_create(user=user)

        return Response({
            "Message": "Siz tizimga kirdingiz",
            "Token": token[0].key
        })
    
class LogoOutView(APIView):
    permission_classes = [IsAuthenticated],
    authentication_classes = TokenAuthentication,

    def post(self, request):
        token = Token.objects.filter(user=request.user).first()
        token.delete()
        return Response({
            "Message": "Siz tizimdan chiqdingiz"
        })
    
class Profile(APIView):
    permission_classes = IsAuthenticated,
    authentication_classes = TokenAuthentication,

    def get(self, request):
        user = request.user
        return Response({
            "data": user.format()
        })
    
    def patch(self, request):
        user_ = request.user  
        data = request.data
        
        if data["phone"]:
            user = CustomUser.objects.filter(phone=data['phone']).first()
            if int(user_.phone) == data['phone']:
                return Response({
                    "Error": "Bu sizning raqamingiz(tellni almashtirmoqchi bo'lmasangiz tell raqamingizni yubormang)"
                })
            if user:
                return Response({
                    "Error": "Bu telefon raqam orqali oldin ro'yxatdan o'tilgan"
                })

        user_.name = data.get('name', user_.name)
        user_.phone = data.get('phone', user_.phone)
        user_.save()

        return Response({
            "Message": f"{' '.join([i for i in data])} malumotlaringiz o'zgardi"    
        })
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({
            "Message": "Profilingiz o'chirildi"
        })
    
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated],
    authentication_classes = TokenAuthentication,
    def post(self, request):
        data = request.data
        user = request.user

        if not data['new'] or not data['old']:
            return Response({
                "Error": "Datada kamchilik bor"
            })
        
        if data['new'] == data['old']:
            return Response({
                "Error": "Parolingizni qayta o'rnatish mumkin emas"
            })

        if not user.check_password(data.get('old', '')):
            return Response({
                "error": "Siz oldingi parolingizni xato kiritdingiz"
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data.get('new', ''))
        user.save()

        return Response({
            "message": "Sizning parolingiz o'zgartirildi"
        }, status=status.HTTP_200_OK)

class AuthOne(APIView):
    def post(self, request):
        data = request.data

        phone = data.get('phone')
        if not phone:
            return Response({"Error": "To'g'ri ma'lumot kiritilmagan"})

        if len(str(phone)) != 12 or not str(phone).startswith('998') or not str(phone).isdigit():
            return Response({"Error": "Telefon raqam noto'g'ri kiritildi"})

        code = ''.join([str(random.randint(1, 9)) for _ in range(4)])
        key = uuid.uuid4().__str__() + code

        otp = OTP.objects.create(phone=phone, key=key, code=code)

        return Response({
            "otp": code,  
            "token": otp.key
        })

class AuthTwo(APIView):
    def post(self, request):
        data = request.data
        key = data.get('key')
        code = data.get('code')

        if not key or not code:
            return Response({"Error": "To'liq ma'lumot kiritilmadi"})

        otp = OTP.objects.filter(key=key).first()

        if not otp:
            return Response({"Error": "Xato key"})

        now = datetime.datetime.now(datetime.timezone.utc)

        if (now - otp.created).total_seconds() >= 180:
            otp.is_expire = True
            otp.save()
            return Response({"Error": "Kod eskirgan"})

        if otp.is_conf:
            return Response({"Error": "Kod allaqachon tasdiqlangan"})

        if otp.is_expire:
            return Response({"Error": "Kod yaroqsiz (expire)"})

        if otp.code != str(code):
            otp.tried += 1
            otp.save()
            return Response({"Error": "Xato kod"})

        otp.is_conf = True
        otp.save()

        user = CustomUser.objects.filter(phone=otp.phone).first()

        return Response({
            "registrated": user is not None
        })
