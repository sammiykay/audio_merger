from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ajax_merge_audio, download_and_delete, get_progress, home

urlpatterns = [
    path('', home, name=''),
    path('merge/', ajax_merge_audio, name='merge'),
    path('download/<str:filename>/', download_and_delete, name='download_and_delete'),
    path('progress/', get_progress, name='get_progress'),
]