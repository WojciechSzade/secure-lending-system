from django.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractUser
import random
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from encrypted_model_fields.fields import EncryptedCharField
from django.utils.translation import gettext_lazy as _


def create_new_unique_number_for_user(length, name):
    for i in range(0, 100):
        unique_number = random.randint(10**(length-1), 10**length-1)
        filter_kwargs = {name: unique_number}
        if not User.objects.filter(**filter_kwargs).exists():
            break
    else:
        raise Exception(f"Can't create a unique {name} for User")
    return str(unique_number)


def create_new_unique_number_for_secret_info(length, name):
    for i in range(0, 100):
        unique_number = random.randint(10**(length-1), 10**length-1)
        filter_kwargs = {name: unique_number}
        if not SecretInfo.objects.filter(**filter_kwargs).exists():
            break
    else:
        raise Exception(f"Can't create a unique {name} for SecretInfo")
    return str(unique_number)


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    balance = models.IntegerField(default=100)
    account_number = models.CharField(
        unique=True, max_length=4, default=lambda: create_new_unique_number_for_user(4, "account_number"))

    def generate_secret_info(self):
        SecretInfo.objects.create(user=self)


class SecretInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = EncryptedCharField(
        unique=True, max_length=16, default=lambda: create_new_unique_number_for_secret_info(16, "card_number"))
    personal_id = EncryptedCharField(
        unique=True, max_length=9, default=lambda: create_new_unique_number_for_secret_info(9, "personal_id"))


class Transfer(models.Model):
    def DoesUserExistValidator(value):
        if not User.objects.filter(account_number=value).exists():
            raise ValidationError(
                f"User with account number {value} does not exist")

    userFrom = models.ForeignKey(
        User, to_field="account_number", on_delete=models.DO_NOTHING, related_name='userFrom')
    userTo = models.ForeignKey(
        User, to_field="account_number", on_delete=models.DO_NOTHING, related_name='userTo', validators=[DoesUserExistValidator])
    userToName = models.CharField(max_length=100)
    amount = models.IntegerField(validators=[MinValueValidator(1)])
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    validated = models.BooleanField(default=False)
    valid = models.BooleanField(default=None, null=True)
    executed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}: {self.amount} PLN (from {self.userFrom} to {self.userTo})"

    def validate(self):
        if self.userFrom.balance < self.amount:
            self.validated = False
            self.valid = False
            self.save()
            return False
        self.validated = True
        self.valid = True
        self.save()
        return True

    def execute(self):
        if not self.validate():
            return False
        try:
            with transaction.atomic():
                self.userFrom.balance -= self.amount
                print(self.userFrom.balance)
                self.userFrom.save()
                self.userTo.refresh_from_db()
                self.userTo.balance += self.amount
                print(self.userTo.balance)
                self.userTo.save()
                self.executed = True
                self.save()
        except Exception as e:
            return False
        return True
