from django.urls import path
from . import views


urlpatterns=[
    path('',views.home,name='home'),
    path('room/<str:pk>/',views.room,name='room'),
    path('createroom/',views.createRoom,name='create-room'),
    path('updateroom/<int:pk>/',views.updateRoom,name='update-room'),


    path('deleteroom/<int:pk>/',views.deleteRoom,name='delete-room'),
    path('delete-message/<int:pk>/',views.delete_message,name='delete-message'),

    path("login/",views.loginPage,name="login"),
    path("logout/",views.logoutUser,name="logout"),
    path("register/",views.registerPage,name="register"),
    path('profile/<int:pk>/',views.UserProfile,name='user-profile'),
    path('export_comments/<int:pk>/',views.export_comments,name='export-comment'),

    path('accept-membership-request/<int:request_id>/', views.accept_membership_request, name='accept-membership-request'),
    path('reject-membership-request/<int:request_id>/', views.reject_membership_request, name='reject-membership-request'),
]
