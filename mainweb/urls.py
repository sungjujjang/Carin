from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("sw.js", views.swjs),
    path('mypage/', views.mypage_view, name='mypage'),
]