import os

import jwt
from bid.decorators import should_not_be_logged_in
from bid.models import UserProfile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, View

from .forms import UserForm

# Create your views here.


@method_decorator(should_not_be_logged_in, name='dispatch')
class ResetPasswordView(View):

    def get(self, request):
        print(request.GET.get('token'))
        if request.GET.get('token'):
            token = request.GET.get('token')
            try:
                decoded = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=['HS256'])
                print(decoded)
                return render(request, 'change_password.html', decoded)
            except:
                messages.warning(request, 'Invalid token')
                return redirect(reverse('password_reset'))
        return render(request, 'reset_password.html')

    def post(self, request):
        if request.POST.get('password1'):
            print('change password')
            print(request.POST)
            if request.POST.get('password1') == request.POST.get('password2'):
                user = User.objects.get(id=request.POST.get('userId'))
                user.set_password(request.POST.get('password1'))
                user.save()
                messages.success(request, 'Password Reset successfully')
                return redirect(reverse('login'))
            else:
                messages.warning(request, 'Password do not match')
                return redirect(reverse('password_reset'))
        else:
            print('send email')
            print(request.POST.get('email'))
            user = User.objects.filter(email=request.POST.get('email'))
            if not user:
                messages.warning(request, 'User with Email not found')
                return redirect(reverse('password_reset'))
            token = jwt.encode({"email": request.POST.get(
                'email'), "username": user[0].username, "userId": user[0].id}, settings.SECRET_KEY, algorithm="HS256")
            if user:
                send_mail(
                    'Password Reset',
                    f'''
                    Hi {user[0].first_name},
                    Your Username is: {user[0].username}
                    Reset password by clicking here: {request.build_absolute_uri()}?token={token}
                    ''',
                    settings.EMAIL_HOST_USER,
                    [user[0].email],
                    fail_silently=False,
                )
                messages.success(
                    request, 'Password reset link sent to your email')
                return redirect(reverse('login'))
            else:
                messages.warning(request, 'Email not found')
                return redirect(reverse('password_reset'))


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'change_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        print(request.POST)
        if request.POST.get('password1') == request.POST.get('password2'):
            user = User.objects.get(id=request.user.id)
            user.set_password(request.POST.get('password1'))
            user.save()
            messages.success(request, 'Password changed successfully')
            user = authenticate(
                request, username=request.user.username, password=request.POST.get('password1'))
            login(request, user)
            return redirect(reverse('home'))
        else:
            messages.warning(request, 'Password do not match')
            return redirect(reverse('password_change'))


class HomePageView(View):
    template_name = 'home.html'

    def get(self, request):
        if request.user.is_authenticated:
            current_year = str(request.user.active_year.year)
        else:
            current_year = os.environ.get('CURRENT_YEAR')
        users = UserProfile.objects.filter(
            year=int(current_year))
        users_array = []
        for user in users:
            users_array.append(user)
        users_array.sort(key=lambda x: x.amount, reverse=True)
        return render(request, self.template_name, {'users': users_array})


@method_decorator(should_not_be_logged_in, name='dispatch')
class RegisterUserView(CreateView):
    template_name = 'register.html'
    context_object_name = 'form'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('login')
