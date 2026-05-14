from django.db import models
from django.contrib.auth.models import User  # ✔ هذا هو الحل

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField(default=0)

    image = models.ImageField(upload_to='services/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
