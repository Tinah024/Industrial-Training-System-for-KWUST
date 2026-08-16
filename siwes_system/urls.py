from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("accounts/", include("accounts.urls")),
    path("logbook/", include("logbook.urls")),
    path("supervisors/", include("supervisors.urls")),
    path("students/", include("students.urls")),
    path("student/messages/", include("messaging.urls")),
    path('reports/', include('reports.urls')),
]