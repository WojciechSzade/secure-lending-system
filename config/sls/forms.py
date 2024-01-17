from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginUserForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)


class TransferForm(ModelForm):
	class Meta:
		model = Transfer
		fields = ['userTo', 'userToName', 'amount', 'title']
          
	userTo = forms.CharField(required=True, label="Receiver's account number", widget=forms.NumberInput(attrs={'placeholder': 'Receiver\'s account number'}))
	userToName = forms.CharField(required=True, label="Receiver's name", widget=forms.TextInput(attrs={'placeholder': 'Receiver\'s name'}))
	amount = forms.IntegerField(required=True, label="Amount", widget=forms.NumberInput(attrs={'placeholder': 'Amount'}))
	title = forms.CharField(required=True, label="Transfer title", widget=forms.TextInput(attrs={'placeholder': 'Transfer title'}))
	
	def clean_userTo(self):
		userTo_account_number = self.cleaned_data.get('userTo')
		if not User.objects.filter(account_number=userTo_account_number).exists():
			raise forms.ValidationError(f"Account number {userTo_account_number} is invalid - it does not exist.")
		userTo = User.objects.filter(account_number=userTo_account_number).first()
        
		return userTo