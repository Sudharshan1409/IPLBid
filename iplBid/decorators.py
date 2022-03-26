from django.shortcuts import HttpResponseRedirect,redirect

def should_not_be_logged_in(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return func(request, *args, **kwargs)
    return wrapper_func
