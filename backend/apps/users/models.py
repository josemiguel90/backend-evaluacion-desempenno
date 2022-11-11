from enum import unique

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
    PermissionsMixin

from apps.evaluation_in_area.models import EvaluationArea
from apps.workers.models import Worker


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        """ Create and saves a new User """
        if not username:
            raise ValueError("User mas have a username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user 
    
    def create_superuser(self, username, password):
        """ Create a new Super User """
        user = self.create_user(username, password)
        user.is_staff = True 
        user.is_superuser = True 
        user.save(using=self._db)
        return user 
    

class User(AbstractBaseUser, PermissionsMixin):

    """ Custom user models that supports using email instead of username """
    username = models.CharField(max_length=255,  unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    worker = models.OneToOneField(to=Worker, on_delete=models.RESTRICT, null=True)

    # ROLS
    is_staff = models.BooleanField(default=False)
    area = models.OneToOneField(to=EvaluationArea, on_delete=models.SET_NULL, null=True, related_name='users')
    
    objects = UserManager()
    USERNAME_FIELD = 'username'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
