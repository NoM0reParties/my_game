from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from dj_app import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('quiz/', include('quiz.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
