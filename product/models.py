from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=300)
    short_desc = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)