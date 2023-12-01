from django.urls import path
from .views import EventsView, JoinEventView

urlpatterns = [
    path('', EventsView.as_view(), name='events'),
    path('join', JoinEventView.as_view(), name='join-event')
]