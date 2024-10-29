from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from .forms import MovieForm
from .models import Movie, Director, Actor
from .models import Feedback
from django.views.generic import ListView, DetailView
from bs4 import BeautifulSoup
from django.http import JsonResponse
import requests
from django.utils.text import slugify
from datetime import datetime


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
    return render(request, 'movie_app/home_page.html')


def parse_movies(request):
    url = 'https://ticketon.kz/cinema'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    movies = []

    for movie in soup.find_all('a', class_='list-item__link'):
        link = 'https://ticketon.kz' + movie.get('href')
        title_tag = movie.find('span', class_='list-item__event')
        if title_tag:
            title = title_tag.get_text(strip=True)
            movies.append({'title': title, 'url': link})

    for movie_data in movies:
        response = requests.get(movie_data['url'])
        movie_soup = BeautifulSoup(response.content, 'html.parser')

        # Инициализация переменных для данных о фильме
        year = 'Не указан'
        distributor = '[Дистрибьютор не указан]'
        country = 'Не указана'
        director_name = 'Не указан'
        cast_names = []
        genre = 'Не указан'
        duration = 'Не указана'
        age_rating = 'Не указано'
        premiere_date = 'Не указана'

        # Извлечение данных
        for p in movie_soup.find_all('p'):
            strong_tag = p.find('strong')
            if strong_tag:
                label = strong_tag.get_text(strip=True).lower()
                value = p.get_text(strip=True).replace(strong_tag.get_text(strip=True), '').strip(' :')

                if 'год выпуска' in label:
                    year = value
                elif 'дистрибьютор' in label:
                    distributor = value
                elif 'страна производства' in label:
                    country = value
                elif 'режиссер' in label:
                    director_name = value
                elif 'главные роли' in label:
                    cast_names = value.split(', ')
                elif 'жанр' in label:
                    genre = value
                elif 'продолжительность' in label:
                    duration = value
                elif 'возрастное ограничение' in label:
                    age_rating = value


        # Сохранение режиссера
        director, _ = Director.objects.get_or_create(first_name=director_name.split()[0],
                                                     last_name=director_name.split()[1])

        # Сохранение актеров
        actors = []
        for actor_name in cast_names:
            actor_first_name, actor_last_name = actor_name.split(' ', 1)
            actor, _ = Actor.objects.get_or_create(first_name=actor_first_name, last_name=actor_last_name)
            actors.append(actor)

        movie = Movie(
            name=title,
            year=int(year) if year.isdigit() else None,
            director=director,
            budget=1000000,
            rating=7,
            slug=slugify(title)
        )
        movie.save()
        movie.actor.set(actors)
        movie.save()

    return render(request, 'movie_app/success.html', {'movies': movies})
