from .forms import RegisterUserForm
from django.views.generic.edit import CreateView



class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'registration/register.html'
