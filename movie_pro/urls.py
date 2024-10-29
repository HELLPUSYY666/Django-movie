from django.contrib import admin
from django.urls import path, include
from movie_app import views
from movie_app.views import MovieListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page),
    path('done_review/', views.done_review, name='done_review'),
    path('all', MovieListView.as_view(), name='movie-list'),
    path('director/', views.DirectorListView.as_view(), name='show-directors'),
    path('director/<int:director_id>/', views.DirectorDetailView.as_view(), name='director-detail'),
    path('actor/', views.ActorListView.as_view(), name='actor'),
    path('actor/<int:actor_id>/', views.ActorDetailView.as_view(), name='actor-detail'),
    path('movie/<slug:slug_movie>/', views.show_one_movie, name='movie-detail'),
    path('__debug__/', include('debug_toolbar.urls')),
]
