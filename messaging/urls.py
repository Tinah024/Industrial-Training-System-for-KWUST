from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('notifications/', views.notifications, name='notifications'),
]