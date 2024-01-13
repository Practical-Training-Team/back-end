from django.urls import path, include

from signupsignin import views

urlpatterns = [
    path('signin/', views.signin, name='signin', ),
    path('signup/',views.signup, name='signup'),
]