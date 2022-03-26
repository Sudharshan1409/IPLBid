from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import User
from .forms import UserForm
from django.utils.decorators import method_decorator
from .decorators import should_not_be_logged_in
from django.urls import reverse
# Create your views here.

class HomePageView(TemplateView):
    template_name = 'home.html'

@method_decorator(should_not_be_logged_in,name = 'dispatch')
class RegisterUserView(CreateView):
    template_name = 'register.html'
    context_object_name = 'form'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('login')