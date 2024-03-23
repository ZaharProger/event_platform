from django.urls import path
from .views import LoginView, LogoutView, AccountDataView, UserGroupsView, UsersView

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('account/', AccountDataView.as_view(), name='account'),
    path('auth/', LoginView.as_view(), name='login'),
    path('groups/', UserGroupsView.as_view(), name='groups'),
    path('logout/', LogoutView.as_view(), name='logout')
]
