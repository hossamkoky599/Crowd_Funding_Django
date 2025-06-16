# Crowd-Funding-Web-app
python3 manage.py shell


from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='admin2@example.com')
user.is_active = True
user.save()