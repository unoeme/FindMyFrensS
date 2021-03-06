from django.db import models
import bcrypt
import re

class UserManager(models.Manager):
    def reg(self, data):
        errors = {}
        if len(data['email']) < 1:
            errors["email"] = "Please enter an email!"
        elif not re.match(r'[A-Za-z-0-9-_]+(.[A-Za-z-0-9-_]+)*@[A-Za-z-0-9-_]+(.[A-Za-z-0-9-_]+)*\.([A-Za-z]{2,})', data['email']):
            errors["email"] = "Please enter a valid email!"
        elif User.objects.filter(email=data['email']):
            errors["email"] = "Email taken!"
        if len(data['password']) < 8:
            errors["password"] = "Passwords must be at least 8 characters!"
        elif data['password'] != data['passconfirm']:
            errors["password"] = "Passwords must match!"
        if len(data['first_name']) < 2:
            errors["first_name"] = "First name must be at least 2 characters"
        elif not data['first_name'].isalpha(): 
            errors["first_name"] = "First name must be alphabetical"
        return errors
    def log(self, data):
        errors = {}
        if len(data['password']) < 1 or len(data['email']) < 1:
            errors["login"] = "Enter email and password"
        elif User.objects.filter(email=data['email']):
            if bcrypt.checkpw(data['password'].encode(), User.objects.get(email=data['email']).password.encode()):
                pass
            else:
                errors["login"] = "Could not log you in!"
        else:
            errors["login"] = "Please Register!"
        return errors
    def update(self,data, number):
        errors = {}
        if len(data['email']) < 1:
            errors["email"] = "Please enter an email!"
        elif not re.match('[A-Za-z-0-9-_]+(.[A-Za-z-0-9-_]+)*@[A-Za-z-0-9-_]+(.[A-Za-z-0-9-_]+)*(.[A-Za-z]{2,})', data['email']):
            errors["email"] = "Please enter a valid email!"
        elif User.objects.filter(email=data['email']):
            if User.objects.get(email=data['email']) == User.objects.get(id = number):
                pass
            else:
                errors["email"] = "Email taken!"
        if len(data['first_name']) < 2:
            errors["first_name"] = "First name must be at least 2 characters"
        elif not data['first_name'].isalpha(): 
            errors["first_name"] = "First name must be alphabetical"
        return errors
    def updatepassword(self,data):
        errors = {}
        if len(data['password']) < 8:
            errors["password"] = "Passwords must be at least 8 characters!"
        elif data['password'] != data['passconfirm']:
            errors["password"] = "Passwords must match!"
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    current = models.CharField(max_length=255)
    backup  = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    description = models.TextField()
    user_level = models.IntegerField()
    verified = models.IntegerField()
    image = models.ImageField(upload_to='media', default='none.jpg')
    objects = UserManager()
