from django.shortcuts import render
from .forms import *
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django_otp.decorators import otp_required
from .models import *


def register(request):
    form = RegisterUserForm()
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("/account/two_factor/setup/")
    return render(request, 'sls/register.html', {'form': form})


@otp_required
def index(request):
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
    logout(request)
    return redirect('/')


@otp_required
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


@otp_required
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


@otp_required
def personal_info(request):
    context = {
        'user': request.user
    }
    return render(request, 'sls/personal_info.html', context=context)
