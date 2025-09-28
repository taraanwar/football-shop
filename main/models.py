import uuid
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    thumbnail = models.URLField()
    CATEGORY_CHOICES = [
        ("shoes", "Shoes"),
        ("jersey", "Jersey"),
    ]
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name