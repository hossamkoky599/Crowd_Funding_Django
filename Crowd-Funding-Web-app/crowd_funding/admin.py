# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, EmailActivation, PasswordReset

# class CustomUserAdmin(UserAdmin):
#     list_display = ['email', 'first_name', 'last_name', 'mobile_phone', 'is_active', 'date_joined']
#     list_filter = ['is_active', 'is_staff', 'date_joined']
#     search_fields = ['email', 'first_name', 'last_name']
#     ordering = ['-date_joined']
    
#     fieldsets = UserAdmin.fieldsets + (
#         ('Additional Info', {'fields': ('mobile_phone', 'profile_picture')}),
#     )

# admin.site.register(User, CustomUserAdmin)
# admin.site.register(EmailActivation)
# admin.site.register(PasswordReset)

from django.contrib import admin
from .models import User, EmailActivation, PasswordReset, Category, Tag, Projects, ProjectImages, Donation, Comment, Report, Rating,ExtraInfo

# Register User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile_phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('email', 'first_name', 'last_name')

# Register EmailActivation model
@admin.register(EmailActivation)
class EmailActivationAdmin(admin.ModelAdmin):
    list_display = ('user', 'activation_key', 'created_at')
    search_fields = ('user__email',)

# Register PasswordReset model
@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'reset_key', 'created_at', 'used')
    search_fields = ('user__email',)

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Register Tag model
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register Projects model
@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('title', 'uid', 'category', 'totalTarget', 'startTime', 'endTime')
    list_filter = ('category', 'startTime', 'endTime')
    search_fields = ('title', 'details')
    filter_horizontal = ('tags',)  # Makes tags easier to select

# Register ProjectImages model
@admin.register(ProjectImages)
class ProjectImagesAdmin(admin.ModelAdmin):
    list_display = ('project', 'image')
    search_fields = ('project__title',)

# Register Donation model
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'project__title')

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'content', 'created_at', 'parent')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'project__title', 'content')

# Register Report model
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'comment', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'project__title', 'reason')

# Register Rating model
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__email', 'project__title')



@admin.register(ExtraInfo)
class ExtraInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'birth_date')
    search_fields = ('user__email', 'address')
