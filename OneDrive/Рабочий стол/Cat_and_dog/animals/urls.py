from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.AnimalListView.as_view(), name='animal_list'),
    path('animal/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    path('animal/<int:animal_id>/adopt/', views.submit_adoption_application, name='submit_adoption'),
    path('shelter-stats/', views.shelter_statistics, name='shelter_stats'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('recommendations/', views.personal_recommendations, name='personal_recommendations'),
    path('my-applications/', views.my_applications, name='my_applications'),
]