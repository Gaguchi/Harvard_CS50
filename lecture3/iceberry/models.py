from django.db import models

# Create your models here.

class Ice_Cream(models.Model):
    name = models.CharField(max_length=64)
    image = models.ImageField(upload_to='product_images')
    barcode = models.CharField(max_length=64)
