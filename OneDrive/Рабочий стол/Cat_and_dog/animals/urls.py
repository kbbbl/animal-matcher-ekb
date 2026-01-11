from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnimalListView.as_view(), name='animal_list'),
    path('animal/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    path('animal/<int:animal_id>/adopt/', views.submit_adoption_application, name='submit_adoption'),
    path('shelter-stats/', views.shelter_statistics, name='shelter_stats'),
]