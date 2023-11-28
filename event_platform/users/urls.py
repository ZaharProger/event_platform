from django.urls import path
from .views import LoginView, LogoutView

urlpatterns = [
    # path('', UsersView.as_view(), name='users'),
    path('auth/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
