from django.contrib import admin
from django.urls import include, path
from . import views



app_name = "user"

urlpatterns = [
	path('register/', views.register, name="register"),
	path('registered/', views.registered, name="registered"),
	path('home/', views.home, name="home"),
	path('', views.login_request, name="login"),
	path('logout/', views.logout_request, name="logout"),
]
