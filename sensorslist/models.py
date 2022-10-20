from django.db import models



class Sensor(models.Model):
    name = models.CharField(max_length=30)
    user = models.CharField(max_length=30)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.name