from django.db import models

class employe(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.email