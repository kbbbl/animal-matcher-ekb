from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnimalListView.as_view(), name='animal_list'),
    path('animal/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    path('statistics/', views.shelter_statistics, name='shelter_statistics'),
]