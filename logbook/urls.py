from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_logbook, name='submit_logbook'),
    path('my-entries/', views.my_logbook, name='my_logbook'),
]