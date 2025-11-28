from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from .serializers import VerifyOTPAndLoginCodeSerializer, RequestOTPSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# Create your views here.

class RequestOPTView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)

        if serializer.is_valid():
            user, created = serializer.save()

            if created:
                message = 'ثبت نام شما با موفقیت انجام شد در ادامه کد تایید را برای ورود وارد کنید.'
            else:
                message = 'کد تایید ارسال شد لطفا ان را وارد کنید.'

            return Response({
                'detail': message,
                'is_new_user': created,
            },status=status.HTTP_200_OK)


        return Response(
            serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPAndLoginCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']

            return Response({
                'detail': 'ورود موفقیت امیز',
                'user_info':{'id': user.id,
                'phone': user.phone,
                'first_name':user.first_name,
                'last_name': user.last_name,
                },
                'token': token
            },status=status.HTTP_200_OK)


        return Response(
            serializer.errors,status=status.HTTP_400_BAD_REQUEST)
