from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    CustomTokenObtainPairSerializer, 
    RegisterCustomerSerializer, 
    RegisterOrganizerSerializer,
    UserSerializer,
    OrganizerProfileSerializer
)
from .services import UserService, OrganizerService
from apps.common.utils import success_response, error_response
from apps.common.exceptions import ApplicationError
from .models import OrganizerProfile, Role

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterCustomerView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=RegisterCustomerSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = UserService.create_user(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    first_name=serializer.validated_data.get('first_name', ''),
                    last_name=serializer.validated_data.get('last_name', ''),
                    phone=serializer.validated_data.get('phone', '')
                )
                user_data = UserSerializer(user).data
                return success_response(
                    data=user_data, 
                    message="Customer registered successfully.", 
                    status_code=status.HTTP_201_CREATED
                )
            except ApplicationError as e:
                return error_response(str(e))
        return error_response("Validation Error", errors=serializer.errors)


class RegisterOrganizerView(APIView):
    permission_classes = (AllowAny,)
    
    @extend_schema(
        request=RegisterOrganizerSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request):
        serializer = RegisterOrganizerSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user, profile = OrganizerService.create_organizer(
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password'],
                    organization_name=serializer.validated_data['organization_name'],
                    first_name=serializer.validated_data.get('first_name', ''),
                    last_name=serializer.validated_data.get('last_name', ''),
                    phone=serializer.validated_data.get('phone', '')
                )
                
                # We could send a verification email via celery task here
                
                user_data = UserSerializer(user).data
                profile_data = OrganizerProfileSerializer(profile).data
                
                return success_response(
                    data={'user': user_data, 'profile': profile_data}, 
                    message="Organizer registered successfully.", 
                    status_code=status.HTTP_201_CREATED
                )
            except ApplicationError as e:
                return error_response(str(e))
        return error_response("Validation Error", errors=serializer.errors)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={205: OpenApiResponse(description='Logout successful.')}
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return error_response("Refresh token is required.")
                
            token = RefreshToken(refresh_token)
            token.blacklist()

            return success_response(message="Logout successful.", status_code=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return error_response("Invalid token or token already blacklisted.")


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        responses={200: UserSerializer}
    )
    def get(self, request):
        user = request.user
        data = {'user': UserSerializer(user).data}
        
        if user.role == Role.ORGANIZER:
            try:
                data['organizer_profile'] = OrganizerProfileSerializer(user.organizer_profile).data
            except OrganizerProfile.DoesNotExist:
                pass
                
        return success_response(data=data)
        
    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, message="Profile updated successfully.")
            
        return error_response("Validation Error", errors=serializer.errors)
