from django.urls import path
from . import views


app_name = 'login'
urlpatterns = [
    path('', views.login_request, name='login'),
    path('logout', views.logout_request, name='logout')
]
