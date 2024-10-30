from django.contrib import admin
from django.urls import path, include
from movie_app import views
from movie_app.views import MovieListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='main'),
    path('done_review/', views.done_review, name='done_review'),
    path('all/', views.MovieListView.as_view(), name='movie-list'),
    path('parse_movies/', views.parse_movies, name='parse_movies'),
    path('director/', views.DirectorListView.as_view(), name='show-directors'),
    path('director/<int:pk>/', views.DirectorDetailView.as_view(), name='director-detail'),
    path('actor/', views.ActorListView.as_view(), name='actor'),
    path('actor/<int:pk>/', views.ActorDetailView.as_view(), name='actor-detail'),
    path('movie/<int:pk>/', views.show_one_movie, name='movie-detail'),
    path('__debug__/', include('debug_toolbar.urls')),
]
