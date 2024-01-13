from django.db import models

class AudioFile(models.Model):
    description = models.CharField(max_length=10000)
    audio_file = models.FileField(upload_to='audio_files/')
