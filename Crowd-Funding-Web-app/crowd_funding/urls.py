from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *



from .views import ProjectSearchView

router = DefaultRouter()
router.register(r'register', UserRegistrationView, basename='register')
router.register(r'projects', ProjectView, basename='projects')

urlpatterns = [

    path('projects/search/', ProjectSearchView.as_view(), name='project-search'),

    path('Cprojects/<int:pk>/cancel/', CancelProjectView.as_view(), name='cancel-project'),
    path('projects/<int:pk>/template/', project_detail_template, name='project-detail-template'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/similar/', SimilarProjectsView.as_view(), name='similar-projects'),

    path('', include(router.urls)),
    path('activate/<uuid:activation_key>/', ActivateAccountView.as_view(), name='activate'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('reset-password/<uuid:reset_key>/', PasswordResetConfirmView.as_view(), name='reset-password'),
    path('userprofile/', UserProfileView.as_view(), name='user-profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #############################
    path('check-auth/', CheckAuthView.as_view(), name='check-auth'),
    
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/list/', CommentListView.as_view(), name='comment-list'),

    path('projects/<int:pk>/rate/', RatingCreateView.as_view(), name='project-rate'),
    path('reports/', ReportCreateView.as_view(), name='report-create'),
    path('donations/', DonationCreateView.as_view(), name='donation-create'),
   


    path('extra-info/', ExtraInfoMeView.as_view(), name='extra-info-me'), 
    path('delete-account/', DeleteUserView.as_view(), name='delete-account'),
    path('update-profile/', UpdateUserProfileView.as_view(), name='update-profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('home-projects/', home_projects, name='home-projects'),
]
  




# # hossam.hassam.0.1.0.1.2@gmail.com
#  # hossamkoky599


