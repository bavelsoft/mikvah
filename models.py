from django.db import models

class Appointment(models.Model):
    datetime = models.DateTimeField()
    contact = models.CharField(max_length=20)
    minutes_offset = models.IntegerField()
    textable = models.BooleanField()
