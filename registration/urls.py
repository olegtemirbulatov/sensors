from django.urls import path
from .views import RegisterUser


app_name = 'registration'
urlpatterns = [
    path('', RegisterUser.as_view(), name='registration'),
]
