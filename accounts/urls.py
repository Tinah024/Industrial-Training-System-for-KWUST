from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('assign-supervisors/', views.assign_supervisors, name='assign_supervisors'),                          # ← new
    path('assign-supervisor/<int:student_id>/', views.assign_supervisor_save, name='assign_supervisor_save'), # ← new
    path('create-supervisor/', views.create_supervisor, name='create_supervisor'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('message-oversight/', views.message_oversight, name='message_oversight'),
    path('message-oversight/<int:student_id>/<int:supervisor_id>/', views.message_oversight_thread, name='message_oversight_thread'),
]