from django.urls import path
from .views import ajax_merge_audio, download_and_delete, home

urlpatterns = [
    path('', home),
    path('merge/', ajax_merge_audio, name='merge'),
    path('download/<str:filename>/', download_and_delete, name='download_and_delete'),
]
