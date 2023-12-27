from django.shortcuts import render
from .forms import RegisterUserForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django_otp.decorators import otp_required


def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("/account/two_factor/setup/")

    form = RegisterUserForm()
    return render(request, 'sls/register.html', {'form': form})

@otp_required
def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'sls/index.html', context=context)
    
def logout_view(request):
    logout(request)
    return redirect('/')