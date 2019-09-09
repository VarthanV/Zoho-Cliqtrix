from django.db import models

class Bookmark(models.Model):
    email=models.EmailField()
    url=models.URLField()
    title=models.CharField(max_length=100)
    def __str__(self):
        return self.title