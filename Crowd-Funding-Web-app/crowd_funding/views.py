from rest_framework.authtoken.models import Token
from rest_framework.decorators import action ,api_view
from rest_framework import generics, status, views, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render ,get_object_or_404
from django.conf import settings
from django.contrib.auth import login
from .models import User, EmailActivation, PasswordReset, Projects, Comment, Rating, Report, Donation
from .serializers import *
from django.db.models import Sum
from django.db.models import Avg, Value, FloatField
from django.utils.timezone import now
from django.db.models.functions import Coalesce

from rest_framework import filters

import uuid
from django.db.models import Sum

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
# class UserLoginView(views.APIView):
#     permission_classes = [AllowAny]               ###### Try as Unautheticated
#     def post(self, request):
#         serializer = UserLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             "message": "Login successful.",
#             "token": token.key,
#             "user": UserProfileSerializer(user).data
#         })


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful.",
            "token": token.key,
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
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
    
###Projects viewsets\
class ProjectView(viewsets.ModelViewSet):
    queryset=Projects.objects.prefetch_related("tags","images").all()
    serializer_class=ProjectSerializer
    permission_classes = [IsAuthenticated]
    ##Pass the data to the serialziers
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    ## list the projects in the templates
    # def list(self,request,args,*kwargs):
    #     projects = self.get_queryset()
    #     return render(request, 'projects.html', {'projects': projects})
    def perform_create(self, serializer):
        ##log errors
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
        serializer.save(uid=self.request.user)

    ### add image for custom project view url "add-image" 
    @action(detail=True,methods=['POST'],url_path='add-image') 
    def add_image(self,request,pk=None):
        project=self.get_object()
        serializer=ProjectImagesSerializer( data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    ##Custom Update Method
    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        ## if there is new tags in the updated data add them to itis project
        if 'tags' in request.data:
            project.tags.set(request.data['tags'])
##Logout
class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
    
    ###################################3
# Project Details 


class CheckAuthView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'is_authenticated': True, 'email': request.user.email})
        return Response({'is_authenticated': False})

class ProjectDetailView(generics.RetrieveAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SimilarProjectsView(APIView):
    def get(self, request, pk):
        try:
            project = Projects.objects.get(pk=pk)
            tags = project.tags.all()
            similar_projects = Projects.objects.filter(tags__in=tags).exclude(pk=pk).distinct()[:4]
            serializer = ProjectSerializer(similar_projects, many=True, context={'request': request})
            return Response(serializer.data)
        except Projects.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent')
        parent_comment = Comment.objects.filter(pk=parent_id).first() if parent_id else None

        if parent_comment:
            # Reply: use the project from the parent
            project = parent_comment.project
        else:
            # Normal comment: get project from data
            project_id = self.request.data.get('project')
            if not project_id:
                raise serializers.ValidationError("Project ID is required for top-level comments.")
            project = Projects.objects.get(pk=project_id)

        serializer.save(
            user=self.request.user,
            project=project,
            parent=parent_comment
        )
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer


    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        if project_id:
            return Comment.objects.filter(project_id=project_id, parent=None).order_by('-created_at')
        return Comment.objects.none()     
    
class RatingCreateView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs['pk'] 
        value = request.data.get('value')

        if not (1 <= int(value) <= 5):
            return Response({"error": "Invalid rating value. Must be 1 to 5."}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Projects, pk=project_id)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            project=project,
            defaults={'score': value}
        )

        return Response({"message": "Rating submitted successfully."}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project_id = self.request.data.get('project_id')
        comment_id = self.request.data.get('comment_id')
        serializer.save(
            user=self.request.user,
            project=Projects.objects.get(pk=project_id) if project_id else None,
            comment=Comment.objects.get(pk=comment_id) if comment_id else None
        )

class DonationCreateView(generics.CreateAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = Projects.objects.get(pk=project_id)
        

        serializer.save(user=self.request.user, project=project)
        
        
        total_donations = project.donations.aggregate(Sum('amount'))['amount__sum'] or 0
        
        project.totalDonations = total_donations
        project.save()




class CancelProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            project = Projects.objects.get(pk=pk, uid=request.user)
            if project.can_cancel():
                project.delete()  # بنحذف المشروع عشان is_active مش موجود
                return Response({"message": "Project cancelled successfully"})
            return Response({"error": "Cannot cancel project"}, status=status.HTTP_400_BAD_REQUEST)
        except Projects.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
def project_detail_template(request, pk):
    project = get_object_or_404(Projects, pk=pk)
    tags = project.tags.all()
    similar_projects = Projects.objects.filter(tags__in=tags).exclude(pk=pk).distinct()[:4]
    return render(request, 'projects.html', {
        'project': project,
        'similar_projects': similar_projects
    })

# Extra user info view
class ExtraInfoMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        extra_info, created = ExtraInfo.objects.get_or_create(user=request.user)
        serializer = ExtraInfoSerializer(extra_info)
        return Response(serializer.data)

    def put(self, request):
        extra_info, created = ExtraInfo.objects.get_or_create(user=request.user)
        serializer = ExtraInfoSerializer(extra_info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Delete user account
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(password):
            return Response({'error': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)

# Update user profile
class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateUserProfileSerializer(
            request.user, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


@api_view(['GET'])
def home_projects(request):
    current_time = now()
    base_qs = Projects.objects.filter(is_canceled=False)

    latest_projects = base_qs.order_by('-created_at') \
        .annotate(avg_rating=Coalesce(Avg('ratings__score'), Value(0, output_field=FloatField())))[:5]

    featured_projects = base_qs.filter(is_featured=True).order_by('-created_at') \
        .annotate(avg_rating=Coalesce(Avg('ratings__score'), Value(0, output_field=FloatField())))[:5]

    top_rated_projects = base_qs.annotate(
    avg_rating=Coalesce(Avg('ratings__score'), Value(0, output_field=FloatField()))
    ).order_by('-avg_rating')[:5]
   

    return Response({
        "latest_projects": ProjectSerializer(latest_projects, many=True, context={'request': request}).data,
        "featured_projects": ProjectSerializer(featured_projects, many=True, context={'request': request}).data,
        "top_rated_projects": ProjectSerializer(top_rated_projects, many=True, context={'request': request}).data,
    })





# search by using tags and id
class ProjectSearchView(generics.ListAPIView):
    queryset = Projects.objects.prefetch_related("tags", "images").all()
    serializer_class = ProjectSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'tags__name']

    def get_serializer_context(self):
        return {'request': self.request}
