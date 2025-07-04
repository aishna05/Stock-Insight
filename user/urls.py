from django.urls import path
from .views import home
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView
from .views import RegisterView
from .views import register_view, login_view, dashboard_view

urlpatterns = [
    # path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path("api/v1/register/", RegisterView.as_view()),
    path("api/v1/token/", TokenObtainPairView.as_view()),
    path("api/v1/token/refresh/", TokenRefreshView.as_view()),  # Uncomment if you want to use token refresh
]
