from rest_framework import serializers
from core.models import JobListing

class JobListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=JobListing
        fields=('title','company','location','rating_value','review_number','description')