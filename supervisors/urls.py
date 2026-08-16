from django.urls import path
from . import views

urlpatterns = [
    path('review/', views.review_logbook_list, name='review_logbook_list'),
    path('review/<int:entry_id>/', views.review_logbook_entry, name='review_logbook_entry'),

    path('dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:student_user_id>/', views.message_thread, name='message_thread'),
    path('profile/edit/', views.supervisor_profile_edit, name='supervisor_profile_edit'),
]