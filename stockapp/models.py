from django.db import models
class Image(models.Model):
    name=models.CharField(max_length=100)
    img=models.ImageField()
    def __str__(self):
        return self.name
class Country(models.Model):
    name=models.CharField(max_length=200)
    code = models.CharField(max_length=20) 
    def __str__(self):
        return self.name
           
    