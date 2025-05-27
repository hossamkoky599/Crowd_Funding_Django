from rest_framework import generics, status, views, viewsets
from rest_framework.response import Response
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import User, EmailActivation, PasswordReset
from .serializers import *
import uuid
### Try With Unautheticated
from rest_framework.permissions import AllowAny
# Register user and send activation email
class UserRegistrationView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]               ###### Try as Unautheticated
    def perform_create(self, serializer):
        user = serializer.save()
        activation = EmailActivation.objects.create(user=user)
        activation_link = f"http://localhost:8000/api/activate/{activation.activation_key}/"
        print(f"Sending activation email to: {user.email}")
        sent =send_mail(
            subject="Activate your account",
            message=f"Click the link to activate your account: {activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        print(f"Email sent successfully: {sent}")

# Account activation
class ActivateAccountView(views.APIView):
    def get(self, request, activation_key):
        try:
            activation = EmailActivation.objects.get(activation_key=activation_key)
            if activation.is_expired():
                return Response({"error": "Activation link expired."}, status=status.HTTP_400_BAD_REQUEST)
            activation.user.is_active = True
            activation.user.save()
            activation.delete()
            return Response({"message": "Account activated successfully."})
        except EmailActivation.DoesNotExist:
            return Response({"error": "Invalid activation key."}, status=status.HTTP_400_BAD_REQUEST)

# Login
class UserLoginView(views.APIView):
    permission_classes = [AllowAny]               ###### Try as Unautheticated
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            "message": "Login successful.",
            "user": UserProfileSerializer(user).data
        })

# Request password reset
class PasswordResetRequestView(views.APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        reset = PasswordReset.objects.create(user=user)
        reset_link = f"http://localhost:8000/api/reset-password/{reset.reset_key}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return Response({"message": "Password reset email sent."})

# Confirm password reset
class PasswordResetConfirmView(views.APIView):
    def post(self, request, reset_key):
        try:
            reset = PasswordReset.objects.get(reset_key=reset_key, used=False)
            if reset.is_expired():
                return Response({"error": "Reset link expired."}, status=status.HTTP_400_BAD_REQUEST)
        except PasswordReset.DoesNotExist:
            return Response({"error": "Invalid reset key."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset.user.set_password(serializer.validated_data['new_password'])
        reset.user.save()
        reset.used = True
        reset.save()
        return Response({"message": "Password reset successful."})

# Get user profile
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
