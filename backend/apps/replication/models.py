from django.db import models


class Replication(models.Model):

    time_stamp = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=80)
