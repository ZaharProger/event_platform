from django.urls import path
from .views import LoginView, LogoutView, AccountDataView

urlpatterns = [
    path('account/', AccountDataView.as_view(), name='account'),
    path('auth/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
