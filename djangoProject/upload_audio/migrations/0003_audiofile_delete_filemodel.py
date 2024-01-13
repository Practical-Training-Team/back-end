# Generated by Django 5.0.1 on 2024-01-10 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_audio', '0002_alter_filemodel_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('audio_file', models.FileField(upload_to='audio_files/')),
            ],
        ),
        migrations.DeleteModel(
            name='FileModel',
        ),
    ]
