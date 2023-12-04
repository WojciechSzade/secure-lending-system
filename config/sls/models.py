from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class CharPassword(models.Model):
    char = models.CharField(('password'), max_length=128)

class Password(models.Model):
    chars = models.ManyToManyField(CharPassword)
    
    def hash_password(self, raw_password):
        chars = []
        for char in raw_password:
            hashed_char = make_password(char)
            CharPassword.objects.create(char=hashed_char)
            chars.append(char)
        self.chars.set(chars)
    
class User(AbstractUser):
    password = models.ForeignKey(Password, on_delete=models.CASCADE, null=True, blank=True)
    password_length = models.IntegerField(default=8)
    
    def set_password(self, raw_password):
        if self.password is not None:
            self.password.delete()
        password = Password.objects.create()
        password.hash_password(raw_password)
        self.password = password
        self.password_length = len(raw_password)
        self.save()
        
    def check_password_char(self, raw_char, index):
        hashed_password_char = self.password.chars.all()[index].char
        return check_password(raw_char, hashed_password_char)
    
    def check_password_chars(self, raw_chars, indexes):
        for i, index in enumerate(indexes):
            if not self.check_password_char(raw_chars[i], index):
                return False
        return True
    
    def check_password(self, raw_password):
        if len(raw_password) != self.password_length:
            return False
        return self.check_password_chars(raw_password, range(self.password_length))
        