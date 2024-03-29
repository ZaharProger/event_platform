from django.urls import path
from .views import DocsView, TemplatesView

urlpatterns = [
    path('', DocsView.as_view(), name='docs'),
    path('templates', TemplatesView.as_view(), name='templates')
]