from django.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractUser
import random
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from encrypted_model_fields.fields import EncryptedCharField



class User(AbstractUser):    
    def create_new_account_number():
        for i in range(0, 100):                   
            unique_account_number = random.randint(1000, 9999)
            if not User.objects.filter(account_number=unique_account_number).exists():
                break
        else:
            raise Exception("Can't create a unique referrence number")
        return str(unique_account_number)
    
    def create_new_card_number():
        return random.randint(1000000000000000, 9999999999999999)
    
    def create_new_personal_id():
        return random.randint(100000000, 999999999)
        
    balance = models.IntegerField(default=100)
    account_number = models.CharField(default=create_new_account_number, unique=True, max_length=4)
    card_number = EncryptedCharField(max_length=16, default=create_new_account_number)
    personal_id = EncryptedCharField(max_length=9, default=create_new_personal_id)


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
