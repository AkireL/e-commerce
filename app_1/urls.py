from django.urls import path
from app_1.views import my_view

urlpatterns = [
     path('', my_view)
]