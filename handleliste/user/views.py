from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from shopping_list import views
# Create your views here.


def register(request):

	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			login(request, user)
			return redirect("user:registered")
		else:
			for msg in form.errors:
				messages.error(request, f"{form.errors[msg]}")
				return redirect("user:register")

	form = UserCreationForm()
	return render(request, "user/register.html", context={"form": form})


def registered(request):
	return redirect('index')


def home(request):
	return render(request, "user/home.html")


def logout_request(request):
	logout(request)
	messages.success(request, "Logged out successfully!")
	return redirect('user:login')


def login_request(request):

	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect("index")
			else:
				messages.error(request, "Invalid username or password.")
		else:
			messages.error(request, "Invalid username or password.")

		render(request, "user/login.html", {"form": form})

	form = AuthenticationForm()

	return render(request, "user/login.html", {"form": form})

