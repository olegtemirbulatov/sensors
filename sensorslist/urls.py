from django.urls import path
from . import views



app_name = 'sensorslist'
urlpatterns = [
    path('', views.sensorshow, name='sensorslist'),
    path('delete_data/', views.delete_data, name='delete_data'),
    path('save_data/', views.save_data, name='save_data'),
    path('load_data/', views.load_data, name='load_data'),
    path('plot_data/', views.plot_data, name='plot_data'),
]
# <!--<div id="container" style="width: 75%;">-->
#         //    <!--<canvas id="population-chart" data-url="{% url 'core:population-chart' %}"></canvas>-->
#         //<!--</div>-->
