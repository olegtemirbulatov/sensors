from .models import Sensor
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Sensor
from .devices import *



@login_required(login_url='/login')
def sensorshow(request):
    print(request)
    print(request.method == 'GET')
    sensors_list = Sensor.objects.all().order_by('-pub_date') #sort by adding date
    template = loader.get_template('sensorslist/sensors.html')
    context = {
        'sensors_list': sensors_list,
        'username': request.user.username,
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt # to avoid error 403
def delete_data(request):
    req = dict(request.POST)
    for key in req.keys():
        req[key] = req[key][0]
    object_to_delete = Sensor.objects.filter(user=req['User'], name=req['Name'])
    object_to_delete.delete()
    return HttpResponse(status=200)


@csrf_exempt # to avoid error 403
def save_data(request):
    req = dict(request.POST)
    for key in req.keys():
        req[key] = req[key][0]
    object_to_save = Sensor(user=req['User'], name=req['Name'], pub_date=timezone.now())
    object_to_save.save()
    return HttpResponse(status=200)


@csrf_exempt # to avoid error 403
def load_data(request):
    req = dict(request.POST)
    for key in req.keys():
        req[key] = req[key][0]
    create_device(str(req['Name']))
    write_measurements(str(req['Name']))
    return HttpResponse(status=200)


@csrf_exempt # to avoid error 403
def plot_data(request):
    req = dict(request.POST)
    for key in req.keys():
        req[key] = req[key][0]
    
    # запрос в бд
    sensor_name = req['Name']
    device_filter = f'r.device == "{sensor_name}"'
    query = f'from(bucket: "{config.get("APP", "INFLUX_BUCKET")}") ' \
            f'|> range(start: 0, stop: now()) ' \
            f'|> filter(fn: (r) => {device_filter} and r._field == "Temperature")' \
            '|> sort(columns: ["_time"]) '
    data = get_measurements(query)
    
    # формирование списков значений с данными и временем
    time_index = data[3].index('_time')
    meas_index = data[3].index('_value')
    time = list()
    meas = list()
    for i in range(len(data[4:-1])):
        time.append(data[4+i][time_index])
        meas.append(data[4+i][meas_index])
    
    return JsonResponse(data={
        'time': time,
        'meas': meas,
    })




#class IndexView(generic.ListView):
#    template_name = 'sensorslist/sensors.html'
#    context_object_name = 'all_sensors'#
#
#    def get_queryset(self):
#        return Question.objects.all()