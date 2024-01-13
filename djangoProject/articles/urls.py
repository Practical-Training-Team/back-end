from django.urls import path, include
from articles import views

urlpatterns = [
    path('article/',views.get_articles),
    path('likes/',views.increase_article_thumb),
    path('singlearticle/',views.get_single_article_content),
    path('articlepopularitylist/',views.article_popularity_list),
    path('pictureclassify',views.pictures_classify),
    path('search/',views.search),
    path('analysis/',views.analysis_user_audio),
    #path('media/create_sentence_audio/<int:id>/<str:file_name>.m4a', views.server_response_sentence, name='audio_file'),
]

#media/create_sentence_audio/<int:id>/<str:file_name>.m4a