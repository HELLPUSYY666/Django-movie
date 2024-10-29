from django.urls import path
from . import views
from views import MovieListView, DirectorListView, ActorListView, ActorDetailView

urlpatterns = [
    path('', views.main_page, name='main'),
    path('all', MovieListView.as_view(), name='movie-list'),
    path('done_review/', views.done_review, name='done_review'),
    path('director/', views.DirectorListView.as_view(), name='director'),
    path('director/<int:pk>/', views.DirectorDetailView.as_view(), name='director-detail'),
    path('actor/', views.ActorListView.as_view(), name='actor'),
    path('actor/<int:pk>/', views.ActorDetailView.as_view(), name='actor-detail'),
    path('movie/<slug:slug_movie>/', views.show_one_movie, name='movie-detail'),
]
