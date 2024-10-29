from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from .forms import MovieForm
from .models import Movie, Director, Actor
from django.db.models import F, Value
from .models import Feedback
from django.views.generic import ListView, DetailView


def show_one_movie(request, slug_movie: str):
    movie = get_object_or_404(Movie, slug=slug_movie)

    form = MovieForm()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            feed = Feedback(
                review=form.cleaned_data['review'],
            )
            feed.save()
            return HttpResponseRedirect('/done_review')

    return render(request, 'movie_app/one_movie.html', {
        'movie': movie,
        'form': form
    })


class MovieListView(ListView):
    model = Movie
    template_name = 'movie_app/all_movie.html'
    context_object_name = 'movies'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class DirectorListView(ListView):
    model = Director
    template_name = 'movie_app/all_director.html'
    context_object_name = 'directors'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class DirectorDetailView(DetailView):
    model = Director
    template_name = 'movie_app/one_director.html'


class ActorListView(ListView):
    model = Actor
    template_name = 'movie_app/all_actor.html'
    context_object_name = 'actors'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movie_app/one_actor.html'


def get_rate_movie(request):
    form = MovieForm()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponseRedirect('/done_review')
    return render(request, 'movie_app/one_movie.html', context={'form': form})


def done_review(request):
    return render(request, 'movie_app/done_review.html')

def main_page(request):
    return render(request, 'movie_app/all_movie.html')
