from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('merge/', views.ajax_merge_audio, name='ajax_merge_audio'),
    path('', views.home, name=''),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
