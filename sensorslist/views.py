from .models import Sensor
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Sensor



def sensorshow(request):
    print(request)
    print(request.method == 'GET')
    sensors_list = Sensor.objects.all().order_by('-pub_date') #sort by adding date
    template = loader.get_template('sensorslist/sensors.html')
    context = {
        'sensors_list': sensors_list,
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt # error 403
def delete_data(request):
    req = dict(request.POST)
    for key in req.keys():
        req[key] = req[key][0]
    object_to_delete = Sensor.objects.filter(name=req['Name'], user=req['User'])
    object_to_delete.delete()
    return HttpResponse(status=200)




#class IndexView(generic.ListView):
#    template_name = 'sensorslist/sensors.html'
#    context_object_name = 'all_sensors'#
#
#    def get_queryset(self):
#        return Question.objects.all()