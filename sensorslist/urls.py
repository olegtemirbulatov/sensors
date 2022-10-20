from django.urls import path
from . import views



app_name = 'sensorslist'
urlpatterns = [
    path('', views.sensorshow, name='sensorslist'),
    path('delete_data/', views.delete_data, name='delete_data')
]
