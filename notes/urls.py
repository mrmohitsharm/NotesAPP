from django.urls import path
from . import views

urlpatterns = [

    path('', views.notes_list, name='notes_list'),

    path('add/', views.add_note, name='add_note'),

    path(
        'update/<str:note_id>/',
        views.update_note,
        name='update_note'
    ),

    path(
        'delete/<str:note_id>/',
        views.delete_note,
        name='delete_note'
    ),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),
    path(
    'profile/',
    views.profile,
    name='profile'
),
]