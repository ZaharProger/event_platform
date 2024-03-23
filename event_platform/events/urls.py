from django.urls import path
from .views import EventsView, JoinEventView, CompleteEventView, InviteEventUsersView

urlpatterns = [
    path('', EventsView.as_view(), name='events'),
    path('join', JoinEventView.as_view(), name='join-event'),
    path('complete', CompleteEventView.as_view(), name='complete-event'),
    path('invite', InviteEventUsersView.as_view(), name='invite-users')
]