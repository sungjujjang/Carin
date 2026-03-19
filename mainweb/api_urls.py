from django.urls import path

from . import views

urlpatterns = [
    path('create_room/', views.create_room_view, name='create_room'),
    path('create_room', views.create_room_view, name='create_room'),
    path('search_room/', views.get_room_view, name='search_room'),
    path('search_room', views.get_room_view, name='search_room'),
    path('part_room/', views.participant_room_view, name='participant_room_view'),
    path('part_room', views.participant_room_view, name='participant_room_view'),
    path('my_room/', views.get_myroom_view, name='get_myroom_view'),
    path('my_room', views.get_myroom_view, name='get_myroom_view'),
    path('leave_room/', views.leave_room_view, name='leave_room_view'),
    path('leave_room', views.leave_room_view, name='leave_room_view'),
    path('webpush/save_information', views.save_webpush),
]