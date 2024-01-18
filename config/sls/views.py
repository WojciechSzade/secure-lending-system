from django.shortcuts import render
from .forms import *
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import redirect
from .models import *
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from two_factor.views import LoginView
from functools import wraps
from django.contrib.sites.shortcuts import get_current_site
from django.dispatch import receiver
from two_factor.signals import user_verified
from django.core.mail import send_mail


def if_not_otp_but_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/account/login/')
        if request.user.is_authenticated and not request.user.is_verified():
            return redirect("/account/two_factor/")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def register(request):
    form = RegisterUserForm()
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.generate_secret_info()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful.")
            return redirect("/account/two_factor/setup/")
    return render(request, 'sls/register.html', {'form': form})


@if_not_otp_but_authenticated
def index(request):
    if_not_otp_but_authenticated(request)
    last_from = Transfer.objects.filter(userFrom=request.user).last()
    last_to = Transfer.objects.filter(userTo=request.user).last()
    last_transaction = None
    if last_from and last_to:
        last_transaction = last_from if last_from.date > last_to.date else last_to
    elif last_from:
        last_transaction = last_from
    elif last_to:
        last_transaction = last_to

    context = {
        'user': request.user,
        'last_transaction': last_transaction,
    }
    return render(request, 'sls/index.html', context=context)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'two_factor/logged_out.html')
    else:
        return redirect('/account/login/')


@if_not_otp_but_authenticated
def change_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
    context = {
        'user': request.user,
        'form': form,
    }
    return render(request, 'sls/change_password.html', context=context)


def reset_password(request):
    form = PasswordResetForm()
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
    context = {
        'user': request.user,
        'form': form,
    }
    return render(request, 'sls/reset_password.html', context=context)
            


@if_not_otp_but_authenticated
def transfer(request):
    form = TransferForm()
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            form.instance.userFrom = request.user
            transfer = form.save()
            if transfer.execute():
                return render(request, 'sls/transfer_message.html', context={'transfer': transfer, 'message': 'Transfer successful.'})
            else:
                return render(request, 'sls/transfer_message.html', context={'transfer': transfer, 'message': 'Transfer failed.'})
    context = {
        'user': request.user,
        'form': form,
    }
    return render(request, 'sls/transfer.html', context=context)


@if_not_otp_but_authenticated
def transfer_history(request):
    transfersFrom = Transfer.objects.filter(
        userFrom=request.user, executed=True)
    transfersTo = Transfer.objects.filter(userTo=request.user, executed=True)
    transfers = transfersFrom | transfersTo
    transfers = transfers.order_by('-date')
    context = {
        'user': request.user,
        'transfers': transfers,
    }
    return render(request, 'sls/transfer_history.html', context=context)


@if_not_otp_but_authenticated
def profile(request, show_secrets=0):
    context = {
        'user': request.user
    }
    if show_secrets == 1:
        context['show_secrets'] = True
        context['secret_info'] = SecretInfo.objects.filter(
            user=request.user).first()

    return render(request, 'sls/profile.html', context=context)


@receiver(user_verified)
def test_receiver(request, user, device, **kwargs):
    current_site = get_current_site(request)
    send_mail(
        'New succesfull login to your account',
        f'Hello {user.username},\n'
        f'You have successfully logged in to your account on {current_site.domain}.\n'
        f'Autorization method: {device.name}.\n'
        f'If this was not you, please change your password and the two-factor authentication method immediately.\n'
        f'Best regards,\n'
        f'{current_site.domain} team',
        'noreply@' + current_site.domain,
        [user.email],
    )