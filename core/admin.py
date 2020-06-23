from django.contrib import admin
from core.models import JobListing,Job,Location,Extension

# Register your models here.
admin.site.register(JobListing)
admin.site.register(Job)
admin.site.register(Location)
admin.site.register(Extension)