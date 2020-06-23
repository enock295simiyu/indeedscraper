from  django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views
from .views import login, JoblistingAPIView, populate
router=routers.DefaultRouter()
urlpatterns=[
    path('',JoblistingAPIView.as_view(),name='instances'),
    path('api_auth',include('rest_framework.urls',namespace='rest_framework')),
    path('api/login',login),
    path('api/login',views.obtain_auth_token,name='login'),
    path('api/populate',populate,name='populate'),
]