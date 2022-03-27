from django.shortcuts import render
from django.views.generic import View, CreateView
from django.contrib.auth.models import User
from .forms import UserForm
from bid.models import UserProfile
from django.utils.decorators import method_decorator
from bid.decorators import should_not_be_logged_in
from django.urls import reverse
# Create your views here.

class HomePageView(View):
    template_name = 'home.html'
    def get(self, request):
        users = UserProfile.objects.all()
        users_array = []
        for user in users:
            users_array.append(user)
        users_array.sort(key=lambda x: x.amount, reverse=True)
        return render(request, self.template_name, {'users': users_array})

@method_decorator(should_not_be_logged_in,name = 'dispatch')
class RegisterUserView(CreateView):
    template_name = 'register.html'
    context_object_name = 'form'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('login')