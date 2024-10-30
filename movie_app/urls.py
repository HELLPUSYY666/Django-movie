from django.urls import path, include
from . import views
from views import MovieListView

urlpatterns = [
    path('', views.main_page, name='main'),
    path('all/', views.MovieListView.as_view(), name='movie-list'),
    path('parse_movies/', views.parse_movies, name='parse_movies'),
    path('done_review/', views.done_review, name='done_review'),
    path('director/', views.DirectorListView.as_view(), name='director'),
    path('director/<int:pk>/', views.DirectorDetailView.as_view(), name='director-detail'),
    path('actor/', views.ActorListView.as_view(), name='actor'),
    path('actor/<int:pk>/', views.ActorDetailView.as_view(), name='actor-detail'),
    path('movie/<int:pk>/', views.show_one_movie, name='movie-detail'),
    path('__debug__/', include('debug_toolbar.urls')),
]
