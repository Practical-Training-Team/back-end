from django.urls import path, include

from userfunction import views

urlpatterns = [
    path('history/', views.return_history_checkin_record),
    path('checkin/',views.checkin),
    path('activity_ranking/',views.activity_ranking),
    # path('insertdata',views.write_Data),
    path('rake_user_info/',views.rake_user_info),
    path('update_user_info/',views.update_user_info),
    path('honor_rank/',views.honor_rank),
    path("return_user_info_personal/",views.return_user_info_personal),
    path("picture_personal/",views.picture_personal),
]