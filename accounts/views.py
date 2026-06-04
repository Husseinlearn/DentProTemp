from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UnifiedUserSerializer , DoctorProfileSerializer
from rest_framework import status
from django.contrib.auth import authenticate, login
from .models import CustomUser, Doctor
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
# Create your views here.
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def register_user(request):
    serializer = UnifiedUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'تم إنشاء المستخدم بنجاح'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    serializer = UnifiedUserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'تم التعديل على المستخدم بنجاح'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)

    if user:
        access_token = AccessToken.for_user(user)
        return Response({
            'access': str(access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    
    return Response({'error': 'الايميل  أو كلمة المرور غير موجود'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UnifiedUserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    users = CustomUser.objects.all()
    serializer = UnifiedUserSerializer(users, many=True)
    return Response(serializer.data)



class DoctorListSimpleAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        doctors = Doctor.objects.all()
        data = [
            {
                "id": str(doctor.id),
                "name": doctor.user.get_full_name(),
                "email": doctor.user.email
            }
            for doctor in doctors
        ]
        return Response(data)

class DoctorDetailAPIView(generics.RetrieveAPIView):
    queryset = Doctor.objects.select_related('user', 'user__profile').all()
    serializer_class = DoctorProfileSerializer
    lookup_field = 'id'
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_user(request):
#     try:
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return Response({"detail": "Refresh token is required."}, status=400)

#         token = RefreshToken(refresh_token)
#         token.blacklist()  #  إضافة التوكن إلى قائمة الحظر

#         return Response({"detail": "Logout successful. Token blacklisted."}, status=status.HTTP_205_RESET_CONTENT)

#     except Exception as e:
#         return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

# def login_user(request):
#     email = request.data.get('email')
#     password = request.data.get('password')

#     user = authenticate(request, email=email, password=password)

#     if user is not None:
#         #  حظر كل التوكنات السابقة (Logout from all previous sessions)
#         try:
#             tokens = OutstandingToken.objects.filter(user=user)
#             for token in tokens:
#                 _, _ = BlacklistedToken.objects.get_or_create(token=token)
#         except:
#             pass  # تجاهل الخطأ إذا لم يتم تفعيل الـ Blacklist

#         #  إنشاء توكنات جديدة
#         refresh = RefreshToken.for_user(user)
#         access = refresh.access_token

#         return Response({
#             'refresh': str(refresh),
#             'access': str(access),
#             'user': {
#                 'id': str(user.id),
#                 'email': user.email,
#                 'username': user.username,
#                 'user_type': user.user_type,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#             }
#         })

#     return Response({'detail': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)