# enroll/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import send_mail
from .models import User, OTP
from .serializers import RegisterSerializer, VerifyOTPSerializer, ResendOTPSerializer, CreatePasswordSerializer
from .utils import create_response
import random
import datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Email already registered')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(email=email)
            otp = self.create_otp(user)
            print(otp.code)
            # self.send_otp(email, otp.code)
            response_data = create_response(
                'success', 
                status.HTTP_201_CREATED, 
                'OTP sent to email', 
                {'email': email, 'account_id': user.account_id, 'chat_id': user.chat_id}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid data', serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def create_otp(self, user):
        code = ''.join(random.choices('0123456789', k=6))
        expires_at = timezone.now() + datetime.timedelta(minutes=10)
        otp = OTP.objects.create(user=user, code=code, expires_at=expires_at)
        return otp

    def send_otp(self, email, code):
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {code}',
            'support@bixmerchant.com',
            [email],
            fail_silently=False,
        )

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
                otp = OTP.objects.filter(user=user, code=code).latest('created_at')
            except (User.DoesNotExist, OTP.DoesNotExist):
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid email or OTP')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if otp.is_expired():
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'OTP has expired')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()
            response_data = create_response(
                'success', 
                status.HTTP_200_OK, 
                'Email verified', 
                {'email': email, 'account_id': user.account_id, 'chat_id': user.chat_id}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid data', serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid email')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if user.is_verified:
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Email already verified')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            otp = OTP.objects.filter(user=user).latest('created_at')

            if otp.attempts >= 3 and timezone.now() < otp.created_at + datetime.timedelta(hours=1):
                response_data = create_response('error', status.HTTP_429_TOO_MANY_REQUESTS, 'Too many attempts, try again later')
                return Response(response_data, status=status.HTTP_429_TOO_MANY_REQUESTS)

            otp.attempts += 1
            otp.save()
            self.send_otp(email, otp.code)
            response_data = create_response(
                'success', 
                status.HTTP_200_OK, 
                'OTP resent', 
                {'email': email, 'account_id': user.account_id, 'chat_id': user.chat_id}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid data', serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def send_otp(self, email, code):
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

class CreatePasswordView(APIView):
    def post(self, request):
        serializer = CreatePasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']

            if password != confirm_password:
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Passwords do not match')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid email')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_verified:
                response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Email not verified')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()
            response_data = create_response(
                'success', 
                status.HTTP_200_OK, 
                'Password set, you can now login', 
                {'email': email, 'account_id': user.account_id, 'chat_id': user.chat_id}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response('error', status.HTTP_400_BAD_REQUEST, 'Invalid data', serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
