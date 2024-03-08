from django.db import models

class Member(models.Model):
    pass
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    # phone, department (Choices or Foreign Key), roll num
    # 
