from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class JobListing(models.Model):
    title=models.CharField(max_length=100,null=True)
    company=models.CharField(max_length=100,null=True)
    location=models.CharField(max_length=100,null=True)
    rating_value=models.FloatField(null=True,blank=True)
    search_cat=models.CharField(null=True,blank=True,max_length=100)
    search_loc=models.CharField(null=True,blank=True,max_length=100)
    review_number=models.PositiveIntegerField(null=True,blank=True)
    description=models.TextField()
    def __str__(self):
        return self.title+'('+self.company+')'



class Location(models.Model):
    name=models.CharField(null=True,blank=True,max_length=100)
    def __str__(self):
        return self.name

class Job(models.Model):
    name=models.CharField(null=True,blank=True,max_length=100)

    def __str__(self):
        return self.name

class Extension(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return self.name