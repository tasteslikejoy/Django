from django.db import models
from django.contrib.auth.models import User



class BrandAD(models.Model):
    name_brand_ad = models.CharField(max_length=50)
    email_brand_ad = models.EmailField()

    # user_brand_ad = models.OneToOneField(User, on_delete=models.CASCADE) # Дописать свой класс USER_MODIFICATE

class PostAD(models.Model):
    title_ad = models.CharField(max_length=50)
    text_ad = models.TextField(max_length=150)
    site_brand_ad = models.URLField()
    # image_ad = models.ImageField()

    post_ad_one_to_one = models.OneToOneField(BrandAD, on_delete=models.CASCADE)






