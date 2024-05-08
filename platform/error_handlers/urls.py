from django.conf.urls import handler403, handler404
from django.urls import path
from . import views

urlpatterns = [
    path('403/', views.custom_403, name='custom_403'),
    path('404/', views.custom_404, name='custom_404'),
]
