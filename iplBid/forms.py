from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import get_object_or_404
from bid.models import UserProfile

class UserForm(UserCreationForm):
    class Meta():
        fields = ('first_name','last_name','username','email','password1','password2')
        username = forms.RegexField(label=("Username"), max_length=30, regex=r'^[\w.@+-]+$',
        help_text = ("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': ("This value may contain only letters, numbers and @/./+/-/_ characters.")})
        model = User

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email Address'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
    
    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with the following email already exists")
        return self.cleaned_data


class LoginForm(AuthenticationForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].label = 'Username or Email'
        self.fields['password'].label = 'Password'
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        print(username)
        print(password)
        if '@' in username:
            try:
                user = get_object_or_404(User, email=username)
                print(user)
            except:
                raise forms.ValidationError('Incorrect Email')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect Password')
            else:
                self.cleaned_data['username'] = user.username
        else:
            try:
                user = get_object_or_404(User, username=username)
                print(user)
            except:
                raise forms.ValidationError('Incorrect Username')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect Password')
        return super().clean()
