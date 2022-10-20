from django.shortcuts import render
from .forms import RegisterUserForm
from django.views.generic.edit import CreateView



class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'registration/register.html'
    #successful_url = render('polls/index.html')
    #registration -> homepage

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        #c_def = self.get_user_context(title='Регистрация')
        return dict(list(context.items()))# + list(c_def.items()))
