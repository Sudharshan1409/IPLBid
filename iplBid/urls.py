"""iplBid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from bid import views

from .forms import LoginForm
from .views import ChangePasswordView, HomePageView, RegisterUserView, ResetPasswordView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bid/", include("bid.urls", namespace="bid")),
    path("", HomePageView.as_view(), name="home"),
    path("signup/", RegisterUserView.as_view(), name="signup"),
    path("password/reset/", ResetPasswordView.as_view(), name="password_reset"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
    path(
        "login/",
        LoginView.as_view(template_name="login.html", authentication_form=LoginForm),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(next_page="/"),
        name="logout",
        kwargs={"next_page": "/"},
    ),
    path("dream11/add_match/", views.AddMatchView.as_view(), name="add_match"),
    path("dream11/scores/", views.ScoresView.as_view(), name="scores"),
    path("dream11/add_player/", views.AddPlayerView.as_view(), name="add_player"),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
