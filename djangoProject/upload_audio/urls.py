from django.urls import path
from .views import AudioFileUploadView

urlpatterns = [
    path('upload/audio/', AudioFileUploadView.as_view(), name='audio_upload'),
]
