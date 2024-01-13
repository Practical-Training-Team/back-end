from django.urls import path, include

from score import views

urlpatterns = [
    path('sentence/',views.server_response_sentence),
    #path('download/', views.download_file),
    path('analysis/',views.analysis_user_audio),
    #path('media/create_sentence_audio/<int:id>/<str:file_name>.m4a', views.server_response_sentence, name='audio_file'),
    #path('insertsentence/',views.insert_sentence),
    path('picture_view/',views.picture_view),
]


#media/create_sentence_audio/<int:id>/<str:file_name>.m4a